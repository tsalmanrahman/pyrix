from typing import List, Dict, Any, Optional
from app.core.db import db

class HREmployeeService:
    """Employee Lifecycle Service: Profiles, Temporary/Casual Rosters, Document Vault & Transfers."""

    @staticmethod
    def get_employees(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT e.id, e.company_id, e.employee_code, e.first_name, e.last_name,
                   (e.first_name + ' ' + e.last_name) AS full_name,
                   e.email, e.phone, e.national_id, e.tin_number, e.tax_zone, e.tax_circle,
                   e.date_of_birth, e.gender, e.blood_group, e.joining_date, e.employment_status,
                   e.basic_salary, e.gross_salary, e.bank_name, e.bank_account_number, e.bank_routing_number,
                   e.emergency_contact_name, e.emergency_contact_phone, e.is_pf_member, e.is_active,
                   d.dept_name, d.dept_code, des.designation_title, g.grade_name, g.grade_code, s.shift_name
            FROM hr_employees e
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_designations des ON e.designation_id = des.id
            JOIN hr_grades g ON e.grade_id = g.id
            JOIN hr_shifts s ON e.shift_id = s.id
        """
        params = ()
        if company_id:
            sql += " WHERE e.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY e.employee_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_employee_by_id(employee_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT e.id, e.company_id, e.employee_code, e.first_name, e.last_name,
                   (e.first_name + ' ' + e.last_name) AS full_name,
                   e.email, e.phone, e.national_id, e.tin_number, e.tax_zone, e.tax_circle,
                   e.date_of_birth, e.gender, e.blood_group, e.joining_date, e.employment_status,
                   e.basic_salary, e.gross_salary, e.bank_name, e.bank_account_number, e.bank_routing_number,
                   e.emergency_contact_name, e.emergency_contact_phone, e.is_pf_member, e.is_active,
                   d.dept_name, d.dept_code, des.designation_title, g.grade_name, g.grade_code, s.shift_name
            FROM hr_employees e
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_designations des ON e.designation_id = des.id
            JOIN hr_grades g ON e.grade_id = g.id
            JOIN hr_shifts s ON e.shift_id = s.id
            WHERE e.id = ?
        """
        return db.query_one(sql, (employee_id,))

    @staticmethod
    def get_contract_workers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT cw.id, cw.company_id, cw.department_id, cw.worker_code, cw.worker_name,
                   cw.contractor_agency, cw.worker_type, cw.daily_rate, cw.contract_start_date,
                   cw.contract_end_date, cw.status, d.dept_name
            FROM hr_contract_workers cw
            JOIN hr_departments d ON cw.department_id = d.id
        """
        params = ()
        if company_id:
            sql += " WHERE cw.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY cw.worker_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_documents(employee_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT doc.id, doc.employee_id, doc.doc_title, doc.doc_type, doc.doc_file_ref,
                   doc.issue_date, doc.expiry_date, doc.verification_status, doc.verified_by,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code
            FROM hr_documents doc
            JOIN hr_employees e ON doc.employee_id = e.id
        """
        params = ()
        if employee_id:
            sql += " WHERE doc.employee_id = ?"
            params = (employee_id,)
        sql += " ORDER BY doc.created_at DESC"
        return db.query(sql, params)

    @staticmethod
    def get_transfers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT t.id, t.company_id, t.employee_id, t.transfer_number, t.transfer_date, t.transfer_type,
                   t.previous_salary, t.revised_salary, t.reason, t.approved_by, t.status,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   d1.dept_name AS from_dept_name, d2.dept_name AS to_dept_name,
                   des1.designation_title AS from_designation, des2.designation_title AS to_designation
            FROM hr_transfers t
            JOIN hr_employees e ON t.employee_id = e.id
            JOIN hr_departments d1 ON t.from_dept_id = d1.id
            JOIN hr_departments d2 ON t.to_dept_id = d2.id
            JOIN hr_designations des1 ON t.from_designation_id = des1.id
            JOIN hr_designations des2 ON t.to_designation_id = des2.id
        """
        params = ()
        if company_id:
            sql += " WHERE t.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY t.transfer_date DESC"
        return db.query(sql, params)

    @staticmethod
    def get_transfer_by_id(transfer_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT t.id, t.company_id, t.employee_id, t.transfer_number, t.transfer_date, t.transfer_type,
                   t.previous_salary, t.revised_salary, t.reason, t.approved_by, t.status,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   d1.dept_name AS from_dept_name, d2.dept_name AS to_dept_name,
                   des1.designation_title AS from_designation, des2.designation_title AS to_designation
            FROM hr_transfers t
            JOIN hr_employees e ON t.employee_id = e.id
            JOIN hr_departments d1 ON t.from_dept_id = d1.id
            JOIN hr_departments d2 ON t.to_dept_id = d2.id
            JOIN hr_designations des1 ON t.from_designation_id = des1.id
            JOIN hr_designations des2 ON t.to_designation_id = des2.id
            WHERE t.id = ?
        """
        return db.query_one(sql, (transfer_id,))
