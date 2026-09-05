from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class InvTransactionService:

    # =========================================================================
    # 1. GOODS RECEIVING NOTES (GRN / MRR)
    # =========================================================================
    @staticmethod
    def get_grn_list(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT grn.*, w.warehouse_name, w.warehouse_code, c.short_code AS company_code,
               (SELECT COUNT(*) FROM inv_grn_items gi WHERE gi.grn_id = grn.id) AS item_count
        FROM inv_grn_headers grn
        JOIN companies c ON grn.company_id = c.id
        JOIN inv_warehouses w ON grn.warehouse_id = w.id
        """
        params = ()
        if company_id:
            sql += " WHERE grn.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY grn.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_grn_by_id(grn_id: str) -> Optional[Dict[str, Any]]:
        grn = db.query_one(
            """
            SELECT grn.*, w.warehouse_name, w.warehouse_code, w.address AS warehouse_address,
                   c.name AS company_name, c.short_code AS company_code, c.currency AS company_currency
            FROM inv_grn_headers grn
            JOIN companies c ON grn.company_id = c.id
            JOIN inv_warehouses w ON grn.warehouse_id = w.id
            WHERE grn.id = ?
            """,
            (grn_id,)
        )
        if not grn:
            return None
        grn["items"] = db.query(
            """
            SELECT gi.*, it.item_code, it.item_name, it.uom_code, b.bin_code
            FROM inv_grn_items gi
            JOIN inv_items it ON gi.item_id = it.id
            LEFT JOIN inv_bins b ON gi.bin_id = b.id
            WHERE gi.grn_id = ?
            ORDER BY gi.code ASC
            """,
            (grn_id,)
        )
        return grn

    # =========================================================================
    # 2. GOODS ISSUE CHALLANS (Outbound Dispatches, WIP, Spares)
    # =========================================================================
    @staticmethod
    def get_issues(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT iss.*, w.warehouse_name, c.short_code AS company_code,
               (SELECT COUNT(*) FROM inv_issue_items ii WHERE ii.issue_id = iss.id) AS item_count
        FROM inv_issues iss
        JOIN companies c ON iss.company_id = c.id
        JOIN inv_warehouses w ON iss.warehouse_id = w.id
        """
        params = ()
        if company_id:
            sql += " WHERE iss.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY iss.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_issue_by_id(issue_id: str) -> Optional[Dict[str, Any]]:
        issue = db.query_one(
            """
            SELECT iss.*, w.warehouse_name, w.warehouse_code, w.address AS warehouse_address,
                   c.name AS company_name, c.short_code AS company_code, c.currency AS company_currency
            FROM inv_issues iss
            JOIN companies c ON iss.company_id = c.id
            JOIN inv_warehouses w ON iss.warehouse_id = w.id
            WHERE iss.id = ?
            """,
            (issue_id,)
        )
        if not issue:
            return None
        issue["items"] = db.query(
            """
            SELECT ii.*, it.item_code, it.item_name, it.uom_code, b.bin_code
            FROM inv_issue_items ii
            JOIN inv_items it ON ii.item_id = it.id
            LEFT JOIN inv_bins b ON ii.bin_id = b.id
            WHERE ii.issue_id = ?
            ORDER BY ii.code ASC
            """,
            (issue_id,)
        )
        return issue

    # =========================================================================
    # 3. INTER-WAREHOUSE STOCK TRANSFER ORDERS (STO)
    # =========================================================================
    @staticmethod
    def get_stock_transfers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT st.*, wf.warehouse_name AS from_warehouse, wt.warehouse_name AS to_warehouse, c.short_code AS company_code,
               (SELECT COUNT(*) FROM inv_transfer_items ti WHERE ti.transfer_id = st.id) AS item_count
        FROM inv_stock_transfers st
        JOIN companies c ON st.company_id = c.id
        JOIN inv_warehouses wf ON st.from_warehouse_id = wf.id
        JOIN inv_warehouses wt ON st.to_warehouse_id = wt.id
        """
        params = ()
        if company_id:
            sql += " WHERE st.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY st.code DESC"
        return db.query(sql, params)

    @staticmethod
    def get_transfer_by_id(transfer_id: str) -> Optional[Dict[str, Any]]:
        transfer = db.query_one(
            """
            SELECT st.*, wf.warehouse_name AS from_warehouse, wf.address AS from_address,
                   wt.warehouse_name AS to_warehouse, wt.address AS to_address,
                   c.name AS company_name, c.short_code AS company_code
            FROM inv_stock_transfers st
            JOIN companies c ON st.company_id = c.id
            JOIN inv_warehouses wf ON st.from_warehouse_id = wf.id
            JOIN inv_warehouses wt ON st.to_warehouse_id = wt.id
            WHERE st.id = ?
            """,
            (transfer_id,)
        )
        if not transfer:
            return None
        transfer["items"] = db.query(
            """
            SELECT ti.*, it.item_code, it.item_name, it.uom_code
            FROM inv_transfer_items ti
            JOIN inv_items it ON ti.item_id = it.id
            WHERE ti.transfer_id = ?
            ORDER BY ti.code ASC
            """,
            (transfer_id,)
        )
        return transfer

    # =========================================================================
    # 4. PHYSICAL CYCLE COUNT ADJUSTMENTS (+/-)
    # =========================================================================
    @staticmethod
    def get_adjustments(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT adj.*, w.warehouse_name, c.short_code AS company_code
        FROM inv_adjustments adj
        JOIN companies c ON adj.company_id = c.id
        JOIN inv_warehouses w ON adj.warehouse_id = w.id
        """
        params = ()
        if company_id:
            sql += " WHERE adj.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY adj.code DESC"
        return db.query(sql, params)
