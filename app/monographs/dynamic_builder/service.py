import json
from typing import List, Dict, Any, Optional
from app.core.db import db
from app.core.cache import cache

class DynamicOptionService:
    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        cached = cache.get("dynamic_categories")
        if cached is not None:
            return cached
        res = db.query(
            "SELECT * FROM dynamic_categories WHERE is_active = 1 ORDER BY sort_order ASC, code ASC"
        )
        cache.set("dynamic_categories", res, ttl=300.0)
        return res

    @staticmethod
    def get_options_by_category(category_code: Optional[str] = None) -> List[Dict[str, Any]]:
        cache_key = f"dynamic_options_{category_code or 'all'}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        if category_code:
            options = db.query(
                """
                SELECT o.*, c.name AS category_name, c.icon AS category_icon
                FROM dynamic_options o
                LEFT JOIN dynamic_categories c ON o.category_code = c.category_code
                WHERE o.category_code = ? AND o.is_visible = 1
                ORDER BY o.sort_order ASC, o.code ASC
                """,
                (category_code,)
            )
        else:
            options = db.query(
                """
                SELECT o.*, c.name AS category_name, c.icon AS category_icon
                FROM dynamic_options o
                LEFT JOIN dynamic_categories c ON o.category_code = c.category_code
                WHERE o.is_visible = 1
                ORDER BY c.sort_order ASC, o.sort_order ASC, o.code ASC
                """
            )
        for opt in options:
            if opt.get("options_json"):
                try:
                    opt["options_parsed"] = json.loads(opt["options_json"])
                except Exception:
                    opt["options_parsed"] = []
            else:
                opt["options_parsed"] = []
        cache.set(cache_key, options, ttl=180.0)
        return options

    @staticmethod
    def update_option_value(option_key: str, new_value: str, user: str = "Operator Admin", ip: str = "127.0.0.1") -> bool:
        current = db.query_one("SELECT current_value, label FROM dynamic_options WHERE option_key = ?", (option_key,))
        if not current:
            return False
        
        old_val = current["current_value"]
        db.execute(
            "UPDATE dynamic_options SET current_value = ?, updated_at = GETDATE() WHERE option_key = ?",
            (str(new_value), option_key)
        )
        
        # Log to audit trail
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('UPDATE_OPTION', 'dynamic_options', ?, ?, ?, ?, ?)
            """,
            (option_key, str(old_val), str(new_value), user, ip)
        )
        cache.invalidate_prefix("dynamic_options_")
        return True

    @staticmethod
    def reorder_options(order_list: List[int], user: str = "Operator Admin", ip: str = "127.0.0.1") -> bool:
        for idx, option_code in enumerate(order_list):
            db.execute(
                "UPDATE dynamic_options SET sort_order = ? WHERE code = ?",
                (idx + 1, option_code)
            )
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('REORDER_LAYOUT', 'dynamic_options', 'layout_grid', 'reordered', ?, ?, ?)
            """,
            (json.dumps(order_list), user, ip)
        )
        cache.invalidate_prefix("dynamic_options_")
        return True

    @staticmethod
    def create_custom_option(
        company_id: Optional[str],
        option_key: str,
        category_code: str,
        label: str,
        description: str,
        field_type: str,
        default_value: str,
        unit: Optional[str] = None,
        icon: str = "sliders",
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        step_val: Optional[float] = None,
        options_json: Optional[str] = None,
        user: str = "Operator Admin",
        ip: str = "127.0.0.1"
    ) -> bool:
        # Get next sort order
        max_order_row = db.query_one(
            "SELECT ISNULL(MAX(sort_order), 0) AS max_o FROM dynamic_options WHERE category_code = ?",
            (category_code,)
        )
        max_order = max_order_row["max_o"] if max_order_row else 0
        
        db.execute(
            """
            INSERT INTO dynamic_options
            (company_id, option_key, category_code, label, description, field_type, current_value, default_value, options_json, min_val, max_val, step_val, unit, icon, sort_order, is_visible, is_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (company_id, option_key, category_code, label, description, field_type, default_value, default_value, options_json, min_val, max_val, step_val, unit, icon, max_order + 1)
        )

        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('CREATE_CUSTOM_FIELD', 'dynamic_options', ?, 'None', ?, ?, ?)
            """,
            (option_key, default_value, user, ip)
        )
        return True

    @staticmethod
    def delete_custom_option(option_key: str, user: str = "Operator Admin", ip: str = "127.0.0.1") -> bool:
        opt = db.query_one("SELECT is_system FROM dynamic_options WHERE option_key = ?", (option_key,))
        if not opt or opt["is_system"] == 1:
            return False
        
        db.execute("DELETE FROM dynamic_options WHERE option_key = ?", (option_key,))
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('DELETE_OPTION', 'dynamic_options', ?, 'Deleted', 'None', ?, ?)
            """,
            (option_key, user, ip)
        )
        return True
