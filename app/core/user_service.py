from typing import Optional, Dict, Any, List
from fastapi import Request
import uuid
import hashlib
from app.core.db import db
from app.core.company_service import CompanyService

ROLE_SHORT_MAP = {
    "Principal Systems Architect": "Sys Admin",
    "Chief Financial Officer / GL Controller": "CFO / Finance",
    "Chief Financial Officer": "CFO",
    "Supply Chain & Plant Director": "Supply Director",
    "Supply Chain Director": "Supply Director",
    "Chief Enterprise Architect & Sys Admin": "Sys Admin",
}

class UserService:
    COOKIE_USER_ID = "pyrix_user_id"
    COOKIE_SESSION = "pyrix_session_token"

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _enrich_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not user:
            return None
        
        name = user.get("full_name", "")
        parts = name.strip().split()
        if len(parts) >= 2:
            user["initials"] = (parts[0][0] + parts[-1][0]).upper()
            user["short_name"] = f"{parts[0]} {parts[-1][0]}."
        elif parts:
            user["initials"] = parts[0][:2].upper()
            user["short_name"] = parts[0]
        else:
            user["initials"] = "AV"
            user["short_name"] = "Admin"

        # Role summary for compact header display
        job = user.get("job_title", "")
        if job in ROLE_SHORT_MAP:
            user["role_summary"] = ROLE_SHORT_MAP[job]
        elif "/" in job:
            user["role_summary"] = job.split("/")[0].strip()
        elif "&" in job:
            user["role_summary"] = job.split("&")[0].strip()
        elif len(job) > 16:
            user["role_summary"] = job[:15] + "…"
        else:
            user["role_summary"] = job or "Sys Admin"

        # Ensure theme_pref defaults to light
        user["theme_pref"] = user.get("theme_pref") or "light"

        return user

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        user = db.query_one(
            """
            SELECT u.*, c.name AS company_name, c.short_code AS company_code, c.currency
            FROM users u
            LEFT JOIN companies c ON u.primary_company_id = c.id
            WHERE LOWER(u.email) = LOWER(?) AND COALESCE(u.isDelete, 0) = 0
            """,
            (email.strip(),)
        )
        return UserService._enrich_user(user)

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        user = db.query_one(
            """
            SELECT u.*, c.name AS company_name, c.short_code AS company_code, c.currency
            FROM users u
            LEFT JOIN companies c ON u.primary_company_id = c.id
            WHERE u.id = ? AND COALESCE(u.isDelete, 0) = 0
            """,
            (user_id,)
        )
        return UserService._enrich_user(user)

    @staticmethod
    def get_all_active_users() -> List[Dict[str, Any]]:
        users = db.query(
            """
            SELECT u.*, c.short_code AS company_code, c.name AS company_name
            FROM users u
            LEFT JOIN companies c ON u.primary_company_id = c.id
            WHERE COALESCE(u.isDelete, 0) = 0
            ORDER BY u.code ASC
            """
        )
        return [UserService._enrich_user(u) for u in users]

    @staticmethod
    def authenticate(email_or_emp_id: str, password: str) -> Optional[Dict[str, Any]]:
        user = db.query_one(
            """
            SELECT u.*, c.name AS company_name, c.short_code AS company_code
            FROM users u
            LEFT JOIN companies c ON u.primary_company_id = c.id
            WHERE (LOWER(u.email) = LOWER(?) OR UPPER(u.employee_id) = UPPER(?))
              AND COALESCE(u.isDelete, 0) = 0 AND u.is_active = 1
            """,
            (email_or_emp_id.strip(), email_or_emp_id.strip())
        )
        if not user:
            return None

        # Check plaintext or sha256
        pw_hash = UserService.hash_password(password)
        if user["password_hash"] == password or user["password_hash"] == pw_hash:
            # Update last_login
            db.execute("UPDATE users SET last_login = GETDATE() WHERE id = ?", (user["id"],))
            return UserService._enrich_user(user)
        return None

    @staticmethod
    def resolve_current_user(request: Request) -> Optional[Dict[str, Any]]:
        """Resolves logged-in user from cookie. Returns None if unauthenticated."""
        user_id = request.cookies.get(UserService.COOKIE_USER_ID)
        if user_id:
            try:
                user = UserService.get_user_by_id(user_id)
                if user:
                    return user
            except Exception:
                pass
        return None

    @staticmethod
    def get_accessible_companies(user: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Returns the list of conglomerate subsidiaries accessible to the given user."""
        if not user:
            return CompanyService.get_all_companies()

        clearance = str(user.get("clearance_tier") or "")
        # TIER_4_ROOT and TIER_3_GROUP or Administrators have access to all companies
        if clearance in ("TIER_4_ROOT", "TIER_3_GROUP"):
            return CompanyService.get_all_companies()

        # Specific subsidiary-bound staff have access to their assigned primary company
        primary_id = user.get("primary_company_id")
        if primary_id:
            comp = CompanyService.get_company_by_id(str(primary_id))
            if comp:
                return [comp]

        return CompanyService.get_all_companies()

    @staticmethod
    def update_profile(
        user_id: str,
        full_name: str,
        email: str,
        phone: str,
        job_title: str,
        department: str,
        primary_company_id: Optional[str] = None,
        theme_pref: str = "light"
    ) -> bool:
        if primary_company_id and str(primary_company_id).strip():
            db.execute(
                """
                UPDATE users
                SET full_name = ?, email = ?, phone = ?, job_title = ?, department = ?, primary_company_id = ?, theme_pref = ?
                WHERE id = ?
                """,
                (full_name.strip(), email.strip(), phone.strip(), job_title.strip(), department.strip(), str(primary_company_id).strip(), theme_pref, user_id)
            )
        else:
            db.execute(
                """
                UPDATE users
                SET full_name = ?, email = ?, phone = ?, job_title = ?, department = ?, primary_company_id = NULL, theme_pref = ?
                WHERE id = ?
                """,
                (full_name.strip(), email.strip(), phone.strip(), job_title.strip(), department.strip(), theme_pref, user_id)
            )
        return True

    @staticmethod
    def update_theme_pref(user_id: str, theme_pref: str) -> bool:
        """Persists the user's selected theme preference ('light' or 'dark') in the database."""
        safe_theme = "dark" if theme_pref.strip().lower() == "dark" else "light"
        db.execute(
            "UPDATE users SET theme_pref = ? WHERE id = ?",
            (safe_theme, user_id)
        )
        return True

    @staticmethod
    def change_password(user_id: str, new_password: str) -> bool:
        pw_hash = UserService.hash_password(new_password)
        db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
        return True
