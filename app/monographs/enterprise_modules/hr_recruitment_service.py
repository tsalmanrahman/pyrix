from typing import List, Dict, Any, Optional
from app.core.db import db

class HRRecruitmentService:
    """Recruitment Service: Job Requisitions, e-Approvals, CV Bank, Interview Scoring & Onboarding."""

    @staticmethod
    def get_job_requisitions(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT r.id, r.company_id, r.department_id, r.requisition_number, r.position_title,
                   r.vacancies_count, r.experience_years_required, r.budgeted_salary, r.target_joining_date,
                   r.justification, r.status, d.dept_name,
                   (SELECT COUNT(*) FROM hr_candidates c WHERE c.requisition_id = r.id) AS applicant_count
            FROM hr_job_requisitions r
            JOIN hr_departments d ON r.department_id = d.id
        """
        params = ()
        if company_id:
            sql += " WHERE r.company_id = ?"
            params = (company_id,)
        sql += " ORDER BY r.created_at DESC"
        return db.query(sql, params)

    @staticmethod
    def get_candidates(requisition_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT c.id, c.requisition_id, c.candidate_name, c.email, c.phone,
                   c.years_of_experience, c.key_skills, c.expected_salary, c.interview_score,
                   c.interview_feedback, c.hiring_status, c.applied_date,
                   r.position_title, r.requisition_number
            FROM hr_candidates c
            JOIN hr_job_requisitions r ON c.requisition_id = r.id
        """
        params = ()
        if requisition_id:
            sql += " WHERE c.requisition_id = ?"
            params = (requisition_id,)
        sql += " ORDER BY c.interview_score DESC"
        return db.query(sql, params)

    @staticmethod
    def get_candidate_by_id(candidate_id: str) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT c.id, c.requisition_id, c.candidate_name, c.email, c.phone,
                   c.years_of_experience, c.key_skills, c.expected_salary, c.interview_score,
                   c.interview_feedback, c.hiring_status, c.applied_date,
                   r.position_title, r.requisition_number, r.budgeted_salary
            FROM hr_candidates c
            JOIN hr_job_requisitions r ON c.requisition_id = r.id
            WHERE c.id = ?
        """
        return db.query_one(sql, (candidate_id,))
