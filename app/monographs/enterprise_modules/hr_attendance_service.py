from typing import List, Dict, Any, Optional
from app.core.db import db

class HRAttendanceService:
    """Time & Attendance Service: Biometric punch logs, leave applications & Overtime matrix."""

    @staticmethod
    def get_attendance_logs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT a.id, a.company_id, a.employee_id, a.attendance_date, a.clock_in_time,
                   a.clock_out_time, a.terminal_device_ip, a.attendance_status, a.is_late,
                   a.late_minutes, a.overtime_hours, a.remarks,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   d.dept_name, s.shift_name
            FROM hr_attendance_logs a
            JOIN hr_employees e ON a.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_shifts s ON e.shift_id = s.id
        """
        params = ()
        if company_id:
            sql += " WHERE a.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY a.attendance_date DESC, a.clock_in_time ASC"
        return db.query(sql, params)

    @staticmethod
    def get_leave_applications(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT la.id, la.company_id, la.employee_id, la.leave_type_id, la.application_number,
                   la.start_date, la.end_date, la.leave_days, la.reason, la.approver_name,
                   la.status, la.applied_at,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   lt.leave_name, lt.leave_code
            FROM hr_leave_applications la
            JOIN hr_employees e ON la.employee_id = e.id
            JOIN hr_leave_types lt ON la.leave_type_id = lt.id
        """
        params = ()
        if company_id:
            sql += " WHERE la.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY la.applied_at DESC"
        return db.query(sql, params)

    @staticmethod
    def get_overtime_records(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ot.id, ot.company_id, ot.employee_id, ot.ot_date, ot.ot_hours,
                   ot.hourly_rate, ot.multiplier_factor, ot.total_ot_amount, ot.supervisor_name,
                   ot.status,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   d.dept_name
            FROM hr_overtime_records ot
            JOIN hr_employees e ON ot.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
        """
        params = ()
        if company_id:
            sql += " WHERE ot.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY ot.ot_date DESC"
        return db.query(sql, params)
