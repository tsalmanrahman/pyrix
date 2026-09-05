from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class InvMasterService:

    # =========================================================================
    # 1. WAREHOUSES & STORAGE FACILITIES
    # =========================================================================
    @staticmethod
    def get_warehouses(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT w.*, c.name AS company_name, c.short_code AS company_code,
               (SELECT COUNT(*) FROM inv_bins b WHERE b.warehouse_id = w.id) AS bin_count,
               (SELECT ISNULL(SUM(sb.on_hand_qty), 0) FROM inv_stock_balances sb WHERE sb.warehouse_id = w.id) AS total_stock_qty
        FROM inv_warehouses w
        JOIN companies c ON w.company_id = c.id
        WHERE w.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND w.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY c.sort_order ASC, w.code ASC"
        return db.query(sql, params)

    # =========================================================================
    # 2. STORAGE BINS (Aisle/Rack/Shelf/Bin)
    # =========================================================================
    @staticmethod
    def get_bins(warehouse_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT b.*, w.warehouse_name, w.warehouse_code
        FROM inv_bins b
        JOIN inv_warehouses w ON b.warehouse_id = w.id
        WHERE b.is_active = 1
        """
        params = ()
        if warehouse_id:
            sql += " AND b.warehouse_id = ?"
            params = (warehouse_id,)
        sql += " ORDER BY w.code ASC, b.bin_code ASC"
        return db.query(sql, params)

    # =========================================================================
    # 3. PRODUCT GROUPS & CATEGORIES
    # =========================================================================
    @staticmethod
    def get_product_groups(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT g.*, c.short_code AS company_code,
               (SELECT COUNT(*) FROM inv_items it WHERE it.group_id = g.id) AS item_count
        FROM inv_product_groups g
        JOIN companies c ON g.company_id = c.id
        WHERE g.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND g.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY g.code ASC"
        return db.query(sql, params)

    # =========================================================================
    # 4. UNITS OF MEASURE (UOM)
    # =========================================================================
    @staticmethod
    def get_uom_list(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM inv_uom WHERE is_active = 1 ORDER BY code ASC")

    # =========================================================================
    # 5. MASTER ITEMS CATALOG
    # =========================================================================
    @staticmethod
    def get_items(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT it.*, g.group_name, g.group_type, c.short_code AS company_code,
               (SELECT ISNULL(SUM(sb.on_hand_qty), 0) FROM inv_stock_balances sb WHERE sb.item_id = it.id) AS total_on_hand,
               (SELECT ISNULL(SUM(sb.reserved_qty), 0) FROM inv_stock_balances sb WHERE sb.item_id = it.id) AS total_reserved,
               (SELECT ISNULL(SUM(sb.in_transit_qty), 0) FROM inv_stock_balances sb WHERE sb.item_id = it.id) AS total_in_transit
        FROM inv_items it
        JOIN companies c ON it.company_id = c.id
        LEFT JOIN inv_product_groups g ON it.group_id = g.id
        WHERE it.is_active = 1
        """
        params = ()
        if company_id:
            sql += " AND it.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY it.code ASC"
        return db.query(sql, params)
