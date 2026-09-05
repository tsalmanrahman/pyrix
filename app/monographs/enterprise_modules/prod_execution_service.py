from typing import List, Dict, Any, Optional
from app.core.db import db

class ProdExecutionService:
    @staticmethod
    def get_requisitions(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT req.*, i.item_code, i.item_name, i.uom_code
                FROM prod_requisitions req
                JOIN inv_items i ON req.item_id = i.id
                WHERE req.company_id = ?
                ORDER BY req.code DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT req.*, i.item_code, i.item_name, i.uom_code
            FROM prod_requisitions req
            JOIN inv_items i ON req.item_id = i.id
            ORDER BY req.code DESC
            """
        )

    @staticmethod
    def get_orders(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT o.*, i.item_code, i.item_name, i.uom_code, p.plant_name, b.bom_code, b.revision_number,
                       req.requisition_number
                FROM prod_orders o
                JOIN inv_items i ON o.item_id = i.id
                JOIN prod_plants p ON o.plant_id = p.id
                JOIN prod_bom_headers b ON o.bom_id = b.id
                LEFT JOIN prod_requisitions req ON o.requisition_id = req.id
                WHERE o.company_id = ?
                ORDER BY o.code DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT o.*, i.item_code, i.item_name, i.uom_code, p.plant_name, b.bom_code, b.revision_number,
                   req.requisition_number
            FROM prod_orders o
            JOIN inv_items i ON o.item_id = i.id
            JOIN prod_plants p ON o.plant_id = p.id
            JOIN prod_bom_headers b ON o.bom_id = b.id
            LEFT JOIN prod_requisitions req ON o.requisition_id = req.id
            ORDER BY o.code DESC
            """
        )

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT o.*, i.item_code, i.item_name, i.uom_code, p.plant_name, p.plant_code, p.location AS plant_location,
                   b.bom_code, b.revision_number, c.name AS company_name
            FROM prod_orders o
            JOIN inv_items i ON o.item_id = i.id
            JOIN prod_plants p ON o.plant_id = p.id
            JOIN prod_bom_headers b ON o.bom_id = b.id
            JOIN companies c ON o.company_id = c.id
            WHERE o.id = ?
            """,
            (order_id,)
        )

    @staticmethod
    def get_job_cards(order_id: Optional[str] = None, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT jc.*, o.order_number, res.resource_name, res.resource_code, rt.routing_code
            FROM prod_job_cards jc
            JOIN prod_orders o ON jc.order_id = o.id
            JOIN prod_resources res ON jc.resource_id = res.id
            JOIN prod_routings rt ON jc.routing_id = rt.id
            WHERE 1=1
        """
        params = []
        if order_id:
            query += " AND jc.order_id = ?"
            params.append(order_id)
        if company_id:
            query += " AND o.company_id = ?"
            params.append(company_id)
        query += " ORDER BY jc.operation_seq ASC"
        return db.query(query, tuple(params))

    @staticmethod
    def get_material_issues(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT mi.*, o.order_number, i.item_code, i.item_name, i.uom_code, w.warehouse_name
                FROM prod_material_issues mi
                JOIN prod_orders o ON mi.order_id = o.id
                JOIN inv_items i ON mi.item_id = i.id
                JOIN inv_warehouses w ON mi.warehouse_id = w.id
                WHERE mi.company_id = ?
                ORDER BY mi.code DESC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT mi.*, o.order_number, i.item_code, i.item_name, i.uom_code, w.warehouse_name
            FROM prod_material_issues mi
            JOIN prod_orders o ON mi.order_id = o.id
            JOIN inv_items i ON mi.item_id = i.id
            JOIN inv_warehouses w ON mi.warehouse_id = w.id
            ORDER BY mi.code DESC
            """
        )

    @staticmethod
    def get_conversions(company_id: Optional[str] = None, conversion_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT conv.*, si.item_code AS source_code, si.item_name AS source_name,
                   ti.item_code AS target_code, ti.item_name AS target_name
            FROM prod_conversions conv
            JOIN inv_items si ON conv.source_item_id = si.id
            JOIN inv_items ti ON conv.target_item_id = ti.id
            WHERE 1=1
        """
        params = []
        if company_id:
            query += " AND conv.company_id = ?"
            params.append(company_id)
        if conversion_type:
            query += " AND conv.conversion_type = ?"
            params.append(conversion_type)
        query += " ORDER BY conv.code DESC"
        return db.query(query, tuple(params))

    @staticmethod
    def get_conversion_by_id(conversion_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT conv.*, si.item_code AS source_code, si.item_name AS source_name,
                   ti.item_code AS target_code, ti.item_name AS target_name, c.name AS company_name
            FROM prod_conversions conv
            JOIN inv_items si ON conv.source_item_id = si.id
            JOIN inv_items ti ON conv.target_item_id = ti.id
            JOIN companies c ON conv.company_id = c.id
            WHERE conv.id = ?
            """,
            (conversion_id,)
        )
