from typing import List, Dict, Any, Optional
from app.core.db import db

class InvAnalysisService:

    # =========================================================================
    # 1. MULTI-WAREHOUSE STOCK BALANCE MATRIX
    # =========================================================================
    @staticmethod
    def get_stock_balance_matrix(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT sb.*, w.warehouse_name, w.warehouse_code, b.bin_code,
               it.item_code, it.item_name, it.uom_code, it.standard_cost,
               (sb.on_hand_qty * it.standard_cost) AS total_valuation,
               (sb.on_hand_qty - sb.reserved_qty) AS available_to_promise,
               c.short_code AS company_code
        FROM inv_stock_balances sb
        JOIN companies c ON sb.company_id = c.id
        JOIN inv_warehouses w ON sb.warehouse_id = w.id
        JOIN inv_items it ON sb.item_id = it.id
        LEFT JOIN inv_bins b ON sb.bin_id = b.id
        """
        params = ()
        if company_id:
            sql += " WHERE sb.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY w.code ASC, it.code ASC"
        return db.query(sql, params)

    # =========================================================================
    # 2. GOODS IN TRANSIT (GIT) MONITOR
    # =========================================================================
    @staticmethod
    def get_goods_in_transit(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT st.transfer_number, st.transfer_date, st.dispatch_date, st.carrier_name, st.vehicle_no, st.tracking_ref,
               wf.warehouse_name AS from_warehouse, wt.warehouse_name AS to_warehouse,
               it.item_code, it.item_name, ti.transfer_qty, it.uom_code, ti.line_total,
               c.short_code AS company_code
        FROM inv_stock_transfers st
        JOIN companies c ON st.company_id = c.id
        JOIN inv_warehouses wf ON st.from_warehouse_id = wf.id
        JOIN inv_warehouses wt ON st.to_warehouse_id = wt.id
        JOIN inv_transfer_items ti ON ti.transfer_id = st.id
        JOIN inv_items it ON ti.item_id = it.id
        WHERE st.status = 'IN_TRANSIT'
        """
        params = ()
        if company_id:
            sql += " AND st.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY st.code DESC"
        return db.query(sql, params)

    # =========================================================================
    # 3. ABC CLASSIFICATION & REORDER POINT MONITOR
    # =========================================================================
    @staticmethod
    def get_abc_analysis(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
        SELECT it.item_code, it.item_name, it.uom_code, it.standard_cost, it.min_reorder_qty, it.safety_stock_qty,
               ISNULL(SUM(sb.on_hand_qty), 0) AS current_on_hand,
               ISNULL(SUM(sb.on_hand_qty * it.standard_cost), 0) AS total_inventory_value,
               CASE 
                 WHEN ISNULL(SUM(sb.on_hand_qty * it.standard_cost), 0) >= 50000 THEN 'CATEGORY_A_FAST_MOVING'
                 WHEN ISNULL(SUM(sb.on_hand_qty * it.standard_cost), 0) >= 20000 THEN 'CATEGORY_B_STANDARD'
                 ELSE 'CATEGORY_C_SLOW_MOVING'
               END AS abc_category,
               CASE 
                 WHEN ISNULL(SUM(sb.on_hand_qty), 0) <= it.safety_stock_qty THEN 'CRITICAL_REORDER'
                 WHEN ISNULL(SUM(sb.on_hand_qty), 0) <= it.min_reorder_qty THEN 'REORDER_WARNING'
                 ELSE 'ADEQUATE_STOCK'
               END AS replenishment_status
        FROM inv_items it
        LEFT JOIN inv_stock_balances sb ON sb.item_id = it.id
        WHERE it.is_active = 1
        GROUP BY it.item_code, it.item_name, it.uom_code, it.standard_cost, it.min_reorder_qty, it.safety_stock_qty
        ORDER BY total_inventory_value DESC
        """
        return db.query(sql)
