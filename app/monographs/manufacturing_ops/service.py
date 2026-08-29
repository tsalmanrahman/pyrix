from typing import List, Dict, Any, Optional
from app.core.db import db

class ManufacturingService:
    @staticmethod
    def get_all_machines() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM manufacturing_telemetry ORDER BY line_name, machine_name")

    @staticmethod
    def get_plant_summary() -> Dict[str, Any]:
        machines = db.query("SELECT * FROM manufacturing_telemetry")
        total_machines = len(machines)
        running = sum(1 for m in machines if m["status"] == "RUNNING")
        idle = sum(1 for m in machines if m["status"] == "IDLE")
        alert = sum(1 for m in machines if m["status"] == "ALERT")
        avg_eff = round(sum(m["efficiency_pct"] for m in machines) / total_machines, 1) if total_machines else 0
        total_units = sum(m["total_units_today"] for m in machines)
        total_defects = sum(m["defect_count"] for m in machines)
        defect_rate = round((total_defects / total_units * 100), 2) if total_units else 0

        return {
            "total_machines": total_machines,
            "running": running,
            "idle": idle,
            "alert": alert,
            "average_efficiency": avg_eff,
            "total_units_today": total_units,
            "total_defects": total_defects,
            "defect_rate_pct": defect_rate
        }

    @staticmethod
    def update_machine_status(machine_id: str, new_status: str, user: str = "Floor Lead", ip: str = "127.0.0.1") -> bool:
        cur = db.query_one("SELECT status, machine_name FROM manufacturing_telemetry WHERE machine_id = ?", (machine_id,))
        if not cur:
            return False
        
        old_status = cur["status"]
        db.execute(
            "UPDATE manufacturing_telemetry SET status = ?, last_heartbeat = GETDATE() WHERE machine_id = ?",
            (new_status, machine_id)
        )
        
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('MACHINE_STATUS_CHANGE', 'manufacturing_telemetry', ?, ?, ?, ?, ?)
            """,
            (machine_id, old_status, new_status, user, ip)
        )
        return True

    @staticmethod
    def adjust_line_speed(machine_id: str, new_speed: int, user: str = "Floor Lead", ip: str = "127.0.0.1") -> bool:
        db.execute(
            "UPDATE manufacturing_telemetry SET actual_ppm = ?, last_heartbeat = GETDATE() WHERE machine_id = ?",
            (new_speed, machine_id)
        )
        db.execute(
            """
            INSERT INTO audit_logs (action_type, entity_name, entity_id, old_value, new_value, user_name, ip_address)
            VALUES ('SPEED_ADJUSTMENT', 'manufacturing_telemetry', ?, 'speed_change', ?, ?, ?)
            """,
            (machine_id, f"{new_speed} PPM", user, ip)
        )
        return True
