import json
import logging
from app.config import get_settings
from app.core.db import db

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PyrixDB-Init")

def ensure_database_exists():
    """Connects to master and creates PyrixDB if missing."""
    logger.info(f"Checking if database '{settings.DB_NAME}' exists on {settings.DB_SERVER}...")
    try:
        with db.get_cursor(use_master=True, commit=False, autocommit=True) as cursor:
            cursor.execute(
                f"""
                IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{settings.DB_NAME}')
                BEGIN
                    CREATE DATABASE [{settings.DB_NAME}];
                END
                """
            )
        logger.info(f"Database [{settings.DB_NAME}] is ready.")
    except Exception as e:
        logger.error(f"Error ensuring database exists: {e}")
        raise

def initialize_tables():
    """Initializes tables using id=GUID and code=INT secondary numeric key."""
    logger.info(f"Initializing tables with GUID primary keys and INT code in [{settings.DB_NAME}]...")

    ddl_scripts = [
        # 1. Companies Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'companies')
        BEGIN
            CREATE TABLE companies (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(101, 1) NOT NULL,
                name NVARCHAR(150) NOT NULL,
                short_code VARCHAR(20) UNIQUE NOT NULL,
                industry NVARCHAR(100) NOT NULL,
                tagline NVARCHAR(200),
                currency VARCHAR(10) DEFAULT 'USD',
                fiscal_year VARCHAR(20) DEFAULT 'FY 2026-2027',
                headquarters NVARCHAR(150) DEFAULT 'Main Industrial Zone',
                logo_icon VARCHAR(50) DEFAULT 'factory',
                accent_color VARCHAR(30) DEFAULT '#0078D4',
                is_active BIT DEFAULT 1,
                sort_order INT DEFAULT 0,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 2. Dynamic Categories Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dynamic_categories')
        BEGIN
            CREATE TABLE dynamic_categories (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                category_code VARCHAR(50) UNIQUE NOT NULL,
                name NVARCHAR(100) NOT NULL,
                description NVARCHAR(255),
                icon VARCHAR(50) NOT NULL,
                sort_order INT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 3. Dynamic Options Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dynamic_options')
        BEGIN
            CREATE TABLE dynamic_options (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES companies(id),
                category_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES dynamic_categories(id),
                option_key VARCHAR(100) NOT NULL,
                category_code VARCHAR(50) NOT NULL,
                label NVARCHAR(150) NOT NULL,
                description NVARCHAR(350),
                field_type VARCHAR(30) NOT NULL,
                current_value NVARCHAR(MAX),
                default_value NVARCHAR(MAX),
                options_json NVARCHAR(MAX) NULL,
                min_val FLOAT NULL,
                max_val FLOAT NULL,
                step_val FLOAT NULL,
                unit NVARCHAR(30) NULL,
                icon VARCHAR(50) NOT NULL DEFAULT 'sliders',
                sort_order INT DEFAULT 0,
                is_visible BIT DEFAULT 1,
                is_system BIT DEFAULT 0,
                updated_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 4. Appearance Settings Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'appearance_settings')
        BEGIN
            CREATE TABLE appearance_settings (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES companies(id),
                theme_mode VARCHAR(30) DEFAULT 'light',
                accent_color VARCHAR(30) DEFAULT '#0078D4',
                font_family VARCHAR(50) DEFAULT 'SF Pro Display',
                glass_blur_px INT DEFAULT 24,
                glass_opacity_pct INT DEFAULT 75,
                sidebar_style VARCHAR(30) DEFAULT 'floating',
                border_glow BIT DEFAULT 1,
                sound_effects BIT DEFAULT 0,
                updated_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 5. Manufacturing Telemetry Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'manufacturing_telemetry')
        BEGIN
            CREATE TABLE manufacturing_telemetry (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES companies(id),
                machine_code VARCHAR(50) NOT NULL,
                machine_name NVARCHAR(100) NOT NULL,
                line_name NVARCHAR(100) NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'RUNNING',
                efficiency_pct FLOAT DEFAULT 94.5,
                target_ppm INT DEFAULT 120,
                actual_ppm INT DEFAULT 118,
                temperature_c FLOAT DEFAULT 62.4,
                vibration_mm_s FLOAT DEFAULT 1.25,
                total_units_today INT DEFAULT 14250,
                defect_count INT DEFAULT 18,
                operator_name NVARCHAR(100) DEFAULT 'Senior Specialist',
                shift_name NVARCHAR(50) DEFAULT 'Shift A (Morning)',
                last_heartbeat DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 6. Enterprise Modules Catalog Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'enterprise_modules')
        BEGIN
            CREATE TABLE enterprise_modules (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                module_code VARCHAR(80) UNIQUE NOT NULL,
                name NVARCHAR(120) NOT NULL,
                domain_group NVARCHAR(100) NOT NULL,
                domain_code VARCHAR(50) NOT NULL,
                route_slug VARCHAR(80) UNIQUE NOT NULL,
                icon VARCHAR(50) NOT NULL DEFAULT 'box',
                description NVARCHAR(300),
                status VARCHAR(30) DEFAULT 'ACTIVE',
                badge_count INT DEFAULT 0,
                sort_order INT DEFAULT 0,
                is_enabled BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 7. Module Transactions / Records Table (Company Scoped)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'module_records')
        BEGIN
            CREATE TABLE module_records (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                module_code VARCHAR(80) NOT NULL,
                record_type VARCHAR(50) NOT NULL,
                ref_number NVARCHAR(60) NOT NULL,
                title NVARCHAR(150) NOT NULL,
                status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',
                amount FLOAT NULL,
                party_name NVARCHAR(120) NULL,
                created_by NVARCHAR(80) DEFAULT 'System User',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 8. Audit Logs Table
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'audit_logs')
        BEGIN
            CREATE TABLE audit_logs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES companies(id),
                action_type VARCHAR(50) NOT NULL,
                entity_name NVARCHAR(100) NOT NULL,
                entity_id NVARCHAR(100) NOT NULL,
                old_value NVARCHAR(MAX),
                new_value NVARCHAR(MAX),
                user_name NVARCHAR(100) DEFAULT 'System Operator',
                ip_address VARCHAR(50) DEFAULT '127.0.0.1',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 9. GL Accounts Master (Chart of Accounts)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_accounts')
        BEGIN
            CREATE TABLE gl_accounts (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1001, 1) NOT NULL,
                account_number VARCHAR(50) NOT NULL UNIQUE,
                account_name NVARCHAR(200) NOT NULL,
                account_type VARCHAR(50) NOT NULL,
                financial_statement VARCHAR(50) NOT NULL,
                normal_balance VARCHAR(10) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 10. GL Company Mappings (Entity Account Allocation Matrix)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_company_mappings')
        BEGIN
            CREATE TABLE gl_company_mappings (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(2001, 1) NOT NULL,
                gl_account_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES gl_accounts(id),
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                company_account_alias VARCHAR(50) NULL,
                allow_direct_posting BIT DEFAULT 1,
                posting_currency VARCHAR(10) NOT NULL,
                is_enabled BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 11. GL Sub Accounts Master (Sub-ledger breakdown)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_sub_accounts')
        BEGIN
            CREATE TABLE gl_sub_accounts (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(3001, 1) NOT NULL,
                gl_account_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES gl_accounts(id),
                sub_account_code VARCHAR(50) NOT NULL,
                sub_account_name NVARCHAR(200) NOT NULL,
                sub_account_type VARCHAR(50) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 12. GL Departments Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_departments')
        BEGIN
            CREATE TABLE gl_departments (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(4001, 1) NOT NULL,
                dept_code VARCHAR(30) NOT NULL UNIQUE,
                dept_name NVARCHAR(150) NOT NULL,
                head_of_dept NVARCHAR(150) NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 13. GL Cost Centres Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_cost_centres')
        BEGIN
            CREATE TABLE gl_cost_centres (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(5001, 1) NOT NULL,
                cost_centre_code VARCHAR(30) NOT NULL UNIQUE,
                cost_centre_name NVARCHAR(150) NOT NULL,
                department_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES gl_departments(id),
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 14. GL Budget Sets Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'gl_budget_sets')
        BEGIN
            CREATE TABLE gl_budget_sets (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(6001, 1) NOT NULL,
                budget_code VARCHAR(50) NOT NULL UNIQUE,
                budget_title NVARCHAR(200) NOT NULL,
                fiscal_year VARCHAR(20) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                cost_centre_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES gl_cost_centres(id),
                gl_account_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES gl_accounts(id),
                allocated_amount FLOAT NOT NULL,
                utilized_amount FLOAT DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 15. Sourcing: Vendors Master Profile
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_vendors')
        BEGIN
            CREATE TABLE sourcing_vendors (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1001, 1) NOT NULL,
                vendor_code VARCHAR(50) NOT NULL UNIQUE,
                vendor_name NVARCHAR(200) NOT NULL,
                vendor_group VARCHAR(50) NOT NULL,
                vendor_org_type VARCHAR(50) DEFAULT 'CORPORATE',
                contact_person NVARCHAR(150),
                email VARCHAR(150),
                phone VARCHAR(50),
                address NVARCHAR(300),
                tax_id_tin VARCHAR(50),
                vat_bin VARCHAR(50),
                bank_name NVARCHAR(150),
                bank_branch NVARCHAR(150),
                bank_account VARCHAR(50),
                bank_swift VARCHAR(50),
                credit_terms_days INT DEFAULT 30,
                currency VARCHAR(10) DEFAULT 'USD',
                rating_stars FLOAT DEFAULT 4.5,
                is_active BIT DEFAULT 1,
                isDelete BIT DEFAULT 0,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 16. Sourcing: Vendor Company Mappings Matrix
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_vendor_company_mappings')
        BEGIN
            CREATE TABLE sourcing_vendor_company_mappings (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(2001, 1) NOT NULL,
                vendor_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                vendor_account_alias VARCHAR(50),
                payment_method VARCHAR(50) DEFAULT 'BANK_TRANSFER',
                is_approved BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 17. Sourcing: Vendor Enlistment & Classification Tiers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_vendor_enlistments')
        BEGIN
            CREATE TABLE sourcing_vendor_enlistments (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(3001, 1) NOT NULL,
                vendor_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                category_name NVARCHAR(100) NOT NULL,
                enlistment_tier VARCHAR(30) DEFAULT 'TIER_1_APPROVED',
                valid_from DATE NOT NULL,
                valid_to DATE NOT NULL,
                financial_capacity_usd FLOAT DEFAULT 500000.0,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                inspection_status VARCHAR(50) DEFAULT 'VERIFIED_PASSED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 18. Sourcing: Buyers Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_buyers')
        BEGIN
            CREATE TABLE sourcing_buyers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(4001, 1) NOT NULL,
                buyer_code VARCHAR(30) NOT NULL UNIQUE,
                buyer_name NVARCHAR(150) NOT NULL,
                department_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES gl_departments(id),
                assigned_categories NVARCHAR(250),
                max_approval_limit FLOAT DEFAULT 50000.0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 19. Sourcing: Purchasing Organizations
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_purchasing_orgs')
        BEGIN
            CREATE TABLE sourcing_purchasing_orgs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(5001, 1) NOT NULL,
                org_code VARCHAR(30) NOT NULL UNIQUE,
                org_name NVARCHAR(150) NOT NULL,
                org_type VARCHAR(30) DEFAULT 'CENTRAL',
                company_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES companies(id),
                head_of_procurement NVARCHAR(150),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 20. Sourcing: Price Terms & Validity Profiles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_price_terms')
        BEGIN
            CREATE TABLE sourcing_price_terms (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(6001, 1) NOT NULL,
                term_code VARCHAR(30) NOT NULL UNIQUE,
                term_name NVARCHAR(150) NOT NULL,
                incoterm VARCHAR(20) NOT NULL,
                credit_days INT DEFAULT 30,
                validity_period_months INT DEFAULT 12,
                description NVARCHAR(250),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 21. Sourcing: C&F Agents & Indentors Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_cnf_agents')
        BEGIN
            CREATE TABLE sourcing_cnf_agents (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(7001, 1) NOT NULL,
                agent_code VARCHAR(30) NOT NULL UNIQUE,
                agent_name NVARCHAR(150) NOT NULL,
                port_location NVARCHAR(150) NOT NULL,
                license_number VARCHAR(80),
                contact_person NVARCHAR(100),
                phone VARCHAR(50),
                email VARCHAR(100),
                rating_score FLOAT DEFAULT 4.8,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 22. Sourcing: Multi-Currency Exchange Rates
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_exchange_rates')
        BEGIN
            CREATE TABLE sourcing_exchange_rates (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(8001, 1) NOT NULL,
                base_currency VARCHAR(10) DEFAULT 'USD',
                foreign_currency VARCHAR(10) NOT NULL,
                exchange_rate FLOAT NOT NULL,
                effective_date DATE DEFAULT CAST(GETDATE() AS DATE),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 23. Sourcing: Purchase Requisitions (PR Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_requisitions')
        BEGIN
            CREATE TABLE sourcing_requisitions (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(10001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                req_number VARCHAR(50) NOT NULL UNIQUE,
                req_type VARCHAR(50) NOT NULL,
                department_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES gl_departments(id),
                cost_centre_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES gl_cost_centres(id),
                title NVARCHAR(200) NOT NULL,
                priority VARCHAR(20) DEFAULT 'MEDIUM',
                requester_name NVARCHAR(100) NOT NULL,
                total_estimated_amount FLOAT DEFAULT 0.0,
                currency VARCHAR(10) DEFAULT 'USD',
                status VARCHAR(30) DEFAULT 'PENDING_APPROVAL',
                is_closed BIT DEFAULT 0,
                notes NVARCHAR(500),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 24. Sourcing: Purchase Requisition Items (PR Lines)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_requisition_items')
        BEGIN
            CREATE TABLE sourcing_requisition_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                requisition_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_requisitions(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                specification NVARCHAR(300),
                uom VARCHAR(20) DEFAULT 'PCS',
                quantity FLOAT NOT NULL,
                estimated_unit_price FLOAT NOT NULL,
                estimated_total FLOAT NOT NULL,
                required_by_date DATE
            );
        END
        """,

        # 25. Sourcing: Request For Quotation (RFQ)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_rfqs')
        BEGIN
            CREATE TABLE sourcing_rfqs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(11001, 1) NOT NULL,
                rfq_number VARCHAR(50) NOT NULL UNIQUE,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                requisition_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sourcing_requisitions(id),
                title NVARCHAR(200) NOT NULL,
                submission_deadline DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'OPEN',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 26. Sourcing: RFQ Vendor Bids & Quotations
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_rfq_bids')
        BEGIN
            CREATE TABLE sourcing_rfq_bids (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(12001, 1) NOT NULL,
                rfq_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_rfqs(id),
                vendor_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                bid_reference VARCHAR(50) NOT NULL,
                quoted_amount FLOAT NOT NULL,
                delivery_days INT NOT NULL,
                payment_terms NVARCHAR(100),
                technical_score FLOAT DEFAULT 90.0,
                commercial_score FLOAT DEFAULT 90.0,
                rank_position INT DEFAULT 1,
                is_winner BIT DEFAULT 0,
                remarks NVARCHAR(300),
                submitted_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 27. Sourcing: Comparative Statements (CS Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_comparative_statements')
        BEGIN
            CREATE TABLE sourcing_comparative_statements (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(13001, 1) NOT NULL,
                cs_number VARCHAR(50) NOT NULL UNIQUE,
                rfq_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_rfqs(id),
                title NVARCHAR(200) NOT NULL,
                winning_vendor_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                winning_amount FLOAT NULL,
                evaluation_summary NVARCHAR(500),
                evaluated_by NVARCHAR(100),
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 28. Sourcing: Purchase Orders (PO Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_purchase_orders')
        BEGIN
            CREATE TABLE sourcing_purchase_orders (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(14001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                po_number VARCHAR(50) NOT NULL UNIQUE,
                po_category VARCHAR(50) NOT NULL,
                vendor_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                requisition_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sourcing_requisitions(id),
                cs_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sourcing_comparative_statements(id),
                currency VARCHAR(10) DEFAULT 'USD',
                exchange_rate FLOAT DEFAULT 1.0,
                subtotal FLOAT NOT NULL,
                tax_amount FLOAT DEFAULT 0.0,
                freight_amount FLOAT DEFAULT 0.0,
                total_amount FLOAT NOT NULL,
                payment_terms NVARCHAR(100) DEFAULT 'Net 30 Days',
                incoterm VARCHAR(20) DEFAULT 'FOB',
                delivery_date DATE,
                shipping_address NVARCHAR(300),
                billing_address NVARCHAR(300),
                status VARCHAR(30) DEFAULT 'PENDING_APPROVAL',
                current_approval_tier INT DEFAULT 1,
                max_approval_tier INT DEFAULT 3,
                created_by NVARCHAR(100) DEFAULT 'Procurement Officer',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 29. Sourcing: Purchase Order Items (PO Lines)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_po_items')
        BEGIN
            CREATE TABLE sourcing_po_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                po_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_purchase_orders(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL,
                line_total FLOAT NOT NULL,
                received_qty FLOAT DEFAULT 0.0
            );
        END
        """,

        # 30. Sourcing: Letters of Credit (LC Register)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_letters_of_credit')
        BEGIN
            CREATE TABLE sourcing_letters_of_credit (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(15001, 1) NOT NULL,
                lc_number VARCHAR(50) NOT NULL UNIQUE,
                po_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_purchase_orders(id),
                issuing_bank NVARCHAR(150) NOT NULL,
                branch_name NVARCHAR(150),
                lc_amount FLOAT NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                margin_pct FLOAT DEFAULT 15.0,
                margin_amount FLOAT NOT NULL,
                issue_date DATE NOT NULL,
                expiry_date DATE NOT NULL,
                shipment_deadline DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'OPENED',
                forwarding_letter_ref VARCHAR(80),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 31. Sourcing: C&F Shipping Document Dispatches
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_cnf_dispatches')
        BEGIN
            CREATE TABLE sourcing_cnf_dispatches (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(16001, 1) NOT NULL,
                dispatch_number VARCHAR(50) NOT NULL UNIQUE,
                lc_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sourcing_letters_of_credit(id),
                po_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_purchase_orders(id),
                cnf_agent_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_cnf_agents(id),
                bl_number VARCHAR(80) NOT NULL,
                vessel_name NVARCHAR(100),
                port_of_discharge NVARCHAR(100) DEFAULT 'Chittagong Sea Port',
                dispatch_date DATE NOT NULL,
                eta_date DATE,
                status VARCHAR(30) DEFAULT 'DISPATCHED',
                forwarding_letter_text NVARCHAR(MAX),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 32. Sourcing: Goods Return Notes (GRN Return Memo)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_goods_returns')
        BEGIN
            CREATE TABLE sourcing_goods_returns (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(17001, 1) NOT NULL,
                return_number VARCHAR(50) NOT NULL UNIQUE,
                po_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_purchase_orders(id),
                vendor_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sourcing_vendors(id),
                return_date DATE NOT NULL,
                reason NVARCHAR(250) NOT NULL,
                total_returned_value FLOAT NOT NULL,
                status VARCHAR(30) DEFAULT 'ISSUED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 33. Sourcing: Multi-Tier Digital e-Approvals Tracking
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sourcing_approvals')
        BEGIN
            CREATE TABLE sourcing_approvals (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(18001, 1) NOT NULL,
                entity_type VARCHAR(30) NOT NULL,
                entity_id UNIQUEIDENTIFIER NOT NULL,
                tier_level INT NOT NULL,
                tier_name NVARCHAR(100) NOT NULL,
                approver_name NVARCHAR(100) NOT NULL,
                approver_role NVARCHAR(100) NOT NULL,
                action VARCHAR(30) DEFAULT 'PENDING',
                comments NVARCHAR(300),
                action_date DATETIME,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """
    ]

    for ddl in ddl_scripts:
        db.execute(ddl)

    logger.info("All tables verified/created with GUID primary keys and numeric Code.")

def seed_companies():
    """Seeds multi-company conglomerate subsidiaries."""
    count = db.query_one("SELECT COUNT(*) AS cnt FROM companies")["cnt"]
    if count == 0:
        companies_data = [
            ("Apex Precision Manufacturing Group Ltd", "APEX", "Precision Manufacturing & Electronics", "High-speed CNC, SMT Lines & Industrial Assembly", "USD", "FY 2026-2027", "Plant Delta 01 - Industrial Park", "factory", "#0078D4", 1),
            ("Horizon Property & Infrastructure Developments", "HORIZON", "Real Estate & Civil Construction", "Commercial High-Rises, Townships & Land Assets", "USD", "FY 2026-2027", "Horizon Landmark Tower, Fl 24", "home", "#F59E0B", 2),
            ("Delta Global Logistics & Intermodal C&F", "DELTA", "Supply Chain & Port Freight", "Ocean Clearing & Forwarding, Fleet Routing & Customs", "USD", "FY 2026-2027", "Port Logistics Terminal Berth 4", "truck", "#06B6D4", 3),
            ("Titan Heavy Engineering & Robotics Works", "TITAN", "Heavy Metallurgy & Fabrication", "Structural Steel, KUKA Robotic Welding Cells & Foundry", "USD", "FY 2026-2027", "Steel Fabrication Complex B", "wrench", "#8B5CF6", 4),
            ("Prime Consumer Goods & Retail Distribution", "PRIME", "FMCG & Multi-Warehouse Retail", "Fast-Moving Goods, Warehouses & Regional Distribution", "USD", "FY 2026-2027", "Central Distribution Hub 09", "package", "#10B981", 5),
        ]
        for c in companies_data:
            db.execute(
                """
                INSERT INTO companies (name, short_code, industry, tagline, currency, fiscal_year, headquarters, logo_icon, accent_color, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                c
            )
        logger.info("Seeded 5 Conglomerate Subsidiary Companies.")

def seed_categories():
    """Seeds dynamic categories."""
    cat_count = db.query_one("SELECT COUNT(*) AS cnt FROM dynamic_categories")["cnt"]
    if cat_count == 0:
        categories = [
            ("general", "General & System", "System identification, device naming, and global plant runtime", "cpu", 1),
            ("finance", "Financial & Treasury", "General ledger, receivables, payables, and cash flow", "book-open", 2),
            ("supply_chain", "Supply Chain & Logistics", "Procurement, inventory, sales, and distribution", "shopping-cart", 3),
            ("manufacturing", "Plant Operations & Line Telemetry", "Shop-floor lines, assembly speeds, automated defect triggers", "factory", 4),
            ("property", "Property & Construction", "Real estate sales, project costing, and engineering", "home", 5),
            ("hr", "Human Capital & CRM", "HRIS, payroll, CRM pipeline, and administration", "users", 6),
            ("appearance", "Aesthetics & Glassmorphism", "macOS frosted glass blur, Windows 11 Fluent themes, accent glow", "palette", 7),
            ("database", "SQL Server 2025 Diagnostics", "Connection pool thresholds, query cache, telemetry sync rate", "database", 8),
            ("dynamic_fields", "Dynamic Layout & Field Studio", "Add custom fields and drag-and-drop reorder cards at runtime", "layout-grid", 9),
            ("security", "Security & Audit Trail", "Operator permissions, multi-factor guards, session timeout", "shield-check", 10),
        ]
        for c in categories:
            db.execute(
                """
                INSERT INTO dynamic_categories (category_code, name, description, icon, sort_order, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                c
            )
        logger.info("Seeded dynamic_categories.")

def seed_dynamic_options():
    """Seeds rich dynamic options."""
    opt_count = db.query_one("SELECT COUNT(*) AS cnt FROM dynamic_options")["cnt"]
    if opt_count == 0:
        options = [
            ("system_plant_name", "general", "Plant Facility Identifier", "Unique plant facility name shown in top navigation and headers", "text", "Plant Delta 01 - Main Production Hall", "Plant Delta 01", None, None, None, None, None, "building-2", 1, 1, 1),
            ("system_auto_sync", "general", "Real-Time Telemetry Sync", "Continuously sync sensor telemetry directly to SQL Server 2025", "toggle", "true", "true", None, None, None, None, None, "refresh-cw", 2, 1, 1),
            ("system_heartbeat_interval", "general", "Telemetry Heartbeat Rate", "Interval in seconds between plant machine telemetry samples", "slider", "5", "5", None, 1, 60, 1, "sec", "activity", 3, 1, 0),
            ("system_operating_mode", "general", "Plant Operating State", "Primary production shift operational profile", "select", "high_output", "standard", json.dumps([{"label": "Standard Efficiency", "value": "standard"}, {"label": "High Output (Overclocked Line)", "value": "high_output"}, {"label": "Night Maintenance Shift", "value": "maintenance"}, {"label": "Eco-Idle Power Saver", "value": "eco"}]), None, None, None, None, "zap", 4, 1, 0),
            ("mfg_auto_reject_defects", "manufacturing", "Automated Optical Defect Rejection", "Instantly trigger pneumatic kickers when camera defect detection > 2%", "toggle", "true", "true", None, None, None, None, None, "scan", 1, 1, 0),
            ("mfg_target_line_speed", "manufacturing", "Assembly Conveyor Target Speed", "Target output speed in units per minute across Main Line A", "slider", "120", "100", None, 30, 200, 5, "PPM", "gauge", 2, 1, 0),
            ("app_acrylic_blur", "appearance", "macOS Frosted Glass Blur Depth", "Adjust backdrop blur filter intensity for floating menus and cards", "slider", "24", "20", None, 4, 48, 2, "px", "sparkles", 1, 1, 0),
            ("db_pool_max_size", "database", "SQL Server Connection Pool Capacity", "Maximum simultaneous worker connections in thread-safe pool", "slider", "50", "30", None, 10, 150, 5, "conns", "layers", 1, 1, 0),
        ]
        for opt in options:
            db.execute(
                """
                INSERT INTO dynamic_options 
                (option_key, category_code, label, description, field_type, current_value, default_value, options_json, min_val, max_val, step_val, unit, icon, sort_order, is_visible, is_system)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (opt[0], opt[1], opt[2], opt[3], opt[4], opt[5], opt[6], opt[7], opt[8], opt[9], opt[10], opt[11], opt[12], opt[13], opt[15])
            )
        logger.info("Seeded dynamic_options.")

def seed_enterprise_modules():
    """Seeds the 21 enterprise modules from the system blueprint."""
    count = db.query_one("SELECT COUNT(*) AS cnt FROM enterprise_modules")["cnt"]
    if count == 0:
        modules = [
            ("GENERAL_LEDGER", "General Ledger", "Financial & Treasury", "finance", "general-ledger", "book-open", "Chart of accounts, journal vouchers, fiscal period closing, balance sheet & P&L", "ACTIVE", 2, 1),
            ("ACCOUNTS_RECEIVABLE", "Accounts Receivable", "Financial & Treasury", "finance", "accounts-receivable", "receipt", "Customer billing, overdue aging reports, collection forecasting & credit limits", "ACTIVE", 5, 2),
            ("ACCOUNTS_PAYABLE", "Accounts Payable", "Financial & Treasury", "finance", "accounts-payable", "credit-card", "Vendor invoice approvals, 3-way matching, disbursement batches & tax withholding", "ACTIVE", 3, 3),
            ("CASH_BOOK", "Cash Book", "Financial & Treasury", "finance", "cash-book", "wallet", "Bank reconciliation, petty cash balances, daily liquidity & cash flow forecasting", "ACTIVE", 0, 4),
            ("SOURCING", "Sourcing & Procurement", "Supply Chain & Logistics", "supply_chain", "sourcing", "shopping-cart", "Supplier evaluation, purchase requisitions, RFQ tenders & contract milestones", "ACTIVE", 4, 5),
            ("INVENTORY_MANAGEMENT", "Inventory Management", "Supply Chain & Logistics", "supply_chain", "inventory", "package", "Multi-warehouse stock, lot/batch tracking, reorder thresholds & FIFO valuation", "ACTIVE", 1, 6),
            ("SALES_MANAGEMENT", "Sales Management", "Supply Chain & Logistics", "supply_chain", "sales", "badge-percent", "Sales orders, dynamic discount matrices, territory targets & customer fulfillment", "ACTIVE", 6, 7),
            ("DISTRIBUTION_TRANSPORTATION", "Distribution & Transportation", "Supply Chain & Logistics", "supply_chain", "distribution", "truck", "Fleet dispatch routing, carrier manifests, freight charges & proof of delivery", "ACTIVE", 0, 8),
            ("CNF_JOB_MANAGEMENT", "C&F Job Management", "Supply Chain & Logistics", "supply_chain", "cnf-jobs", "container", "Clearing & forwarding, bill of lading, customs clearance & port container tracking", "ACTIVE", 2, 9),
            ("PLANNING_MRP", "Planning (MRP)", "Manufacturing & Plant", "manufacturing", "mrp-planning", "calendar-clock", "Material requirements planning, master production schedule (MPS) & lead times", "ACTIVE", 1, 10),
            ("PRODUCTION_MANAGEMENT", "Production Management", "Manufacturing & Plant", "manufacturing", "production", "factory", "Shop-floor work orders, machine routing, BOM explosion & real-time line telemetry", "ACTIVE", 0, 11),
            ("FIXED_ASSETS_MAINTENANCE", "Fixed Assets & Maintenance", "Manufacturing & Plant", "manufacturing", "fixed-assets", "wrench", "Asset registry, depreciation schedules, work order repair & preventive maintenance", "ACTIVE", 3, 12),
            ("PROPERTY_SALES_REGISTRATION", "Property Sales & Registration", "Property & Construction", "property", "property-sales", "home", "Unit booking catalog, allotment letters, installment schedules & title deed registry", "ACTIVE", 8, 13),
            ("PROPERTY_DEVELOPMENT", "Property Development System", "Property & Construction", "property", "property-dev", "map-pin", "Land parcel acquisition, zoning, master planning phases & handover timelines", "ACTIVE", 0, 14),
            ("PROPERTY_PROJECT_COST", "Property Project Cost Management", "Property & Construction", "property", "property-cost", "calculator", "Cost center allocation, contractor variance analysis, retention money & budgets", "ACTIVE", 2, 15),
            ("DESIGN_CONSTRUCTION", "Design & Construction Management", "Property & Construction", "property", "construction", "hard-hat", "Bill of Quantities (BOQ), civil work milestones, architectural drawings & site logs", "ACTIVE", 4, 16),
            ("HRIS", "HRIS (Human Resources)", "Human Capital & Admin", "hr", "hris", "users", "Employee records, biometric attendance, payroll calculation & shift scheduling", "ACTIVE", 0, 17),
            ("CRM", "CRM (Customer Relations)", "Human Capital & Admin", "hr", "crm", "user-check", "Lead pipeline, opportunity stages, interaction logs & customer support tickets", "ACTIVE", 7, 18),
            ("ADMINISTRATIVE_FUNCTIONS", "Administrative Functions", "Human Capital & Admin", "hr", "admin-functions", "briefcase", "Gate pass approvals, stationery requisitions, corporate SOPs & office policies", "ACTIVE", 1, 19),
            ("SYSTEM_ADMINISTRATION", "System Administration", "Intelligence & Admin", "analytics", "system-admin", "shield-check", "User access roles, MS SQL Server 2025 diagnostics, security policies & audit logs", "ACTIVE", 0, 20),
        ]

        for m in modules:
            db.execute(
                """
                INSERT INTO enterprise_modules
                (module_code, name, domain_group, domain_code, route_slug, icon, description, status, badge_count, sort_order, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                m
            )
        logger.info("Seeded all 21 enterprise modules.")

def seed_company_records():
    """Seeds company-specific transactions (Sales Orders, STO, PO, JV, Allotments)."""
    rec_count = db.query_one("SELECT COUNT(*) AS cnt FROM module_records")["cnt"]
    if rec_count == 0:
        apex = db.query_one("SELECT id FROM companies WHERE short_code = 'APEX'")
        horizon = db.query_one("SELECT id FROM companies WHERE short_code = 'HORIZON'")
        delta = db.query_one("SELECT id FROM companies WHERE short_code = 'DELTA'")
        titan = db.query_one("SELECT id FROM companies WHERE short_code = 'TITAN'")
        prime = db.query_one("SELECT id FROM companies WHERE short_code = 'PRIME'")

        records = [
            # 1. Apex Manufacturing Records
            (apex["id"], "SALES_MANAGEMENT", "SALES_ORDER", "SO-APX-8801", "Precision Fastener Export Order (x20,000 units)", "PROCESSING", 145000.00, "EuroAutomotive AG", "Apex Sales Lead"),
            (apex["id"], "SALES_MANAGEMENT", "SALES_ORDER", "SO-APX-8802", "Aerospace Titanium Bushings Batch #2", "APPROVED", 92400.00, "Boeing Subcontractor", "Apex Sales Lead"),
            (apex["id"], "INVENTORY_MANAGEMENT", "STO", "STO-APX-301", "Stock Transfer Order: Plant Delta 01 -> Assembly Bay 04", "IN_TRANSIT", 48000.00, "Internal Plant Transfer", "Warehouse Head"),
            (apex["id"], "SOURCING", "PO", "PO-APX-1092", "Bulk CNC Carbide Cutting Tool Inserts", "APPROVED", 28500.00, "Sandvik Coromant", "Procurement Lead"),
            (apex["id"], "GENERAL_LEDGER", "JV", "JV-APX-0820", "Plant Delta 01 Monthly Power & Spindle Depr", "COMPLETED", 36200.00, "Factory Overhead GL", "Chief Accountant"),
            (apex["id"], "PRODUCTION_MANAGEMENT", "WORK_ORDER", "WO-APX-5510", "High-Precision 5-Axis CNC Milling Batch", "IN_PROGRESS", 0.0, "Line 01 Heavy Fab", "Floor Supervisor"),

            # 2. Horizon Property Records
            (horizon["id"], "PROPERTY_SALES_REGISTRATION", "ALLOTMENT", "ALLOT-HRZ-104", "Horizon Grand Tower - 3BR Executive Penthouse #18A", "CONFIRMED", 850000.00, "Dr. Robert Vance", "Property Allotment Desk"),
            (horizon["id"], "PROPERTY_SALES_REGISTRATION", "ALLOTMENT", "ALLOT-HRZ-105", "Commercial Plaza Ground Floor Retail Suite #G02", "UNDER_REVIEW", 1200000.00, "Global Coffee Brands", "Commercial Sales Lead"),
            (horizon["id"], "PROPERTY_PROJECT_COST", "COST_AUDIT", "CST-HRZ-901", "Deep Piling Subcontractor Certificate #04", "APPROVED", 420000.00, "Bauer Foundation JV", "Senior Quantity Surveyor"),
            (horizon["id"], "DESIGN_CONSTRUCTION", "BOQ", "BOQ-HRZ-302", "Structural Steel Reinforcement BOQ Revision 4", "APPROVED", 0.0, "Apex Design Bureau", "Project Chief Engineer"),
            (horizon["id"], "GENERAL_LEDGER", "JV", "JV-HRZ-0801", "Escrow Account Real Estate Installment Inflow", "COMPLETED", 650000.00, "Escrow Trust Account", "Finance Controller"),

            # 3. Delta Global Logistics Records
            (delta["id"], "CNF_JOB_MANAGEMENT", "CNF_JOB", "CNF-DLT-4401", "Customs Clearance: 40ft High-Cube Reefer Container", "IN_CUSTOMS", 18500.00, "Port Authority Terminal", "C&F Specialist"),
            (delta["id"], "DISTRIBUTION_TRANSPORTATION", "DISPATCH", "DSP-DLT-892", "Intermodal Container Fleet Dispatch Route 14", "EN_ROUTE", 0.0, "Volvo Heavy Fleet #08", "Fleet Dispatcher"),
            (delta["id"], "SALES_MANAGEMENT", "SALES_ORDER", "SO-DLT-204", "Ocean Freight Booking - 200 TEU Antwerp Hub", "CONFIRMED", 310000.00, "Maersk Line Alliance", "Logistics Executive"),
            (delta["id"], "ACCOUNTS_RECEIVABLE", "INVOICE", "INV-DLT-661", "Freight Forwarding Demurrage & Handling", "PENDING", 42300.00, "Continental Import Corp", "Billing Officer"),

            # 4. Titan Heavy Engineering Records
            (titan["id"], "PRODUCTION_MANAGEMENT", "WORK_ORDER", "WO-TTN-110", "KUKA 6-Axis Robotic Welding Heavy Chassis", "IN_PROGRESS", 0.0, "Robotics Cell 02", "Robotics Lead"),
            (titan["id"], "SOURCING", "PO", "PO-TTN-405", "Structural Grade High-Tensile Steel Plates (100 Tons)", "APPROVED", 195000.00, "Nippon Steel Corp", "Materials Officer"),
            (titan["id"], "FIXED_ASSETS_MAINTENANCE", "MNT_WO", "MNT-TTN-08", "Hydraulic Press Spindle Preventive Maintenance", "SCHEDULED", 12000.00, "Plant Maintenance", "Chief Millwright"),

            # 5. Prime Consumer Goods Records
            (prime["id"], "INVENTORY_MANAGEMENT", "STO", "STO-PRM-771", "Stock Transfer Order: Central Hub -> Regional Depot C", "COMPLETED", 75000.00, "Warehouse Network", "Logistics Head"),
            (prime["id"], "SALES_MANAGEMENT", "SALES_ORDER", "SO-PRM-9912", "FMCG Supermarket Chain Bulk Distribution", "PROCESSING", 112000.00, "Metro Hypermarkets", "Retail Director"),
            (prime["id"], "CRM", "LEAD", "CRM-PRM-301", "National Wholesale Distributorship Franchise Request", "QUALIFIED", 500000.00, "Eastern Trading Alliance", "Franchise Lead"),
        ]

        for r in records:
            db.execute(
                """
                INSERT INTO module_records (company_id, module_code, record_type, ref_number, title, status, amount, party_name, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                r
            )
        logger.info("Seeded multi-company transactional records.")

def seed_gl_master_data():
    """Seeds master data for General Ledger (COA, Mappings, Sub Accounts, Depts, Cost Centres, Budgets)."""
    coa_count = db.query_one("SELECT COUNT(*) AS cnt FROM gl_accounts")["cnt"]
    if coa_count == 0:
        # 1. Seed Chart of Accounts
        accounts = [
            ("1010-00", "Cash & Liquid Bank Equivalents", "ASSET", "BALANCE_SHEET", "DEBIT"),
            ("1020-00", "Trade Accounts Receivable Control", "ASSET", "BALANCE_SHEET", "DEBIT"),
            ("1030-00", "Inventory & Materials Valuation", "ASSET", "BALANCE_SHEET", "DEBIT"),
            ("1050-00", "Machinery, Plant & Heavy Equipment", "ASSET", "BALANCE_SHEET", "DEBIT"),
            ("2010-00", "Trade Accounts Payable Control", "LIABILITY", "BALANCE_SHEET", "CREDIT"),
            ("2030-00", "Accrued Taxes & Payroll Withholding", "LIABILITY", "BALANCE_SHEET", "CREDIT"),
            ("3010-00", "Share Capital & Retained Earnings", "EQUITY", "BALANCE_SHEET", "CREDIT"),
            ("4010-00", "Gross Commercial Operating Revenue", "REVENUE", "INCOME_STATEMENT", "CREDIT"),
            ("5010-00", "Cost of Goods Sold & Direct Materials", "EXPENSE", "INCOME_STATEMENT", "DEBIT"),
            ("6010-00", "Executive & Plant Payroll Expense", "EXPENSE", "INCOME_STATEMENT", "DEBIT"),
            ("6020-00", "Industrial Electricity & Utilities", "EXPENSE", "INCOME_STATEMENT", "DEBIT"),
            ("6030-00", "Preventive Maintenance & Repairs", "EXPENSE", "INCOME_STATEMENT", "DEBIT"),
        ]
        for a in accounts:
            db.execute(
                """
                INSERT INTO gl_accounts (account_number, account_name, account_type, financial_statement, normal_balance, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                a
            )
        logger.info("Seeded 12 Standard Master GL Accounts (Chart of Accounts).")

        # 2. Seed Departments
        dept_count = db.query_one("SELECT COUNT(*) AS cnt FROM gl_departments")["cnt"]
        if dept_count == 0:
            departments = [
                ("DEP-FIN", "Corporate Finance & Treasury", "Chief Financial Officer"),
                ("DEP-PRD", "Precision Plant Production", "VP Manufacturing"),
                ("DEP-SCM", "Global Supply Chain & Logistics", "Director Supply Chain"),
                ("DEP-ENG", "Civil Works & Structural Engineering", "Chief Project Engineer"),
                ("DEP-HRM", "Human Resources & Talent Development", "Head of HR"),
                ("DEP-OPS", "Executive Operations & IT Systems", "Operations Admin"),
            ]
            for d in departments:
                db.execute(
                    """
                    INSERT INTO gl_departments (dept_code, dept_name, head_of_dept, is_active)
                    VALUES (?, ?, ?, 1)
                    """,
                    d
                )
            logger.info("Seeded 6 Core Organizational Departments.")

        # Query companies and departments for relationships
        apex = db.query_one("SELECT id FROM companies WHERE short_code = 'APEX'")
        horizon = db.query_one("SELECT id FROM companies WHERE short_code = 'HORIZON'")
        delta = db.query_one("SELECT id FROM companies WHERE short_code = 'DELTA'")
        titan = db.query_one("SELECT id FROM companies WHERE short_code = 'TITAN'")
        prime = db.query_one("SELECT id FROM companies WHERE short_code = 'PRIME'")

        dep_fin = db.query_one("SELECT id FROM gl_departments WHERE dept_code = 'DEP-FIN'")
        dep_prd = db.query_one("SELECT id FROM gl_departments WHERE dept_code = 'DEP-PRD'")
        dep_scm = db.query_one("SELECT id FROM gl_departments WHERE dept_code = 'DEP-SCM'")
        dep_eng = db.query_one("SELECT id FROM gl_departments WHERE dept_code = 'DEP-ENG'")

        # 3. Seed Cost Centres
        cost_centres = [
            ("CC-APX-101", "Plant Delta SMT Robotic Assembly", dep_prd["id"], apex["id"]),
            ("CC-APX-102", "5-Axis CNC Precision Milling Bay", dep_prd["id"], apex["id"]),
            ("CC-HRZ-201", "Horizon Grand Tower Site Operations", dep_eng["id"], horizon["id"]),
            ("CC-HRZ-202", "Land Parcel Zoning & Master Survey", dep_eng["id"], horizon["id"]),
            ("CC-DLT-301", "Ocean Port Berth #4 Freight Terminal", dep_scm["id"], delta["id"]),
            ("CC-TTN-401", "KUKA 6-Axis Heavy Fabrication Cell", dep_prd["id"], titan["id"]),
            ("CC-PRM-501", "Regional Retail Distribution Hub 09", dep_scm["id"], prime["id"]),
            ("CC-CORP-901", "Corporate Treasury & Statutory Audit", dep_fin["id"], apex["id"]),
        ]
        for cc in cost_centres:
            db.execute(
                """
                INSERT INTO gl_cost_centres (cost_centre_code, cost_centre_name, department_id, company_id, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                cc
            )
        logger.info("Seeded 8 Enterprise Cost Centres.")

        # 4. Seed GL Company Mappings
        gl_accs = db.query("SELECT id, account_number FROM gl_accounts")
        for acc in gl_accs:
            for comp in [apex, horizon, delta, titan, prime]:
                db.execute(
                    """
                    INSERT INTO gl_company_mappings (gl_account_id, company_id, company_account_alias, allow_direct_posting, posting_currency, is_enabled)
                    VALUES (?, ?, ?, 1, 'USD', 1)
                    """,
                    (acc["id"], comp["id"], f"{acc['account_number']}")
                )
        logger.info("Seeded Multi-Company GL Account Mappings.")

        # 5. Seed GL Sub Accounts
        acc_rev = db.query_one("SELECT id FROM gl_accounts WHERE account_number = '4010-00'")
        acc_cogs = db.query_one("SELECT id FROM gl_accounts WHERE account_number = '5010-00'")
        acc_maint = db.query_one("SELECT id FROM gl_accounts WHERE account_number = '6030-00'")

        sub_accounts = [
            (acc_rev["id"], "SUB-REV-EXP", "High-Precision Export Contracts", "PRODUCT_LINE"),
            (acc_rev["id"], "SUB-REV-DOM", "Domestic Commercial Supply Agreements", "GEOGRAPHIC"),
            (acc_cogs["id"], "SUB-MAT-CNC", "Direct Carbide Tooling & Raw Titanium", "DEPARTMENTAL"),
            (acc_maint["id"], "SUB-MNT-KUKA", "Robotics Spindle Overhaul & Calibration", "PROJECT"),
        ]
        for sa in sub_accounts:
            db.execute(
                """
                INSERT INTO gl_sub_accounts (gl_account_id, sub_account_code, sub_account_name, sub_account_type, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                sa
            )
        logger.info("Seeded 4 Granular Sub Accounts.")

        # 6. Seed Budget Sets
        cc_apx = db.query_one("SELECT id FROM gl_cost_centres WHERE cost_centre_code = 'CC-APX-101'")
        cc_hrz = db.query_one("SELECT id FROM gl_cost_centres WHERE cost_centre_code = 'CC-HRZ-201'")
        cc_dlt = db.query_one("SELECT id FROM gl_cost_centres WHERE cost_centre_code = 'CC-DLT-301'")
        acc_util = db.query_one("SELECT id FROM gl_accounts WHERE account_number = '6020-00'")
        acc_cogs_id = acc_cogs["id"]

        budgets = [
            ("BUD-2026-APX-01", "Plant Delta Annual Power & Grid Quota", "2026-2027", apex["id"], cc_apx["id"], acc_util["id"], 480000.00, 114200.00, "APPROVED"),
            ("BUD-2026-APX-02", "Direct Tooling & Raw Material Budget", "2026-2027", apex["id"], cc_apx["id"], acc_cogs_id, 1200000.00, 385000.00, "APPROVED"),
            ("BUD-2026-HRZ-01", "Civil Subcontractor Milestone Budget", "2026-2027", horizon["id"], cc_hrz["id"], acc_cogs_id, 3500000.00, 920000.00, "APPROVED"),
            ("BUD-2026-DLT-01", "Port Handling & Terminal Fleet Budget", "2026-2027", delta["id"], cc_dlt["id"], acc_util["id"], 650000.00, 182000.00, "APPROVED"),
        ]
        for b in budgets:
            db.execute(
                """
                INSERT INTO gl_budget_sets (budget_code, budget_title, fiscal_year, company_id, cost_centre_id, gl_account_id, allocated_amount, utilized_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                b
            )
        logger.info("Seeded 4 Master Budget Sets.")

def seed_sourcing_master_and_transactions():
    """Seeds comprehensive Sourcing & Procurement master data and realistic transactions."""
    vendor_count = db.query_one("SELECT COUNT(*) AS cnt FROM sourcing_vendors")["cnt"]
    if vendor_count == 0:
        # 1. Sourcing Vendors Master Profile
        vendors = [
            ("VND-001", "Sandvik Coromant Global AB", "MANUFACTURER_OEM", "CORPORATE", "Magnus Larsson", "procurement@sandvik.com", "+46 26 26 00 00", "Sandviken, Sweden", "TIN-SWE-8890", "VAT-SE-9912", "Skandinaviska Enskilda Banken", "Stockholm Central", "SEB-99882201", "ESSESESS", 45, "USD", 4.9),
            ("VND-002", "Iscar Precision Tools Ltd", "MANUFACTURER_OEM", "CORPORATE", "Avi Ben-David", "sales@iscar.com", "+972 4 997 0311", "Tefen Industrial Zone, Israel", "TIN-ISR-4410", "VAT-IL-7721", "Bank Leumi", "Haifa Bay Branch", "BL-1029384", "LUMIILIT", 30, "USD", 4.7),
            ("VND-003", "Kyocera Precision Tools Japan", "DISTRIBUTOR", "CORPORATE", "Kenji Takahashi", "global_orders@kyocera.jp", "+81 75 604 3500", "Kyoto, Japan", "TIN-JPN-1102", "VAT-JP-8819", "Mizuho Bank", "Kyoto Central", "MZ-4499201", "MHCBJPJT", 30, "USD", 4.6),
            ("VND-004", "Nippon Steel Structural Solutions", "MANUFACTURER_OEM", "CORPORATE", "Hiroshi Sato", "export@nipponsteel.com", "+81 3 6867 4111", "Tokyo, Japan", "TIN-JPN-9941", "VAT-JP-3301", "MUFG Bank", "Tokyo Head Office", "MUFG-7711902", "BOTKJPJT", 60, "USD", 4.8),
            ("VND-005", "Linde Industrial Gases & Cryogenics", "LOCAL_SUPPLIER", "CORPORATE", "Marcus Weber", "industrial@linde.com", "+49 89 35757 0", "Munich, Germany", "TIN-DEU-5521", "VAT-DE-1109", "Deutsche Bank", "Munich Commercial", "DB-8819024", "DEUTDEDD", 30, "EUR", 4.8),
            ("VND-006", "Siemens Industrial Automation & Drives", "MANUFACTURER_OEM", "CORPORATE", "Hans Becker", "automation@siemens.com", "+49 911 895 0", "Nuremberg, Germany", "TIN-DEU-7720", "VAT-DE-9940", "Commerzbank", "Frankfurt Central", "CB-6629103", "COBADEFF", 45, "EUR", 4.9),
            ("VND-007", "Bengal National Hardware & Steel Syndicate", "LOCAL_SUPPLIER", "PARTNERSHIP", "Rashidul Islam", "bengal_hardware@dhaka.net", "+880 2 9567812", "Tejgaon Industrial Area, Dhaka", "TIN-BD-229910", "BIN-BD-009182", "City Bank Ltd", "Principal Branch", "CBL-9918230", "CIBLBDDH", 30, "USD", 4.4),
            ("VND-008", "Avery Dennison Packaging Materials", "LOCAL_SUPPLIER", "CORPORATE", "Farhana Anis", "fmcg_supplies@avery.com", "+880 2 8831920", "DEPZ Savar, Dhaka", "TIN-BD-441829", "BIN-BD-004491", "Standard Chartered Bank", "Gulshan Branch", "SCB-3388291", "SCBLBDDX", 30, "USD", 4.5),
        ]
        for v in vendors:
            db.execute(
                """
                INSERT INTO sourcing_vendors 
                (vendor_code, vendor_name, vendor_group, vendor_org_type, contact_person, email, phone, address, tax_id_tin, vat_bin, bank_name, bank_branch, bank_account, bank_swift, credit_terms_days, currency, rating_stars, is_active, isDelete)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
                """,
                v
            )
        logger.info("Seeded 8 Master Sourcing Vendors.")

        # 2. Purchasing Orgs
        orgs = [
            ("PUR-ORG-01", "Apex Central Procurement Division", "CENTRAL", "Director SCM & Procurement"),
            ("PUR-ORG-02", "Plant Delta 01 Site Procurement", "PLANT_SPECIFIC", "Plant Procurement Head"),
            ("PUR-ORG-03", "Horizon Infrastructure Sourcing Unit", "CENTRAL", "Head of Civil Procurement"),
        ]
        for o in orgs:
            db.execute(
                """
                INSERT INTO sourcing_purchasing_orgs (org_code, org_name, org_type, head_of_procurement, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                o
            )
        logger.info("Seeded 3 Purchasing Organizations.")

        # 3. Sourcing Buyers
        buyers = [
            ("BYR-101", "Mahmudur Rahman", "Machining, Tooling & Precision CNC", 100000.0),
            ("BYR-102", "Shamim Chowdhury", "Electrical, SMT Components & PLCs", 75000.0),
            ("BYR-103", "Tanvir Ahmed", "Structural Rebar, Cement & Civil Assets", 250000.0),
            ("BYR-104", "Nusrat Jahan", "Corporate Stationery, Consumables & Admin", 25000.0),
        ]
        for b in buyers:
            db.execute(
                """
                INSERT INTO sourcing_buyers (buyer_code, buyer_name, assigned_categories, max_approval_limit, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                b
            )
        logger.info("Seeded 4 Sourcing Buyers.")

        # 4. Sourcing Price Terms (Incoterms & Payment Terms)
        price_terms = [
            ("TERM-FOB-45", "FOB Sea Port (Net 45 Days Credit)", "FOB", 45, 12, "Free on Board sea vessel, payment 45 days after BL date"),
            ("TERM-CIF-30", "CIF Destination Port (LC at Sight)", "CIF", 0, 12, "Cost, Insurance and Freight included, Letter of Credit at sight"),
            ("TERM-CFR-60", "CFR Sea Port (Net 60 Days Usance LC)", "CFR", 60, 12, "Cost and Freight, 60-day deferred payment LC"),
            ("TERM-EXW-00", "Ex-Works Factory Gate (Cash in Advance)", "EX_WORKS", 0, 6, "Ex-factory pickup, advance payment before release"),
            ("TERM-LOC-30", "Local Delivery Plant Gate (Net 30 Days)", "DDP", 30, 12, "Direct delivered to factory warehouse, Net 30 days after GRN"),
        ]
        for pt in price_terms:
            db.execute(
                """
                INSERT INTO sourcing_price_terms (term_code, term_name, incoterm, credit_days, validity_period_months, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                pt
            )
        logger.info("Seeded 5 Sourcing Price Terms.")

        # 5. Sourcing C&F Agents
        cnf_agents = [
            ("CNF-001", "Bengal Intermodal C&F Services Ltd", "Chittagong Sea Port & Airport Cargo", "LIC-CTG-44910", "Khorshed Alam", "+880 31 718820", "operations@bengalcnf.com", 4.9),
            ("CNF-002", "Port Maritime Freight & Customs Clearing", "Mongla Port & Benapole Land Port", "LIC-MNG-11029", "Zahid Hasan", "+880 41 729910", "clearing@portmaritime.com", 4.7),
        ]
        for ca in cnf_agents:
            db.execute(
                """
                INSERT INTO sourcing_cnf_agents (agent_code, agent_name, port_location, license_number, contact_person, phone, email, rating_score, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                ca
            )
        logger.info("Seeded 2 C&F Agents.")

        # 6. Sourcing Exchange Rates
        fx_rates = [
            ("USD", "USD", 1.0),
            ("USD", "EUR", 1.085),
            ("USD", "GBP", 1.275),
            ("USD", "JPY", 0.0065),
            ("USD", "BDT", 121.50),
        ]
        for fx in fx_rates:
            db.execute(
                """
                INSERT INTO sourcing_exchange_rates (base_currency, foreign_currency, exchange_rate)
                VALUES (?, ?, ?)
                """,
                fx
            )
        logger.info("Seeded 5 Currency Exchange Rates.")

        # Query companies and vendors for transactions
        apex = db.query_one("SELECT id FROM companies WHERE short_code = 'APEX'")
        horizon = db.query_one("SELECT id FROM companies WHERE short_code = 'HORIZON'")
        delta = db.query_one("SELECT id FROM companies WHERE short_code = 'DELTA'")
        titan = db.query_one("SELECT id FROM companies WHERE short_code = 'TITAN'")
        prime = db.query_one("SELECT id FROM companies WHERE short_code = 'PRIME'")

        vnd_sandvik = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-001'")
        vnd_iscar = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-002'")
        vnd_kyocera = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-003'")
        vnd_nippon = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-004'")
        vnd_siemens = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-006'")
        vnd_bengal = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-007'")
        vnd_avery = db.query_one("SELECT id FROM sourcing_vendors WHERE vendor_code = 'VND-008'")

        cnf_bengal = db.query_one("SELECT id FROM sourcing_cnf_agents WHERE agent_code = 'CNF-001'")

        # 7. Vendor Enlistments & Mappings
        for v_id in [vnd_sandvik["id"], vnd_iscar["id"], vnd_kyocera["id"], vnd_siemens["id"]]:
            db.execute(
                """
                INSERT INTO sourcing_vendor_enlistments 
                (vendor_id, category_name, enlistment_tier, valid_from, valid_to, financial_capacity_usd, status, inspection_status)
                VALUES (?, 'High-Precision Cutting Tools & CNC', 'TIER_1_APPROVED', '2026-01-01', '2026-12-31', 1500000.0, 'ACTIVE', 'VERIFIED_PASSED')
                """,
                (v_id,)
            )
            for c_id in [apex["id"], titan["id"]]:
                db.execute(
                    """
                    INSERT INTO sourcing_vendor_company_mappings (vendor_id, company_id, vendor_account_alias, payment_method, is_approved)
                    VALUES (?, ?, 'VND-DIRECT', 'BANK_TRANSFER', 1)
                    """,
                    (v_id, c_id)
                )

        # 8. Requisitions (PR)
        reqs = [
            (apex["id"], "REQ-2026-001", "SPARES", "Bulk CNC Carbide Tool Inserts & Milling Cutters", "HIGH", "M. Rahman (Plant Delta)", 28500.0, "APPROVED", "Approved for RFQ bidding"),
            (horizon["id"], "REQ-2026-002", "DECISION_FORM", "High-Tensile Grade 60 Structural Deformed Rebar (100 Tons)", "URGENT", "T. Ahmed (Civil Lead)", 195000.0, "APPROVED", "Project Tower Horizon Phase 3"),
            (apex["id"], "REQ-2026-003", "SERVICE_REQUEST", "5-Axis CNC Spindle Laser Interferometer Calibration", "MEDIUM", "S. Chowdhury (Maintenance)", 12000.0, "PENDING_APPROVAL", "Annual preventive calibration"),
            (prime["id"], "REQ-2026-004", "STATIONERY", "High-Speed Barcode Shipping Labels & Ribbons (500 Rolls)", "LOW", "N. Jahan (Admin)", 4800.0, "APPROVED", "Central Warehouse dispatch"),
        ]
        for r in reqs:
            db.execute(
                """
                INSERT INTO sourcing_requisitions 
                (company_id, req_number, req_type, title, priority, requester_name, total_estimated_amount, currency, status, is_closed, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'USD', ?, 0, ?)
                """,
                r
            )
        logger.info("Seeded 4 Multi-Type Requisitions.")

        req_1 = db.query_one("SELECT id FROM sourcing_requisitions WHERE req_number = 'REQ-2026-001'")
        req_2 = db.query_one("SELECT id FROM sourcing_requisitions WHERE req_number = 'REQ-2026-002'")

        # Seed PR Items
        if req_1:
            db.execute(
                """
                INSERT INTO sourcing_requisition_items 
                (requisition_id, item_code, item_name, specification, uom, quantity, estimated_unit_price, estimated_total, required_by_date)
                VALUES (?, 'ITM-CNC-001', 'CoroMill Carbide Milling Inserts R390', 'R390-11T308M-PM 1130 Grade', 'PCS', 500, 48.50, 24250.0, '2026-09-30')
                """,
                (req_1["id"],)
            )
            db.execute(
                """
                INSERT INTO sourcing_requisition_items 
                (requisition_id, item_code, item_name, specification, uom, quantity, estimated_unit_price, estimated_total, required_by_date)
                VALUES (?, 'ITM-CNC-002', 'High-Feed End Mill Solid Carbide Shanks', '12mm 4-Flute AlTiN Coating', 'PCS', 50, 85.00, 4250.0, '2026-09-30')
                """,
                (req_1["id"],)
            )

        # 9. RFQ & Comparative Statement
        if req_1:
            db.execute(
                """
                INSERT INTO sourcing_rfqs (rfq_number, company_id, requisition_id, title, submission_deadline, status)
                VALUES ('RFQ-2026-089', ?, ?, 'Tender: CNC Carbide Milling Tool Inserts Batch 02', '2026-09-15', 'EVALUATED')
                """,
                (apex["id"], req_1["id"])
            )
            rfq_1 = db.query_one("SELECT id FROM sourcing_rfqs WHERE rfq_number = 'RFQ-2026-089'")

            # Seed 3 Bids
            db.execute(
                """
                INSERT INTO sourcing_rfq_bids 
                (rfq_id, vendor_id, bid_reference, quoted_amount, delivery_days, payment_terms, technical_score, commercial_score, rank_position, is_winner, remarks)
                VALUES (?, ?, 'BID-SANDVIK-9901', 28500.0, 14, 'Net 45 Days Credit', 96.5, 98.0, 1, 1, 'Lowest evaluated bidder & highest technical compliance')
                """,
                (rfq_1["id"], vnd_sandvik["id"])
            )
            db.execute(
                """
                INSERT INTO sourcing_rfq_bids 
                (rfq_id, vendor_id, bid_reference, quoted_amount, delivery_days, payment_terms, technical_score, commercial_score, rank_position, is_winner, remarks)
                VALUES (?, ?, 'BID-ISCAR-4402', 30200.0, 28, 'LC at Sight', 91.0, 88.0, 2, 0, 'Higher price & longer lead time')
                """,
                (rfq_1["id"], vnd_iscar["id"])
            )
            db.execute(
                """
                INSERT INTO sourcing_rfq_bids 
                (rfq_id, vendor_id, bid_reference, quoted_amount, delivery_days, payment_terms, technical_score, commercial_score, rank_position, is_winner, remarks)
                VALUES (?, ?, 'BID-KYOCERA-8810', 31500.0, 21, '50% Advance + 50%', 88.5, 84.0, 3, 0, 'Advance payment term not preferred')
                """,
                (rfq_1["id"], vnd_kyocera["id"])
            )

            # Seed Comparative Statement
            db.execute(
                """
                INSERT INTO sourcing_comparative_statements 
                (cs_number, rfq_id, title, winning_vendor_id, winning_amount, evaluation_summary, evaluated_by, status)
                VALUES ('CS-2026-042', ?, 'Comparative Statement: CNC Tool Inserts (3 Bidders)', ?, 28500.0, 'Sandvik Coromant evaluated as L1 Winner with 14 days lead time and Net 45 Days payment terms.', 'Procurement Evaluation Committee', 'PO_AWARDED')
                """,
                (rfq_1["id"], vnd_sandvik["id"])
            )
            cs_1 = db.query_one("SELECT id FROM sourcing_comparative_statements WHERE cs_number = 'CS-2026-042'")

        # 10. Purchase Orders (PO)
        pos = [
            (apex["id"], "PO-APX-1092", "IMPORT_WITH_PR", vnd_sandvik["id"], req_1["id"] if req_1 else None, cs_1["id"] if cs_1 else None, "USD", 1.0, 28500.0, 0.0, 0.0, 28500.0, "Net 45 Days", "FOB", "Plant Delta 01 Receiving Dock", "Apex Precision HQ", "APPROVED", 3, 3, "M. Rahman"),
            (horizon["id"], "PO-HRZ-2041", "LOCAL_WITH_PR", vnd_nippon["id"], req_2["id"] if req_2 else None, None, "USD", 1.0, 195000.0, 9750.0, 0.0, 204750.0, "LC at Sight 60D", "CIF", "Horizon Grand Tower Site Gate 2", "Horizon Finance", "APPROVED", 3, 3, "T. Ahmed"),
            (apex["id"], "PO-APX-1095", "SPARES", vnd_siemens["id"], None, None, "EUR", 1.085, 14800.0, 0.0, 450.0, 15250.0, "Net 30 Days", "FOB", "Plant Delta 01 Maintenance Bay", "Apex Precision HQ", "ISSUED", 2, 2, "S. Chowdhury"),
            (prime["id"], "PO-PRM-5020", "STATIONERY_CONSUMABLES", vnd_avery["id"], None, None, "USD", 1.0, 8600.0, 430.0, 0.0, 9030.0, "Net 30 Days", "DDP", "Central Distribution Warehouse", "Prime Retail HQ", "RECEIVED", 2, 2, "N. Jahan"),
        ]
        for p in pos:
            db.execute(
                """
                INSERT INTO sourcing_purchase_orders 
                (company_id, po_number, po_category, vendor_id, requisition_id, cs_id, currency, exchange_rate, subtotal, tax_amount, freight_amount, total_amount, payment_terms, incoterm, shipping_address, billing_address, status, current_approval_tier, max_approval_tier, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                p
            )
        logger.info("Seeded 4 Master Purchase Orders.")

        po_1 = db.query_one("SELECT id FROM sourcing_purchase_orders WHERE po_number = 'PO-APX-1092'")
        po_2 = db.query_one("SELECT id FROM sourcing_purchase_orders WHERE po_number = 'PO-HRZ-2041'")

        if po_1:
            db.execute(
                """
                INSERT INTO sourcing_po_items (po_id, item_code, item_name, uom, quantity, unit_price, line_total, received_qty)
                VALUES (?, 'ITM-CNC-001', 'CoroMill Carbide Milling Inserts R390', 'PCS', 500, 48.50, 24250.0, 500.0)
                """,
                (po_1["id"],)
            )
            db.execute(
                """
                INSERT INTO sourcing_po_items (po_id, item_code, item_name, uom, quantity, unit_price, line_total, received_qty)
                VALUES (?, 'ITM-CNC-002', 'High-Feed End Mill Solid Carbide Shanks', 'PCS', 50, 85.00, 4250.0, 50.0)
                """,
                (po_1["id"],)
            )

            # 11. Letter of Credit (LC) for PO-APX-1092
            db.execute(
                """
                INSERT INTO sourcing_letters_of_credit 
                (lc_number, po_id, issuing_bank, branch_name, lc_amount, currency, margin_pct, margin_amount, issue_date, expiry_date, shipment_deadline, status, forwarding_letter_ref)
                VALUES ('LC-2026-APX-01', ?, 'HSBC Bank Middle East / Dhaka Branch', 'Corporate Banking Unit', 28500.0, 'USD', 15.0, 4275.0, '2026-08-01', '2026-10-30', '2026-09-30', 'OPENED', 'FWD-LC-HSBC-8890')
                """,
                (po_1["id"],)
            )
            lc_1 = db.query_one("SELECT id FROM sourcing_letters_of_credit WHERE lc_number = 'LC-2026-APX-01'")

            # 12. C&F Shipping Document Dispatch
            if lc_1 and cnf_bengal:
                db.execute(
                    """
                    INSERT INTO sourcing_cnf_dispatches 
                    (dispatch_number, lc_id, po_id, cnf_agent_id, bl_number, vessel_name, port_of_discharge, dispatch_date, eta_date, status, forwarding_letter_text)
                    VALUES ('DSP-CNF-2026-01', ?, ?, ?, 'BL-MAERSK-990182', 'M/V Northern Valence V.2608', 'Chittagong Sea Port Berth 4', '2026-08-20', '2026-09-05', 'DISPATCHED', 'Please find attached original Bill of Lading, Commercial Invoice and Packing List for immediate customs assessment.')
                    """,
                    (lc_1["id"], po_1["id"], cnf_bengal["id"])
                )

            # 13. Goods Return Note
            db.execute(
                """
                INSERT INTO sourcing_goods_returns (return_number, po_id, vendor_id, return_date, reason, total_returned_value, status)
                VALUES ('GRN-RET-2026-01', ?, ?, '2026-08-25', 'Micro-chipping defect on 30 units Carbide inserts', 1455.0, 'ISSUED')
                """,
                (po_1["id"], vnd_sandvik["id"])
            )

            # 14. e-Approval History
            approvals = [
                ("PO", po_1["id"], 1, "Tier 1: Department Requester", "M. Rahman", "Plant SCM Lead", "APPROVED", "Approved within department budget", "2026-08-15 09:15:00"),
                ("PO", po_1["id"], 2, "Tier 2: Procurement Head", "K. Al-Mamun", "Director Procurement", "APPROVED", "CS Winner validated and Incoterms verified", "2026-08-15 11:30:00"),
                ("PO", po_1["id"], 3, "Tier 3: CFO / Finance Controller", "J. Smith", "Chief Financial Officer", "APPROVED", "LC Margin funds allocated in treasury", "2026-08-16 14:00:00"),
            ]
            for a in approvals:
                db.execute(
                    """
                    INSERT INTO sourcing_approvals 
                    (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments, action_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    a
                )
        logger.info("Seeded Sourcing LC, C&F Dispatches, Goods Returns, and Multi-Tier e-Approvals.")

def seed_appearance():
    """Seeds default appearance settings."""
    app_count = db.query_one("SELECT COUNT(*) AS cnt FROM appearance_settings")["cnt"]
    if app_count == 0:
        db.execute(
            """
            INSERT INTO appearance_settings 
            (theme_mode, accent_color, font_family, glass_blur_px, glass_opacity_pct, sidebar_style, border_glow, sound_effects)
            VALUES ('light', '#0078D4', 'SF Pro Display', 24, 75, 'floating', 1, 0)
            """
        )
        logger.info("Seeded appearance_settings.")

def setup_database():
    """Main database setup orchestrator."""
    ensure_database_exists()
    initialize_tables()
    seed_companies()
    seed_categories()
    seed_dynamic_options()
    seed_enterprise_modules()
    seed_company_records()
    seed_gl_master_data()
    seed_sourcing_master_and_transactions()
    seed_appearance()
    logger.info("PyrixDB multi-company initialization and seed complete.")

if __name__ == "__main__":
    setup_database()
