from typing import List, Dict, Any, Optional
from app.core.db import db

class ProdQualityService:
    @staticmethod
    def get_qc_inspections(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT qc.*, o.order_number, i.item_code, i.item_name
                FROM prod_qc_inspections qc
                JOIN prod_orders o ON qc.order_id = o.id
                JOIN inv_items i ON o.item_id = i.id
                WHERE qc.company_id = ?
                ORDER BY qc.code DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT qc.*, o.order_number, i.item_code, i.item_name
            FROM prod_qc_inspections qc
            JOIN prod_orders o ON qc.order_id = o.id
            JOIN inv_items i ON o.item_id = i.id
            ORDER BY qc.code DESC
            """
        )

    @staticmethod
    def get_qc_by_id(qc_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT qc.*, o.order_number, i.item_code, i.item_name, c.name AS company_name
            FROM prod_qc_inspections qc
            JOIN prod_orders o ON qc.order_id = o.id
            JOIN inv_items i ON o.item_id = i.id
            JOIN companies c ON qc.company_id = c.id
            WHERE qc.id = ?
            """,
            (qc_id,)
        )

    @staticmethod
    def get_downtime_logs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT dt.*, res.resource_name, res.resource_code, p.plant_name
                FROM prod_downtime_logs dt
                JOIN prod_resources res ON dt.resource_id = res.id
                JOIN prod_plants p ON res.plant_id = p.id
                WHERE dt.company_id = ?
                ORDER BY dt.code DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT dt.*, res.resource_name, res.resource_code, p.plant_name
            FROM prod_downtime_logs dt
            JOIN prod_resources res ON dt.resource_id = res.id
            JOIN prod_plants p ON res.plant_id = p.id
            ORDER BY dt.code DESC
            """
        )

    @staticmethod
    def get_import_data_profiles() -> List[Dict[str, Any]]:
        return [
            {"profile_name": "Opening Raw Materials & WIP Inventory", "file_type": "CSV / Excel (.xlsx)", "entity_target": "Opening Production Stock", "last_imported": "2026-08-01 09:30", "status": "SYNCED", "records_count": 240},
            {"profile_name": "Monthly Sales Demand per Finished SKU", "file_type": "CSV / Excel (.xlsx)", "entity_target": "Demand Forecast (MRP)", "last_imported": "2026-08-15 14:15", "status": "SYNCED", "records_count": 85},
            {"profile_name": "Engineering BOM Recipes & Component Quantities", "file_type": "Excel XML (.xlsx)", "entity_target": "BOM Items Master", "last_imported": "2026-08-10 11:00", "status": "SYNCED", "records_count": 160},
            {"profile_name": "Resource Work Center Capacities & Shifts", "file_type": "CSV (.csv)", "entity_target": "Capacity Scheduling", "last_imported": "2026-08-02 16:45", "status": "SYNCED", "records_count": 32},
        ]

    @staticmethod
    def execute_year_end_process(company_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "fiscal_year": "FY 2026-2027",
            "wip_orders_carried_forward": 4,
            "total_wip_value": 245800.00,
            "cost_variance_closed_to_cogs": 4850.00,
            "status": "YEAR_END_WIP_COMMITTED"
        }
