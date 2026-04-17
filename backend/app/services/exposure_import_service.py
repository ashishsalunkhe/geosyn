import csv
import io
from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.v2 import EntityV2, ExposureLinkV2, FacilityV2, SupplierV2


class ExposureImportService:
    REQUIRED_COLUMNS = {
        "source_object_type",
        "source_object_id",
        "relationship_type",
        "target_entity_name",
    }

    def __init__(self, db: Session):
        self.db = db

    def import_csv(self, csv_text: str, customer_id: str) -> Dict[str, object]:
        reader = csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing a header row.")

        missing = self.REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        created_links = 0
        created_suppliers = 0
        created_facilities = 0
        errors: List[str] = []

        for index, row in enumerate(reader, start=2):
            try:
                source_object_type = (row.get("source_object_type") or "").strip().lower()
                source_object_id = (row.get("source_object_id") or "").strip()
                relationship_type = (row.get("relationship_type") or "").strip()
                target_entity_name = (row.get("target_entity_name") or "").strip()
                target_entity_type = (row.get("target_entity_type") or "company").strip().lower()

                if not source_object_type or not source_object_id or not relationship_type or not target_entity_name:
                    raise ValueError("required value missing")

                target_entity = self._get_or_create_entity(target_entity_name, target_entity_type)

                if source_object_type == "supplier":
                    created_suppliers += int(self._ensure_supplier(customer_id, source_object_id, row))
                elif source_object_type == "facility":
                    created_facilities += int(self._ensure_facility(customer_id, source_object_id, row))

                existing = (
                    self.db.query(ExposureLinkV2)
                    .filter(
                        ExposureLinkV2.customer_id == customer_id,
                        ExposureLinkV2.source_object_type == source_object_type,
                        ExposureLinkV2.source_object_id == source_object_id,
                        ExposureLinkV2.target_entity_id == target_entity.id,
                        ExposureLinkV2.relationship_type == relationship_type,
                    )
                    .first()
                )
                if existing:
                    continue

                self.db.add(
                    ExposureLinkV2(
                        customer_id=customer_id,
                        source_object_type=source_object_type,
                        source_object_id=source_object_id,
                        target_entity_id=target_entity.id,
                        relationship_type=relationship_type,
                        criticality_score=self._to_float(row.get("criticality_score")),
                        exposure_weight=self._to_float(row.get("exposure_weight")),
                        confidence_score=self._to_float(row.get("confidence_score")),
                        created_at=datetime.utcnow(),
                    )
                )
                created_links += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"row {index}: {exc}")

        self.db.commit()
        return {
            "created_links": created_links,
            "created_suppliers": created_suppliers,
            "created_facilities": created_facilities,
            "errors": errors,
        }

    def _get_or_create_entity(self, name: str, entity_type: str) -> EntityV2:
        entity = (
            self.db.query(EntityV2)
            .filter(EntityV2.canonical_name == name, EntityV2.entity_type == entity_type)
            .first()
        )
        if entity:
            return entity

        entity = EntityV2(
            entity_type=entity_type,
            canonical_name=name,
            display_name=name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def _ensure_supplier(self, customer_id: str, supplier_id: str, row: Dict[str, str]) -> bool:
        existing = (
            self.db.query(SupplierV2)
            .filter(SupplierV2.customer_id == customer_id, SupplierV2.id == supplier_id)
            .first()
        )
        if existing:
            return False

        self.db.add(
            SupplierV2(
                id=supplier_id,
                customer_id=customer_id,
                supplier_name=(row.get("source_object_name") or supplier_id).strip(),
                tier_level=self._to_int(row.get("tier_level")),
                country_code=(row.get("source_country_code") or None),
                criticality_score=self._to_float(row.get("criticality_score")),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_facility(self, customer_id: str, facility_id: str, row: Dict[str, str]) -> bool:
        existing = (
            self.db.query(FacilityV2)
            .filter(FacilityV2.customer_id == customer_id, FacilityV2.id == facility_id)
            .first()
        )
        if existing:
            return False

        self.db.add(
            FacilityV2(
                id=facility_id,
                customer_id=customer_id,
                facility_name=(row.get("source_object_name") or facility_id).strip(),
                facility_type=(row.get("source_object_subtype") or None),
                country_code=(row.get("source_country_code") or None),
                criticality_score=self._to_float(row.get("criticality_score")),
                lat=self._to_float(row.get("lat")),
                lng=self._to_float(row.get("lng")),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    @staticmethod
    def _to_float(value: str | None) -> float | None:
        if value is None or value == "":
            return None
        return float(value)

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None
        return int(value)
