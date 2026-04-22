import csv
import io
import json
from datetime import datetime
from typing import Dict, List

from sqlalchemy.orm import Session

from app.models.v2 import (
    CommodityV2,
    CustomerAssetV2,
    EntityRelationshipV2,
    EntityV2,
    ExposureLinkV2,
    FacilityV2,
    PortV2,
    RouteV2,
    SupplierV2,
)


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
        created_ports = 0
        created_routes = 0
        created_commodities = 0
        created_assets = 0
        created_relationships = 0
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
                elif source_object_type == "port":
                    created_ports += int(self._ensure_port(source_object_id, row))
                elif source_object_type == "route":
                    created_routes += int(self._ensure_route(source_object_id, row))
                elif source_object_type == "commodity":
                    created_commodities += int(self._ensure_commodity(source_object_id, row))
                elif source_object_type in {"customer_asset", "asset"}:
                    created_assets += int(self._ensure_customer_asset(customer_id, source_object_id, row))
                else:
                    raise ValueError(f"unsupported source_object_type '{source_object_type}'")

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
                        metadata_json=json.dumps(self._build_link_metadata(row)),
                        created_at=datetime.utcnow(),
                    )
                )
                created_relationships += int(self._ensure_entity_relationship(source_object_type, source_object_id, target_entity.id, row))
                created_links += 1
            except Exception as exc:  # noqa: BLE001
                errors.append(f"row {index}: {exc}")

        self.db.commit()
        return {
            "created_links": created_links,
            "created_suppliers": created_suppliers,
            "created_facilities": created_facilities,
            "created_ports": created_ports,
            "created_routes": created_routes,
            "created_commodities": created_commodities,
            "created_assets": created_assets,
            "created_relationships": created_relationships,
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

        supplier_name = (row.get("source_object_name") or supplier_id).strip()
        entity = self._get_or_create_entity(supplier_name, "company")
        self.db.add(
            SupplierV2(
                id=supplier_id,
                customer_id=customer_id,
                entity_id=entity.id,
                supplier_name=supplier_name,
                tier_level=self._to_int(row.get("tier_level")),
                country_code=(row.get("source_country_code") or None),
                criticality_score=self._to_float(row.get("criticality_score")),
                metadata_json=json.dumps(self._build_object_metadata(row)),
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

        facility_name = (row.get("source_object_name") or facility_id).strip()
        entity = self._get_or_create_entity(facility_name, "facility")
        self.db.add(
            FacilityV2(
                id=facility_id,
                customer_id=customer_id,
                entity_id=entity.id,
                facility_name=facility_name,
                facility_type=(row.get("source_object_subtype") or None),
                country_code=(row.get("source_country_code") or None),
                criticality_score=self._to_float(row.get("criticality_score")),
                lat=self._to_float(row.get("lat")),
                lng=self._to_float(row.get("lng")),
                metadata_json=json.dumps(self._build_object_metadata(row)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_port(self, port_id: str, row: Dict[str, str]) -> bool:
        existing = self.db.query(PortV2).filter(PortV2.id == port_id).first()
        if existing:
            return False

        port_name = (row.get("source_object_name") or port_id).strip()
        entity = self._get_or_create_entity(port_name, "port")
        self.db.add(
            PortV2(
                id=port_id,
                entity_id=entity.id,
                port_code=(row.get("source_object_code") or port_id).strip(),
                port_name=port_name,
                country_code=(row.get("source_country_code") or None),
                lat=self._to_float(row.get("lat")),
                lng=self._to_float(row.get("lng")),
                metadata_json=json.dumps(self._build_object_metadata(row)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_route(self, route_id: str, row: Dict[str, str]) -> bool:
        existing = self.db.query(RouteV2).filter(RouteV2.id == route_id).first()
        if existing:
            return False

        route_name = (row.get("source_object_name") or route_id).strip()
        entity = self._get_or_create_entity(route_name, "route")
        origin_port_id = (row.get("origin_port_id") or "").strip() or None
        destination_port_id = (row.get("destination_port_id") or "").strip() or None
        if origin_port_id:
            self._ensure_port(
                origin_port_id,
                {
                    "source_object_name": (row.get("origin_port_name") or origin_port_id),
                    "source_object_code": (row.get("origin_port_code") or origin_port_id),
                    "source_country_code": (row.get("origin_country_code") or row.get("source_country_code") or ""),
                },
            )
        if destination_port_id:
            self._ensure_port(
                destination_port_id,
                {
                    "source_object_name": (row.get("destination_port_name") or destination_port_id),
                    "source_object_code": (row.get("destination_port_code") or destination_port_id),
                    "source_country_code": (row.get("destination_country_code") or row.get("source_country_code") or ""),
                },
            )
        self.db.add(
            RouteV2(
                id=route_id,
                entity_id=entity.id,
                route_name=route_name,
                route_type=(row.get("source_object_subtype") or row.get("route_type") or None),
                origin_port_id=origin_port_id,
                destination_port_id=destination_port_id,
                metadata_json=json.dumps(self._build_object_metadata(row)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_commodity(self, commodity_id: str, row: Dict[str, str]) -> bool:
        existing = self.db.query(CommodityV2).filter(CommodityV2.id == commodity_id).first()
        if existing:
            return False

        commodity_name = (row.get("source_object_name") or commodity_id).strip()
        entity = self._get_or_create_entity(commodity_name, "commodity")
        self.db.add(
            CommodityV2(
                id=commodity_id,
                entity_id=entity.id,
                commodity_code=(row.get("source_object_code") or commodity_id).strip(),
                commodity_name=commodity_name,
                sector=(row.get("sector") or None),
                metadata_json=json.dumps(self._build_object_metadata(row)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_customer_asset(self, customer_id: str, asset_id: str, row: Dict[str, str]) -> bool:
        existing = (
            self.db.query(CustomerAssetV2)
            .filter(CustomerAssetV2.customer_id == customer_id, CustomerAssetV2.id == asset_id)
            .first()
        )
        if existing:
            return False

        entity = None
        linked_name = (row.get("source_entity_name") or "").strip()
        linked_type = (row.get("source_entity_type") or "financial_asset").strip().lower()
        if linked_name:
            entity = self._get_or_create_entity(linked_name, linked_type)

        self.db.add(
            CustomerAssetV2(
                id=asset_id,
                customer_id=customer_id,
                entity_id=entity.id if entity else None,
                asset_label=(row.get("source_object_name") or asset_id).strip(),
                asset_type=(row.get("source_object_subtype") or None),
                criticality_score=self._to_float(row.get("criticality_score")),
                metadata_json=json.dumps(self._build_object_metadata(row)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _ensure_entity_relationship(
        self,
        source_object_type: str,
        source_object_id: str,
        target_entity_id: str,
        row: Dict[str, str],
    ) -> bool:
        source_entity_id = self._resolve_source_entity_id(source_object_type, source_object_id)
        if not source_entity_id:
            return False
        relationship_type = (row.get("relationship_type") or "").strip()
        existing = (
            self.db.query(EntityRelationshipV2)
            .filter(
                EntityRelationshipV2.source_entity_id == source_entity_id,
                EntityRelationshipV2.target_entity_id == target_entity_id,
                EntityRelationshipV2.relationship_type == relationship_type,
            )
            .first()
        )
        if existing:
            return False
        self.db.add(
            EntityRelationshipV2(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relationship_type=relationship_type,
                weight=self._to_float(row.get("exposure_weight")),
                metadata_json=json.dumps(self._build_link_metadata(row)),
                created_at=datetime.utcnow(),
            )
        )
        self.db.flush()
        return True

    def _resolve_source_entity_id(self, source_object_type: str, source_object_id: str) -> str | None:
        source_object_type = source_object_type.lower()
        if source_object_type == "supplier":
            row = self.db.query(SupplierV2).filter(SupplierV2.id == source_object_id).first()
            return row.entity_id if row else None
        if source_object_type == "facility":
            row = self.db.query(FacilityV2).filter(FacilityV2.id == source_object_id).first()
            return row.entity_id if row else None
        if source_object_type == "port":
            row = self.db.query(PortV2).filter(PortV2.id == source_object_id).first()
            return row.entity_id if row else None
        if source_object_type == "route":
            row = self.db.query(RouteV2).filter(RouteV2.id == source_object_id).first()
            return row.entity_id if row else None
        if source_object_type == "commodity":
            row = self.db.query(CommodityV2).filter(CommodityV2.id == source_object_id).first()
            return row.entity_id if row else None
        if source_object_type in {"customer_asset", "asset"}:
            row = self.db.query(CustomerAssetV2).filter(CustomerAssetV2.id == source_object_id).first()
            return row.entity_id if row else None
        return None

    @staticmethod
    def _build_object_metadata(row: Dict[str, str]) -> Dict[str, str]:
        return {
            key: value
            for key, value in row.items()
            if key.startswith("source_") and value not in (None, "")
        }

    @staticmethod
    def _build_link_metadata(row: Dict[str, str]) -> Dict[str, str]:
        return {
            key: value
            for key, value in row.items()
            if key not in {"source_object_type", "source_object_id", "relationship_type", "target_entity_name", "target_entity_type"}
            and value not in (None, "")
        }

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
