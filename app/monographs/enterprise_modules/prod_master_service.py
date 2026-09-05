from typing import List, Dict, Any, Optional
from app.core.db import db

class ProdMasterService:
    @staticmethod
    def get_processes() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM prod_processes ORDER BY sequence_order ASC")

    @staticmethod
    def get_plants(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT p.*, c.name AS company_name, c.short_code AS company_code,
                       (SELECT COUNT(*) FROM prod_resources r WHERE r.plant_id = p.id) AS resource_count
                FROM prod_plants p
                JOIN companies c ON p.company_id = c.id
                WHERE p.company_id = ?
                ORDER BY p.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT p.*, c.name AS company_name, c.short_code AS company_code,
                   (SELECT COUNT(*) FROM prod_resources r WHERE r.plant_id = p.id) AS resource_count
            FROM prod_plants p
            JOIN companies c ON p.company_id = c.id
            ORDER BY p.code ASC
            """
        )

    @staticmethod
    def get_resources(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT r.*, p.plant_name, p.plant_code, c.short_code AS company_code
                FROM prod_resources r
                JOIN prod_plants p ON r.plant_id = p.id
                JOIN companies c ON r.company_id = c.id
                WHERE r.company_id = ?
                ORDER BY r.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT r.*, p.plant_name, p.plant_code, c.short_code AS company_code
            FROM prod_resources r
            JOIN prod_plants p ON r.plant_id = p.id
            JOIN companies c ON r.company_id = c.id
            ORDER BY r.code ASC
            """
        )

    @staticmethod
    def get_routings(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT rt.*, i.item_code, i.item_name, pr.process_name, pr.stage_type, res.resource_name, res.resource_code
                FROM prod_routings rt
                JOIN inv_items i ON rt.item_id = i.id
                JOIN prod_processes pr ON rt.process_id = pr.id
                JOIN prod_resources res ON rt.resource_id = res.id
                WHERE rt.company_id = ?
                ORDER BY rt.operation_sequence ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT rt.*, i.item_code, i.item_name, pr.process_name, pr.stage_type, res.resource_name, res.resource_code
            FROM prod_routings rt
            JOIN inv_items i ON rt.item_id = i.id
            JOIN prod_processes pr ON rt.process_id = pr.id
            JOIN prod_resources res ON rt.resource_id = res.id
            ORDER BY rt.operation_sequence ASC
            """
        )

    @staticmethod
    def get_capacity(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT cap.*, p.plant_name, res.resource_name, res.resource_code
                FROM prod_capacity cap
                JOIN prod_plants p ON cap.plant_id = p.id
                JOIN prod_resources res ON cap.resource_id = res.id
                WHERE cap.company_id = ?
                ORDER BY cap.code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT cap.*, p.plant_name, res.resource_name, res.resource_code
            FROM prod_capacity cap
            JOIN prod_plants p ON cap.plant_id = p.id
            JOIN prod_resources res ON cap.resource_id = res.id
            ORDER BY cap.code ASC
            """
        )

    @staticmethod
    def get_bom_headers(company_id: Optional[str] = None, bom_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT b.*, i.item_code, i.item_name, i.standard_cost,
                   (SELECT COUNT(*) FROM prod_bom_items bi WHERE bi.bom_id = b.id) AS total_components,
                   (SELECT ISNULL(SUM(bi.quantity * ci.standard_cost), 0) 
                    FROM prod_bom_items bi 
                    JOIN inv_items ci ON bi.component_item_id = ci.id 
                    WHERE bi.bom_id = b.id) AS total_bom_material_cost
            FROM prod_bom_headers b
            JOIN inv_items i ON b.item_id = i.id
            WHERE 1=1
        """
        params = []
        if company_id:
            query += " AND b.company_id = ?"
            params.append(company_id)
        if bom_type:
            query += " AND b.bom_type = ?"
            params.append(bom_type)
        query += " ORDER BY b.code ASC"
        return db.query(query, tuple(params))

    @staticmethod
    def get_bom_by_id(bom_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT b.*, i.item_code, i.item_name, i.standard_cost, c.name AS company_name
            FROM prod_bom_headers b
            JOIN inv_items i ON b.item_id = i.id
            JOIN companies c ON b.company_id = c.id
            WHERE b.id = ?
            """,
            (bom_id,)
        )

    @staticmethod
    def get_bom_items(bom_id: str) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT bi.*, i.item_code, i.item_name, i.standard_cost,
                   (bi.quantity * i.standard_cost) AS component_line_cost
            FROM prod_bom_items bi
            JOIN inv_items i ON bi.component_item_id = i.id
            WHERE bi.bom_id = ?
            ORDER BY bi.operation_seq ASC
            """,
            (bom_id,)
        )
