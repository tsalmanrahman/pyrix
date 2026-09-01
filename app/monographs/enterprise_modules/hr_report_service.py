from typing import List, Dict, Any, Optional
from app.core.db import db

class HRReportService:
    """HR Statements & Statutory Reports Service: Salary Registers, Bank Advice, Tax Computation & PF Ledger."""

    @staticmethod
    def get_executive_summary(company_id: Optional[str] = None) -> Dict[str, Any]:
        sql_emp = "SELECT COUNT(*) AS total_employees, ISNULL(SUM(gross_salary), 0.0) AS total_gross_payroll FROM hr_employees WHERE is_active = 1"
        params_emp = ()
        if company_id:
            sql_emp += " AND company_id = ?"
            params_emp = (company_id,)
        emp_res = db.query_one(sql_emp, params_emp)

        sql_loan = "SELECT ISNULL(SUM(outstanding_balance), 0.0) AS total_loan_outstanding FROM hr_loans WHERE status = 'ACTIVE'"
        params_loan = ()
        if company_id:
            sql_loan += " AND company_id = ?"
            params_loan = (company_id,)
        loan_res = db.query_one(sql_loan, params_loan)

        sql_pf = "SELECT ISNULL(SUM(pf_employee_deduction + pf_employer_matching), 0.0) AS total_pf_accumulated FROM hr_payslips"
        pf_res = db.query_one(sql_pf)

        return {
            "total_headcount": emp_res["total_employees"] if emp_res else 0,
            "monthly_payroll_budget": float(emp_res["total_gross_payroll"]) if emp_res else 0.0,
            "loan_outstanding": float(loan_res["total_loan_outstanding"]) if loan_res else 0.0,
            "total_pf_fund": float(pf_res["total_pf_accumulated"]) if pf_res else 0.0,
        }

    @staticmethod
    def get_salary_register(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ps.id, ps.payslip_number, ps.basic_salary, ps.house_rent_allowance,
                   ps.medical_allowance, ps.conveyance_allowance, ps.special_allowance,
                   ps.overtime_pay, ps.gross_earnings, ps.pf_employee_deduction,
                   ps.income_tax_deduction, ps.loan_emi_deduction, ps.total_deductions,
                   ps.net_salary_payable, ps.bank_account_number,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   d.dept_name, des.designation_title, pr.period_month
            FROM hr_payslips ps
            JOIN hr_employees e ON ps.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
            JOIN hr_designations des ON e.designation_id = des.id
            JOIN hr_payroll_runs pr ON ps.payroll_run_id = pr.id
        """
        params = ()
        if company_id:
            sql += " WHERE e.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY ps.payslip_number ASC"
        return db.query(sql, params)

    @staticmethod
    def get_bank_advice(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ps.id, ps.payslip_number, ps.net_salary_payable, ps.bank_account_number,
                   (e.first_name + ' ' + e.last_name) AS employee_name, e.employee_code,
                   e.bank_name, e.bank_routing_number, d.dept_name
            FROM hr_payslips ps
            JOIN hr_employees e ON ps.employee_id = e.id
            JOIN hr_departments d ON e.department_id = d.id
        """
        params = ()
        if company_id:
            sql += " WHERE e.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY e.employee_code ASC"
        return db.query(sql, params)

    @staticmethod
    def get_pf_ledger(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT e.id AS employee_id, e.employee_code, (e.first_name + ' ' + e.last_name) AS employee_name,
                   d.dept_name, e.joining_date,
                   ISNULL(SUM(ps.pf_employee_deduction), 0.0) AS employee_contribution,
                   ISNULL(SUM(ps.pf_employer_matching), 0.0) AS employer_matching,
                   ISNULL(SUM(ps.pf_employee_deduction + ps.pf_employer_matching), 0.0) AS total_pf_balance
            FROM hr_employees e
            JOIN hr_departments d ON e.department_id = d.id
            LEFT JOIN hr_payslips ps ON e.id = ps.employee_id
        """
        params = ()
        if company_id:
            sql += " WHERE e.company_id = ?"
            params = (company_id,)
        sql += " GROUP BY e.id, e.employee_code, e.first_name, e.last_name, d.dept_name, e.joining_date ORDER BY e.employee_code ASC"
        return db.query(sql, params)
