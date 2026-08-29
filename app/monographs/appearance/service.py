from typing import Dict, Any
from app.core.db import db

class AppearanceService:
    @staticmethod
    def get_appearance() -> Dict[str, Any]:
        res = db.query_one("SELECT TOP 1 * FROM appearance_settings ORDER BY id ASC")
        if not res:
            return {
                "theme_mode": "light",
                "accent_color": "#0078D4",
                "font_family": "SF Pro Display",
                "glass_blur_px": 24,
                "glass_opacity_pct": 75,
                "sidebar_style": "floating",
                "border_glow": 1,
                "sound_effects": 0
            }
        return res

    @staticmethod
    def update_appearance(
        theme_mode: str,
        accent_color: str,
        glass_blur_px: int,
        glass_opacity_pct: int,
        sidebar_style: str,
        border_glow: int,
        user: str = "Operator Admin",
        ip: str = "127.0.0.1"
    ) -> bool:
        db.execute(
            """
            UPDATE appearance_settings
            SET theme_mode = ?, accent_color = ?, glass_blur_px = ?, glass_opacity_pct = ?, 
                sidebar_style = ?, border_glow = ?, updated_at = GETDATE()
            WHERE id = (SELECT TOP 1 id FROM appearance_settings ORDER BY id ASC)
            """,
            (theme_mode, accent_color, glass_blur_px, glass_opacity_pct, sidebar_style, border_glow)
        )
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('UPDATE_APPEARANCE', 'appearance_settings', 'theme', 'prev_theme', ?, ?, ?)
            """,
            (f"{theme_mode}, {accent_color}, blur:{glass_blur_px}px", user, ip)
        )
        return True
