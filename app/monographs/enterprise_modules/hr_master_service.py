from typing import List, Dict, Any, Optional
from app.core.db import db

class HRMasterService:
    """Master Setup Service: Grades, Departments, Designations, Shifts, Holidays, Leave Types & Bank Accounts."""

    @staticmethod
    def get_grades(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT g.id, g.company_id, g.grade_code, g.grade_name, g.rank_level,
                   g.min_basic_salary, g.max_basic_salary, g.hra_pct, g.medical_pct, g.conveyance_pct,
                   g.is_active,
                   (SELECT COUNT(*) FROM hr_employees e WHERE e.grade_id = g.id) AS employee_count
            FROM hr_grades g
        """
        params = ()
        if company_id:
            sql += " WHERE g.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY g.rank_level ASC"
        return db.query(sql, params)

    @staticmethod
    def get_departments(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT d.id, d.company_id, d.dept_code, d.dept_name, d.cost_center_code,
                   d.head_of_dept, d.location_name, d.is_active,
                   (SELECT COUNT(*) FROM hr_employees e WHERE e.department_id = d.id) AS employee_count,
                   (SELECT COUNT(*) FROM hr_designations des WHERE des.department_id = d.id) AS designation_count
            FROM hr_departments d
        """
        params = ()
        if company_id:
            sql += " WHERE d.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY d.dept_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_designations(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT des.id, des.department_id, des.designation_code, des.designation_title, des.skill_level,
                   des.is_active, d.dept_name, d.dept_code,
                   (SELECT COUNT(*) FROM hr_employees e WHERE e.designation_id = des.id) AS employee_count
            FROM hr_designations des
            JOIN hr_departments d ON des.department_id = d.id
        """
        params = ()
        if company_id:
            sql += " WHERE d.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY des.designation_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_shifts(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT s.id, s.company_id, s.shift_code, s.shift_name, s.start_time, s.end_time,
                   s.grace_period_mins, s.half_day_hours, s.is_night_shift, s.night_allowance, s.is_active,
                   (SELECT COUNT(*) FROM hr_employees e WHERE e.shift_id = s.id) AS assigned_staff_count
            FROM hr_shifts s
        """
        params = ()
        if company_id:
            sql += " WHERE s.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY s.shift_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_holidays(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT h.id, h.company_id, h.holiday_name, h.holiday_date, h.holiday_type, h.is_recurring
            FROM hr_holidays h
        """
        params = ()
        if company_id:
            sql += " WHERE h.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY h.holiday_date ASC"
        return db.query(sql, params)

    @staticmethod
    def get_leave_types(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT lt.id, lt.company_id, lt.leave_code, lt.leave_name, lt.yearly_quota,
                   lt.is_paid, lt.is_encashable, lt.max_carryforward, lt.is_active
            FROM hr_leave_types lt
        """
        params = ()
        if company_id:
            sql += " WHERE lt.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY lt.leave_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_bank_accounts(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT b.id, b.company_id, b.bank_name, b.branch_name, b.account_number,
                   b.routing_number, b.currency, b.is_default
            FROM hr_bank_accounts b
        """
        params = ()
        if company_id:
            sql += " WHERE b.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY b.bank_name ASC"
        return db.query(sql, params)
