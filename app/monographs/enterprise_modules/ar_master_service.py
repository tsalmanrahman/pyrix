from typing import List, Dict, Any, Optional
from app.core.db import db

class ARMasterService:

    # =========================================================================
    # 1. Customer Master Profile
    # =========================================================================
    @staticmethod
    def get_all_customers() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT c.*, 
                   arg.group_name AS ar_group_name, 
                   cg.group_name AS commercial_group_name, 
                   cat.category_name, cat.tier_level
            FROM ar_customers c
            LEFT JOIN ar_customer_groups arg ON c.ar_customer_group_id = arg.id
            LEFT JOIN ar_commercial_groups cg ON c.commercial_group_id = cg.id
            LEFT JOIN ar_group_categories cat ON c.group_category_id = cat.id
            WHERE COALESCE(c.isDelete, 0) = 0
            ORDER BY c.customer_code ASC
            """
        )

    @staticmethod
    def get_customer_by_id(customer_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT c.*, 
                   arg.group_name AS ar_group_name, 
                   cg.group_name AS commercial_group_name, 
                   cat.category_name, cat.tier_level
            FROM ar_customers c
            LEFT JOIN ar_customer_groups arg ON c.ar_customer_group_id = arg.id
            LEFT JOIN ar_commercial_groups cg ON c.commercial_group_id = cg.id
            LEFT JOIN ar_group_categories cat ON c.group_category_id = cat.id
            WHERE c.id = ? AND COALESCE(c.isDelete, 0) = 0
            """,
            (customer_id,)
        )

    @staticmethod
    def create_customer(
        customer_code: str,
        customer_name: str,
        ar_customer_group_id: Optional[str] = None,
        commercial_group_id: Optional[str] = None,
        group_category_id: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        tax_bin_number: Optional[str] = None,
        credit_limit: float = 1000000.0,
        payment_terms_days: int = 30,
        discount_percentage: float = 0.0,
        currency: str = "USD",
        billing_address: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_customers (
                customer_code, customer_name, ar_customer_group_id, commercial_group_id, 
                group_category_id, contact_person, email, phone, tax_bin_number, 
                credit_limit, payment_terms_days, discount_percentage, currency, 
                billing_address, is_active, isDelete
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (
                customer_code.strip(), customer_name.strip(), 
                ar_customer_group_id if ar_customer_group_id else None,
                commercial_group_id if commercial_group_id else None,
                group_category_id if group_category_id else None,
                contact_person.strip() if contact_person else None,
                email.strip() if email else None,
                phone.strip() if phone else None,
                tax_bin_number.strip() if tax_bin_number else None,
                credit_limit, payment_terms_days, discount_percentage,
                currency.strip(), billing_address.strip() if billing_address else None
            )
        )

    @staticmethod
    def update_customer(
        customer_id: str,
        customer_code: str,
        customer_name: str,
        ar_customer_group_id: Optional[str] = None,
        commercial_group_id: Optional[str] = None,
        group_category_id: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        tax_bin_number: Optional[str] = None,
        credit_limit: float = 1000000.0,
        payment_terms_days: int = 30,
        discount_percentage: float = 0.0,
        currency: str = "USD",
        billing_address: Optional[str] = None
    ) -> None:
        db.execute(
            """
            UPDATE ar_customers
            SET customer_code = ?, customer_name = ?, ar_customer_group_id = ?, 
                commercial_group_id = ?, group_category_id = ?, contact_person = ?, 
                email = ?, phone = ?, tax_bin_number = ?, credit_limit = ?, 
                payment_terms_days = ?, discount_percentage = ?, currency = ?, 
                billing_address = ?
            WHERE id = ?
            """,
            (
                customer_code.strip(), customer_name.strip(),
                ar_customer_group_id if ar_customer_group_id else None,
                commercial_group_id if commercial_group_id else None,
                group_category_id if group_category_id else None,
                contact_person.strip() if contact_person else None,
                email.strip() if email else None,
                phone.strip() if phone else None,
                tax_bin_number.strip() if tax_bin_number else None,
                credit_limit, payment_terms_days, discount_percentage,
                currency.strip(), billing_address.strip() if billing_address else None,
                customer_id
            )
        )

    @staticmethod
    def delete_customer(customer_id: str) -> None:
        db.execute("UPDATE ar_customers SET isDelete = 1 WHERE id = ?", (customer_id,))

    # =========================================================================
    # 2. AR Customer Groups
    # =========================================================================
    @staticmethod
    def get_ar_customer_groups() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT g.*, cs.set_name AS control_set_name, cs.set_code AS control_set_code
            FROM ar_customer_groups g
            LEFT JOIN ar_control_account_sets cs ON g.control_account_set_id = cs.id
            WHERE COALESCE(g.isDelete, 0) = 0
            ORDER BY g.group_code ASC
            """
        )

    @staticmethod
    def create_ar_customer_group(
        group_code: str,
        group_name: str,
        control_account_set_id: Optional[str] = None,
        default_credit_limit: float = 500000.0,
        grace_period_days: int = 30
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_customer_groups (group_code, group_name, control_account_set_id, default_credit_limit, grace_period_days, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, 1, 0)
            """,
            (group_code.strip(), group_name.strip(), control_account_set_id if control_account_set_id else None, default_credit_limit, grace_period_days)
        )

    @staticmethod
    def update_ar_customer_group(
        group_id: str,
        group_code: str,
        group_name: str,
        control_account_set_id: Optional[str] = None,
        default_credit_limit: float = 500000.0,
        grace_period_days: int = 30
    ) -> None:
        db.execute(
            """
            UPDATE ar_customer_groups
            SET group_code = ?, group_name = ?, control_account_set_id = ?, 
                default_credit_limit = ?, grace_period_days = ?
            WHERE id = ?
            """,
            (group_code.strip(), group_name.strip(), control_account_set_id if control_account_set_id else None, default_credit_limit, grace_period_days, group_id)
        )

    @staticmethod
    def delete_ar_customer_group(group_id: str) -> None:
        db.execute("UPDATE ar_customer_groups SET isDelete = 1 WHERE id = ?", (group_id,))

    # =========================================================================
    # 3. Commercial Customer Groups
    # =========================================================================
    @staticmethod
    def get_commercial_groups() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM ar_commercial_groups WHERE COALESCE(isDelete, 0) = 0 ORDER BY group_code ASC")

    @staticmethod
    def create_commercial_group(group_code: str, group_name: str, region: Optional[str] = None, description: Optional[str] = None) -> None:
        db.execute(
            """
            INSERT INTO ar_commercial_groups (group_code, group_name, region, description, is_active, isDelete)
            VALUES (?, ?, ?, ?, 1, 0)
            """,
            (group_code.strip(), group_name.strip(), region.strip() if region else None, description.strip() if description else None)
        )

    @staticmethod
    def update_commercial_group(group_id: str, group_code: str, group_name: str, region: Optional[str] = None, description: Optional[str] = None) -> None:
        db.execute(
            """
            UPDATE ar_commercial_groups
            SET group_code = ?, group_name = ?, region = ?, description = ?
            WHERE id = ?
            """,
            (group_code.strip(), group_name.strip(), region.strip() if region else None, description.strip() if description else None, group_id)
        )

    @staticmethod
    def delete_commercial_group(group_id: str) -> None:
        db.execute("UPDATE ar_commercial_groups SET isDelete = 1 WHERE id = ?", (group_id,))

    # =========================================================================
    # 4. Group Categories
    # =========================================================================
    @staticmethod
    def get_group_categories() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM ar_group_categories WHERE COALESCE(isDelete, 0) = 0 ORDER BY priority_level ASC, category_code ASC")

    @staticmethod
    def create_group_category(category_code: str, category_name: str, tier_level: str = "Standard", min_turnover: float = 0.0, priority_level: int = 1) -> None:
        db.execute(
            """
            INSERT INTO ar_group_categories (category_code, category_name, tier_level, min_turnover, priority_level, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, 1, 0)
            """,
            (category_code.strip(), category_name.strip(), tier_level.strip(), min_turnover, priority_level)
        )

    @staticmethod
    def update_group_category(category_id: str, category_code: str, category_name: str, tier_level: str = "Standard", min_turnover: float = 0.0, priority_level: int = 1) -> None:
        db.execute(
            """
            UPDATE ar_group_categories
            SET category_code = ?, category_name = ?, tier_level = ?, min_turnover = ?, priority_level = ?
            WHERE id = ?
            """,
            (category_code.strip(), category_name.strip(), tier_level.strip(), min_turnover, priority_level, category_id)
        )

    @staticmethod
    def delete_group_category(category_id: str) -> None:
        db.execute("UPDATE ar_group_categories SET isDelete = 1 WHERE id = ?", (category_id,))

    # =========================================================================
    # 5. Customer Mapping with Company
    # =========================================================================
    @staticmethod
    def get_customer_company_mappings(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if company_id:
            return db.query(
                """
                SELECT m.*, c.customer_code, c.customer_name, c.currency, comp.name AS company_name, comp.short_code AS company_code
                FROM ar_customer_company_mappings m
                JOIN ar_customers c ON m.customer_id = c.id
                JOIN companies comp ON m.company_id = comp.id
                WHERE m.company_id = ? AND COALESCE(m.isDelete, 0) = 0
                ORDER BY c.customer_code ASC
                """,
                (company_id,)
            )
        return db.query(
            """
            SELECT m.*, c.customer_code, c.customer_name, c.currency, comp.name AS company_name, comp.short_code AS company_code
            FROM ar_customer_company_mappings m
            JOIN ar_customers c ON m.customer_id = c.id
            JOIN companies comp ON m.company_id = comp.id
            WHERE COALESCE(m.isDelete, 0) = 0
            ORDER BY comp.short_code ASC, c.customer_code ASC
            """
        )

    @staticmethod
    def create_customer_company_mapping(
        customer_id: str,
        company_id: str,
        subsidiary_account_code: Optional[str] = None,
        allocated_credit_limit: float = 500000.0,
        assigned_sales_rep: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_customer_company_mappings (customer_id, company_id, subsidiary_account_code, allocated_credit_limit, assigned_sales_rep, is_enabled, isDelete)
            VALUES (?, ?, ?, ?, ?, 1, 0)
            """,
            (customer_id, company_id, subsidiary_account_code.strip() if subsidiary_account_code else None, allocated_credit_limit, assigned_sales_rep.strip() if assigned_sales_rep else None)
        )

    @staticmethod
    def update_customer_company_mapping(
        mapping_id: str,
        customer_id: str,
        company_id: str,
        subsidiary_account_code: Optional[str] = None,
        allocated_credit_limit: float = 500000.0,
        assigned_sales_rep: Optional[str] = None
    ) -> None:
        db.execute(
            """
            UPDATE ar_customer_company_mappings
            SET customer_id = ?, company_id = ?, subsidiary_account_code = ?, 
                allocated_credit_limit = ?, assigned_sales_rep = ?
            WHERE id = ?
            """,
            (customer_id, company_id, subsidiary_account_code.strip() if subsidiary_account_code else None, allocated_credit_limit, assigned_sales_rep.strip() if assigned_sales_rep else None, mapping_id)
        )

    @staticmethod
    def delete_customer_company_mapping(mapping_id: str) -> None:
        db.execute("UPDATE ar_customer_company_mappings SET isDelete = 1 WHERE id = ?", (mapping_id,))

    # =========================================================================
    # 6. Customers' Ship to Address
    # =========================================================================
    @staticmethod
    def get_ship_to_addresses(customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if customer_id:
            return db.query(
                """
                SELECT a.*, c.customer_code, c.customer_name
                FROM ar_customer_ship_addresses a
                JOIN ar_customers c ON a.customer_id = c.id
                WHERE a.customer_id = ? AND COALESCE(a.isDelete, 0) = 0
                ORDER BY a.is_default DESC, a.location_name ASC
                """,
                (customer_id,)
            )
        return db.query(
            """
            SELECT a.*, c.customer_code, c.customer_name
            FROM ar_customer_ship_addresses a
            JOIN ar_customers c ON a.customer_id = c.id
            WHERE COALESCE(a.isDelete, 0) = 0
            ORDER BY c.customer_code ASC, a.is_default DESC
            """
        )

    @staticmethod
    def create_ship_to_address(
        customer_id: str,
        location_name: str,
        ship_address: str,
        city: Optional[str] = None,
        division_state: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_phone: Optional[str] = None,
        is_default: bool = False
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_customer_ship_addresses (customer_id, location_name, ship_address, city, division_state, contact_person, contact_phone, is_default, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (customer_id, location_name.strip(), ship_address.strip(), city.strip() if city else None, division_state.strip() if division_state else None, contact_person.strip() if contact_person else None, contact_phone.strip() if contact_phone else None, 1 if is_default else 0)
        )

    @staticmethod
    def update_ship_to_address(
        address_id: str,
        customer_id: str,
        location_name: str,
        ship_address: str,
        city: Optional[str] = None,
        division_state: Optional[str] = None,
        contact_person: Optional[str] = None,
        contact_phone: Optional[str] = None,
        is_default: bool = False
    ) -> None:
        db.execute(
            """
            UPDATE ar_customer_ship_addresses
            SET customer_id = ?, location_name = ?, ship_address = ?, city = ?, 
                division_state = ?, contact_person = ?, contact_phone = ?, is_default = ?
            WHERE id = ?
            """,
            (customer_id, location_name.strip(), ship_address.strip(), city.strip() if city else None, division_state.strip() if division_state else None, contact_person.strip() if contact_person else None, contact_phone.strip() if contact_phone else None, 1 if is_default else 0, address_id)
        )

    @staticmethod
    def delete_ship_to_address(address_id: str) -> None:
        db.execute("UPDATE ar_customer_ship_addresses SET isDelete = 1 WHERE id = ?", (address_id,))

    # =========================================================================
    # 7. A/R Control Account Sets
    # =========================================================================
    @staticmethod
    def get_control_account_sets(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT cs.*, 
                   comp.short_code AS company_code,
                   g1.account_number AS ar_gl_num, g1.account_name AS ar_gl_name,
                   g2.account_number AS discount_gl_num, g2.account_name AS discount_gl_name,
                   g3.account_number AS bad_debt_gl_num, g3.account_name AS bad_debt_gl_name,
                   g4.account_number AS advance_gl_num, g4.account_name AS advance_gl_name
            FROM ar_control_account_sets cs
            LEFT JOIN companies comp ON cs.company_id = comp.id
            LEFT JOIN gl_accounts g1 ON cs.ar_control_gl_id = g1.id
            LEFT JOIN gl_accounts g2 ON cs.sales_discount_gl_id = g2.id
            LEFT JOIN gl_accounts g3 ON cs.bad_debt_provision_gl_id = g3.id
            LEFT JOIN gl_accounts g4 ON cs.advance_received_gl_id = g4.id
            WHERE COALESCE(cs.isDelete, 0) = 0
            ORDER BY cs.set_code ASC
            """
        )

    @staticmethod
    def create_control_account_set(
        set_code: str,
        set_name: str,
        company_id: Optional[str] = None,
        ar_control_gl_id: Optional[str] = None,
        sales_discount_gl_id: Optional[str] = None,
        bad_debt_provision_gl_id: Optional[str] = None,
        advance_received_gl_id: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_control_account_sets (set_code, set_name, company_id, ar_control_gl_id, sales_discount_gl_id, bad_debt_provision_gl_id, advance_received_gl_id, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (set_code.strip(), set_name.strip(), company_id if company_id else None, ar_control_gl_id if ar_control_gl_id else None, sales_discount_gl_id if sales_discount_gl_id else None, bad_debt_provision_gl_id if bad_debt_provision_gl_id else None, advance_received_gl_id if advance_received_gl_id else None)
        )

    @staticmethod
    def update_control_account_set(
        set_id: str,
        set_code: str,
        set_name: str,
        company_id: Optional[str] = None,
        ar_control_gl_id: Optional[str] = None,
        sales_discount_gl_id: Optional[str] = None,
        bad_debt_provision_gl_id: Optional[str] = None,
        advance_received_gl_id: Optional[str] = None
    ) -> None:
        db.execute(
            """
            UPDATE ar_control_account_sets
            SET set_code = ?, set_name = ?, company_id = ?, ar_control_gl_id = ?, 
                sales_discount_gl_id = ?, bad_debt_provision_gl_id = ?, advance_received_gl_id = ?
            WHERE id = ?
            """,
            (set_code.strip(), set_name.strip(), company_id if company_id else None, ar_control_gl_id if ar_control_gl_id else None, sales_discount_gl_id if sales_discount_gl_id else None, bad_debt_provision_gl_id if bad_debt_provision_gl_id else None, advance_received_gl_id if advance_received_gl_id else None, set_id)
        )

    @staticmethod
    def delete_control_account_set(set_id: str) -> None:
        db.execute("UPDATE ar_control_account_sets SET isDelete = 1 WHERE id = ?", (set_id,))

    # =========================================================================
    # 8. Reminder Letter Criteria
    # =========================================================================
    @staticmethod
    def get_reminder_criteria() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM ar_reminder_criteria WHERE COALESCE(isDelete, 0) = 0 ORDER BY overdue_days_threshold ASC")

    @staticmethod
    def create_reminder_criteria(
        criteria_code: str,
        criteria_name: str,
        reminder_level: str,
        overdue_days_threshold: int,
        min_overdue_amount: float = 1000.0,
        penalty_interest_pct: float = 0.0,
        auto_email_enabled: bool = True,
        email_subject_template: Optional[str] = None
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_reminder_criteria (criteria_code, criteria_name, reminder_level, overdue_days_threshold, min_overdue_amount, penalty_interest_pct, auto_email_enabled, email_subject_template, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (criteria_code.strip(), criteria_name.strip(), reminder_level.strip(), overdue_days_threshold, min_overdue_amount, penalty_interest_pct, 1 if auto_email_enabled else 0, email_subject_template.strip() if email_subject_template else None)
        )

    @staticmethod
    def update_reminder_criteria(
        criteria_id: str,
        criteria_code: str,
        criteria_name: str,
        reminder_level: str,
        overdue_days_threshold: int,
        min_overdue_amount: float = 1000.0,
        penalty_interest_pct: float = 0.0,
        auto_email_enabled: bool = True,
        email_subject_template: Optional[str] = None
    ) -> None:
        db.execute(
            """
            UPDATE ar_reminder_criteria
            SET criteria_code = ?, criteria_name = ?, reminder_level = ?, 
                overdue_days_threshold = ?, min_overdue_amount = ?, 
                penalty_interest_pct = ?, auto_email_enabled = ?, email_subject_template = ?
            WHERE id = ?
            """,
            (criteria_code.strip(), criteria_name.strip(), reminder_level.strip(), overdue_days_threshold, min_overdue_amount, penalty_interest_pct, 1 if auto_email_enabled else 0, email_subject_template.strip() if email_subject_template else None, criteria_id)
        )

    @staticmethod
    def delete_reminder_criteria(criteria_id: str) -> None:
        db.execute("UPDATE ar_reminder_criteria SET isDelete = 1 WHERE id = ?", (criteria_id,))

    # =========================================================================
    # 9. Aging Profiles
    # =========================================================================
    @staticmethod
    def get_aging_profiles() -> List[Dict[str, Any]]:
        return db.query("SELECT * FROM ar_aging_profiles WHERE COALESCE(isDelete, 0) = 0 ORDER BY profile_code ASC")

    @staticmethod
    def create_aging_profile(
        profile_code: str,
        profile_name: str,
        bucket_1_label: str = "Current (0-30 Days)",
        bucket_2_label: str = "31-60 Days",
        bucket_3_label: str = "61-90 Days",
        bucket_4_label: str = "91-120 Days",
        bucket_5_label: str = "120+ Days (Doubtful)",
        bad_debt_provision_pct: float = 5.0
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_aging_profiles (profile_code, profile_name, bucket_1_label, bucket_2_label, bucket_3_label, bucket_4_label, bucket_5_label, bad_debt_provision_pct, is_default, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1, 0)
            """,
            (profile_code.strip(), profile_name.strip(), bucket_1_label.strip(), bucket_2_label.strip(), bucket_3_label.strip(), bucket_4_label.strip(), bucket_5_label.strip(), bad_debt_provision_pct)
        )

    @staticmethod
    def update_aging_profile(
        profile_id: str,
        profile_code: str,
        profile_name: str,
        bucket_1_label: str = "Current (0-30 Days)",
        bucket_2_label: str = "31-60 Days",
        bucket_3_label: str = "61-90 Days",
        bucket_4_label: str = "91-120 Days",
        bucket_5_label: str = "120+ Days (Doubtful)",
        bad_debt_provision_pct: float = 5.0
    ) -> None:
        db.execute(
            """
            UPDATE ar_aging_profiles
            SET profile_code = ?, profile_name = ?, bucket_1_label = ?, 
                bucket_2_label = ?, bucket_3_label = ?, bucket_4_label = ?, 
                bucket_5_label = ?, bad_debt_provision_pct = ?
            WHERE id = ?
            """,
            (profile_code.strip(), profile_name.strip(), bucket_1_label.strip(), bucket_2_label.strip(), bucket_3_label.strip(), bucket_4_label.strip(), bucket_5_label.strip(), bad_debt_provision_pct, profile_id)
        )

    @staticmethod
    def delete_aging_profile(profile_id: str) -> None:
        db.execute("UPDATE ar_aging_profiles SET isDelete = 1 WHERE id = ?", (profile_id,))

    # =========================================================================
    # 10. Adjustment Types
    # =========================================================================
    @staticmethod
    def get_adjustment_types() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT t.*, g.account_number AS offset_gl_num, g.account_name AS offset_gl_name
            FROM ar_adjustment_types t
            LEFT JOIN gl_accounts g ON t.default_offset_gl_id = g.id
            WHERE COALESCE(t.isDelete, 0) = 0
            ORDER BY t.adjustment_category ASC, t.adjustment_code ASC
            """
        )

    @staticmethod
    def create_adjustment_type(
        adjustment_code: str,
        adjustment_name: str,
        adjustment_category: str,
        default_offset_gl_id: Optional[str] = None,
        is_tax_applicable: bool = False,
        requires_manager_approval: bool = True
    ) -> None:
        db.execute(
            """
            INSERT INTO ar_adjustment_types (adjustment_code, adjustment_name, adjustment_category, default_offset_gl_id, is_tax_applicable, requires_manager_approval, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (adjustment_code.strip(), adjustment_name.strip(), adjustment_category.strip(), default_offset_gl_id if default_offset_gl_id else None, 1 if is_tax_applicable else 0, 1 if requires_manager_approval else 0)
        )

    @staticmethod
    def update_adjustment_type(
        adjustment_id: str,
        adjustment_code: str,
        adjustment_name: str,
        adjustment_category: str,
        default_offset_gl_id: Optional[str] = None,
        is_tax_applicable: bool = False,
        requires_manager_approval: bool = True
    ) -> None:
        db.execute(
            """
            UPDATE ar_adjustment_types
            SET adjustment_code = ?, adjustment_name = ?, adjustment_category = ?, 
                default_offset_gl_id = ?, is_tax_applicable = ?, requires_manager_approval = ?
            WHERE id = ?
            """,
            (adjustment_code.strip(), adjustment_name.strip(), adjustment_category.strip(), default_offset_gl_id if default_offset_gl_id else None, 1 if is_tax_applicable else 0, 1 if requires_manager_approval else 0, adjustment_id)
        )

    @staticmethod
    def delete_adjustment_type(adjustment_id: str) -> None:
        db.execute("UPDATE ar_adjustment_types SET isDelete = 1 WHERE id = ?", (adjustment_id,))

    # =========================================================================
    # Entity Getters by ID (For Dedicated Edit Views)
    # =========================================================================
    @staticmethod
    def get_ar_customer_group_by_id(group_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_customer_groups WHERE id = ? AND COALESCE(isDelete, 0) = 0", (group_id,))

    @staticmethod
    def get_commercial_group_by_id(group_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_commercial_groups WHERE id = ? AND COALESCE(isDelete, 0) = 0", (group_id,))

    @staticmethod
    def get_group_category_by_id(category_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_group_categories WHERE id = ? AND COALESCE(isDelete, 0) = 0", (category_id,))

    @staticmethod
    def get_customer_company_mapping_by_id(mapping_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_customer_company_mappings WHERE id = ? AND COALESCE(isDelete, 0) = 0", (mapping_id,))

    @staticmethod
    def get_ship_to_address_by_id(address_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_customer_ship_addresses WHERE id = ? AND COALESCE(isDelete, 0) = 0", (address_id,))

    @staticmethod
    def get_control_account_set_by_id(set_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_control_account_sets WHERE id = ? AND COALESCE(isDelete, 0) = 0", (set_id,))

    @staticmethod
    def get_reminder_criteria_by_id(criteria_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_reminder_criteria WHERE id = ? AND COALESCE(isDelete, 0) = 0", (criteria_id,))

    @staticmethod
    def get_aging_profile_by_id(profile_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_aging_profiles WHERE id = ? AND COALESCE(isDelete, 0) = 0", (profile_id,))

    @staticmethod
    def get_adjustment_type_by_id(type_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one("SELECT * FROM ar_adjustment_types WHERE id = ? AND COALESCE(isDelete, 0) = 0", (type_id,))

