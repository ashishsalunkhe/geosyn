from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Iterable, Optional

from sqlalchemy.orm import Session

from app.models.domain import Document, Source
from app.models.v2 import (
    DocumentFragmentV2,
    DocumentEntityV2,
    EntityAliasV2,
    EvidenceDocumentV2,
    IngestSourceV2,
)
from app.utils.datalake_manager import datalake


class ProvenanceServiceV2:
    def __init__(self, db: Session):
        self.db = db

    def ensure_ingest_source(self, legacy_source: Source) -> IngestSourceV2:
        existing = (
            self.db.query(IngestSourceV2)
            .filter(IngestSourceV2.legacy_source_id == legacy_source.id)
            .first()
        )
        if existing:
            existing.reliability_score = legacy_source.reliability_score
            existing.updated_at = datetime.utcnow()
            self.db.flush()
            return existing

        source = IngestSourceV2(
            legacy_source_id=legacy_source.id,
            name=legacy_source.name,
            source_type=legacy_source.source_type or "unknown",
            source_tier=self._derive_source_tier(legacy_source.reliability_score),
            reliability_score=legacy_source.reliability_score,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(source)
        self.db.flush()
        return source

    def store_raw_payload(self, source_name: str, raw_payload: object, metadata: Optional[dict] = None) -> str:
        safe_source = source_name.lower().replace(" ", "_").replace("/", "_")
        return datalake.store_raw_signal(safe_source, raw_payload, metadata=metadata)

    def ensure_evidence_document(
        self,
        legacy_document: Document,
        *,
        raw_payload_ref: Optional[str] = None,
        source_confidence: Optional[float] = None,
    ) -> EvidenceDocumentV2:
        existing = (
            self.db.query(EvidenceDocumentV2)
            .filter(EvidenceDocumentV2.legacy_document_id == legacy_document.id)
            .first()
        )
        if existing:
            if raw_payload_ref and not existing.raw_payload_ref:
                existing.raw_payload_ref = raw_payload_ref
            if source_confidence is not None:
                existing.source_confidence = source_confidence
            existing.summary_text = existing.summary_text or self._derive_summary_text(legacy_document.content)
            self.db.flush()
            self._ensure_fragments(existing)
            self.sync_document_entities(existing)
            return existing

        ingest_source = self.ensure_ingest_source(legacy_document.source)
        evidence_document = EvidenceDocumentV2(
            legacy_document_id=legacy_document.id,
            source_id=ingest_source.id,
            external_id=legacy_document.external_id,
            canonical_url=legacy_document.url,
            title=legacy_document.title or f"Document {legacy_document.id}",
            body_text=legacy_document.content,
            summary_text=self._derive_summary_text(legacy_document.content),
            published_at=legacy_document.published_at,
            event_time=legacy_document.published_at,
            ingested_at=legacy_document.normalized_at or datetime.utcnow(),
            content_hash=self._content_hash(legacy_document.content or ""),
            raw_payload_ref=raw_payload_ref,
            source_confidence=source_confidence if source_confidence is not None else legacy_document.source.reliability_score,
        )
        self.db.add(evidence_document)
        self.db.flush()
        self._ensure_fragments(evidence_document)
        self.sync_document_entities(evidence_document)
        return evidence_document

    def sync_document_entities(self, evidence_document: EvidenceDocumentV2) -> None:
        legacy_document = evidence_document.legacy_document
        if not legacy_document:
            return
        from app.services.event_service_v2 import EventServiceV2

        event_service = EventServiceV2(self.db)
        existing_pairs = {
            (row.entity_id, row.mention_text or "")
            for row in self.db.query(DocumentEntityV2)
            .filter(DocumentEntityV2.document_id == evidence_document.id)
            .all()
        }
        for legacy_entity in legacy_document.entities:
            entity_v2 = event_service.ensure_entity_v2(legacy_entity)
            mention = legacy_entity.name
            pair = (entity_v2.id, mention)
            if pair not in existing_pairs:
                self.db.add(
                    DocumentEntityV2(
                        document_id=evidence_document.id,
                        entity_id=entity_v2.id,
                        mention_text=mention,
                        mention_role="mentioned",
                        confidence_score=1.0,
                        created_at=datetime.utcnow(),
                    )
                )
            self._ensure_alias(entity_v2.id, legacy_entity.name)
        self.db.flush()

    def backfill_documents(self, documents: Iterable[Document]) -> None:
        for document in documents:
            self.ensure_evidence_document(document)
        self.db.flush()

    def _ensure_alias(self, entity_id: str, alias: str) -> None:
        existing = (
            self.db.query(EntityAliasV2)
            .filter(EntityAliasV2.entity_id == entity_id, EntityAliasV2.alias == alias)
            .first()
        )
        if existing:
            return
        self.db.add(
            EntityAliasV2(
                entity_id=entity_id,
                alias=alias,
                alias_type="legacy_name",
                created_at=datetime.utcnow(),
            )
        )

    def _ensure_fragments(self, evidence_document: EvidenceDocumentV2) -> None:
        existing_types = {
            row.fragment_type
            for row in self.db.query(DocumentFragmentV2)
            .filter(DocumentFragmentV2.document_id == evidence_document.id)
            .all()
        }
        if evidence_document.title and "title" not in existing_types:
            self.db.add(
                DocumentFragmentV2(
                    document_id=evidence_document.id,
                    fragment_type="title",
                    fragment_text=evidence_document.title,
                    start_offset=0,
                    end_offset=len(evidence_document.title),
                    created_at=datetime.utcnow(),
                )
            )
        snippet = evidence_document.summary_text or self._derive_summary_text(evidence_document.body_text)
        if snippet and "summary" not in existing_types:
            self.db.add(
                DocumentFragmentV2(
                    document_id=evidence_document.id,
                    fragment_type="summary",
                    fragment_text=snippet,
                    start_offset=0,
                    end_offset=len(snippet),
                    created_at=datetime.utcnow(),
                )
            )

    @staticmethod
    def _derive_summary_text(content: Optional[str]) -> Optional[str]:
        if not content:
            return None
        normalized = " ".join(content.split())
        return normalized[:280] if normalized else None

    @staticmethod
    def _content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def _derive_source_tier(reliability_score: Optional[float]) -> str:
        score = reliability_score or 0.0
        if score >= 0.9:
            return "tier_1"
        if score >= 0.7:
            return "tier_2"
        return "tier_3"
