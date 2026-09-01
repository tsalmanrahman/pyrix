from typing import List, Dict, Any, Optional
from app.core.db import db

class HRPayrollService:
    """Enterprise Payroll & Loan Service: Payroll execution runs, itemized payslips, loans & tax slabs."""

    @staticmethod
    def get_payroll_runs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT pr.id, pr.company_id, pr.payroll_batch_number, pr.period_month, pr.fiscal_year,
                   pr.run_date, pr.total_employees_processed, pr.total_gross_payout, pr.total_deductions,
                   pr.total_net_payout, pr.status, pr.is_gl_posted, pr.gl_journal_ref, pr.bank_advice_locked
            FROM hr_payroll_runs pr
        """
        params = ()
        if company_id:
            sql += " WHERE pr.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY pr.run_date DESC"
        return db.query(sql, params)

    @staticmethod
    def get_payslips(payroll_run_id: Optional[str] = None, company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ps.id, ps.payroll_run_id, ps.employee_id, ps.payslip_number, ps.basic_salary,
                   ps.house_rent_allowance, ps.medical_allowance, ps.conveyance_allowance,
                   ps.special_allowance, ps.overtime_pay, ps.bonus_amount, ps.gross_earnings,
                   ps.pf_employee_deduction, ps.pf_employer_matching, ps.income_tax_deduction,
                   ps.loan_emi_deduction, ps.late_penalty_deduction, ps.total_deductions,
                   ps.net_salary_payable, ps.payment_mode, ps.bank_account_number, ps.status,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code, e.tin_number,
                   d.dept_name, des.designation_title, g.grade_name
            FROM hr_payslips ps
            JOIN hr_employees e ON ps.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_designations des ON e.designation_id = des.id
            JOIN hr_grades g ON e.grade_id = g.id
        """
        params = []
        conditions = []
        if payroll_run_id:
            conditions.append("ps.payroll_run_id = ?")
            params.append(payroll_run_id)
        if company_id:
            conditions.append("e.company_id = ?")
            params.append(company_id)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY ps.payslip_number ASC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_payslip_by_id(payslip_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT ps.id, ps.payroll_run_id, ps.employee_id, ps.payslip_number, ps.basic_salary,
                   ps.house_rent_allowance, ps.medical_allowance, ps.conveyance_allowance,
                   ps.special_allowance, ps.overtime_pay, ps.bonus_amount, ps.gross_earnings,
                   ps.pf_employee_deduction, ps.pf_employer_matching, ps.income_tax_deduction,
                   ps.loan_emi_deduction, ps.late_penalty_deduction, ps.total_deductions,
                   ps.net_salary_payable, ps.payment_mode, ps.bank_account_number, ps.status,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code, e.tin_number,
                   e.joining_date, e.bank_name, e.bank_routing_number,
                   d.dept_name, des.designation_title, g.grade_name,
                   pr.period_month, pr.fiscal_year, pr.run_date
            FROM hr_payslips ps
            JOIN hr_employees e ON ps.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_designations des ON e.designation_id = des.id
            JOIN hr_grades g ON e.grade_id = g.id
            JOIN hr_payroll_runs pr ON ps.payroll_run_id = pr.id
            WHERE ps.id = ?
        """
        return db.query_one(sql, (payslip_id,))

    @staticmethod
    def get_loan_types(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT lt.id, lt.company_id, lt.loan_type_code, lt.loan_type_name,
                   lt.max_loan_limit, lt.max_installments, lt.interest_rate_pct, lt.is_active
            FROM hr_loan_types lt
        """
        params = ()
        if company_id:
            sql += " WHERE lt.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY lt.loan_type_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_loans(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ln.id, ln.company_id, ln.employee_id, ln.loan_type_id, ln.loan_number,
                   ln.principal_amount, ln.interest_rate_pct, ln.tenure_months, ln.monthly_emi,
                   ln.disbursement_date, ln.repayment_start_month, ln.total_paid_amount,
                   ln.outstanding_balance, ln.status, ln.gl_voucher_ref,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   lt.loan_type_name
            FROM hr_loans ln
            JOIN hr_employees e ON ln.employee_id = e.id
            JOIN hr_loan_types lt ON ln.loan_type_id = lt.id
        """
        params = ()
        if company_id:
            sql += " WHERE ln.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY ln.disbursement_date DESC"
        return db.query(sql, params)

    @staticmethod
    def get_tax_slabs(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ts.id, ts.company_id, ts.fiscal_year, ts.slab_order, ts.slab_description,
                   ts.slab_limit, ts.tax_rate_pct, ts.is_active
            FROM hr_tax_slabs ts
        """
        params = ()
        if company_id:
            sql += " WHERE ts.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY ts.slab_order ASC"
        return db.query(sql, params)

    @staticmethod
    def get_tax_deposits(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT td.id, td.company_id, td.deposit_month, td.challan_number, td.challan_date,
                   td.depository_bank, td.total_tax_deposited, td.employees_covered_count,
                   td.gl_voucher_ref, td.status
            FROM hr_tax_deposits td
        """
        params = ()
        if company_id:
            sql += " WHERE td.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY td.challan_date DESC"
        return db.query(sql, params)
