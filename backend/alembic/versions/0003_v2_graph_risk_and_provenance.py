"""v2 graph, risk, and provenance

Revision ID: 0003_v2_graph_risk_and_provenance
Revises: 0002_v2_alerts_and_exposure
Create Date: 2026-04-17 00:30:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "3_graph"
down_revision = "2_alerts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingest_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("legacy_source_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_tier", sa.String(), nullable=True),
        sa.Column("base_url", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("language_code", sa.String(), nullable=True),
        sa.Column("reliability_score", sa.Float(), nullable=True),
        sa.Column("license_class", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name", name="uq_ingest_sources_name"))
    op.create_index("ix_ingest_sources_legacy_source_id", "ingest_sources", ["legacy_source_id"], unique=True)
    op.create_index("ix_ingest_sources_name", "ingest_sources", ["name"])
    op.create_index("ix_ingest_sources_source_type", "ingest_sources", ["source_type"])
    op.create_index("ix_ingest_sources_source_tier", "ingest_sources", ["source_tier"])
    op.create_index("ix_ingest_sources_country_code", "ingest_sources", ["country_code"])
    op.create_index("ix_ingest_sources_language_code", "ingest_sources", ["language_code"])

    op.create_table(
        "evidence_documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("legacy_document_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.String(length=36), sa.ForeignKey("ingest_sources.id"), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("canonical_url", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=True),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("language_code", sa.String(), nullable=True),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("event_time", sa.DateTime(), nullable=True),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
        sa.Column("content_hash", sa.String(), nullable=True),
        sa.Column("raw_payload_ref", sa.String(), nullable=True),
        sa.Column("source_confidence", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.UniqueConstraint("source_id", "external_id", name="uq_evidence_documents_source_external_id"))
    op.create_index("ix_evidence_documents_legacy_document_id", "evidence_documents", ["legacy_document_id"], unique=True)
    op.create_index("ix_evidence_documents_source_id", "evidence_documents", ["source_id"])
    op.create_index("ix_evidence_documents_title", "evidence_documents", ["title"])
    op.create_index("ix_evidence_documents_language_code", "evidence_documents", ["language_code"])
    op.create_index("ix_evidence_documents_country_code", "evidence_documents", ["country_code"])
    op.create_index("ix_evidence_documents_published_at", "evidence_documents", ["published_at"])
    op.create_index("ix_evidence_documents_event_time", "evidence_documents", ["event_time"])
    op.create_index("ix_evidence_documents_ingested_at", "evidence_documents", ["ingested_at"])
    op.create_index("ix_evidence_documents_content_hash", "evidence_documents", ["content_hash"])

    op.create_table(
        "document_fragments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("evidence_documents.id"), nullable=False),
        sa.Column("fragment_type", sa.String(), nullable=False),
        sa.Column("fragment_text", sa.Text(), nullable=False),
        sa.Column("start_offset", sa.Integer(), nullable=True),
        sa.Column("end_offset", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_document_fragments_document_id", "document_fragments", ["document_id"])
    op.create_index("ix_document_fragments_fragment_type", "document_fragments", ["fragment_type"])

    op.create_table(
        "document_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("evidence_documents.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=False),
        sa.Column("mention_text", sa.String(), nullable=True),
        sa.Column("mention_role", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("document_id", "entity_id", "mention_text", name="uq_document_entities_doc_entity_mention"))
    op.create_index("ix_document_entities_document_id", "document_entities", ["document_id"])
    op.create_index("ix_document_entities_entity_id", "document_entities", ["entity_id"])
    op.create_index("ix_document_entities_mention_role", "document_entities", ["mention_role"])

    op.create_table(
        "entity_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=False),
        sa.Column("alias", sa.String(), nullable=False),
        sa.Column("alias_type", sa.String(), nullable=True),
        sa.Column("language_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("entity_id", "alias", name="uq_entity_aliases_entity_alias"))
    op.create_index("ix_entity_aliases_entity_id", "entity_aliases", ["entity_id"])
    op.create_index("ix_entity_aliases_alias", "entity_aliases", ["alias"])
    op.create_index("ix_entity_aliases_alias_type", "entity_aliases", ["alias_type"])

    op.create_table(
        "entity_relationships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source_entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=False),
        sa.Column("relationship_type", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("valid_from", sa.DateTime(), nullable=True),
        sa.Column("valid_to", sa.DateTime(), nullable=True),
        sa.Column("source_document_id", sa.String(length=36), sa.ForeignKey("evidence_documents.id"), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("source_entity_id", "target_entity_id", "relationship_type", name="uq_entity_relationships_edge"))
    op.create_index("ix_entity_relationships_source_entity_id", "entity_relationships", ["source_entity_id"])
    op.create_index("ix_entity_relationships_target_entity_id", "entity_relationships", ["target_entity_id"])
    op.create_index("ix_entity_relationships_relationship_type", "entity_relationships", ["relationship_type"])
    op.create_index("ix_entity_relationships_source_document_id", "entity_relationships", ["source_document_id"])

    op.create_table(
        "ports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("port_code", sa.String(), nullable=True),
        sa.Column("port_name", sa.String(), nullable=False),
        sa.Column("country_code", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("port_code", name="uq_ports_port_code"))
    op.create_index("ix_ports_entity_id", "ports", ["entity_id"], unique=True)
    op.create_index("ix_ports_port_code", "ports", ["port_code"])
    op.create_index("ix_ports_port_name", "ports", ["port_name"])
    op.create_index("ix_ports_country_code", "ports", ["country_code"])

    op.create_table(
        "routes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("route_name", sa.String(), nullable=False),
        sa.Column("route_type", sa.String(), nullable=True),
        sa.Column("origin_port_id", sa.String(length=36), sa.ForeignKey("ports.id"), nullable=True),
        sa.Column("destination_port_id", sa.String(length=36), sa.ForeignKey("ports.id"), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_routes_entity_id", "routes", ["entity_id"], unique=True)
    op.create_index("ix_routes_route_name", "routes", ["route_name"])
    op.create_index("ix_routes_route_type", "routes", ["route_type"])
    op.create_index("ix_routes_origin_port_id", "routes", ["origin_port_id"])
    op.create_index("ix_routes_destination_port_id", "routes", ["destination_port_id"])

    op.create_table(
        "commodities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("commodity_code", sa.String(), nullable=True),
        sa.Column("commodity_name", sa.String(), nullable=False),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("commodity_code", name="uq_commodities_commodity_code"))
    op.create_index("ix_commodities_entity_id", "commodities", ["entity_id"], unique=True)
    op.create_index("ix_commodities_commodity_code", "commodities", ["commodity_code"])
    op.create_index("ix_commodities_commodity_name", "commodities", ["commodity_name"])
    op.create_index("ix_commodities_sector", "commodities", ["sector"])

    op.create_table(
        "customer_assets",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities_v2.id"), nullable=True),
        sa.Column("asset_label", sa.String(), nullable=False),
        sa.Column("asset_type", sa.String(), nullable=True),
        sa.Column("criticality_score", sa.Float(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_index("ix_customer_assets_customer_id", "customer_assets", ["customer_id"])
    op.create_index("ix_customer_assets_entity_id", "customer_assets", ["entity_id"])
    op.create_index("ix_customer_assets_asset_label", "customer_assets", ["asset_label"])
    op.create_index("ix_customer_assets_asset_type", "customer_assets", ["asset_type"])

    op.create_table(
        "risk_scores",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("score_type", sa.String(), nullable=False),
        sa.Column("score_value", sa.Float(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("rationale_text", sa.Text(), nullable=True),
        sa.Column("scored_at", sa.DateTime(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.UniqueConstraint("event_id", "customer_id", "score_type", name="uq_risk_scores_event_customer_type"))
    op.create_index("ix_risk_scores_event_id", "risk_scores", ["event_id"])
    op.create_index("ix_risk_scores_customer_id", "risk_scores", ["customer_id"])
    op.create_index("ix_risk_scores_score_type", "risk_scores", ["score_type"])
    op.create_index("ix_risk_scores_score_value", "risk_scores", ["score_value"])
    op.create_index("ix_risk_scores_severity", "risk_scores", ["severity"])
    op.create_index("ix_risk_scores_scored_at", "risk_scores", ["scored_at"])

    op.create_table(
        "evaluation_labels",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("customer_id", sa.String(length=36), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("alert_id", sa.String(length=36), sa.ForeignKey("alerts_v2.id"), nullable=True),
        sa.Column("label_type", sa.String(), nullable=False),
        sa.Column("label_value", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("labeled_by", sa.String(), nullable=True),
        sa.Column("labeled_at", sa.DateTime(), nullable=False),
        sa.Column("metadata", sa.Text(), nullable=True))
    op.create_index("ix_evaluation_labels_event_id", "evaluation_labels", ["event_id"])
    op.create_index("ix_evaluation_labels_customer_id", "evaluation_labels", ["customer_id"])
    op.create_index("ix_evaluation_labels_alert_id", "evaluation_labels", ["alert_id"])
    op.create_index("ix_evaluation_labels_label_type", "evaluation_labels", ["label_type"])
    op.create_index("ix_evaluation_labels_label_value", "evaluation_labels", ["label_value"])
    op.create_index("ix_evaluation_labels_labeled_at", "evaluation_labels", ["labeled_at"])


def downgrade() -> None:
    op.drop_index("ix_evaluation_labels_labeled_at", table_name="evaluation_labels")
    op.drop_index("ix_evaluation_labels_label_value", table_name="evaluation_labels")
    op.drop_index("ix_evaluation_labels_label_type", table_name="evaluation_labels")
    op.drop_index("ix_evaluation_labels_alert_id", table_name="evaluation_labels")
    op.drop_index("ix_evaluation_labels_customer_id", table_name="evaluation_labels")
    op.drop_index("ix_evaluation_labels_event_id", table_name="evaluation_labels")
    op.drop_table("evaluation_labels")

    op.drop_index("ix_risk_scores_scored_at", table_name="risk_scores")
    op.drop_index("ix_risk_scores_severity", table_name="risk_scores")
    op.drop_index("ix_risk_scores_score_value", table_name="risk_scores")
    op.drop_index("ix_risk_scores_score_type", table_name="risk_scores")
    op.drop_index("ix_risk_scores_customer_id", table_name="risk_scores")
    op.drop_index("ix_risk_scores_event_id", table_name="risk_scores")
    op.drop_table("risk_scores")

    op.drop_index("ix_customer_assets_asset_type", table_name="customer_assets")
    op.drop_index("ix_customer_assets_asset_label", table_name="customer_assets")
    op.drop_index("ix_customer_assets_entity_id", table_name="customer_assets")
    op.drop_index("ix_customer_assets_customer_id", table_name="customer_assets")
    op.drop_table("customer_assets")

    op.drop_index("ix_commodities_sector", table_name="commodities")
    op.drop_index("ix_commodities_commodity_name", table_name="commodities")
    op.drop_index("ix_commodities_commodity_code", table_name="commodities")
    op.drop_index("ix_commodities_entity_id", table_name="commodities")
    op.drop_table("commodities")

    op.drop_index("ix_routes_destination_port_id", table_name="routes")
    op.drop_index("ix_routes_origin_port_id", table_name="routes")
    op.drop_index("ix_routes_route_type", table_name="routes")
    op.drop_index("ix_routes_route_name", table_name="routes")
    op.drop_index("ix_routes_entity_id", table_name="routes")
    op.drop_table("routes")

    op.drop_index("ix_ports_country_code", table_name="ports")
    op.drop_index("ix_ports_port_name", table_name="ports")
    op.drop_index("ix_ports_port_code", table_name="ports")
    op.drop_index("ix_ports_entity_id", table_name="ports")
    op.drop_table("ports")

    op.drop_index("ix_entity_relationships_source_document_id", table_name="entity_relationships")
    op.drop_index("ix_entity_relationships_relationship_type", table_name="entity_relationships")
    op.drop_index("ix_entity_relationships_target_entity_id", table_name="entity_relationships")
    op.drop_index("ix_entity_relationships_source_entity_id", table_name="entity_relationships")
    op.drop_table("entity_relationships")

    op.drop_index("ix_entity_aliases_alias_type", table_name="entity_aliases")
    op.drop_index("ix_entity_aliases_alias", table_name="entity_aliases")
    op.drop_index("ix_entity_aliases_entity_id", table_name="entity_aliases")
    op.drop_table("entity_aliases")

    op.drop_index("ix_document_entities_mention_role", table_name="document_entities")
    op.drop_index("ix_document_entities_entity_id", table_name="document_entities")
    op.drop_index("ix_document_entities_document_id", table_name="document_entities")
    op.drop_table("document_entities")

    op.drop_index("ix_document_fragments_fragment_type", table_name="document_fragments")
    op.drop_index("ix_document_fragments_document_id", table_name="document_fragments")
    op.drop_table("document_fragments")

    op.drop_index("ix_evidence_documents_content_hash", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_ingested_at", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_event_time", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_published_at", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_country_code", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_language_code", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_title", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_source_id", table_name="evidence_documents")
    op.drop_index("ix_evidence_documents_legacy_document_id", table_name="evidence_documents")
    op.drop_table("evidence_documents")

    op.drop_index("ix_ingest_sources_language_code", table_name="ingest_sources")
    op.drop_index("ix_ingest_sources_country_code", table_name="ingest_sources")
    op.drop_index("ix_ingest_sources_source_tier", table_name="ingest_sources")
    op.drop_index("ix_ingest_sources_source_type", table_name="ingest_sources")
    op.drop_index("ix_ingest_sources_name", table_name="ingest_sources")
    op.drop_index("ix_ingest_sources_legacy_source_id", table_name="ingest_sources")
    op.drop_table("ingest_sources")
