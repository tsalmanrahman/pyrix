import json
import logging
import uuid
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
                cost_centre_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES admin_cost_centers(id),
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
                cost_centre_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES admin_cost_centers(id),
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
        """,

        # 34. Sales: Sales Areas & Territories
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_areas')
        BEGIN
            CREATE TABLE sales_areas (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                area_code VARCHAR(30) NOT NULL UNIQUE,
                area_name NVARCHAR(150) NOT NULL,
                region_name NVARCHAR(100) NOT NULL,
                head_of_area NVARCHAR(150),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 35. Sales: Sales Teams & Management Hierarchy (MM > ZM > TSM)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_teams')
        BEGIN
            CREATE TABLE sales_teams (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(2001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                area_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_areas(id),
                team_code VARCHAR(30) NOT NULL UNIQUE,
                team_name NVARCHAR(150) NOT NULL,
                team_type VARCHAR(30) DEFAULT 'TSM_TEAM',
                parent_team_id UNIQUEIDENTIFIER NULL,
                manager_name NVARCHAR(150) NOT NULL,
                target_annual_amount FLOAT DEFAULT 0.0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 36. Sales: Salespersons Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'salespersons')
        BEGIN
            CREATE TABLE salespersons (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(3001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                team_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_teams(id),
                salesperson_code VARCHAR(30) NOT NULL UNIQUE,
                full_name NVARCHAR(150) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(50),
                designation NVARCHAR(100) NOT NULL,
                max_discount_pct FLOAT DEFAULT 5.0,
                monthly_target FLOAT DEFAULT 50000.0,
                commission_pct FLOAT DEFAULT 2.5,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 37. Sales: Product Price Profiles & Price Lists
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_price_profiles')
        BEGIN
            CREATE TABLE sales_price_profiles (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(4001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                profile_code VARCHAR(30) NOT NULL UNIQUE,
                profile_name NVARCHAR(150) NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                price_type VARCHAR(50) DEFAULT 'BASE_PRICE',
                is_default BIT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 38. Sales: Product Price List Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_product_prices')
        BEGIN
            CREATE TABLE sales_product_prices (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                profile_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_price_profiles(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                base_price FLOAT NOT NULL,
                min_selling_price FLOAT NOT NULL,
                max_discount_pct FLOAT DEFAULT 15.0,
                is_active BIT DEFAULT 1,
                updated_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 39. Sales: Discount Limits Matrix
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_discount_limits')
        BEGIN
            CREATE TABLE sales_discount_limits (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                role_name NVARCHAR(100) NOT NULL,
                max_discount_pct FLOAT NOT NULL,
                requires_approval_above_pct FLOAT NOT NULL,
                approver_role NVARCHAR(100) NOT NULL,
                is_active BIT DEFAULT 1
            );
        END
        """,

        # 40. Sales: Sales Quotes & Revisions
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_quotes')
        BEGIN
            CREATE TABLE sales_quotes (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(10001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                quote_number VARCHAR(50) NOT NULL UNIQUE,
                revision_no INT DEFAULT 1,
                customer_name NVARCHAR(200) NOT NULL,
                customer_id UNIQUEIDENTIFIER NULL,
                salesperson_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES salespersons(id),
                quote_date DATE NOT NULL,
                valid_until DATE NOT NULL,
                subtotal FLOAT NOT NULL,
                discount_amount FLOAT DEFAULT 0.0,
                tax_amount FLOAT DEFAULT 0.0,
                total_amount FLOAT NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                status VARCHAR(30) DEFAULT 'SUBMITTED',
                progress_notes NVARCHAR(500),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 41. Sales: Sales Quote Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_quote_items')
        BEGIN
            CREATE TABLE sales_quote_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                quote_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_quotes(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL,
                discount_pct FLOAT DEFAULT 0.0,
                line_total FLOAT NOT NULL,
                remarks NVARCHAR(250)
            );
        END
        """,

        # 42. Sales: Sales Orders (SO Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_orders')
        BEGIN
            CREATE TABLE sales_orders (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(20001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                quote_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_quotes(id),
                order_number VARCHAR(50) NOT NULL UNIQUE,
                customer_name NVARCHAR(200) NOT NULL,
                customer_id UNIQUEIDENTIFIER NULL,
                salesperson_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES salespersons(id),
                order_date DATE NOT NULL,
                expected_delivery_date DATE NOT NULL,
                payment_terms NVARCHAR(100) DEFAULT 'Net 30 Days',
                delivery_terms NVARCHAR(100) DEFAULT 'FOB Plant Gate',
                shipping_address NVARCHAR(300),
                billing_address NVARCHAR(300),
                currency VARCHAR(10) DEFAULT 'USD',
                exchange_rate FLOAT DEFAULT 1.0,
                subtotal FLOAT NOT NULL,
                discount_amount FLOAT DEFAULT 0.0,
                tax_amount FLOAT DEFAULT 0.0,
                total_amount FLOAT NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                hold_reason NVARCHAR(250) NULL,
                is_on_hold BIT DEFAULT 0,
                current_approval_tier INT DEFAULT 1,
                max_approval_tier INT DEFAULT 2,
                is_gl_posted BIT DEFAULT 0,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 43. Sales: Sales Order Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_order_items')
        BEGIN
            CREATE TABLE sales_order_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                order_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_orders(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL,
                discount_pct FLOAT DEFAULT 0.0,
                line_total FLOAT NOT NULL,
                packing_spec NVARCHAR(200) DEFAULT 'Standard Heavy Corrugated Box',
                delivered_qty FLOAT DEFAULT 0.0,
                invoiced_qty FLOAT DEFAULT 0.0
            );
        END
        """,

        # 44. Sales: Delivery Orders (DO Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_delivery_orders')
        BEGIN
            CREATE TABLE sales_delivery_orders (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(30001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                order_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_orders(id),
                do_number VARCHAR(50) NOT NULL UNIQUE,
                do_date DATE NOT NULL,
                dispatch_date DATE NOT NULL,
                carrier_name NVARCHAR(150),
                vehicle_no VARCHAR(50),
                tracking_ref VARCHAR(80),
                delivery_address NVARCHAR(300),
                status VARCHAR(30) DEFAULT 'DISPATCHED',
                gate_pass_ref VARCHAR(80),
                created_by NVARCHAR(100) DEFAULT 'Warehouse Dispatch Lead',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 45. Sales: Delivery Order Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_do_items')
        BEGIN
            CREATE TABLE sales_do_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                do_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_delivery_orders(id),
                order_item_id UNIQUEIDENTIFIER NULL,
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                ordered_qty FLOAT NOT NULL,
                dispatch_qty FLOAT NOT NULL,
                unit_price FLOAT NOT NULL,
                line_total FLOAT NOT NULL
            );
        END
        """,

        # 46. Sales: Sales Invoices (Commercial & Export Invoices)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_invoices')
        BEGIN
            CREATE TABLE sales_invoices (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(40001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                order_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_orders(id),
                do_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_delivery_orders(id),
                invoice_number VARCHAR(50) NOT NULL UNIQUE,
                invoice_type VARCHAR(30) DEFAULT 'COMMERCIAL',
                customer_name NVARCHAR(200) NOT NULL,
                invoice_date DATE NOT NULL,
                due_date DATE NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                exchange_rate FLOAT DEFAULT 1.0,
                subtotal FLOAT NOT NULL,
                discount_amount FLOAT DEFAULT 0.0,
                tax_amount FLOAT DEFAULT 0.0,
                total_amount FLOAT NOT NULL,
                paid_amount FLOAT DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'ISSUED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 47. Sales: Sales Invoice Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_invoice_items')
        BEGIN
            CREATE TABLE sales_invoice_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                invoice_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES sales_invoices(id),
                item_code VARCHAR(50) NOT NULL,
                item_name NVARCHAR(200) NOT NULL,
                uom VARCHAR(20) DEFAULT 'PCS',
                quantity FLOAT NOT NULL,
                unit_price FLOAT NOT NULL,
                discount_pct FLOAT DEFAULT 0.0,
                line_total FLOAT NOT NULL
            );
        END
        """,

        # 48. Sales: Sales Returns & Credit Memos
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_returns')
        BEGIN
            CREATE TABLE sales_returns (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(50001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                order_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_orders(id),
                invoice_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES sales_invoices(id),
                return_number VARCHAR(50) NOT NULL UNIQUE,
                customer_name NVARCHAR(200) NOT NULL,
                return_date DATE NOT NULL,
                reason NVARCHAR(300) NOT NULL,
                return_amount FLOAT NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                credit_memo_ref VARCHAR(50) NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 49. Sales: Sales Budgets & Targets
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_budgets')
        BEGIN
            CREATE TABLE sales_budgets (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(60001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                fiscal_year VARCHAR(20) NOT NULL,
                salesperson_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES salespersons(id),
                target_category NVARCHAR(100) NOT NULL,
                annual_target FLOAT NOT NULL,
                q1_target FLOAT NOT NULL,
                q2_target FLOAT NOT NULL,
                q3_target FLOAT NOT NULL,
                q4_target FLOAT NOT NULL,
                achieved_amount FLOAT DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 50. Sales: Multi-Tier e-Approvals Tracking
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sales_approvals')
        BEGIN
            CREATE TABLE sales_approvals (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70001, 1) NOT NULL,
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
        """,

        # 51. Inventory: Warehouses & Storage Facilities Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_warehouses')
        BEGIN
            CREATE TABLE inv_warehouses (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                warehouse_code VARCHAR(30) NOT NULL UNIQUE,
                warehouse_name NVARCHAR(150) NOT NULL,
                warehouse_type VARCHAR(50) DEFAULT 'CENTRAL_STORE',
                address NVARCHAR(300),
                manager_name NVARCHAR(150) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 52. Inventory: Multi-Bin Storage Locations (Aisle/Rack/Shelf/Bin)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_bins')
        BEGIN
            CREATE TABLE inv_bins (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                bin_code VARCHAR(50) NOT NULL,
                aisle VARCHAR(20) NOT NULL,
                rack VARCHAR(20) NOT NULL,
                shelf VARCHAR(20) NOT NULL,
                bin_number VARCHAR(20) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 53. Inventory: Product Groups & Categorization
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_product_groups')
        BEGIN
            CREATE TABLE inv_product_groups (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(2001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                group_code VARCHAR(30) NOT NULL UNIQUE,
                group_name NVARCHAR(150) NOT NULL,
                group_type VARCHAR(50) DEFAULT 'FINISHED_GOODS',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 54. Inventory: Units of Measure (UOM) & Conversion
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_uom')
        BEGIN
            CREATE TABLE inv_uom (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                uom_code VARCHAR(20) NOT NULL UNIQUE,
                uom_name NVARCHAR(100) NOT NULL,
                base_uom VARCHAR(20) DEFAULT 'PCS',
                conversion_ratio FLOAT DEFAULT 1.0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 55. Inventory: Master Items Catalog
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_items')
        BEGIN
            CREATE TABLE inv_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(3001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                group_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES inv_product_groups(id),
                uom_code VARCHAR(20) DEFAULT 'PCS',
                item_code VARCHAR(50) NOT NULL UNIQUE,
                item_name NVARCHAR(200) NOT NULL,
                specification NVARCHAR(300),
                standard_cost FLOAT NOT NULL DEFAULT 0.0,
                min_reorder_qty FLOAT DEFAULT 100.0,
                safety_stock_qty FLOAT DEFAULT 50.0,
                is_serialized BIT DEFAULT 0,
                item_status VARCHAR(30) DEFAULT 'ACTIVE',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 56. Inventory: Stock Balances Matrix (Multi-Warehouse / Bin)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_stock_balances')
        BEGIN
            CREATE TABLE inv_stock_balances (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                bin_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES inv_bins(id),
                item_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_items(id),
                on_hand_qty FLOAT NOT NULL DEFAULT 0.0,
                reserved_qty FLOAT NOT NULL DEFAULT 0.0,
                in_transit_qty FLOAT NOT NULL DEFAULT 0.0,
                last_updated DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 57. Inventory: Goods Receiving Notes (GRN Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_grn_headers')
        BEGIN
            CREATE TABLE inv_grn_headers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(10001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                grn_number VARCHAR(50) NOT NULL UNIQUE,
                grn_type VARCHAR(30) DEFAULT 'VENDOR_PO',
                po_ref VARCHAR(50) NULL,
                supplier_name NVARCHAR(200) NOT NULL,
                grn_date DATE NOT NULL,
                challan_ref VARCHAR(80) NULL,
                received_by NVARCHAR(100) NOT NULL,
                qc_status VARCHAR(30) DEFAULT 'PASSED',
                total_received_value FLOAT NOT NULL DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'POSTED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 58. Inventory: Goods Receiving Note Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_grn_items')
        BEGIN
            CREATE TABLE inv_grn_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                grn_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_grn_headers(id),
                item_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_items(id),
                bin_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES inv_bins(id),
                received_qty FLOAT NOT NULL,
                accepted_qty FLOAT NOT NULL,
                rejected_qty FLOAT DEFAULT 0.0,
                unit_cost FLOAT NOT NULL,
                line_total FLOAT NOT NULL,
                batch_number VARCHAR(50) NULL,
                remarks NVARCHAR(250) NULL
            );
        END
        """,

        # 59. Inventory: Goods Issue Challans (Header)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_issues')
        BEGIN
            CREATE TABLE inv_issues (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(20001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                issue_number VARCHAR(50) NOT NULL UNIQUE,
                issue_type VARCHAR(30) DEFAULT 'DELIVERY_DISPATCH',
                order_ref VARCHAR(50) NULL,
                cost_centre_name NVARCHAR(100) NULL,
                issue_date DATE NOT NULL,
                gate_pass_ref VARCHAR(80) NULL,
                issued_by NVARCHAR(100) NOT NULL,
                recipient_name NVARCHAR(150) NOT NULL,
                total_issue_value FLOAT NOT NULL DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'DISPATCHED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 60. Inventory: Goods Issue Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_issue_items')
        BEGIN
            CREATE TABLE inv_issue_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                issue_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_issues(id),
                item_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_items(id),
                bin_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES inv_bins(id),
                issued_qty FLOAT NOT NULL,
                unit_cost FLOAT NOT NULL,
                line_total FLOAT NOT NULL,
                remarks NVARCHAR(250) NULL
            );
        END
        """,

        # 61. Inventory: Inter-Warehouse Stock Transfer Orders (STO)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_stock_transfers')
        BEGIN
            CREATE TABLE inv_stock_transfers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(30001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                from_warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                to_warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                transfer_number VARCHAR(50) NOT NULL UNIQUE,
                transfer_date DATE NOT NULL,
                dispatch_date DATE NOT NULL,
                carrier_name NVARCHAR(150) NULL,
                vehicle_no VARCHAR(50) NULL,
                tracking_ref VARCHAR(80) NULL,
                total_transfer_value FLOAT NOT NULL DEFAULT 0.0,
                status VARCHAR(30) DEFAULT 'IN_TRANSIT',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 62. Inventory: Stock Transfer Items
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_transfer_items')
        BEGIN
            CREATE TABLE inv_transfer_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(1, 1) NOT NULL,
                transfer_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_stock_transfers(id),
                item_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_items(id),
                transfer_qty FLOAT NOT NULL,
                received_qty FLOAT DEFAULT 0.0,
                unit_cost FLOAT NOT NULL,
                line_total FLOAT NOT NULL
            );
        END
        """,

        # 63. Inventory: Physical Cycle Count Adjustments (+/-)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_adjustments')
        BEGIN
            CREATE TABLE inv_adjustments (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(40001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                warehouse_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_warehouses(id),
                adjustment_number VARCHAR(50) NOT NULL UNIQUE,
                adjustment_date DATE NOT NULL,
                reason_type VARCHAR(50) NOT NULL,
                total_variance_amount FLOAT NOT NULL DEFAULT 0.0,
                adjusted_by NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 64. Inventory: Serial Number Registry & Warranties
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_warranties')
        BEGIN
            CREATE TABLE inv_warranties (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(50001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES companies(id),
                item_id UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES inv_items(id),
                serial_number VARCHAR(80) NOT NULL UNIQUE,
                customer_name NVARCHAR(200) NOT NULL,
                order_ref VARCHAR(50) NULL,
                invoice_ref VARCHAR(50) NULL,
                warranty_start_date DATE NOT NULL,
                warranty_end_date DATE NOT NULL,
                warranty_months INT DEFAULT 12,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 65. Inventory: Multi-Tier Approvals Tracking
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'inv_approvals')
        BEGIN
            CREATE TABLE inv_approvals (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(60001, 1) NOT NULL,
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
        """,

        # 66. Fixed Assets: Asset Groups & Categories
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_asset_groups')
        BEGIN
            CREATE TABLE fa_asset_groups (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                group_code VARCHAR(30) NOT NULL,
                group_name NVARCHAR(150) NOT NULL,
                asset_type VARCHAR(50) DEFAULT 'TANGIBLE_DEPRECIATING',
                is_depreciating BIT DEFAULT 1,
                default_useful_life_years INT DEFAULT 10,
                default_depr_rate DECIMAL(6, 2) DEFAULT 10.00,
                gl_cost_account VARCHAR(50) DEFAULT '1500-PLANT',
                gl_acc_depr_account VARCHAR(50) DEFAULT '1505-ACC-PLANT',
                gl_depr_expense_account VARCHAR(50) DEFAULT '6500-DEPR-PLANT',
                gl_gain_loss_account VARCHAR(50) DEFAULT '7200-GAIN-LOSS-ASSET',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 67. Fixed Assets: Primary Physical Locations
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_locations')
        BEGIN
            CREATE TABLE fa_locations (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                location_code VARCHAR(30) NOT NULL,
                location_name NVARCHAR(150) NOT NULL,
                location_type VARCHAR(50) DEFAULT 'MANUFACTURING_PLANT',
                address NVARCHAR(250),
                manager_name NVARCHAR(100),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 68. Fixed Assets: 2D Sub-Locations & Machine Bays
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_sub_locations')
        BEGIN
            CREATE TABLE fa_sub_locations (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70201, 1) NOT NULL,
                location_id UNIQUEIDENTIFIER NOT NULL,
                sub_location_code VARCHAR(30) NOT NULL,
                sub_location_name NVARCHAR(150) NOT NULL,
                floor_or_bay NVARCHAR(100),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 69. Fixed Assets: Depreciation Policies
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_depreciation_policies')
        BEGIN
            CREATE TABLE fa_depreciation_policies (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                policy_code VARCHAR(30) NOT NULL,
                policy_name NVARCHAR(150) NOT NULL,
                method VARCHAR(50) DEFAULT 'STRAIGHT_LINE',
                useful_life_years INT DEFAULT 10,
                salvage_value_pct DECIMAL(5, 2) DEFAULT 5.00,
                depr_rate DECIMAL(6, 2) DEFAULT 10.00,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 70. Fixed Assets: Master Asset Register
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_assets')
        BEGIN
            CREATE TABLE fa_assets (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70401, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                group_id UNIQUEIDENTIFIER NOT NULL,
                location_id UNIQUEIDENTIFIER NOT NULL,
                sub_location_id UNIQUEIDENTIFIER,
                policy_id UNIQUEIDENTIFIER NOT NULL,
                asset_tag VARCHAR(50) NOT NULL UNIQUE,
                asset_name NVARCHAR(200) NOT NULL,
                serial_number VARCHAR(100),
                barcode VARCHAR(100),
                manufacturer NVARCHAR(150),
                model_number NVARCHAR(100),
                purchase_date DATE NOT NULL,
                capitalization_date DATE,
                purchase_cost DECIMAL(18, 2) NOT NULL,
                accumulated_depreciation DECIMAL(18, 2) DEFAULT 0.00,
                net_book_value DECIMAL(18, 2) NOT NULL,
                custodian_name NVARCHAR(100),
                department_name NVARCHAR(100),
                supplier_name NVARCHAR(150),
                warranty_expiry DATE,
                insurance_policy_ref VARCHAR(100),
                is_leased BIT DEFAULT 0,
                is_capitalized BIT DEFAULT 1,
                status VARCHAR(30) DEFAULT 'IN_SERVICE',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 71. Fixed Assets: Capital Asset Receiving Notes (Asset GRN)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_grn_headers')
        BEGIN
            CREATE TABLE fa_grn_headers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70501, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                location_id UNIQUEIDENTIFIER NOT NULL,
                grn_number VARCHAR(50) NOT NULL UNIQUE,
                po_ref VARCHAR(50),
                supplier_name NVARCHAR(150) NOT NULL,
                grn_date DATE NOT NULL,
                received_by NVARCHAR(100) NOT NULL,
                qc_status VARCHAR(30) DEFAULT 'PASSED_QA_INSPECTION',
                total_cost DECIMAL(18, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'POSTED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) DEFAULT 'GL-JV-2026-CAP-001',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 72. Fixed Assets: Asset Transfers Log
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_transfers')
        BEGIN
            CREATE TABLE fa_transfers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70601, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                asset_id UNIQUEIDENTIFIER NOT NULL,
                transfer_number VARCHAR(50) NOT NULL UNIQUE,
                transfer_date DATE NOT NULL,
                from_location_id UNIQUEIDENTIFIER NOT NULL,
                to_location_id UNIQUEIDENTIFIER NOT NULL,
                from_custodian NVARCHAR(100),
                to_custodian NVARCHAR(100) NOT NULL,
                reason NVARCHAR(250),
                status VARCHAR(30) DEFAULT 'COMPLETED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 73. Fixed Assets: Disposals & Write-offs
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_disposals')
        BEGIN
            CREATE TABLE fa_disposals (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                asset_id UNIQUEIDENTIFIER NOT NULL,
                disposal_number VARCHAR(50) NOT NULL UNIQUE,
                disposal_date DATE NOT NULL,
                disposal_type VARCHAR(50) DEFAULT 'SALE',
                disposal_proceeds DECIMAL(18, 2) DEFAULT 0.00,
                original_cost DECIMAL(18, 2) NOT NULL,
                acc_depr_at_disposal DECIMAL(18, 2) NOT NULL,
                net_book_value DECIMAL(18, 2) NOT NULL,
                gain_loss_amount DECIMAL(18, 2) NOT NULL,
                buyer_name NVARCHAR(150),
                approved_by NVARCHAR(100),
                status VARCHAR(30) DEFAULT 'POSTED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) DEFAULT 'GL-JV-2026-DSP-001',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 74. Fixed Assets: Depreciation Runs
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_depreciation_runs')
        BEGIN
            CREATE TABLE fa_depreciation_runs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                run_number VARCHAR(50) NOT NULL UNIQUE,
                period_name NVARCHAR(100) NOT NULL,
                run_date DATE NOT NULL,
                total_depreciation_amount DECIMAL(18, 2) NOT NULL,
                total_assets_processed INT NOT NULL,
                status VARCHAR(30) DEFAULT 'POSTED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) DEFAULT 'GL-JV-2026-DPR-001',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 75. Fixed Assets: Depreciation Itemized Lines
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_depreciation_lines')
        BEGIN
            CREATE TABLE fa_depreciation_lines (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(70901, 1) NOT NULL,
                run_id UNIQUEIDENTIFIER NOT NULL,
                asset_id UNIQUEIDENTIFIER NOT NULL,
                opening_cost DECIMAL(18, 2) NOT NULL,
                opening_acc_depr DECIMAL(18, 2) NOT NULL,
                period_depreciation DECIMAL(18, 2) NOT NULL,
                closing_acc_depr DECIMAL(18, 2) NOT NULL,
                closing_nbv DECIMAL(18, 2) NOT NULL
            );
        END
        """,

        # 76. Fixed Assets: Physical Verification Audits
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_physical_audits')
        BEGIN
            CREATE TABLE fa_physical_audits (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(71001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                location_id UNIQUEIDENTIFIER NOT NULL,
                audit_number VARCHAR(50) NOT NULL UNIQUE,
                audit_date DATE NOT NULL,
                auditor_name NVARCHAR(100) NOT NULL,
                total_audited INT NOT NULL,
                found_count INT NOT NULL,
                missing_count INT NOT NULL,
                damaged_count INT NOT NULL,
                status VARCHAR(30) DEFAULT 'VERIFIED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 77. Fixed Assets: Multi-Tier Approvals Tracking
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fa_approvals')
        BEGIN
            CREATE TABLE fa_approvals (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(71101, 1) NOT NULL,
                entity_type VARCHAR(30) NOT NULL,
                entity_id UNIQUEIDENTIFIER NOT NULL,
                tier_level INT NOT NULL,
                tier_name NVARCHAR(100) NOT NULL,
                approver_name NVARCHAR(100) NOT NULL,
                approver_role NVARCHAR(100) NOT NULL,
                action VARCHAR(30) DEFAULT 'APPROVED',
                comments NVARCHAR(300),
                action_date DATETIME,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """


        # 78. HR: Employee Grades & Pay Scale Bands
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_grades')
        BEGIN
            CREATE TABLE hr_grades (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                grade_code VARCHAR(50) NOT NULL,
                grade_name NVARCHAR(100) NOT NULL,
                rank_level INT NOT NULL,
                min_basic_salary DECIMAL(18, 2) NOT NULL,
                max_basic_salary DECIMAL(18, 2) NOT NULL,
                hra_pct DECIMAL(5, 2) DEFAULT 25.00,
                medical_pct DECIMAL(5, 2) DEFAULT 10.00,
                conveyance_pct DECIMAL(5, 2) DEFAULT 10.00,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 79. HR: Organizational Departments
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_departments')
        BEGIN
            CREATE TABLE hr_departments (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                dept_code VARCHAR(50) NOT NULL,
                dept_name NVARCHAR(150) NOT NULL,
                cost_center_code VARCHAR(50) NOT NULL,
                head_of_dept NVARCHAR(100),
                location_name NVARCHAR(150),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 80. HR: Designations & Job Titles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_designations')
        BEGIN
            CREATE TABLE hr_designations (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80201, 1) NOT NULL,
                department_id UNIQUEIDENTIFIER NOT NULL,
                designation_code VARCHAR(50) NOT NULL,
                designation_title NVARCHAR(150) NOT NULL,
                skill_level VARCHAR(50) DEFAULT 'SENIOR_PROFESSIONAL',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 81. HR: Work-Shifts & Roster Configuration
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_shifts')
        BEGIN
            CREATE TABLE hr_shifts (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                shift_code VARCHAR(50) NOT NULL,
                shift_name NVARCHAR(100) NOT NULL,
                start_time VARCHAR(10) NOT NULL,
                end_time VARCHAR(10) NOT NULL,
                grace_period_mins INT DEFAULT 15,
                half_day_hours DECIMAL(4, 2) DEFAULT 4.00,
                is_night_shift BIT DEFAULT 0,
                night_allowance DECIMAL(18, 2) DEFAULT 0.00,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 82. HR: Annual Holiday Calendar
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_holidays')
        BEGIN
            CREATE TABLE hr_holidays (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80401, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                holiday_name NVARCHAR(150) NOT NULL,
                holiday_date DATE NOT NULL,
                holiday_type VARCHAR(50) DEFAULT 'PUBLIC_HOLIDAY',
                is_recurring BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 83. HR: Leave Policies & Entitlement Types
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_leave_types')
        BEGIN
            CREATE TABLE hr_leave_types (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80501, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                leave_code VARCHAR(50) NOT NULL,
                leave_name NVARCHAR(100) NOT NULL,
                yearly_quota INT NOT NULL,
                is_paid BIT DEFAULT 1,
                is_encashable BIT DEFAULT 0,
                max_carryforward INT DEFAULT 5,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 84. HR: Corporate Bank Accounts for Salary Disbursement
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_bank_accounts')
        BEGIN
            CREATE TABLE hr_bank_accounts (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80601, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                bank_name NVARCHAR(150) NOT NULL,
                branch_name NVARCHAR(150) NOT NULL,
                account_number VARCHAR(50) NOT NULL,
                routing_number VARCHAR(50) NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                is_default BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 85. HR: Master Employee Profiles & Dossiers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_employees')
        BEGIN
            CREATE TABLE hr_employees (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                department_id UNIQUEIDENTIFIER NOT NULL,
                designation_id UNIQUEIDENTIFIER NOT NULL,
                grade_id UNIQUEIDENTIFIER NOT NULL,
                shift_id UNIQUEIDENTIFIER NOT NULL,
                employee_code VARCHAR(50) NOT NULL UNIQUE,
                first_name NVARCHAR(100) NOT NULL,
                last_name NVARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                national_id VARCHAR(50) NOT NULL,
                tin_number VARCHAR(50),
                tax_zone NVARCHAR(100),
                tax_circle NVARCHAR(100),
                date_of_birth DATE NOT NULL,
                gender VARCHAR(20) DEFAULT 'MALE',
                blood_group VARCHAR(10) DEFAULT 'O+',
                joining_date DATE NOT NULL,
                employment_status VARCHAR(50) DEFAULT 'PERMANENT',
                basic_salary DECIMAL(18, 2) NOT NULL,
                gross_salary DECIMAL(18, 2) NOT NULL,
                bank_name NVARCHAR(150),
                bank_account_number VARCHAR(50),
                bank_routing_number VARCHAR(50),
                emergency_contact_name NVARCHAR(100),
                emergency_contact_phone VARCHAR(50),
                is_pf_member BIT DEFAULT 1,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 86. HR: Temporary / Casual / Daily Worker Rosters
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_contract_workers')
        BEGIN
            CREATE TABLE hr_contract_workers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                department_id UNIQUEIDENTIFIER NOT NULL,
                worker_code VARCHAR(50) NOT NULL UNIQUE,
                worker_name NVARCHAR(150) NOT NULL,
                contractor_agency NVARCHAR(150),
                worker_type VARCHAR(50) DEFAULT 'DAILY_WAGE',
                daily_rate DECIMAL(18, 2) NOT NULL,
                contract_start_date DATE NOT NULL,
                contract_end_date DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 87. HR: Digital Document Vault & Credentials Archive
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_documents')
        BEGIN
            CREATE TABLE hr_documents (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(80901, 1) NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                doc_title NVARCHAR(200) NOT NULL,
                doc_type VARCHAR(50) NOT NULL,
                doc_file_ref VARCHAR(250) NOT NULL,
                issue_date DATE,
                expiry_date DATE,
                verification_status VARCHAR(30) DEFAULT 'VERIFIED',
                verified_by NVARCHAR(100),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 88. HR: Employee Transfers & Promotions Log
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_transfers')
        BEGIN
            CREATE TABLE hr_transfers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                transfer_number VARCHAR(50) NOT NULL UNIQUE,
                transfer_date DATE NOT NULL,
                transfer_type VARCHAR(50) DEFAULT 'INTER_PLANT_TRANSFER',
                from_dept_id UNIQUEIDENTIFIER NOT NULL,
                to_dept_id UNIQUEIDENTIFIER NOT NULL,
                from_designation_id UNIQUEIDENTIFIER NOT NULL,
                to_designation_id UNIQUEIDENTIFIER NOT NULL,
                previous_salary DECIMAL(18, 2) NOT NULL,
                revised_salary DECIMAL(18, 2) NOT NULL,
                reason NVARCHAR(300),
                approved_by NVARCHAR(100),
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 89. HR: Recruitment Manpower Requisitions
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_job_requisitions')
        BEGIN
            CREATE TABLE hr_job_requisitions (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                department_id UNIQUEIDENTIFIER NOT NULL,
                requisition_number VARCHAR(50) NOT NULL UNIQUE,
                position_title NVARCHAR(150) NOT NULL,
                vacancies_count INT DEFAULT 1,
                experience_years_required INT DEFAULT 3,
                budgeted_salary DECIMAL(18, 2) NOT NULL,
                target_joining_date DATE NOT NULL,
                justification NVARCHAR(400),
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 90. HR: CV Bank, Candidates & Interview Evaluations
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_candidates')
        BEGIN
            CREATE TABLE hr_candidates (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81201, 1) NOT NULL,
                requisition_id UNIQUEIDENTIFIER NOT NULL,
                candidate_name NVARCHAR(150) NOT NULL,
                email VARCHAR(150) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                years_of_experience DECIMAL(4, 1) NOT NULL,
                key_skills NVARCHAR(300),
                expected_salary DECIMAL(18, 2) NOT NULL,
                interview_score DECIMAL(5, 2) DEFAULT 88.50,
                interview_feedback NVARCHAR(400),
                hiring_status VARCHAR(50) DEFAULT 'SELECTED_FOR_OFFER',
                applied_date DATE NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 91. HR: Employee Loan Type Profiles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_loan_types')
        BEGIN
            CREATE TABLE hr_loan_types (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                loan_type_code VARCHAR(50) NOT NULL,
                loan_type_name NVARCHAR(150) NOT NULL,
                max_loan_limit DECIMAL(18, 2) NOT NULL,
                max_installments INT NOT NULL,
                interest_rate_pct DECIMAL(5, 2) DEFAULT 0.00,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 92. HR: Employee Loans & Salary Advances Ledger
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_loans')
        BEGIN
            CREATE TABLE hr_loans (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81401, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                loan_type_id UNIQUEIDENTIFIER NOT NULL,
                loan_number VARCHAR(50) NOT NULL UNIQUE,
                principal_amount DECIMAL(18, 2) NOT NULL,
                interest_rate_pct DECIMAL(5, 2) DEFAULT 0.00,
                tenure_months INT NOT NULL,
                monthly_emi DECIMAL(18, 2) NOT NULL,
                disbursement_date DATE NOT NULL,
                repayment_start_month VARCHAR(20) NOT NULL,
                total_paid_amount DECIMAL(18, 2) DEFAULT 0.00,
                outstanding_balance DECIMAL(18, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                gl_voucher_ref VARCHAR(50) DEFAULT 'GL-JV-2026-LN-001',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 93. HR: Statutory Income Tax Slabs & Allowable Rebate Settings
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_tax_slabs')
        BEGIN
            CREATE TABLE hr_tax_slabs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81501, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                fiscal_year VARCHAR(20) NOT NULL,
                slab_order INT NOT NULL,
                slab_description NVARCHAR(150) NOT NULL,
                slab_limit DECIMAL(18, 2) NOT NULL,
                tax_rate_pct DECIMAL(5, 2) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 94. HR: Treasury Tax Deposit Log
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_tax_deposits')
        BEGIN
            CREATE TABLE hr_tax_deposits (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81601, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                deposit_month VARCHAR(20) NOT NULL,
                challan_number VARCHAR(50) NOT NULL UNIQUE,
                challan_date DATE NOT NULL,
                depository_bank NVARCHAR(150) NOT NULL,
                total_tax_deposited DECIMAL(18, 2) NOT NULL,
                employees_covered_count INT NOT NULL,
                gl_voucher_ref VARCHAR(50) DEFAULT 'GL-JV-2026-TAX-001',
                status VARCHAR(30) DEFAULT 'VERIFIED_BY_TREASURY',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 95. HR: Daily Biometric Terminal Clock-In Attendance Logs
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_attendance_logs')
        BEGIN
            CREATE TABLE hr_attendance_logs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                attendance_date DATE NOT NULL,
                clock_in_time VARCHAR(10) NOT NULL,
                clock_out_time VARCHAR(10),
                terminal_device_ip VARCHAR(50) DEFAULT '192.168.10.201 (BioMetric-RFID-01)',
                attendance_status VARCHAR(30) DEFAULT 'PRESENT',
                is_late BIT DEFAULT 0,
                late_minutes INT DEFAULT 0,
                overtime_hours DECIMAL(4, 2) DEFAULT 0.00,
                remarks NVARCHAR(200),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 96. HR: Online Leave Applications & Multi-Tier Approvals
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_leave_applications')
        BEGIN
            CREATE TABLE hr_leave_applications (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                leave_type_id UNIQUEIDENTIFIER NOT NULL,
                application_number VARCHAR(50) NOT NULL UNIQUE,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                leave_days INT NOT NULL,
                reason NVARCHAR(300) NOT NULL,
                approver_name NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                applied_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 97. HR: Overtime Records Matrix
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_overtime_records')
        BEGIN
            CREATE TABLE hr_overtime_records (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(81901, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                ot_date DATE NOT NULL,
                ot_hours DECIMAL(4, 2) NOT NULL,
                hourly_rate DECIMAL(18, 2) NOT NULL,
                multiplier_factor DECIMAL(3, 1) DEFAULT 1.5,
                total_ot_amount DECIMAL(18, 2) NOT NULL,
                supervisor_name NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 98. HR: Monthly Payroll Batch Execution Runs
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_payroll_runs')
        BEGIN
            CREATE TABLE hr_payroll_runs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(82001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                payroll_batch_number VARCHAR(50) NOT NULL UNIQUE,
                period_month VARCHAR(20) NOT NULL,
                fiscal_year VARCHAR(20) NOT NULL,
                run_date DATE NOT NULL,
                total_employees_processed INT NOT NULL,
                total_gross_payout DECIMAL(18, 2) NOT NULL,
                total_deductions DECIMAL(18, 2) NOT NULL,
                total_net_payout DECIMAL(18, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'POSTED',
                is_gl_posted BIT DEFAULT 1,
                gl_journal_ref VARCHAR(50) DEFAULT 'GL-JV-2026-PAY-001',
                bank_advice_locked BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 99. HR: Itemized Payslips with Full Gross-to-Net Breakdown
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'hr_payslips')
        BEGIN
            CREATE TABLE hr_payslips (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(82101, 1) NOT NULL,
                payroll_run_id UNIQUEIDENTIFIER NOT NULL,
                employee_id UNIQUEIDENTIFIER NOT NULL,
                payslip_number VARCHAR(50) NOT NULL UNIQUE,
                basic_salary DECIMAL(18, 2) NOT NULL,
                house_rent_allowance DECIMAL(18, 2) NOT NULL,
                medical_allowance DECIMAL(18, 2) NOT NULL,
                conveyance_allowance DECIMAL(18, 2) NOT NULL,
                special_allowance DECIMAL(18, 2) DEFAULT 0.00,
                overtime_pay DECIMAL(18, 2) DEFAULT 0.00,
                bonus_amount DECIMAL(18, 2) DEFAULT 0.00,
                gross_earnings DECIMAL(18, 2) NOT NULL,
                pf_employee_deduction DECIMAL(18, 2) NOT NULL,
                pf_employer_matching DECIMAL(18, 2) NOT NULL,
                income_tax_deduction DECIMAL(18, 2) DEFAULT 0.00,
                loan_emi_deduction DECIMAL(18, 2) DEFAULT 0.00,
                late_penalty_deduction DECIMAL(18, 2) DEFAULT 0.00,
                total_deductions DECIMAL(18, 2) NOT NULL,
                net_salary_payable DECIMAL(18, 2) NOT NULL,
                payment_mode VARCHAR(50) DEFAULT 'BANK_TRANSFER',
                bank_account_number VARCHAR(50),
                status VARCHAR(30) DEFAULT 'PAID',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,


        # 100. Production: Manufacturing Processes Master
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_processes')
        BEGIN
            CREATE TABLE prod_processes (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90001, 1) NOT NULL,
                process_code VARCHAR(50) NOT NULL UNIQUE,
                process_name NVARCHAR(150) NOT NULL,
                stage_type VARCHAR(50) NOT NULL,
                sequence_order INT NOT NULL,
                default_cost_center VARCHAR(50) DEFAULT 'CC-PRD-01',
                description NVARCHAR(300),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 101. Production: Manufacturing Plants, Works & Bays
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_plants')
        BEGIN
            CREATE TABLE prod_plants (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                plant_code VARCHAR(50) NOT NULL,
                plant_name NVARCHAR(150) NOT NULL,
                location NVARCHAR(200) NOT NULL,
                manager_name NVARCHAR(100) NOT NULL,
                total_bays INT DEFAULT 6,
                shift_mode VARCHAR(50) DEFAULT '3_SHIFTS_24_7',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 102. Production: Production Resources & Work Centers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_resources')
        BEGIN
            CREATE TABLE prod_resources (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90201, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                plant_id UNIQUEIDENTIFIER NOT NULL,
                resource_code VARCHAR(50) NOT NULL,
                resource_name NVARCHAR(150) NOT NULL,
                resource_type VARCHAR(50) DEFAULT 'CNC_MACHINE',
                hourly_cost_rate DECIMAL(18, 2) NOT NULL,
                capacity_hours_per_day DECIMAL(5, 2) DEFAULT 16.00,
                efficiency_pct DECIMAL(5, 2) DEFAULT 92.50,
                status VARCHAR(30) DEFAULT 'OPERATIONAL',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 103. Production: Operational Routing & Standard Time Matrix
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_routings')
        BEGIN
            CREATE TABLE prod_routings (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                routing_code VARCHAR(50) NOT NULL,
                routing_name NVARCHAR(150) NOT NULL,
                item_id UNIQUEIDENTIFIER NOT NULL,
                process_id UNIQUEIDENTIFIER NOT NULL,
                resource_id UNIQUEIDENTIFIER NOT NULL,
                operation_sequence INT NOT NULL,
                operation_description NVARCHAR(250) NOT NULL,
                setup_time_mins INT DEFAULT 30,
                run_time_mins INT DEFAULT 45,
                labor_hours DECIMAL(6, 2) DEFAULT 1.50,
                machine_hours DECIMAL(6, 2) DEFAULT 1.25,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 104. Production: Plant & Resource Capacity Parameters
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_capacity')
        BEGIN
            CREATE TABLE prod_capacity (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90401, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                plant_id UNIQUEIDENTIFIER NOT NULL,
                resource_id UNIQUEIDENTIFIER NOT NULL,
                period_month VARCHAR(20) NOT NULL,
                shift_hours_per_day DECIMAL(5, 2) DEFAULT 16.00,
                working_days INT DEFAULT 26,
                total_available_hours DECIMAL(8, 2) NOT NULL,
                planned_load_hours DECIMAL(8, 2) NOT NULL,
                capacity_utilization_pct DECIMAL(5, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'OPTIMAL',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 105. Production: Multi-Level Engineering Bill Of Materials (BOM) Headers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_bom_headers')
        BEGIN
            CREATE TABLE prod_bom_headers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90501, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                bom_code VARCHAR(50) NOT NULL UNIQUE,
                bom_type VARCHAR(30) DEFAULT 'STANDARD',
                item_id UNIQUEIDENTIFIER NOT NULL,
                revision_number VARCHAR(20) DEFAULT 'REV-1.0',
                base_quantity FLOAT DEFAULT 1.0,
                uom_code VARCHAR(20) DEFAULT 'PCS',
                expected_yield_pct DECIMAL(5, 2) DEFAULT 98.50,
                effective_from DATE NOT NULL,
                is_approved BIT DEFAULT 1,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 106. Production: BOM Component Items & Scrap Allowances
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_bom_items')
        BEGIN
            CREATE TABLE prod_bom_items (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90601, 1) NOT NULL,
                bom_id UNIQUEIDENTIFIER NOT NULL,
                component_item_id UNIQUEIDENTIFIER NOT NULL,
                quantity FLOAT NOT NULL,
                uom_code VARCHAR(20) DEFAULT 'PCS',
                scrap_allowance_pct DECIMAL(5, 2) DEFAULT 2.00,
                is_critical BIT DEFAULT 1,
                operation_seq INT DEFAULT 10,
                remarks NVARCHAR(200),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 107. Production: Demand Requisitions (from Sales Orders / Forecast)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_requisitions')
        BEGIN
            CREATE TABLE prod_requisitions (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                requisition_number VARCHAR(50) NOT NULL UNIQUE,
                demand_source VARCHAR(50) DEFAULT 'SALES_ORDER',
                item_id UNIQUEIDENTIFIER NOT NULL,
                requested_qty FLOAT NOT NULL,
                required_by_date DATE NOT NULL,
                priority VARCHAR(20) DEFAULT 'HIGH',
                requested_by NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 108. Production: Master Production Orders (Discrete Work Orders)
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_orders')
        BEGIN
            CREATE TABLE prod_orders (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                plant_id UNIQUEIDENTIFIER NOT NULL,
                order_number VARCHAR(50) NOT NULL UNIQUE,
                requisition_id UNIQUEIDENTIFIER NULL,
                item_id UNIQUEIDENTIFIER NOT NULL,
                bom_id UNIQUEIDENTIFIER NOT NULL,
                planned_qty FLOAT NOT NULL,
                completed_qty FLOAT DEFAULT 0.0,
                scrap_qty FLOAT DEFAULT 0.0,
                planned_start_date DATE NOT NULL,
                planned_end_date DATE NOT NULL,
                actual_start_date DATE NULL,
                actual_end_date DATE NULL,
                status VARCHAR(30) DEFAULT 'IN_PROGRESS',
                priority VARCHAR(20) DEFAULT 'HIGH',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 109. Production: Shop Floor Job Cards & Route Traveler Execution
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_job_cards')
        BEGIN
            CREATE TABLE prod_job_cards (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(90901, 1) NOT NULL,
                order_id UNIQUEIDENTIFIER NOT NULL,
                routing_id UNIQUEIDENTIFIER NOT NULL,
                resource_id UNIQUEIDENTIFIER NOT NULL,
                job_card_number VARCHAR(50) NOT NULL UNIQUE,
                operation_seq INT NOT NULL,
                operation_title NVARCHAR(150) NOT NULL,
                scheduled_hours DECIMAL(6, 2) NOT NULL,
                actual_hours DECIMAL(6, 2) NOT NULL,
                planned_qty FLOAT NOT NULL,
                completed_qty FLOAT NOT NULL,
                rejected_qty FLOAT DEFAULT 0.0,
                operator_name NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'COMPLETED',
                started_at DATETIME,
                completed_at DATETIME,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 110. Production: Materials Requisition & Issue to WIP
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_material_issues')
        BEGIN
            CREATE TABLE prod_material_issues (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(91001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                order_id UNIQUEIDENTIFIER NOT NULL,
                warehouse_id UNIQUEIDENTIFIER NOT NULL,
                issue_number VARCHAR(50) NOT NULL UNIQUE,
                issue_date DATE NOT NULL,
                item_id UNIQUEIDENTIFIER NOT NULL,
                required_qty FLOAT NOT NULL,
                issued_qty FLOAT NOT NULL,
                unit_cost DECIMAL(18, 2) NOT NULL,
                total_cost DECIMAL(18, 2) NOT NULL,
                issued_by NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'ISSUED_TO_WIP',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 111. Production: Material-to-Material Conversions & Assembly Reversals
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_conversions')
        BEGIN
            CREATE TABLE prod_conversions (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(91101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                conversion_number VARCHAR(50) NOT NULL UNIQUE,
                conversion_type VARCHAR(30) DEFAULT 'ASSEMBLY_CONVERSION',
                source_item_id UNIQUEIDENTIFIER NOT NULL,
                target_item_id UNIQUEIDENTIFIER NOT NULL,
                input_qty FLOAT NOT NULL,
                output_qty FLOAT NOT NULL,
                conversion_date DATE NOT NULL,
                unit_cost DECIMAL(18, 2) NOT NULL,
                total_value DECIMAL(18, 2) NOT NULL,
                operator_name NVARCHAR(100) NOT NULL,
                remarks NVARCHAR(300),
                status VARCHAR(30) DEFAULT 'POSTED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 112. Production: Quality Control Inspections & Release Authorizations
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_qc_inspections')
        BEGIN
            CREATE TABLE prod_qc_inspections (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(91201, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                order_id UNIQUEIDENTIFIER NOT NULL,
                inspection_number VARCHAR(50) NOT NULL UNIQUE,
                inspection_stage VARCHAR(50) DEFAULT 'FINAL_INSPECTION',
                sample_size_qty FLOAT NOT NULL,
                passed_qty FLOAT NOT NULL,
                rejected_qty FLOAT NOT NULL,
                defect_category VARCHAR(100) DEFAULT 'MINOR_TOLERANCE',
                inspection_date DATE NOT NULL,
                inspector_name NVARCHAR(100) NOT NULL,
                disposition VARCHAR(50) DEFAULT 'ACCEPTED_FOR_DISPATCH',
                status VARCHAR(30) DEFAULT 'APPROVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 113. Production: Machine Stoppage & Downtime Tracker
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_downtime_logs')
        BEGIN
            CREATE TABLE prod_downtime_logs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(91301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                resource_id UNIQUEIDENTIFIER NOT NULL,
                log_number VARCHAR(50) NOT NULL UNIQUE,
                downtime_date DATE NOT NULL,
                duration_mins INT NOT NULL,
                downtime_category VARCHAR(50) DEFAULT 'TOOLING_CHANGE',
                root_cause NVARCHAR(250) NOT NULL,
                technician_name NVARCHAR(100) NOT NULL,
                estimated_cost_loss DECIMAL(18, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'RESOLVED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 114. Production: Standard vs Actual Costing & Variance Records
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prod_cost_records')
        BEGIN
            CREATE TABLE prod_cost_records (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(91401, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                order_id UNIQUEIDENTIFIER NOT NULL,
                raw_material_cost DECIMAL(18, 2) NOT NULL,
                direct_labor_cost DECIMAL(18, 2) NOT NULL,
                machine_overhead_cost DECIMAL(18, 2) NOT NULL,
                scrap_variance_cost DECIMAL(18, 2) NOT NULL,
                total_actual_cost DECIMAL(18, 2) NOT NULL,
                standard_cost DECIMAL(18, 2) NOT NULL,
                variance_amount DECIMAL(18, 2) NOT NULL,
                variance_pct DECIMAL(5, 2) NOT NULL,
                cost_date DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'COMMITTED',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

# 1. Admin Company Configs
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_company_configs')
        BEGIN
            CREATE TABLE admin_company_configs (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                registration_no NVARCHAR(100) NOT NULL,
                tax_id NVARCHAR(100) NOT NULL,
                base_currency VARCHAR(10) DEFAULT 'USD',
                fiscal_start_month INT DEFAULT 4,
                multi_currency_enabled BIT DEFAULT 1,
                address_line1 NVARCHAR(200) NOT NULL,
                city NVARCHAR(100) NOT NULL,
                state NVARCHAR(100) NOT NULL,
                postal_code VARCHAR(20) NOT NULL,
                country VARCHAR(50) DEFAULT 'United States',
                phone VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                website VARCHAR(150),
                logo_path VARCHAR(255) DEFAULT '/static/img/brand/logo.svg',
                default_locale VARCHAR(20) DEFAULT 'en_US',
                status VARCHAR(30) DEFAULT 'ACTIVE',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 2. Business Units
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_business_units')
        BEGIN
            CREATE TABLE admin_business_units (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95201, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                unit_code VARCHAR(50) NOT NULL,
                unit_name NVARCHAR(150) NOT NULL,
                unit_type VARCHAR(50) DEFAULT 'OPERATING_DIVISION',
                manager_name NVARCHAR(100) NOT NULL,
                location NVARCHAR(200),
                cost_center_count INT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 3. Cost Centers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_cost_centers')
        BEGIN
            CREATE TABLE admin_cost_centers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                business_unit_id UNIQUEIDENTIFIER NOT NULL,
                cost_center_code VARCHAR(50) NOT NULL,
                name NVARCHAR(150) NOT NULL,
                department NVARCHAR(100) NOT NULL,
                manager_name NVARCHAR(100) NOT NULL,
                is_profit_center BIT DEFAULT 0,
                budget_allocation DECIMAL(18, 2) DEFAULT 0.00,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 4. Countries
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_countries')
        BEGIN
            CREATE TABLE admin_countries (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95401, 1) NOT NULL,
                country_code VARCHAR(10) NOT NULL UNIQUE,
                country_name NVARCHAR(100) NOT NULL,
                dial_code VARCHAR(10) NOT NULL,
                currency_code VARCHAR(10) NOT NULL,
                region VARCHAR(50) NOT NULL,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 5. States
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_states')
        BEGIN
            CREATE TABLE admin_states (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95501, 1) NOT NULL,
                country_code VARCHAR(10) NOT NULL,
                state_code VARCHAR(20) NOT NULL,
                state_name NVARCHAR(100) NOT NULL,
                tax_zone VARCHAR(50) DEFAULT 'STANDARD_ZONE',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 6. Currencies
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_currencies')
        BEGIN
            CREATE TABLE admin_currencies (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95601, 1) NOT NULL,
                currency_code VARCHAR(10) NOT NULL UNIQUE,
                currency_name NVARCHAR(100) NOT NULL,
                symbol NVARCHAR(10) NOT NULL,
                decimal_places INT DEFAULT 2,
                is_base_currency BIT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 7. Exchange Rates
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_exchange_rates')
        BEGIN
            CREATE TABLE admin_exchange_rates (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                currency_code VARCHAR(10) NOT NULL,
                target_currency VARCHAR(10) DEFAULT 'USD',
                exchange_rate DECIMAL(18, 6) NOT NULL,
                effective_date DATE NOT NULL,
                rate_type VARCHAR(30) DEFAULT 'SPOT_RATE',
                entered_by NVARCHAR(100) NOT NULL,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 8. Fiscal Calendars
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_fiscal_calendars')
        BEGIN
            CREATE TABLE admin_fiscal_calendars (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                fiscal_year_name VARCHAR(50) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                total_periods INT DEFAULT 12,
                is_closed BIT DEFAULT 0,
                opening_balance_locked BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 9. Fiscal Periods
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_fiscal_periods')
        BEGIN
            CREATE TABLE admin_fiscal_periods (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(95901, 1) NOT NULL,
                calendar_id UNIQUEIDENTIFIER NOT NULL,
                period_number INT NOT NULL,
                period_name VARCHAR(50) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'OPEN',
                closed_at DATETIME,
                closed_by NVARCHAR(100),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 10. Printers
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_printers')
        BEGIN
            CREATE TABLE admin_printers (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                printer_name NVARCHAR(150) NOT NULL,
                printer_type VARCHAR(50) DEFAULT 'NETWORK_PRINT_SERVER',
                ip_address VARCHAR(50) NOT NULL,
                port INT DEFAULT 9100,
                paper_size VARCHAR(20) DEFAULT 'A4',
                default_tray VARCHAR(30) DEFAULT 'Tray 1',
                is_default BIT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 11. Roles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_roles')
        BEGIN
            CREATE TABLE admin_roles (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96101, 1) NOT NULL,
                role_code VARCHAR(50) NOT NULL UNIQUE,
                role_name NVARCHAR(100) NOT NULL,
                description NVARCHAR(250),
                security_level INT DEFAULT 1,
                is_system_role BIT DEFAULT 0,
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 12. Role Permissions Matrix
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_role_permissions')
        BEGIN
            CREATE TABLE admin_role_permissions (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96201, 1) NOT NULL,
                role_id UNIQUEIDENTIFIER NOT NULL,
                module_code VARCHAR(50) NOT NULL,
                sub_area_code VARCHAR(50) NOT NULL,
                can_view BIT DEFAULT 1,
                can_create BIT DEFAULT 0,
                can_edit BIT DEFAULT 0,
                can_delete BIT DEFAULT 0,
                can_approve BIT DEFAULT 0,
                can_export BIT DEFAULT 0,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 13. User Profiles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_user_profiles')
        BEGIN
            CREATE TABLE admin_user_profiles (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96301, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                user_id UNIQUEIDENTIFIER NULL FOREIGN KEY REFERENCES users(id),
                user_code VARCHAR(50) NOT NULL,
                full_name NVARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(50),
                role_id UNIQUEIDENTIFIER,
                business_unit_id UNIQUEIDENTIFIER,
                cost_center_id UNIQUEIDENTIFIER,
                avatar_url VARCHAR(255) DEFAULT '/static/img/avatars/default.png',
                mfa_enabled BIT DEFAULT 0,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                last_login_at DATETIME,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 14. User Data Scopes
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_user_data_scopes')
        BEGIN
            CREATE TABLE admin_user_data_scopes (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96401, 1) NOT NULL,
                user_id UNIQUEIDENTIFIER NOT NULL,
                scope_type VARCHAR(50) DEFAULT 'COST_CENTER',
                entity_id UNIQUEIDENTIFIER NOT NULL,
                entity_name NVARCHAR(150) NOT NULL,
                access_mode VARCHAR(20) DEFAULT 'READ_WRITE',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 15. Tax Authorities
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_tax_authorities')
        BEGIN
            CREATE TABLE admin_tax_authorities (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96501, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                authority_code VARCHAR(50) NOT NULL,
                authority_name NVARCHAR(150) NOT NULL,
                jurisdiction NVARCHAR(100) NOT NULL,
                tax_office NVARCHAR(150) NOT NULL,
                contact_person NVARCHAR(100),
                phone VARCHAR(50),
                reporting_cycle VARCHAR(30) DEFAULT 'MONTHLY',
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 16. Tax Categories
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_tax_categories')
        BEGIN
            CREATE TABLE admin_tax_categories (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96601, 1) NOT NULL,
                category_code VARCHAR(50) NOT NULL UNIQUE,
                category_name NVARCHAR(100) NOT NULL,
                tax_type VARCHAR(50) DEFAULT 'VALUE_ADDED_TAX',
                default_rate DECIMAL(5, 2) DEFAULT 15.00,
                description NVARCHAR(250),
                is_active BIT DEFAULT 1,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 17. Tax Profiles
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_tax_profiles')
        BEGIN
            CREATE TABLE admin_tax_profiles (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96701, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                profile_code VARCHAR(50) NOT NULL,
                profile_name NVARCHAR(150) NOT NULL,
                category_id UNIQUEIDENTIFIER NOT NULL,
                authority_id UNIQUEIDENTIFIER NOT NULL,
                rate_percent DECIMAL(5, 2) NOT NULL,
                gl_account_code VARCHAR(50) DEFAULT '2150-TAX-PAYABLE',
                is_recoverable BIT DEFAULT 1,
                effective_date DATE NOT NULL,
                status VARCHAR(30) DEFAULT 'ACTIVE',
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 18. Periodic Closures
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_periodic_closures')
        BEGIN
            CREATE TABLE admin_periodic_closures (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96801, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                fiscal_period_id UNIQUEIDENTIFIER NOT NULL,
                module_code VARCHAR(50) NOT NULL,
                module_name NVARCHAR(100) NOT NULL,
                closing_date DATE NOT NULL,
                closed_by NVARCHAR(100) NOT NULL,
                status VARCHAR(30) DEFAULT 'CLOSED_VERIFIED',
                reconciliation_notes NVARCHAR(250),
                verified_balance DECIMAL(18, 2) DEFAULT 0.00,
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 19. Integrity Scans
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_integrity_scans')
        BEGIN
            CREATE TABLE admin_integrity_scans (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(96901, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                scan_type VARCHAR(50) DEFAULT 'FULL_DATABASE_INTEGRITY',
                scan_title NVARCHAR(150) NOT NULL,
                items_checked INT DEFAULT 0,
                anomalies_found INT DEFAULT 0,
                auto_repaired INT DEFAULT 0,
                scan_status VARCHAR(30) DEFAULT 'CLEAN_VERIFIED',
                scan_duration_ms INT DEFAULT 1850,
                log_details NVARCHAR(MAX),
                created_at DATETIME DEFAULT GETDATE()
            );
        END
        """,

        # 20. Audit Vault
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_audit_vault')
        BEGIN
            CREATE TABLE admin_audit_vault (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(97001, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                event_timestamp DATETIME DEFAULT GETDATE(),
                user_name NVARCHAR(100) NOT NULL,
                user_ip VARCHAR(50) DEFAULT '192.168.1.10',
                event_action VARCHAR(50) NOT NULL,
                module_code VARCHAR(50) NOT NULL,
                entity_name VARCHAR(100) NOT NULL,
                record_ref VARCHAR(100) NOT NULL,
                change_details NVARCHAR(500),
                security_severity VARCHAR(20) DEFAULT 'INFO'
            );
        END
        """,

        # 21. Backup Points
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_backup_points')
        BEGIN
            CREATE TABLE admin_backup_points (
                id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
                code INT IDENTITY(97101, 1) NOT NULL,
                company_id UNIQUEIDENTIFIER NOT NULL,
                backup_number VARCHAR(50) NOT NULL,
                backup_type VARCHAR(50) DEFAULT 'FULL_DATABASE_BACKUP',
                file_path NVARCHAR(255) NOT NULL,
                file_size_mb DECIMAL(10, 2) NOT NULL,
                status VARCHAR(30) DEFAULT 'VERIFIED_HEALTHY',
                verified_at DATETIME DEFAULT GETDATE(),
                verified_by NVARCHAR(100) NOT NULL,
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

def seed_sales_master_and_transactions():
    """Seeds comprehensive Sales Management master data, price lists, quotations, orders, delivery orders, and invoices."""
    area_count = db.query_one("SELECT COUNT(*) AS cnt FROM sales_areas")["cnt"]
    if area_count == 0:
        apex = db.query_one("SELECT id FROM companies WHERE short_code = 'APEX'")
        horizon = db.query_one("SELECT id FROM companies WHERE short_code = 'HORIZON'")
        delta = db.query_one("SELECT id FROM companies WHERE short_code = 'DELTA'")
        titan = db.query_one("SELECT id FROM companies WHERE short_code = 'TITAN'")
        prime = db.query_one("SELECT id FROM companies WHERE short_code = 'PRIME'")

        # 1. Sales Areas & Territories
        areas = [
            (apex["id"], "AREA-APX-01", "Northern Precision & Export Zone", "Industrial North", "Magnus Vance"),
            (horizon["id"], "AREA-HRZ-01", "Metropolitan Real Estate District", "Capital Region", "Dr. Robert Vance"),
            (delta["id"], "AREA-DLT-01", "Maritime Port Logistics Corridor", "Coastal Region", "Khorshed Alam"),
            (titan["id"], "AREA-TTN-01", "Heavy Metallurgy & Structural Hub", "Industrial South", "Hiroshi Sato"),
            (prime["id"], "AREA-PRM-01", "National Retail Supermarket Network", "Central Region", "Farhana Anis"),
        ]
        for a in areas:
            db.execute(
                """
                INSERT INTO sales_areas (company_id, area_code, area_name, region_name, head_of_area, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                a
            )
        logger.info("Seeded 5 Sales Areas.")

        area_apx = db.query_one("SELECT id FROM sales_areas WHERE area_code = 'AREA-APX-01'")
        area_hrz = db.query_one("SELECT id FROM sales_areas WHERE area_code = 'AREA-HRZ-01'")
        area_dlt = db.query_one("SELECT id FROM sales_areas WHERE area_code = 'AREA-DLT-01'")
        area_ttn = db.query_one("SELECT id FROM sales_areas WHERE area_code = 'AREA-TTN-01'")
        area_prm = db.query_one("SELECT id FROM sales_areas WHERE area_code = 'AREA-PRM-01'")

        # 2. Sales Teams (MM > ZM > TSM Hierarchy)
        teams = [
            (apex["id"], area_apx["id"] if area_apx else None, "TEAM-APX-MM", "Apex High-Tech & Precision Division", "MM_TEAM", "Alexander Vance", 5000000.0),
            (apex["id"], area_apx["id"] if area_apx else None, "TEAM-APX-ZM1", "Automotive & Aerospace CNC Zone", "ZM_TEAM", "Marcus Sterling", 3000000.0),
            (apex["id"], area_apx["id"] if area_apx else None, "TEAM-APX-TSM1", "Precision Fasteners Territory", "TSM_TEAM", "Mahmudur Rahman", 1500000.0),
            (horizon["id"], area_hrz["id"] if area_hrz else None, "TEAM-HRZ-TSM", "Luxury High-Rise & Commercial Towers", "TSM_TEAM", "Tanvir Ahmed", 8000000.0),
            (delta["id"], area_dlt["id"] if area_dlt else None, "TEAM-DLT-TSM", "Ocean Freight & Port Logistics Team", "TSM_TEAM", "Zahid Hasan", 4500000.0),
            (prime["id"], area_prm["id"] if area_prm else None, "TEAM-PRM-TSM", "FMCG Supermarket Key Accounts", "TSM_TEAM", "Nusrat Jahan", 2500000.0),
        ]
        for t in teams:
            db.execute(
                """
                INSERT INTO sales_teams (company_id, area_id, team_code, team_name, team_type, manager_name, target_annual_amount, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                t
            )
        logger.info("Seeded 6 Sales Teams across MM, ZM and TSM tiers.")

        team_tsm_apx = db.query_one("SELECT id FROM sales_teams WHERE team_code = 'TEAM-APX-TSM1'")
        team_tsm_hrz = db.query_one("SELECT id FROM sales_teams WHERE team_code = 'TEAM-HRZ-TSM'")
        team_tsm_dlt = db.query_one("SELECT id FROM sales_teams WHERE team_code = 'TEAM-DLT-TSM'")
        team_tsm_prm = db.query_one("SELECT id FROM sales_teams WHERE team_code = 'TEAM-PRM-TSM'")

        # 3. Salespersons
        salespersons_data = [
            (apex["id"], team_tsm_apx["id"] if team_tsm_apx else None, "REP-101", "Mahmudur Rahman", "m.rahman@pyrix.internal", "+1 555 0192", "Territory Sales Lead (CNC)", 10.0, 125000.0, 3.0),
            (apex["id"], team_tsm_apx["id"] if team_tsm_apx else None, "REP-102", "Alexander Vance", "alex.vance@pyrix.internal", "+1 555 0100", "Principal Systems & Key Accounts", 20.0, 250000.0, 4.0),
            (horizon["id"], team_tsm_hrz["id"] if team_tsm_hrz else None, "REP-201", "Tanvir Ahmed", "t.ahmed@pyrix.internal", "+1 555 0244", "Commercial Real Estate Lead", 5.0, 500000.0, 2.0),
            (delta["id"], team_tsm_dlt["id"] if team_tsm_dlt else None, "REP-301", "Zahid Hasan", "z.hasan@pyrix.internal", "+1 555 0311", "Intermodal Logistics Executive", 8.0, 300000.0, 2.5),
            (prime["id"], team_tsm_prm["id"] if team_tsm_prm else None, "REP-401", "Farhana Anis", "f.anis@pyrix.internal", "+1 555 0489", "National Supermarket Account Exec", 12.0, 200000.0, 3.5),
        ]
        for sp in salespersons_data:
            db.execute(
                """
                INSERT INTO salespersons (company_id, team_id, salesperson_code, full_name, email, phone, designation, max_discount_pct, monthly_target, commission_pct, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                sp
            )
        logger.info("Seeded 5 Salespersons.")

        rep_101 = db.query_one("SELECT id FROM salespersons WHERE salesperson_code = 'REP-101'")
        rep_102 = db.query_one("SELECT id FROM salespersons WHERE salesperson_code = 'REP-102'")
        rep_201 = db.query_one("SELECT id FROM salespersons WHERE salesperson_code = 'REP-201'")
        rep_301 = db.query_one("SELECT id FROM salespersons WHERE salesperson_code = 'REP-301'")
        rep_401 = db.query_one("SELECT id FROM salespersons WHERE salesperson_code = 'REP-401'")

        # 4. Product Price Profiles
        price_profiles = [
            (apex["id"], "PRF-APX-STD", "Apex Standard Precision Tariff (Export)", "USD", "BASE_PRICE", 1),
            (apex["id"], "PRF-APX-OEM", "Automotive OEM Contract Rate Matrix", "USD", "SPECIAL_CUSTOMER", 0),
            (horizon["id"], "PRF-HRZ-RES", "Horizon Residential Penthouse Catalog", "USD", "BASE_PRICE", 1),
            (delta["id"], "PRF-DLT-FRT", "Delta Global Freight Schedule 2026", "USD", "BASE_PRICE", 1),
            (prime["id"], "PRF-PRM-WHL", "Prime FMCG National Wholesale Tier", "USD", "WHOLESALE", 1),
        ]
        for pp in price_profiles:
            db.execute(
                """
                INSERT INTO sales_price_profiles (company_id, profile_code, profile_name, currency, price_type, is_default, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                pp
            )
        logger.info("Seeded 5 Product Price Profiles.")

        prof_apx_std = db.query_one("SELECT id FROM sales_price_profiles WHERE profile_code = 'PRF-APX-STD'")
        prof_hrz_res = db.query_one("SELECT id FROM sales_price_profiles WHERE profile_code = 'PRF-HRZ-RES'")
        prof_dlt_frt = db.query_one("SELECT id FROM sales_price_profiles WHERE profile_code = 'PRF-DLT-FRT'")
        prof_prm_whl = db.query_one("SELECT id FROM sales_price_profiles WHERE profile_code = 'PRF-PRM-WHL'")

        # 5. Product Prices Catalog
        product_prices = [
            (prof_apx_std["id"] if prof_apx_std else None, "ITM-CNC-M8", "M8 High-Tensile Precision Socket Screws (Box 1000)", "BOX", 145.0, 120.0, 15.0),
            (prof_apx_std["id"] if prof_apx_std else None, "ITM-AERO-01", "Aerospace Titanium Bearing Bushings (Set 4)", "SET", 924.0, 800.0, 10.0),
            (prof_apx_std["id"] if prof_apx_std else None, "ITM-SMT-PCB", "5-Axis Surface Mount PCB Motherboard Assembly", "PCS", 450.0, 380.0, 12.0),
            (prof_hrz_res["id"] if prof_hrz_res else None, "UNIT-HRZ-PH", "Horizon Grand Tower Executive Penthouse Suite", "UNIT", 850000.0, 800000.0, 5.0),
            (prof_dlt_frt["id"] if prof_dlt_frt else None, "FRT-TEU-200", "Intermodal Sea Freight Container Transport (200 TEU)", "TEU", 1550.0, 1350.0, 10.0),
            (prof_prm_whl["id"] if prof_prm_whl else None, "FMCG-SUP-10", "FMCG Supermarket Fast-Moving Master Carton Pack", "CTN", 112.0, 95.0, 20.0),
        ]
        for p in product_prices:
            if p[0]:
                db.execute(
                    """
                    INSERT INTO sales_product_prices (profile_id, item_code, item_name, uom, base_price, min_selling_price, max_discount_pct, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    p
                )
        logger.info("Seeded Product Prices Catalog.")

        # 6. Discount Limits Matrix
        discount_limits = [
            ("Field Sales Representative", 5.0, 5.0, "Territory Sales Manager"),
            ("Territory Sales Manager (TSM)", 10.0, 10.0, "Zonal Sales Manager"),
            ("Zonal Sales Manager (ZM)", 15.0, 15.0, "Commercial Director / CFO"),
            ("Commercial Director / Sys Admin", 25.0, 25.0, "Executive Board"),
        ]
        for dl in discount_limits:
            db.execute(
                """
                INSERT INTO sales_discount_limits (role_name, max_discount_pct, requires_approval_above_pct, approver_role, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                dl
            )
        logger.info("Seeded 4 Role-Based Discount Limits.")

        # 7. Sales Quotes (with Items)
        quotes = [
            (apex["id"], "SQ-2026-APX-01", 1, "EuroAutomotive AG (Germany)", rep_101["id"] if rep_101 else None, "2026-08-10", "2026-09-30", 150000.0, 5000.0, 0.0, 145000.0, "USD", "CONVERTED_TO_SO", "Formal tender accepted and converted to SO-APX-8801"),
            (apex["id"], "SQ-2026-APX-02", 2, "Boeing Subcontractor Aviation Corp", rep_102["id"] if rep_102 else None, "2026-08-15", "2026-10-15", 95000.0, 2600.0, 0.0, 92400.0, "USD", "CONVERTED_TO_SO", "Revision 2 with upgraded titanium specifications"),
            (horizon["id"], "SQ-2026-HRZ-01", 1, "Dr. Robert Vance (Private Trust)", rep_201["id"] if rep_201 else None, "2026-08-01", "2026-09-15", 850000.0, 0.0, 0.0, 850000.0, "USD", "CONVERTED_TO_SO", "Penthouse #18A high-floor allotment quotation"),
            (delta["id"], "SQ-2026-DLT-01", 1, "Maersk Line Alliance Intermodal", rep_301["id"] if rep_301 else None, "2026-08-20", "2026-10-01", 320000.0, 10000.0, 0.0, 310000.0, "USD", "ACCEPTED", "200 TEU Antwerp Hub clearing & transit quote"),
            (prime["id"], "SQ-2026-PRM-01", 1, "Metro Hypermarkets National", rep_401["id"] if rep_401 else None, "2026-08-22", "2026-09-22", 115000.0, 3000.0, 0.0, 112000.0, "USD", "CONVERTED_TO_SO", "Quarterly supermarket stock replenishment"),
        ]
        for q in quotes:
            db.execute(
                """
                INSERT INTO sales_quotes (company_id, quote_number, revision_no, customer_name, salesperson_id, quote_date, valid_until, subtotal, discount_amount, tax_amount, total_amount, currency, status, progress_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                q
            )
        logger.info("Seeded 5 Multi-Status Sales Quotes.")

        sq_1 = db.query_one("SELECT id FROM sales_quotes WHERE quote_number = 'SQ-2026-APX-01'")
        sq_2 = db.query_one("SELECT id FROM sales_quotes WHERE quote_number = 'SQ-2026-APX-02'")

        if sq_1:
            db.execute(
                """
                INSERT INTO sales_quote_items (quote_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, remarks)
                VALUES (?, 'ITM-CNC-M8', 'M8 High-Tensile Precision Socket Screws (Box 1000)', 'BOX', 1000, 145.0, 0.0, 145000.0, 'Batch 1 Export Grade')
                """,
                (sq_1["id"],)
            )
        if sq_2:
            db.execute(
                """
                INSERT INTO sales_quote_items (quote_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, remarks)
                VALUES (?, 'ITM-AERO-01', 'Aerospace Titanium Bearing Bushings (Set 4)', 'SET', 100, 924.0, 0.0, 92400.0, 'EN 9100 Certified')
                """,
                (sq_2["id"],)
            )

        # 8. Sales Orders (SO Header & Lines)
        orders = [
            (apex["id"], sq_1["id"] if sq_1 else None, "SO-APX-8801", "EuroAutomotive AG (Germany)", rep_101["id"] if rep_101 else None, "2026-08-12", "2026-09-25", "Net 45 Days", "FOB Plant Delta Dock", "Plant Delta 01 Receiving Dock", "EuroAutomotive HQ Frankfurt", "USD", 1.0, 150000.0, 5000.0, 0.0, 145000.0, "DO_ISSUED", 0, None, 2, 2, 1),
            (apex["id"], sq_2["id"] if sq_2 else None, "SO-APX-8802", "Boeing Subcontractor Aviation Corp", rep_102["id"] if rep_102 else None, "2026-08-18", "2026-10-10", "Net 30 Days", "CIF Destination Port", "Boeing Receiving Facility Seattle", "Boeing Commercial Aviation", "USD", 1.0, 95000.0, 2600.0, 0.0, 92400.0, "APPROVED", 0, None, 2, 2, 0),
            (horizon["id"], None, "SO-HRZ-9101", "Dr. Robert Vance (Private Trust)", rep_201["id"] if rep_201 else None, "2026-08-05", "2026-12-31", "Installment Schedule", "Handover Certificate", "Horizon Grand Tower Fl 18", "Horizon Landmark Tower", "USD", 1.0, 850000.0, 0.0, 0.0, 850000.0, "APPROVED", 0, None, 3, 3, 1),
            (delta["id"], None, "SO-DLT-2040", "Maersk Line Alliance Intermodal", rep_301["id"] if rep_301 else None, "2026-08-25", "2026-09-30", "Net 30 Days", "Port Berth 4 Dispatch", "Berth #4 Ocean Terminal", "Maersk Line Copenhagen", "USD", 1.0, 320000.0, 10000.0, 0.0, 310000.0, "DO_ISSUED", 0, None, 2, 2, 1),
            (prime["id"], None, "SO-PRM-9912", "Metro Hypermarkets National", rep_401["id"] if rep_401 else None, "2026-08-24", "2026-09-15", "Net 15 Days", "Central Hub Delivery", "Central Supermarket Depot #4", "Metro Retail HQ", "USD", 1.0, 115000.0, 3000.0, 0.0, 112000.0, "INVOICED", 0, None, 1, 1, 1),
            (titan["id"], None, "SO-TTN-7701", "Nippon Steel Structural Fabrication", rep_101["id"] if rep_101 else None, "2026-08-28", "2026-10-30", "LC at Sight 60D", "FOB Steel Complex B", "Tokyo Steel Terminal Berth", "Nippon Steel Corp Tokyo", "USD", 1.0, 195000.0, 0.0, 0.0, 195000.0, "ON_HOLD", 1, "Credit limit review pending by CFO", 1, 2, 0),
        ]
        for o in orders:
            db.execute(
                """
                INSERT INTO sales_orders 
                (company_id, quote_id, order_number, customer_name, salesperson_id, order_date, expected_delivery_date, payment_terms, delivery_terms, shipping_address, billing_address, currency, exchange_rate, subtotal, discount_amount, tax_amount, total_amount, status, is_on_hold, hold_reason, current_approval_tier, max_approval_tier, is_gl_posted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                o
            )
        logger.info("Seeded 6 Sales Orders across 5 subsidiaries.")

        so_apx_1 = db.query_one("SELECT id FROM sales_orders WHERE order_number = 'SO-APX-8801'")
        so_apx_2 = db.query_one("SELECT id FROM sales_orders WHERE order_number = 'SO-APX-8802'")
        so_prm_1 = db.query_one("SELECT id FROM sales_orders WHERE order_number = 'SO-PRM-9912'")

        if so_apx_1:
            db.execute(
                """
                INSERT INTO sales_order_items (order_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, packing_spec, delivered_qty, invoiced_qty)
                VALUES (?, 'ITM-CNC-M8', 'M8 High-Tensile Precision Socket Screws (Box 1000)', 'BOX', 1000, 145.0, 0.0, 145000.0, 'Heavy Wooden Export Pallet (x20 Boxes)', 1000.0, 1000.0)
                """,
                (so_apx_1["id"],)
            )
        if so_apx_2:
            db.execute(
                """
                INSERT INTO sales_order_items (order_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, packing_spec, delivered_qty, invoiced_qty)
                VALUES (?, 'ITM-AERO-01', 'Aerospace Titanium Bearing Bushings (Set 4)', 'SET', 100, 924.0, 0.0, 92400.0, 'Anti-Static Vacuum Sealed Aerospace Bags', 0.0, 0.0)
                """,
                (so_apx_2["id"],)
            )
        if so_prm_1:
            db.execute(
                """
                INSERT INTO sales_order_items (order_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total, packing_spec, delivered_qty, invoiced_qty)
                VALUES (?, 'FMCG-SUP-10', 'FMCG Supermarket Fast-Moving Master Carton Pack', 'CTN', 1000, 112.0, 0.0, 112000.0, 'Shrink-wrapped Corrugated Master Carton', 1000.0, 1000.0)
                """,
                (so_prm_1["id"],)
            )

        # 9. Delivery Orders (DO)
        if so_apx_1:
            db.execute(
                """
                INSERT INTO sales_delivery_orders 
                (company_id, order_id, do_number, do_date, dispatch_date, carrier_name, vehicle_no, tracking_ref, delivery_address, status, gate_pass_ref, created_by)
                VALUES (?, ?, 'DO-APX-2026-001', '2026-08-20', '2026-08-20', 'DHL Global Forwarding Fleet', 'TRK-DH-8802', 'TRACK-DHL-991823', 'Plant Delta 01 Receiving Dock, Bay 04', 'DISPATCHED', 'GP-2026-APX-082', 'Plant Dispatch Manager')
                """,
                (apex["id"], so_apx_1["id"])
            )
            do_1 = db.query_one("SELECT id FROM sales_delivery_orders WHERE do_number = 'DO-APX-2026-001'")
            if do_1:
                db.execute(
                    """
                    INSERT INTO sales_do_items (do_id, order_item_id, item_code, item_name, uom, ordered_qty, dispatch_qty, unit_price, line_total)
                    VALUES (?, NULL, 'ITM-CNC-M8', 'M8 High-Tensile Precision Socket Screws (Box 1000)', 'BOX', 1000, 1000, 145.0, 145000.0)
                    """,
                    (do_1["id"],)
                )

        # 10. Sales Invoices
        if so_apx_1:
            do_row = db.query_one("SELECT id FROM sales_delivery_orders WHERE do_number = 'DO-APX-2026-001'")
            db.execute(
                """
                INSERT INTO sales_invoices 
                (company_id, order_id, do_id, invoice_number, invoice_type, customer_name, invoice_date, due_date, currency, exchange_rate, subtotal, discount_amount, tax_amount, total_amount, paid_amount, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, ?, 'INV-APX-2026-8801', 'COMMERCIAL', 'EuroAutomotive AG (Germany)', '2026-08-20', '2026-10-04', 'USD', 1.0, 145000.0, 0.0, 0.0, 145000.0, 145000.0, 'PAID', 1, 'JV-APX-0820')
                """,
                (apex["id"], so_apx_1["id"], do_row["id"] if do_row else None)
            )
            inv_1 = db.query_one("SELECT id FROM sales_invoices WHERE invoice_number = 'INV-APX-2026-8801'")
            if inv_1:
                db.execute(
                    """
                    INSERT INTO sales_invoice_items (invoice_id, item_code, item_name, uom, quantity, unit_price, discount_pct, line_total)
                    VALUES (?, 'ITM-CNC-M8', 'M8 High-Tensile Precision Socket Screws (Box 1000)', 'BOX', 1000, 145.0, 0.0, 145000.0)
                    """,
                    (inv_1["id"],)
                )

        # 11. Sales Returns
        if so_apx_1:
            db.execute(
                """
                INSERT INTO sales_returns (company_id, order_id, invoice_id, return_number, customer_name, return_date, reason, return_amount, status, credit_memo_ref)
                VALUES (?, ?, NULL, 'RET-APX-2026-01', 'EuroAutomotive AG (Germany)', '2026-08-25', 'Surface passivation coating minor flaw on 30 sample boxes', 4350.0, 'CREDITED', 'CM-APX-9901')
                """,
                (apex["id"], so_apx_1["id"])
            )

        # 12. Sales Budgets
        budgets = [
            (apex["id"], "FY 2026-2027", rep_101["id"] if rep_101 else None, "Precision CNC & Aerospace", 1500000.0, 350000.0, 400000.0, 380000.0, 370000.0, 237400.0, "APPROVED"),
            (apex["id"], "FY 2026-2027", rep_102["id"] if rep_102 else None, "Global Automotive OEM Key Accounts", 3000000.0, 750000.0, 800000.0, 720000.0, 730000.0, 1450000.0, "APPROVED"),
            (horizon["id"], "FY 2026-2027", rep_201["id"] if rep_201 else None, "Commercial Real Estate & Towers", 8000000.0, 2000000.0, 2500000.0, 1800000.0, 1700000.0, 2050000.0, "APPROVED"),
            (prime["id"], "FY 2026-2027", rep_401["id"] if rep_401 else None, "FMCG Supermarket Network", 2500000.0, 600000.0, 650000.0, 620000.0, 630000.0, 612000.0, "APPROVED"),
        ]
        for b in budgets:
            db.execute(
                """
                INSERT INTO sales_budgets (company_id, fiscal_year, salesperson_id, target_category, annual_target, q1_target, q2_target, q3_target, q4_target, achieved_amount, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                b
            )

        # 13. Sales Approvals
        if so_apx_1:
            approvals = [
                ("SO", so_apx_1["id"], 1, "Tier 1: Territory Sales Manager", "M. Rahman", "TSM Lead", "APPROVED", "Order price verified against Export tariff PRF-APX-STD", "2026-08-12 10:15:00"),
                ("SO", so_apx_1["id"], 2, "Tier 2: CFO / Commercial Controller", "Sarah Jenkins", "Chief Financial Officer", "APPROVED", "Customer credit terms Net 45 validated", "2026-08-12 14:30:00"),
            ]
            for a in approvals:
                db.execute(
                    """
                    INSERT INTO sales_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments, action_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    a
                )
        logger.info("Seeded Sales Management Master & Transactional Blueprint data.")


def seed_inventory_master_and_transactions():
    """Seeds comprehensive Inventory master data, warehouses, bins, items, stock balances, GRNs, Issues, STOs, and Warranties."""
    wh_count = db.query_one("SELECT COUNT(*) AS cnt FROM inv_warehouses")["cnt"]
    if wh_count == 0:
        apex = db.query_one("SELECT id FROM companies WHERE short_code = 'APEX'")
        horizon = db.query_one("SELECT id FROM companies WHERE short_code = 'HORIZON'")
        delta = db.query_one("SELECT id FROM companies WHERE short_code = 'DELTA'")
        titan = db.query_one("SELECT id FROM companies WHERE short_code = 'TITAN'")
        prime = db.query_one("SELECT id FROM companies WHERE short_code = 'PRIME'")

        # 1. Warehouses Master
        warehouses = [
            (apex["id"], "WH-APX-01", "Apex Central Raw Materials & Stores", "CENTRAL_STORE", "Plant Delta 01 - Gate 2", "Marcus Sterling"),
            (apex["id"], "WH-APX-02", "Apex High-Bay Finished Goods Depot", "FINISHED_GOODS", "Plant Delta 01 - Bay 04", "Rashid Al-Hassan"),
            (horizon["id"], "WH-HRZ-01", "Horizon Landmark Project Site Store", "PROJECT_SITE", "Horizon Landmark Tower Fl B2", "Tanvir Ahmed"),
            (delta["id"], "WH-DLT-01", "Delta Port Intermodal CFS Yard", "TRANSIT_CFS", "Berth 4 Marine Terminal", "Khorshed Alam"),
            (titan["id"], "WH-TTN-01", "Titan Heavy Metallurgy Ingot Yard", "HEAVY_YARD", "Titan Complex B Yard", "Hiroshi Sato"),
            (prime["id"], "WH-PRM-01", "Prime National Retail FMCG Distribution Center", "CENTRAL_DC", "Central Logistics Park DC-08", "Farhana Anis"),
        ]
        for w in warehouses:
            db.execute(
                """
                INSERT INTO inv_warehouses (company_id, warehouse_code, warehouse_name, warehouse_type, address, manager_name, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                w
            )
        logger.info("Seeded 6 Warehouses across 5 subsidiaries.")

        wh_apx_1 = db.query_one("SELECT id FROM inv_warehouses WHERE warehouse_code = 'WH-APX-01'")
        wh_apx_2 = db.query_one("SELECT id FROM inv_warehouses WHERE warehouse_code = 'WH-APX-02'")

        # 2. Multi-Bin Storage Locations
        if wh_apx_1 and wh_apx_2:
            bins = [
                (wh_apx_1["id"], "BIN-A1-01", "Aisle A", "Rack 01", "Shelf 1", "Bin 01"),
                (wh_apx_1["id"], "BIN-A1-02", "Aisle A", "Rack 01", "Shelf 2", "Bin 02"),
                (wh_apx_1["id"], "BIN-B2-01", "Aisle B", "Rack 02", "Shelf 1", "Bin 01"),
                (wh_apx_2["id"], "BIN-FG-01", "Aisle HighBay", "Rack 01", "Shelf 1", "Bin 01"),
                (wh_apx_2["id"], "BIN-FG-02", "Aisle HighBay", "Rack 01", "Shelf 2", "Bin 02"),
            ]
            for b in bins:
                db.execute(
                    """
                    INSERT INTO inv_bins (warehouse_id, bin_code, aisle, rack, shelf, bin_number, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    b
                )
            logger.info("Seeded 5 Storage Bins.")

        # 3. Product Groups
        groups = [
            (apex["id"], "GRP-RM-CNC", "CNC Raw Materials & Fasteners", "RAW_MATERIALS"),
            (apex["id"], "GRP-FG-AERO", "Aerospace & Automotive Assemblies", "FINISHED_GOODS"),
            (apex["id"], "GRP-TOOL-CN", "Carbide Tooling & Plant Consumables", "CONSUMABLES"),
            (horizon["id"], "GRP-CIVIL-RM", "Civil Construction Steel & Concrete", "RAW_MATERIALS"),
            (delta["id"], "GRP-FRT-EQP", "Port Container Cargo Handling Spares", "SPARE_PARTS"),
            (prime["id"], "GRP-FMCG-FG", "Supermarket Retail Consumer Goods", "FINISHED_GOODS"),
        ]
        for g in groups:
            db.execute(
                """
                INSERT INTO inv_product_groups (company_id, group_code, group_name, group_type, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                g
            )
        logger.info("Seeded 6 Product Groups.")

        grp_rm = db.query_one("SELECT id FROM inv_product_groups WHERE group_code = 'GRP-RM-CNC'")
        grp_fg = db.query_one("SELECT id FROM inv_product_groups WHERE group_code = 'GRP-FG-AERO'")
        grp_tool = db.query_one("SELECT id FROM inv_product_groups WHERE group_code = 'GRP-TOOL-CN'")

        # 4. Units of Measure (UOM)
        uoms = [
            (apex["id"], "PCS", "Pieces (Base Unit)", "PCS", 1.0),
            (apex["id"], "BOX", "Box (1000 Pieces)", "PCS", 1000.0),
            (apex["id"], "SET", "Assembly Set (4 Pieces)", "PCS", 4.0),
            (apex["id"], "KG", "Kilogram (Weight)", "KG", 1.0),
            (apex["id"], "TON", "Metric Ton (1000 KG)", "KG", 1000.0),
            (apex["id"], "MTR", "Meter (Length)", "MTR", 1.0),
        ]
        for u in uoms:
            db.execute(
                """
                INSERT INTO inv_uom (company_id, uom_code, uom_name, base_uom, conversion_ratio, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                u
            )
        logger.info("Seeded 6 UOMs & Conversion Ratios.")

        # 5. Master Inventory Items
        items = [
            (apex["id"], grp_rm["id"] if grp_rm else None, "BOX", "ITM-CNC-M8", "M8 High-Tensile Socket Screws (Box 1000)", "DIN 912 Class 12.9 Black Oxide Finish", 120.0, 200.0, 100.0, 0, "ACTIVE"),
            (apex["id"], grp_fg["id"] if grp_fg else None, "SET", "ITM-AERO-01", "Aerospace Titanium Bearing Bushings (Set 4)", "Ti-6Al-4V Grade 5 Precision CNC Milled", 800.0, 50.0, 20.0, 1, "ACTIVE"),
            (apex["id"], grp_fg["id"] if grp_fg else None, "PCS", "ITM-SMT-PCB", "5-Axis Surface Mount PCB Assembly", "FR4 High-Temp Multilayer SMT Assembled", 380.0, 100.0, 50.0, 1, "ACTIVE"),
            (apex["id"], grp_tool["id"] if grp_tool else None, "BOX", "TOOL-CARBIDE-10", "Sandvik Coromant Milling Carbide Inserts", "Grade GC1130 PVD Coated Milling Inserts (Box 10)", 48.50, 100.0, 50.0, 0, "ACTIVE"),
        ]
        for it in items:
            db.execute(
                """
                INSERT INTO inv_items (company_id, group_id, uom_code, item_code, item_name, specification, standard_cost, min_reorder_qty, safety_stock_qty, is_serialized, item_status, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                it
            )
        logger.info("Seeded 4 Master Inventory Items.")

        itm_m8 = db.query_one("SELECT id FROM inv_items WHERE item_code = 'ITM-CNC-M8'")
        itm_aero = db.query_one("SELECT id FROM inv_items WHERE item_code = 'ITM-AERO-01'")
        itm_pcb = db.query_one("SELECT id FROM inv_items WHERE item_code = 'ITM-SMT-PCB'")
        itm_tool = db.query_one("SELECT id FROM inv_items WHERE item_code = 'TOOL-CARBIDE-10'")

        bin_1 = db.query_one("SELECT id FROM inv_bins WHERE bin_code = 'BIN-A1-01'")
        bin_fg = db.query_one("SELECT id FROM inv_bins WHERE bin_code = 'BIN-FG-01'")

        # 6. Real-Time Stock Balances
        if wh_apx_1 and itm_m8:
            db.execute(
                """
                INSERT INTO inv_stock_balances (company_id, warehouse_id, bin_id, item_id, on_hand_qty, reserved_qty, in_transit_qty)
                VALUES (?, ?, ?, ?, 1500.0, 500.0, 200.0)
                """,
                (apex["id"], wh_apx_1["id"], bin_1["id"] if bin_1 else None, itm_m8["id"])
            )
        if wh_apx_2 and itm_aero:
            db.execute(
                """
                INSERT INTO inv_stock_balances (company_id, warehouse_id, bin_id, item_id, on_hand_qty, reserved_qty, in_transit_qty)
                VALUES (?, ?, ?, ?, 250.0, 100.0, 0.0)
                """,
                (apex["id"], wh_apx_2["id"], bin_fg["id"] if bin_fg else None, itm_aero["id"])
            )
        if wh_apx_2 and itm_pcb:
            db.execute(
                """
                INSERT INTO inv_stock_balances (company_id, warehouse_id, bin_id, item_id, on_hand_qty, reserved_qty, in_transit_qty)
                VALUES (?, ?, ?, ?, 480.0, 120.0, 50.0)
                """,
                (apex["id"], wh_apx_2["id"], bin_fg["id"] if bin_fg else None, itm_pcb["id"])
            )
        if wh_apx_1 and itm_tool:
            db.execute(
                """
                INSERT INTO inv_stock_balances (company_id, warehouse_id, bin_id, item_id, on_hand_qty, reserved_qty, in_transit_qty)
                VALUES (?, ?, ?, ?, 800.0, 0.0, 100.0)
                """,
                (apex["id"], wh_apx_1["id"], bin_1["id"] if bin_1 else None, itm_tool["id"])
            )
        logger.info("Seeded Real-Time Stock Balances.")

        # 7. Goods Receiving Notes (GRN)
        if wh_apx_1 and itm_tool:
            db.execute(
                """
                INSERT INTO inv_grn_headers (company_id, warehouse_id, grn_number, grn_type, po_ref, supplier_name, grn_date, challan_ref, received_by, qc_status, total_received_value, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, 'GRN-APX-2026-001', 'VENDOR_PO', 'PO-APX-2026-01', 'Sandvik Coromant Nordic AB', '2026-08-18', 'CH-SDV-99182', 'Marcus Sterling', 'PASSED', 48500.0, 'POSTED', 1, 'JV-INV-0818')
                """,
                (apex["id"], wh_apx_1["id"])
            )
            grn_1 = db.query_one("SELECT id FROM inv_grn_headers WHERE grn_number = 'GRN-APX-2026-001'")
            if grn_1:
                db.execute(
                    """
                    INSERT INTO inv_grn_items (grn_id, item_id, bin_id, received_qty, accepted_qty, rejected_qty, unit_cost, line_total, batch_number, remarks)
                    VALUES (?, ?, ?, 1000.0, 1000.0, 0.0, 48.50, 48500.0, 'BATCH-SDV-2608', 'Passed optical dimension inspection')
                    """,
                    (grn_1["id"], itm_tool["id"], bin_1["id"] if bin_1 else None)
                )

        # 8. Goods Issue Challans
        if wh_apx_2 and itm_m8:
            db.execute(
                """
                INSERT INTO inv_issues (company_id, warehouse_id, issue_number, issue_type, order_ref, cost_centre_name, issue_date, gate_pass_ref, issued_by, recipient_name, total_issue_value, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, 'ISS-APX-2026-001', 'DELIVERY_DISPATCH', 'SO-APX-8801', 'Export Sales Commercial', '2026-08-20', 'GP-2026-APX-082', 'Rashid Al-Hassan', 'EuroAutomotive AG (Carrier: DHL)', 120000.0, 'DISPATCHED', 1, 'JV-ISS-0820')
                """,
                (apex["id"], wh_apx_2["id"])
            )
            iss_1 = db.query_one("SELECT id FROM inv_issues WHERE issue_number = 'ISS-APX-2026-001'")
            if iss_1:
                db.execute(
                    """
                    INSERT INTO inv_issue_items (issue_id, item_id, bin_id, issued_qty, unit_cost, line_total, remarks)
                    VALUES (?, ?, ?, 1000.0, 120.0, 120000.0, 'Dispatched against Delivery Order DO-APX-2026-001')
                    """,
                    (iss_1["id"], itm_m8["id"], bin_fg["id"] if bin_fg else None)
                )

        # 9. Inter-Warehouse Stock Transfers (STO)
        if wh_apx_1 and wh_apx_2 and itm_m8:
            db.execute(
                """
                INSERT INTO inv_stock_transfers (company_id, from_warehouse_id, to_warehouse_id, transfer_number, transfer_date, dispatch_date, carrier_name, vehicle_no, tracking_ref, total_transfer_value, status)
                VALUES (?, ?, ?, 'STO-APX-2026-01', '2026-08-24', '2026-08-24', 'Apex Internal Shuttling Fleet', 'TRK-INT-02', 'TRACK-STO-9912', 24000.0, 'IN_TRANSIT')
                """,
                (apex["id"], wh_apx_1["id"], wh_apx_2["id"])
            )
            sto_1 = db.query_one("SELECT id FROM inv_stock_transfers WHERE transfer_number = 'STO-APX-2026-01'")
            if sto_1:
                db.execute(
                    """
                    INSERT INTO inv_transfer_items (transfer_id, item_id, transfer_qty, received_qty, unit_cost, line_total)
                    VALUES (?, ?, 200.0, 0.0, 120.0, 24000.0)
                    """,
                    (sto_1["id"], itm_m8["id"])
                )

        # 10. Physical Cycle Count Adjustments
        if wh_apx_1:
            db.execute(
                """
                INSERT INTO inv_adjustments (company_id, warehouse_id, adjustment_number, adjustment_date, reason_type, total_variance_amount, adjusted_by, status)
                VALUES (?, ?, 'ADJ-APX-2026-01', '2026-08-25', 'CYCLE_COUNT_GAIN', 850.0, 'Marcus Sterling', 'APPROVED')
                """,
                (apex["id"], wh_apx_1["id"])
            )

        # 11. Serialized Warranties Registry
        if itm_aero and itm_pcb:
            warranties = [
                (apex["id"], itm_aero["id"], "SN-AERO-2026-8801", "Boeing Subcontractor Aviation Corp", "SO-APX-8802", "INV-APX-2026-8802", "2026-08-18", "2028-08-18", 24, "ACTIVE"),
                (apex["id"], itm_pcb["id"], "SN-SMT-2026-9901", "Siemens Smart Energy Infrastructure", "SO-APX-8801", "INV-APX-2026-8801", "2026-08-20", "2027-08-20", 12, "ACTIVE"),
            ]
            for w in warranties:
                db.execute(
                    """
                    INSERT INTO inv_warranties (company_id, item_id, serial_number, customer_name, order_ref, invoice_ref, warranty_start_date, warranty_end_date, warranty_months, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    w
                )

        # 12. Multi-Tier e-Approvals Tracking
        if wh_apx_1:
            grn_row = db.query_one("SELECT id FROM inv_grn_headers WHERE grn_number = 'GRN-APX-2026-001'")
            if grn_row:
                approvals = [
                    ("GRN", grn_row["id"], 1, "Tier 1: Quality QA Inspection", "Engr. K. Hasan", "Lead QA Metallurgist", "APPROVED", "Material test certificate compliant with DIN 912 specs", "2026-08-18 11:30:00"),
                    ("GRN", grn_row["id"], 2, "Tier 2: Warehouse Store Inwarding", "Marcus Sterling", "Central Stores Manager", "APPROVED", "Stock placed in Bin BIN-A1-01 and balance updated", "2026-08-18 14:00:00"),
                ]
                for a in approvals:
                    db.execute(
                        """
                        INSERT INTO inv_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments, action_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        a
                    )
        logger.info("Seeded Inventory Master, Transactions, Transfers, Balances & Warranties.")

def seed_fixed_assets_master_and_transactions():
    """Seeds multi-company Fixed Assets Master Data, Capital Assets, Depreciation, and Audits."""
    fa_count = db.query_one("SELECT COUNT(*) AS cnt FROM fa_assets")["cnt"]
    if fa_count == 0:
        companies = db.query("SELECT id, short_code FROM companies ORDER BY code ASC")
        for comp in companies:
            cid = comp["id"]
            code_prefix = comp["short_code"]

            # 1. Seed Asset Groups
            grp_plant_id = str(uuid.uuid4())
            grp_bldg_id = str(uuid.uuid4())
            grp_land_id = str(uuid.uuid4())
            grp_veh_id = str(uuid.uuid4())
            grp_it_id = str(uuid.uuid4())
            grp_furn_id = str(uuid.uuid4())

            groups_data = [
                (grp_plant_id, cid, "GRP-PLANT", "Plant & Heavy Machinery", "TANGIBLE_DEPRECIATING", 1, 10, 10.00, "1500-PLANT", "1505-ACC-PLANT", "6500-DEPR-PLANT"),
                (grp_bldg_id, cid, "GRP-BLDG", "Industrial Buildings & Sheds", "TANGIBLE_DEPRECIATING", 1, 30, 3.33, "1510-BLDG", "1515-ACC-BLDG", "6510-DEPR-BLDG"),
                (grp_land_id, cid, "GRP-LAND", "Freehold Industrial Land Plots", "TANGIBLE_NON_DEPRECIATING", 0, 0, 0.00, "1520-LAND", "N/A", "N/A"),
                (grp_veh_id, cid, "GRP-VEH", "Commercial Fleet & Logistics Trucks", "TANGIBLE_DEPRECIATING", 1, 5, 20.00, "1530-VEH", "1535-ACC-VEH", "6530-DEPR-VEH"),
                (grp_it_id, cid, "GRP-IT", "IT Server Clusters & Datacenter Infrastructure", "TANGIBLE_DEPRECIATING", 1, 4, 25.00, "1540-IT", "1545-ACC-IT", "6540-DEPR-IT"),
                (grp_furn_id, cid, "GRP-FURN", "Corporate Furniture & Executive Fixtures", "TANGIBLE_DEPRECIATING", 1, 7, 14.28, "1550-FURN", "1555-ACC-FURN", "6550-DEPR-FURN"),
            ]
            for g in groups_data:
                db.execute(
                    """
                    INSERT INTO fa_asset_groups (id, company_id, group_code, group_name, asset_type, is_depreciating, default_useful_life_years, default_depr_rate, gl_cost_account, gl_acc_depr_account, gl_depr_expense_account)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    g
                )

            # 2. Seed Locations
            loc1_id = str(uuid.uuid4())
            loc2_id = str(uuid.uuid4())

            db.execute(
                """
                INSERT INTO fa_locations (id, company_id, location_code, location_name, location_type, address, manager_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (loc1_id, cid, f"LOC-{code_prefix}-01", f"{code_prefix} Main Manufacturing Facility", "MANUFACTURING_PLANT", "Plot 14-22, High-Tech Industrial Zone", "Marcus Vance, Plant Director")
            )
            db.execute(
                """
                INSERT INTO fa_locations (id, company_id, location_code, location_name, location_type, address, manager_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (loc2_id, cid, f"LOC-{code_prefix}-02", f"{code_prefix} Logistics Terminal & Yard", "LOGISTICS_DEPOT", "Harbor Gate 4, Port Corridor", "Capt. Tariq Al-Mansoor, Logistics Head")
            )

            # 3. Seed Sub-Locations
            subloc1_id = str(uuid.uuid4())
            subloc2_id = str(uuid.uuid4())

            db.execute(
                """
                INSERT INTO fa_sub_locations (id, location_id, sub_location_code, sub_location_name, floor_or_bay)
                VALUES (?, ?, ?, ?, ?)
                """,
                (subloc1_id, loc1_id, f"BAY-{code_prefix}-A1", "Heavy CNC Milling & Turning Bay 1", "Ground Floor, Section A")
            )
            db.execute(
                """
                INSERT INTO fa_sub_locations (id, location_id, sub_location_code, sub_location_name, floor_or_bay)
                VALUES (?, ?, ?, ?, ?)
                """,
                (subloc2_id, loc1_id, f"SRV-{code_prefix}-01", "Tier-3 Datacenter & Server Room", "Building 2, 2nd Floor")
            )

            # 4. Seed Depreciation Policies
            pol_slm_id = str(uuid.uuid4())
            pol_wdv_id = str(uuid.uuid4())
            pol_none_id = str(uuid.uuid4())

            db.execute(
                """
                INSERT INTO fa_depreciation_policies (id, company_id, policy_code, policy_name, method, useful_life_years, salvage_value_pct, depr_rate)
                VALUES (?, ?, 'POL-SLM-10Y', 'Straight-Line 10 Years (10% Residual)', 'STRAIGHT_LINE', 10, 10.00, 9.00)
                """,
                (pol_slm_id, cid)
            )
            db.execute(
                """
                INSERT INTO fa_depreciation_policies (id, company_id, policy_code, policy_name, method, useful_life_years, salvage_value_pct, depr_rate)
                VALUES (?, ?, 'POL-WDV-20P', 'Reducing Balance WDV 20% Annual', 'REDUCING_BALANCE_WDV', 5, 5.00, 20.00)
                """,
                (pol_wdv_id, cid)
            )
            db.execute(
                """
                INSERT INTO fa_depreciation_policies (id, company_id, policy_code, policy_name, method, useful_life_years, salvage_value_pct, depr_rate)
                VALUES (?, ?, 'POL-NON-DEPR', 'Non-Depreciating Capital Asset Policy', 'NON_DEPRECIATING', 0, 100.00, 0.00)
                """,
                (pol_none_id, cid)
            )

            # 5. Seed Master Capital Assets
            asset1_id = str(uuid.uuid4())
            asset2_id = str(uuid.uuid4())
            asset3_id = str(uuid.uuid4())
            asset4_id = str(uuid.uuid4())

            db.execute(
                """
                INSERT INTO fa_assets (id, company_id, group_id, location_id, sub_location_id, policy_id, asset_tag, asset_name, serial_number, barcode, manufacturer, model_number, purchase_date, capitalization_date, purchase_cost, accumulated_depreciation, net_book_value, custodian_name, department_name, supplier_name, warranty_expiry, insurance_policy_ref, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_SERVICE')
                """,
                (asset1_id, cid, grp_plant_id, loc1_id, subloc1_id, pol_slm_id, f"AST-{code_prefix}-CNC-001", "DMG MORI 5-Axis High-Precision CNC Machining Center", "DMG-2024-88421", f"BC-AST-{code_prefix}-001", "DMG MORI Germany", "DMU 50 3rd Gen", "2024-03-15", "2024-04-01", 385000.00, 77000.00, 308000.00, "Engr. Dieter Mueller", "Precision Machining Division", "DMG MORI Global Distribution GmbH", "2027-03-15", f"INS-ALLIANZ-{code_prefix}-9901")
            )

            db.execute(
                """
                INSERT INTO fa_assets (id, company_id, group_id, location_id, sub_location_id, policy_id, asset_tag, asset_name, serial_number, barcode, manufacturer, model_number, purchase_date, capitalization_date, purchase_cost, accumulated_depreciation, net_book_value, custodian_name, department_name, supplier_name, warranty_expiry, insurance_policy_ref, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_SERVICE')
                """,
                (asset2_id, cid, grp_it_id, loc1_id, subloc2_id, pol_wdv_id, f"AST-{code_prefix}-SRV-001", "Dell PowerEdge R760 Enterprise Server Rack Cluster", "DELL-SRV-901844", f"BC-AST-{code_prefix}-002", "Dell Technologies", "PowerEdge R760 Dual Xeon", "2025-01-10", "2025-01-20", 125000.00, 31250.00, 93750.00, "Liam O'Connor", "Information Technology", "Dell Enterprise Middle East", "2028-01-10", f"INS-ALLIANZ-{code_prefix}-9902")
            )

            db.execute(
                """
                INSERT INTO fa_assets (id, company_id, group_id, location_id, sub_location_id, policy_id, asset_tag, asset_name, serial_number, barcode, manufacturer, model_number, purchase_date, capitalization_date, purchase_cost, accumulated_depreciation, net_book_value, custodian_name, department_name, supplier_name, warranty_expiry, insurance_policy_ref, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_SERVICE')
                """,
                (asset3_id, cid, grp_veh_id, loc2_id, None, pol_wdv_id, f"AST-{code_prefix}-TRK-001", "Mercedes-Benz Actros 3340 Heavy Prime Mover Hauler", "WDB-963403-1L99281", f"BC-AST-{code_prefix}-003", "Daimler Commercial Vehicles", "Actros 3340 6x4", "2024-08-20", "2024-09-01", 165000.00, 49500.00, 115500.00, "Hamad Al-Kaabi", "Logistics & Transport", "Daimler Truck Sales Regional", "2026-08-20", f"INS-ALLIANZ-{code_prefix}-9903")
            )

            db.execute(
                """
                INSERT INTO fa_assets (id, company_id, group_id, location_id, sub_location_id, policy_id, asset_tag, asset_name, serial_number, barcode, manufacturer, model_number, purchase_date, capitalization_date, purchase_cost, accumulated_depreciation, net_book_value, custodian_name, department_name, supplier_name, warranty_expiry, insurance_policy_ref, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IN_SERVICE')
                """,
                (asset4_id, cid, grp_land_id, loc1_id, None, pol_none_id, f"AST-{code_prefix}-LND-001", "Freehold Heavy Industrial Development Land (5.5 Acres)", "DEED-LAND-2023-881", f"BC-AST-{code_prefix}-004", "Govt Industrial Development Authority", "Plot 14-22 Heavy Zone", "2023-05-10", "2023-05-10", 1200000.00, 0.00, 1200000.00, "Corporate Secretariat", "Executive Management", "Ministry of Land Development", "2099-12-31", f"INS-ALLIANZ-{code_prefix}-9904")
            )

            # 6. Seed Capital Asset Inwarding GRN
            grn_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO fa_grn_headers (id, company_id, location_id, grn_number, po_ref, supplier_name, grn_date, received_by, qc_status, total_cost, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, ?, ?, 'CAPEX-PO-2026-0041', 'DMG MORI Global Distribution GmbH', '2026-08-15', 'Engr. Dieter Mueller', 'PASSED_QA_INSPECTION', 385000.00, 'POSTED', 1, 'GL-JV-2026-CAP-001')
                """,
                (grn_id, cid, loc1_id, f"AGRN-{code_prefix}-2026-0001")
            )

            # 7. Seed Asset Transfer
            tr_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO fa_transfers (id, company_id, asset_id, transfer_number, transfer_date, from_location_id, to_location_id, from_custodian, to_custodian, reason, status)
                VALUES (?, ?, ?, ?, '2026-07-10', ?, ?, ?, ?, ?, 'COMPLETED')
                """,
                (tr_id, cid, asset2_id, f"ATRN-{code_prefix}-2026-0001", loc2_id, loc1_id, "Liam O'Connor", "Engr. Kevin Vance", "Relocated server compute nodes to Primary Datacenter Bay")
            )

            # 8. Seed Asset Disposal Log
            dsp_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO fa_disposals (id, company_id, asset_id, disposal_number, disposal_date, disposal_type, disposal_proceeds, original_cost, acc_depr_at_disposal, net_book_value, gain_loss_amount, buyer_name, approved_by, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, ?, ?, '2026-06-25', 'SALE', 125000.00, 165000.00, 49500.00, 115500.00, 9500.00, 'Global Heavy Haulage Logistics LLC', 'Chief Financial Officer', 'POSTED', 1, 'GL-JV-2026-DSP-001')
                """,
                (dsp_id, cid, asset3_id, f"ADSP-{code_prefix}-2026-0001")
            )

            # 9. Seed Depreciation Run
            depr_run_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO fa_depreciation_runs (id, company_id, run_number, period_name, run_date, total_depreciation_amount, total_assets_processed, status, is_gl_posted, gl_journal_ref)
                VALUES (?, ?, ?, 'August 2026 Period Depreciation', '2026-08-31', 8458.33, 3, 'POSTED', 1, 'GL-JV-2026-DPR-001')
                """,
                (depr_run_id, cid, f"DEPR-{code_prefix}-2026-M08")
            )

            # 10. Seed Depreciation Itemized Lines
            db.execute(
                """
                INSERT INTO fa_depreciation_lines (run_id, asset_id, opening_cost, opening_acc_depr, period_depreciation, closing_acc_depr, closing_nbv)
                VALUES (?, ?, 385000.00, 73791.67, 3208.33, 77000.00, 308000.00)
                """,
                (depr_run_id, asset1_id)
            )

            # 11. Seed Physical Verification Audit
            aud_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO fa_physical_audits (id, company_id, location_id, audit_number, audit_date, auditor_name, total_audited, found_count, missing_count, damaged_count, status)
                VALUES (?, ?, ?, ?, '2026-08-28', 'Alexander Vance, Internal Asset Controller', 42, 42, 0, 0, 'VERIFIED')
                """,
                (aud_id, cid, loc1_id, f"AUD-{code_prefix}-2026-Q3")
            )

            # 12. Seed Approvals
            approvals = [
                ("ASSET_GRN", grn_id, 1, "Tier 1: Engineering Technical Acceptance", "Engr. Dieter Mueller", "Lead Plant Engineer", "APPROVED", "CNC DMG MORI geometric laser alignment certified and operational", "2026-08-15 14:30:00"),
                ("ASSET_GRN", grn_id, 2, "Tier 2: CFO Capex Capitalization", "CFO / Finance Controller", "Chief Financial Officer", "APPROVED", "Approved for capitalization under Asset Code 1500-PLANT", "2026-08-16 09:15:00"),
            ]
            for a in approvals:
                db.execute(
                    """
                    INSERT INTO fa_approvals (entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments, action_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    a
                )
        logger.info("Seeded Fixed Assets Master, Capital Assets, Depreciation Runs, Audits & Approvals.")

def seed_hr_master_and_transactions():
    """Seeds multi-company Human Resources & Payroll Master Data, Employees, Attendance, Loans, Tax, and Payroll Runs."""
    hr_count = db.query_one("SELECT COUNT(*) AS cnt FROM hr_employees")["cnt"]
    if hr_count == 0:
        companies = db.query("SELECT id, short_code FROM companies ORDER BY code ASC")
        for comp in companies:
            cid = comp["id"]
            code_prefix = comp["short_code"]

            # 1. Seed Grades
            grd1_id = str(uuid.uuid4())
            grd2_id = str(uuid.uuid4())
            grd3_id = str(uuid.uuid4())
            grd4_id = str(uuid.uuid4())
            grd5_id = str(uuid.uuid4())
            grd6_id = str(uuid.uuid4())

            grades = [
                (grd1_id, cid, f"GRD-{code_prefix}-01", "Executive Leadership & Directors", 1, 10000.00, 25000.00, 25.0, 10.0, 10.0),
                (grd2_id, cid, f"GRD-{code_prefix}-02", "Senior Management & Principal Architects", 2, 7000.00, 14000.00, 25.0, 10.0, 10.0),
                (grd3_id, cid, f"GRD-{code_prefix}-03", "Mid-Level Engineers & Senior Specialists", 3, 4500.00, 8500.00, 25.0, 10.0, 10.0),
                (grd4_id, cid, f"GRD-{code_prefix}-04", "Junior Staff & Engineering Associates", 4, 3000.00, 5500.00, 25.0, 10.0, 10.0),
                (grd5_id, cid, f"GRD-{code_prefix}-05", "Technical Plant Operators & CNC Machinists", 5, 2200.00, 4200.00, 25.0, 10.0, 10.0),
                (grd6_id, cid, f"GRD-{code_prefix}-06", "Apprentices, Trainees & Casual Labor", 6, 1500.00, 2600.00, 25.0, 10.0, 10.0),
            ]
            for g in grades:
                db.execute(
                    """
                    INSERT INTO hr_grades (id, company_id, grade_code, grade_name, rank_level, min_basic_salary, max_basic_salary, hra_pct, medical_pct, conveyance_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    g
                )

            # 2. Seed Departments
            dept_eng_id = str(uuid.uuid4())
            dept_plt_id = str(uuid.uuid4())
            dept_fin_id = str(uuid.uuid4())
            dept_scm_id = str(uuid.uuid4())
            dept_qc_id = str(uuid.uuid4())
            dept_hr_id = str(uuid.uuid4())

            depts = [
                (dept_eng_id, cid, f"DPT-{code_prefix}-ENG", "Advanced Engineering & Automation", f"CC-{code_prefix}-ENG", "Dr. Hans Zimmer, VP Engineering", f"{code_prefix} Innovation Wing"),
                (dept_plt_id, cid, f"DPT-{code_prefix}-PLT", "Heavy Plant Operations & Fabrication", f"CC-{code_prefix}-PLT", "Marcus Vance, Plant Director", f"{code_prefix} Main Works Floor"),
                (dept_fin_id, cid, f"DPT-{code_prefix}-FIN", "Finance, Tax & Treasury Control", f"CC-{code_prefix}-FIN", "Elena Rostova, Chief Financial Officer", f"{code_prefix} Corporate HQ Fl 4"),
                (dept_scm_id, cid, f"DPT-{code_prefix}-SCM", "Global Supply Chain & Logistics", f"CC-{code_prefix}-SCM", "Capt. Tariq Al-Mansoor", f"{code_prefix} Logistics Terminal Berth 4"),
                (dept_qc_id, cid, f"DPT-{code_prefix}-QC", "Metallurgy & QA Certification", f"CC-{code_prefix}-QC", "Engr. Kevin Vance", f"{code_prefix} Testing Lab 02"),
                (dept_hr_id, cid, f"DPT-{code_prefix}-HR", "Human Resources & Administration", f"CC-{code_prefix}-HR", "Sarah Jenkins, HR Director", f"{code_prefix} Corporate HQ Fl 3"),
            ]
            for d in depts:
                db.execute(
                    """
                    INSERT INTO hr_departments (id, company_id, dept_code, dept_name, cost_center_code, head_of_dept, location_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    d
                )

            # 3. Seed Designations
            desig_arch_id = str(uuid.uuid4())
            desig_eng_id = str(uuid.uuid4())
            desig_ctrl_id = str(uuid.uuid4())
            desig_mach_id = str(uuid.uuid4())
            desig_hr_id = str(uuid.uuid4())

            desigs = [
                (desig_arch_id, dept_eng_id, f"DSG-{code_prefix}-01", "Principal Systems Architect", "EXECUTIVE_LEAD"),
                (desig_eng_id, dept_plt_id, f"DSG-{code_prefix}-02", "Lead Plant Operations Engineer", "SENIOR_PROFESSIONAL"),
                (desig_ctrl_id, dept_fin_id, f"DSG-{code_prefix}-03", "Senior Financial Controller", "SENIOR_PROFESSIONAL"),
                (desig_mach_id, dept_plt_id, f"DSG-{code_prefix}-04", "Senior 5-Axis CNC Precision Machinist", "SPECIALIST_OPERATOR"),
                (desig_hr_id, dept_hr_id, f"DSG-{code_prefix}-05", "Senior Talent & Payroll Specialist", "PROFESSIONAL"),
            ]
            for ds in desigs:
                db.execute(
                    """
                    INSERT INTO hr_designations (id, department_id, designation_code, designation_title, skill_level)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    ds
                )

            # 4. Seed Shifts
            shift_gen_id = str(uuid.uuid4())
            shift_morn_id = str(uuid.uuid4())
            shift_ngt_id = str(uuid.uuid4())
            shift_sec_id = str(uuid.uuid4())

            shifts = [
                (shift_gen_id, cid, f"SHF-{code_prefix}-GEN", "Corporate General Shift", "08:00", "17:00", 15, 4.0, 0, 0.00),
                (shift_morn_id, cid, f"SHF-{code_prefix}-MRN", "Plant Production Morning Shift", "07:00", "15:30", 10, 4.0, 0, 0.00),
                (shift_ngt_id, cid, f"SHF-{code_prefix}-NGT", "Heavy Machining Night Shift", "23:00", "07:30", 10, 4.0, 1, 45.00),
                (shift_sec_id, cid, f"SHF-{code_prefix}-SEC", "24/7 Security Shift", "00:00", "23:59", 0, 12.0, 0, 25.00),
            ]
            for s in shifts:
                db.execute(
                    """
                    INSERT INTO hr_shifts (id, company_id, shift_code, shift_name, start_time, end_time, grace_period_mins, half_day_hours, is_night_shift, night_allowance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    s
                )

            # 5. Seed Holidays
            holidays = [
                (cid, "International New Year's Day", "2026-01-01", "PUBLIC_HOLIDAY"),
                (cid, "National Independence & Republic Day", "2026-03-26", "GAZETTED_HOLIDAY"),
                (cid, "Summer Corporate Foundation Day", "2026-06-15", "CORPORATE_OFF_DAY"),
                (cid, "National Autumn Festival", "2026-10-12", "PUBLIC_HOLIDAY"),
                (cid, "Annual Winter Holiday & Year-End Closing", "2026-12-25", "GAZETTED_HOLIDAY"),
            ]
            for h in holidays:
                db.execute(
                    """
                    INSERT INTO hr_holidays (company_id, holiday_name, holiday_date, holiday_type)
                    VALUES (?, ?, ?, ?)
                    """,
                    h
                )

            # 6. Seed Leave Types
            lt_cl_id = str(uuid.uuid4())
            lt_sl_id = str(uuid.uuid4())
            lt_el_id = str(uuid.uuid4())
            lt_mat_id = str(uuid.uuid4())

            leave_types = [
                (lt_cl_id, cid, "LV-CL", "Casual Leave (CL)", 10, 1, 0, 3),
                (lt_sl_id, cid, "LV-SL", "Sick & Medical Leave (SL)", 14, 1, 0, 0),
                (lt_el_id, cid, "LV-EL", "Annual Earned Leave (EL)", 18, 1, 1, 10),
                (lt_mat_id, cid, "LV-MAT", "Maternity Leave", 120, 1, 0, 0),
            ]
            for lt in leave_types:
                db.execute(
                    """
                    INSERT INTO hr_leave_types (id, company_id, leave_code, leave_name, yearly_quota, is_paid, is_encashable, max_carryforward)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    lt
                )

            # 7. Seed Corporate Bank Accounts
            bank1_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO hr_bank_accounts (id, company_id, bank_name, branch_name, account_number, routing_number, currency, is_default)
                VALUES (?, ?, 'Standard Chartered Corporate Banking', 'Industrial Commercial Zone Branch', 'SCB-8890-4412-9901', 'SCBLUS33XXX', 'USD', 1)
                """,
                (bank1_id, cid)
            )

            # 8. Seed Master Employees
            emp1_id = str(uuid.uuid4())
            emp2_id = str(uuid.uuid4())
            emp3_id = str(uuid.uuid4())
            emp4_id = str(uuid.uuid4())

            employees = [
                (emp1_id, cid, dept_eng_id, desig_arch_id, grd1_id, shift_gen_id, f"EMP-{code_prefix}-001", "Alexander", "Vance", f"alex.vance@{code_prefix.lower()}.pyrix.internal", "+1 (555) 902-8811", f"NID-{code_prefix}-001928", f"TIN-{code_prefix}-882199", "Large Taxpayer Unit", "Zone 1 Circle 4", "1985-04-12", "MALE", "O+", "2020-01-15", "PERMANENT", 5750.00, 11500.00, "Standard Chartered Bank", "SCB-7721-0091", "SCBLUS33XXX", "Elena Vance (Spouse)", "+1 (555) 902-8812"),
                (emp2_id, cid, dept_plt_id, desig_eng_id, grd2_id, shift_morn_id, f"EMP-{code_prefix}-002", "Dieter", "Mueller", f"dieter.m@{code_prefix.lower()}.pyrix.internal", "+1 (555) 902-8822", f"NID-{code_prefix}-002844", f"TIN-{code_prefix}-882200", "Manufacturing Circle", "Zone 2 Circle 1", "1982-08-24", "MALE", "A+", "2021-03-01", "PERMANENT", 4100.00, 8200.00, "Citibank Commercial", "CITI-8832-1102", "CITIUS33XXX", "Greta Mueller (Spouse)", "+1 (555) 902-8823"),
                (emp3_id, cid, dept_fin_id, desig_ctrl_id, grd2_id, shift_gen_id, f"EMP-{code_prefix}-003", "Elena", "Rostova", f"elena.r@{code_prefix.lower()}.pyrix.internal", "+1 (555) 902-8833", f"NID-{code_prefix}-003711", f"TIN-{code_prefix}-882201", "Corporate Tax Zone", "Zone 1 Circle 2", "1988-11-19", "FEMALE", "B+", "2022-06-15", "PERMANENT", 3900.00, 7800.00, "Standard Chartered Bank", "SCB-7721-0094", "SCBLUS33XXX", "Mikhail Rostov (Brother)", "+1 (555) 902-8834"),
                (emp4_id, cid, dept_plt_id, desig_mach_id, grd5_id, shift_morn_id, f"EMP-{code_prefix}-004", "Rashid", "Al-Nuaimi", f"rashid.a@{code_prefix.lower()}.pyrix.internal", "+1 (555) 902-8844", f"NID-{code_prefix}-004922", f"TIN-{code_prefix}-882202", "Industrial District Circle", "Zone 3 Circle 6", "1994-02-10", "MALE", "AB+", "2023-09-01", "PERMANENT", 2250.00, 4500.00, "HSBC Bank Middle East", "HSBC-4491-8822", "HSBCUS33XXX", "Fatima Al-Nuaimi (Mother)", "+1 (555) 902-8845"),
            ]
            for emp in employees:
                db.execute(
                    """
                    INSERT INTO hr_employees (id, company_id, department_id, designation_id, grade_id, shift_id, employee_code, first_name, last_name, email, phone, national_id, tin_number, tax_zone, tax_circle, date_of_birth, gender, blood_group, joining_date, employment_status, basic_salary, gross_salary, bank_name, bank_account_number, bank_routing_number, emergency_contact_name, emergency_contact_phone, is_pf_member)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    emp
                )

            # 9. Seed Contract / Casual Workers
            contract_workers = [
                (cid, dept_plt_id, f"CW-{code_prefix}-01", "Marco Rossi", "Apex Global Manpower Services", "DAILY_WAGE", 110.00, "2026-01-01", "2026-12-31"),
                (cid, dept_plt_id, f"CW-{code_prefix}-02", "Cheng Wei", "Apex Global Manpower Services", "PIECE_RATE", 95.00, "2026-01-01", "2026-12-31"),
                (cid, dept_scm_id, f"CW-{code_prefix}-03", "Ahmed Al-Fassi", "SecureForce Guard Services", "SECURITY_GUARD", 85.00, "2026-01-01", "2026-12-31"),
            ]
            for cw in contract_workers:
                db.execute(
                    """
                    INSERT INTO hr_contract_workers (company_id, department_id, worker_code, worker_name, contractor_agency, worker_type, daily_rate, contract_start_date, contract_end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    cw
                )

            # 10. Seed Document Vault
            docs = [
                (emp1_id, "Executive Employment Agreement", "CONTRACT", f"DOC-{code_prefix}-EMP001-CTR", "2020-01-15", "2030-01-15", "VERIFIED", "HR Compliance Board"),
                (emp1_id, "National ID Card Verification", "NATIONAL_ID", f"DOC-{code_prefix}-EMP001-NID", "2020-01-10", "2035-01-10", "VERIFIED", "Govt ID Registry"),
                (emp2_id, "Master of Science in Mechanical Metallurgy", "ACADEMIC_DEGREE", f"DOC-{code_prefix}-EMP002-DEG", "2008-07-20", None, "VERIFIED", "University Registrar"),
            ]
            for doc in docs:
                db.execute(
                    """
                    INSERT INTO hr_documents (employee_id, doc_title, doc_type, doc_file_ref, issue_date, expiry_date, verification_status, verified_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    doc
                )

            # 11. Seed Employee Transfers
            db.execute(
                """
                INSERT INTO hr_transfers (company_id, employee_id, transfer_number, transfer_date, transfer_type, from_dept_id, to_dept_id, from_designation_id, to_designation_id, previous_salary, revised_salary, reason, approved_by)
                VALUES (?, ?, ?, '2026-06-01', 'PROMOTION_AND_TRANSFER', ?, ?, ?, ?, 7500.00, 8200.00, 'Promoted to Lead Plant Operations Engineer with relocation to Main Facility', 'Board of Directors')
                """,
                (cid, emp2_id, f"TRF-{code_prefix}-2026-0001", dept_eng_id, dept_plt_id, desig_eng_id, desig_eng_id)
            )

            # 12. Seed Recruitment Requisition & Candidate
            req_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO hr_job_requisitions (id, company_id, department_id, requisition_number, position_title, vacancies_count, experience_years_required, budgeted_salary, target_joining_date, justification, status)
                VALUES (?, ?, ?, ?, 'Senior Metallurgy QC Inspection Specialist', 2, 5, 6500.00, '2026-10-01', 'Required for new DIN 912 aerospace titanium turbine alloy inspection line', 'APPROVED')
                """,
                (req_id, cid, dept_qc_id, f"REQ-{code_prefix}-2026-0042")
            )

            db.execute(
                """
                INSERT INTO hr_candidates (requisition_id, candidate_name, email, phone, years_of_experience, key_skills, expected_salary, interview_score, interview_feedback, hiring_status, applied_date)
                VALUES (?, 'Engr. Viktor Frank', 'viktor.frank@talent-pool.internal', '+1 (555) 919-4411', 6.5, 'X-Ray Fluorescence, Ultrasonic Flaw Detection, DIN 912 Specs', 6200.00, 94.50, 'Exceptional technical depth in non-destructive testing and metallurgy.', 'SELECTED_FOR_OFFER', '2026-08-10')
                """,
                (req_id,)
            )

            # 13. Seed Loan Types & Active Loan
            lt_pers_id = str(uuid.uuid4())
            lt_veh_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO hr_loan_types (id, company_id, loan_type_code, loan_type_name, max_loan_limit, max_installments, interest_rate_pct)
                VALUES (?, ?, 'LN-EMERGENCY', 'Staff Emergency Personal Loan', 5000.00, 12, 0.00)
                """,
                (lt_pers_id, cid)
            )
            db.execute(
                """
                INSERT INTO hr_loan_types (id, company_id, loan_type_code, loan_type_name, max_loan_limit, max_installments, interest_rate_pct)
                VALUES (?, ?, 'LN-VEHICLE', 'Company Vehicle Purchase Advance', 20000.00, 36, 3.50)
                """,
                (lt_veh_id, cid)
            )

            loan_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO hr_loans (id, company_id, employee_id, loan_type_id, loan_number, principal_amount, interest_rate_pct, tenure_months, monthly_emi, disbursement_date, repayment_start_month, total_paid_amount, outstanding_balance, status, gl_voucher_ref)
                VALUES (?, ?, ?, ?, ?, 6000.00, 0.00, 12, 500.00, '2026-05-15', '2026-06', 1500.00, 4500.00, 'ACTIVE', 'GL-JV-2026-LN-001')
                """,
                (loan_id, cid, emp2_id, lt_pers_id, f"LN-{code_prefix}-2026-001")
            )

            # 14. Seed Tax Slabs & Tax Deposit
            tax_slabs = [
                (cid, "FY 2026-2027", 1, "First $350,000 Annual Tax-Free Bracket", 350000.00, 0.00),
                (cid, "FY 2026-2027", 2, "Next $100,000 at 5% Progressive Rate", 100000.00, 5.00),
                (cid, "FY 2026-2027", 3, "Next $300,000 at 10% Progressive Rate", 300000.00, 10.00),
                (cid, "FY 2026-2027", 4, "Next $400,000 at 15% Progressive Rate", 400000.00, 15.00),
                (cid, "FY 2026-2027", 5, "Balance above $1,150,000 at 20% Top Slab", 99999999.00, 20.00),
            ]
            for ts in tax_slabs:
                db.execute(
                    """
                    INSERT INTO hr_tax_slabs (company_id, fiscal_year, slab_order, slab_description, slab_limit, tax_rate_pct)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    ts
                )

            db.execute(
                """
                INSERT INTO hr_tax_deposits (company_id, deposit_month, challan_number, challan_date, depository_bank, total_tax_deposited, employees_covered_count, gl_voucher_ref, status)
                VALUES (?, 'August 2026', ?, '2026-08-31', 'Federal Treasury Depository Bank', 16420.00, 4, 'GL-JV-2026-TAX-001', 'VERIFIED_BY_TREASURY')
                """,
                (cid, f"CHL-{code_prefix}-2026-08")
            )

            # 15. Seed Attendance Logs
            att_records = [
                (cid, emp1_id, "2026-08-31", "08:02", "17:15", "PRESENT", 0, 0, 0.0, "On-time biometric clock-in"),
                (cid, emp2_id, "2026-08-31", "06:58", "15:35", "PRESENT", 0, 0, 0.0, "Morning shift on-time"),
                (cid, emp3_id, "2026-08-31", "08:14", "17:30", "PRESENT", 0, 0, 0.0, "Within 15-min grace window"),
                (cid, emp4_id, "2026-08-31", "06:55", "17:30", "PRESENT", 0, 0, 2.0, "Completed 2.0 hours approved Overtime"),
            ]
            for att in att_records:
                db.execute(
                    """
                    INSERT INTO hr_attendance_logs (company_id, employee_id, attendance_date, clock_in_time, clock_out_time, attendance_status, is_late, late_minutes, overtime_hours, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    att
                )

            # 16. Seed Leave Application
            db.execute(
                """
                INSERT INTO hr_leave_applications (company_id, employee_id, leave_type_id, application_number, start_date, end_date, leave_days, reason, approver_name, status)
                VALUES (?, ?, ?, ?, '2026-08-18', '2026-08-19', 2, 'Personal urgent family commitment', 'Marcus Vance, Plant Director', 'APPROVED')
                """,
                (cid, emp2_id, lt_cl_id, f"LA-{code_prefix}-2026-0012")
            )

            # 17. Seed Overtime Record
            db.execute(
                """
                INSERT INTO hr_overtime_records (company_id, employee_id, ot_date, ot_hours, hourly_rate, multiplier_factor, total_ot_amount, supervisor_name, status)
                VALUES (?, ?, '2026-08-31', 16.0, 25.00, 1.5, 600.00, 'Engr. Dieter Mueller', 'APPROVED')
                """,
                (cid, emp4_id)
            )

            # 18. Seed Monthly Payroll Run & Payslips
            pay_run_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO hr_payroll_runs (id, company_id, payroll_batch_number, period_month, fiscal_year, run_date, total_employees_processed, total_gross_payout, total_deductions, total_net_payout, status, is_gl_posted, gl_journal_ref, bank_advice_locked)
                VALUES (?, ?, ?, 'August 2026', 'FY 2026-2027', '2026-08-31', 4, 32600.00, 5280.00, 27320.00, 'POSTED', 1, 'GL-JV-2026-PAY-001', 1)
                """,
                (pay_run_id, cid, f"PAY-{code_prefix}-2026-M08")
            )

            # 4 Payslips
            payslips = [
                (pay_run_id, emp1_id, f"PS-{code_prefix}-202608-001", 5750.00, 2875.00, 1150.00, 1150.00, 575.00, 0.00, 0.00, 11500.00, 479.00, 479.00, 1150.00, 0.00, 0.00, 1629.00, 9871.00, "SCB-7721-0091"),
                (pay_run_id, emp2_id, f"PS-{code_prefix}-202608-002", 4100.00, 2050.00, 820.00, 820.00, 410.00, 0.00, 0.00, 8200.00, 341.50, 341.50, 620.00, 500.00, 0.00, 1461.50, 6738.50, "CITI-8832-1102"),
                (pay_run_id, emp3_id, f"PS-{code_prefix}-202608-003", 3900.00, 1950.00, 780.00, 780.00, 390.00, 0.00, 0.00, 7800.00, 324.87, 324.87, 580.00, 0.00, 0.00, 904.87, 6895.13, "SCB-7721-0094"),
                (pay_run_id, emp4_id, f"PS-{code_prefix}-202608-004", 2250.00, 1125.00, 450.00, 450.00, 225.00, 600.00, 0.00, 5100.00, 187.42, 187.42, 220.00, 0.00, 0.00, 407.42, 4692.58, "HSBC-4491-8822"),
            ]
            for ps in payslips:
                db.execute(
                    """
                    INSERT INTO hr_payslips (payroll_run_id, employee_id, payslip_number, basic_salary, house_rent_allowance, medical_allowance, conveyance_allowance, special_allowance, overtime_pay, bonus_amount, gross_earnings, pf_employee_deduction, pf_employer_matching, income_tax_deduction, loan_emi_deduction, late_penalty_deduction, total_deductions, net_salary_payable, bank_account_number, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PAID')
                    """,
                    ps
                )
        logger.info("Seeded Human Resources Master, Employees, Attendance, Loans, Tax & Payroll Runs.")


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


def seed_prod_master_and_transactions():
    """Seeds multi-company Production Master, Plants, Resources, Routings, BOMs, Orders, Job Cards & QC."""
    proc_cnt = db.query_one("SELECT COUNT(*) AS cnt FROM prod_processes")["cnt"]
    if proc_cnt == 0:
        processes = [
            ("PROC-CUT-01", "Precision Laser & Plasma Cutting", "FABRICATION", 10, "CC-PRD-CUT", "CNC Fiber laser cutting and sheet metal profiling"),
            ("PROC-MCH-02", "5-Axis High-Speed CNC Machining", "MACHINING", 20, "CC-PRD-CNC", "Milling, turning, contouring, and boring tolerances within +/- 5 microns"),
            ("PROC-WLD-03", "Robotic Arc & TIG Welding", "FABRICATION", 30, "CC-PRD-WLD", "Automated multi-pass structural weld with Argon shielding"),
            ("PROC-COAT-04", "Electrostatic Powder Coating & Anodizing", "SURFACE_FINISH", 40, "CC-PRD-FIN", "Anti-corrosion pre-treatment and thermal powder cure"),
            ("PROC-ASY-05", "Sub-Assembly & Modular Kitting", "ASSEMBLY", 50, "CC-PRD-ASY", "Mechanical and electronic sub-component assembly"),
            ("PROC-QC-06", "High-Precision Coordinate QA Inspection", "QUALITY_TESTING", 60, "CC-PRD-QC", "CMM 3D laser scanning, hardness test & ultrasonic non-destructive testing"),
            ("PROC-BOX-07", "Final Enclosure Assembly & Packaging", "ASSEMBLY", 70, "CC-PRD-BOX", "Final product boxing, serial labeling & anti-static dispatch prep"),
        ]
        for p in processes:
            db.execute(
                """
                INSERT INTO prod_processes (process_code, process_name, stage_type, sequence_order, default_cost_center, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                p
            )
        logger.info("Seeded 7 Production Manufacturing Processes.")

    prod_order_cnt = db.query_one("SELECT COUNT(*) AS cnt FROM prod_orders")["cnt"]
    if prod_order_cnt == 0:
        companies = db.query("SELECT id, short_code FROM companies ORDER BY sort_order")
        item_rows = db.query("SELECT TOP 5 id, item_code, item_name, standard_cost FROM inv_items ORDER BY item_code")
        wh_rows = db.query("SELECT TOP 2 id, warehouse_code FROM inv_warehouses ORDER BY code")
        
        fg_item_id = item_rows[0]["id"] if item_rows else None
        comp_item1_id = item_rows[1]["id"] if len(item_rows) > 1 else fg_item_id
        comp_item2_id = item_rows[2]["id"] if len(item_rows) > 2 else fg_item_id
        wh_id = wh_rows[0]["id"] if wh_rows else None

        for c in companies:
            cid = str(c["id"])
            code_prefix = c["short_code"]

            # 1. Plants (2 per company)
            plant1_id = str(uuid.uuid4())
            plant2_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_plants (id, company_id, plant_code, plant_name, location, manager_name, total_bays, shift_mode, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 8, '3_SHIFTS_24_7', 1)
                """,
                (plant1_id, cid, f"PLANT-{code_prefix}-01", f"{code_prefix} Advanced Heavy Fabrication Works", "Industrial Zone Sector 4, Bay 1-4", "Eng. Marcus Sterling")
            )
            db.execute(
                """
                INSERT INTO prod_plants (id, company_id, plant_code, plant_name, location, manager_name, total_bays, shift_mode, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 6, '2_SHIFTS_16H', 1)
                """,
                (plant2_id, cid, f"PLANT-{code_prefix}-02", f"{code_prefix} High-Precision CNC & Robotics Plant", "High-Tech Manufacturing Complex B", "Dr. Elena Rostova")
            )

            # 2. Resources / Work Centers (4 per company)
            res1_id = str(uuid.uuid4())
            res2_id = str(uuid.uuid4())
            res3_id = str(uuid.uuid4())
            res4_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_resources (id, company_id, plant_id, resource_code, resource_name, resource_type, hourly_cost_rate, capacity_hours_per_day, efficiency_pct, status, is_active)
                VALUES (?, ?, ?, ?, ?, 'CNC_MACHINE', 145.00, 18.00, 94.50, 'OPERATIONAL', 1)
                """,
                (res1_id, cid, plant2_id, f"WC-{code_prefix}-VMC01", "Mazak Integrex 5-Axis CNC Mill-Turn Center")
            )
            db.execute(
                """
                INSERT INTO prod_resources (id, company_id, plant_id, resource_code, resource_name, resource_type, hourly_cost_rate, capacity_hours_per_day, efficiency_pct, status, is_active)
                VALUES (?, ?, ?, ?, ?, 'ROBOTIC_CELL', 95.00, 20.00, 96.00, 'OPERATIONAL', 1)
                """,
                (res2_id, cid, plant1_id, f"WC-{code_prefix}-ROB02", "KUKA 6-Axis Heavy Robotic Welding Cell")
            )
            db.execute(
                """
                INSERT INTO prod_resources (id, company_id, plant_id, resource_code, resource_name, resource_type, hourly_cost_rate, capacity_hours_per_day, efficiency_pct, status, is_active)
                VALUES (?, ?, ?, ?, ?, 'SURFACE_FINISH', 65.00, 16.00, 91.00, 'OPERATIONAL', 1)
                """,
                (res3_id, cid, plant1_id, f"WC-{code_prefix}-COAT03", "Nordson Automated Electrostatic Powder Coat Line")
            )
            db.execute(
                """
                INSERT INTO prod_resources (id, company_id, plant_id, resource_code, resource_name, resource_type, hourly_cost_rate, capacity_hours_per_day, efficiency_pct, status, is_active)
                VALUES (?, ?, ?, ?, ?, 'QUALITY_TESTING', 110.00, 16.00, 98.00, 'OPERATIONAL', 1)
                """,
                (res4_id, cid, plant2_id, f"WC-{code_prefix}-CMM04", "Zeiss Prismo 3D Coordinate Measuring Machine (CMM)")
            )

            # 3. Capacity Records (4 per company)
            capacity_data = [
                (cid, plant2_id, res1_id, "2026-08", 18.00, 26, 468.00, 420.00, 89.74, "OPTIMAL"),
                (cid, plant1_id, res2_id, "2026-08", 20.00, 26, 520.00, 480.00, 92.31, "HIGH_LOAD"),
                (cid, plant1_id, res3_id, "2026-08", 16.00, 26, 416.00, 310.00, 74.52, "BALANCED"),
                (cid, plant2_id, res4_id, "2026-08", 16.00, 26, 416.00, 395.00, 94.95, "OPTIMAL"),
            ]
            for cap in capacity_data:
                db.execute(
                    """
                    INSERT INTO prod_capacity (company_id, plant_id, resource_id, period_month, shift_hours_per_day, working_days, total_available_hours, planned_load_hours, capacity_utilization_pct, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    cap
                )

            # Process IDs lookup
            proc1_id = db.query_one("SELECT id FROM prod_processes WHERE process_code = 'PROC-MCH-02'")["id"]
            proc2_id = db.query_one("SELECT id FROM prod_processes WHERE process_code = 'PROC-WLD-03'")["id"]
            proc3_id = db.query_one("SELECT id FROM prod_processes WHERE process_code = 'PROC-COAT-04'")["id"]
            proc4_id = db.query_one("SELECT id FROM prod_processes WHERE process_code = 'PROC-QC-06'")["id"]

            # 4. Standard Routings (4 steps for Finished Good)
            rout1_id = str(uuid.uuid4())
            rout2_id = str(uuid.uuid4())
            rout3_id = str(uuid.uuid4())
            rout4_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_routings (id, company_id, routing_code, routing_name, item_id, process_id, resource_id, operation_sequence, operation_description, setup_time_mins, run_time_mins, labor_hours, machine_hours, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 10, '5-Axis Precision Surface Contouring & Boring', 45, 60, 1.75, 1.50, 1)
                """,
                (rout1_id, cid, f"RT-{code_prefix}-01", f"{code_prefix} High-Spec Precision Machining Route", fg_item_id, proc1_id, res1_id)
            )
            db.execute(
                """
                INSERT INTO prod_routings (id, company_id, routing_code, routing_name, item_id, process_id, resource_id, operation_sequence, operation_description, setup_time_mins, run_time_mins, labor_hours, machine_hours, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 20, 'Robotic Shielded Argon Enclosure Welding', 30, 40, 1.25, 1.00, 1)
                """,
                (rout2_id, cid, f"RT-{code_prefix}-02", f"{code_prefix} Structural Enclosure Weld Route", fg_item_id, proc2_id, res2_id)
            )
            db.execute(
                """
                INSERT INTO prod_routings (id, company_id, routing_code, routing_name, item_id, process_id, resource_id, operation_sequence, operation_description, setup_time_mins, run_time_mins, labor_hours, machine_hours, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 30, 'Electrostatic Primer & Thermal Powder Coating', 20, 30, 0.75, 0.50, 1)
                """,
                (rout3_id, cid, f"RT-{code_prefix}-03", f"{code_prefix} Protective Polymer Coating Route", fg_item_id, proc3_id, res3_id)
            )
            db.execute(
                """
                INSERT INTO prod_routings (id, company_id, routing_code, routing_name, item_id, process_id, resource_id, operation_sequence, operation_description, setup_time_mins, run_time_mins, labor_hours, machine_hours, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 40, 'Zeiss 3D CMM Laser Coordinate QA & Defect Sign-off', 15, 20, 0.50, 0.35, 1)
                """,
                (rout4_id, cid, f"RT-{code_prefix}-04", f"{code_prefix} Metrology QA & Certification Route", fg_item_id, proc4_id, res4_id)
            )

            # 5. BOM Header & Items (Standard BOM & Assembly BOM)
            bom_std_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_bom_headers (id, company_id, bom_code, bom_type, item_id, revision_number, base_quantity, uom_code, expected_yield_pct, effective_from, is_approved, is_active)
                VALUES (?, ?, ?, 'STANDARD', ?, 'REV-2.4', 1.0, 'PCS', 98.20, '2026-01-01', 1, 1)
                """,
                (bom_std_id, cid, f"BOM-{code_prefix}-ENG01", fg_item_id)
            )
            db.execute(
                """
                INSERT INTO prod_bom_items (bom_id, component_item_id, quantity, uom_code, scrap_allowance_pct, is_critical, operation_seq, remarks)
                VALUES (?, ?, 2.0, 'BOX', 1.50, 1, 10, 'Titanium carbide cutting tooling & inserts')
                """,
                (bom_std_id, comp_item1_id)
            )
            db.execute(
                """
                INSERT INTO prod_bom_items (bom_id, component_item_id, quantity, uom_code, scrap_allowance_pct, is_critical, operation_seq, remarks)
                VALUES (?, ?, 1.0, 'SET', 2.00, 1, 20, 'Precision aerospace structural bushings set')
                """,
                (bom_std_id, comp_item2_id)
            )

            # Assembly BOM (Fast Kitting)
            bom_asy_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_bom_headers (id, company_id, bom_code, bom_type, item_id, revision_number, base_quantity, uom_code, expected_yield_pct, effective_from, is_approved, is_active)
                VALUES (?, ?, ?, 'ASSEMBLY', ?, 'REV-1.0', 1.0, 'KIT', 99.50, '2026-03-01', 1, 1)
                """,
                (bom_asy_id, cid, f"BOM-{code_prefix}-ASY02", comp_item2_id)
            )
            db.execute(
                """
                INSERT INTO prod_bom_items (bom_id, component_item_id, quantity, uom_code, scrap_allowance_pct, is_critical, operation_seq, remarks)
                VALUES (?, ?, 4.0, 'PCS', 0.50, 1, 50, 'Fastener hardware kit components')
                """,
                (bom_asy_id, comp_item1_id)
            )

            # 6. Production Requisitions (2 per company)
            req1_id = str(uuid.uuid4())
            req2_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_requisitions (id, company_id, requisition_number, demand_source, item_id, requested_qty, required_by_date, priority, requested_by, status)
                VALUES (?, ?, ?, 'SALES_ORDER', ?, 150.0, '2026-09-15', 'URGENT', 'Sales VP Arthur Pendelton', 'APPROVED')
                """,
                (req1_id, cid, f"PRQ-{code_prefix}-2026-001", fg_item_id)
            )
            db.execute(
                """
                INSERT INTO prod_requisitions (id, company_id, requisition_number, demand_source, item_id, requested_qty, required_by_date, priority, requested_by, status)
                VALUES (?, ?, ?, 'BUFFER_STOCK', ?, 80.0, '2026-09-25', 'MEDIUM', 'Inventory Planner Sarah Lin', 'APPROVED')
                """,
                (req2_id, cid, f"PRQ-{code_prefix}-2026-002", comp_item2_id)
            )

            # 7. Production Orders (2 per company: 1 COMPLETED, 1 IN_PROGRESS)
            ord1_id = str(uuid.uuid4())
            ord2_id = str(uuid.uuid4())
            db.execute(
                """
                INSERT INTO prod_orders (id, company_id, plant_id, order_number, requisition_id, item_id, bom_id, planned_qty, completed_qty, scrap_qty, planned_start_date, planned_end_date, actual_start_date, actual_end_date, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, 150.0, 148.0, 2.0, '2026-08-01', '2026-08-20', '2026-08-02', '2026-08-19', 'COMPLETED', 'HIGH')
                """,
                (ord1_id, cid, plant2_id, f"WO-{code_prefix}-2026-001", req1_id, fg_item_id, bom_std_id)
            )
            db.execute(
                """
                INSERT INTO prod_orders (id, company_id, plant_id, order_number, requisition_id, item_id, bom_id, planned_qty, completed_qty, scrap_qty, planned_start_date, planned_end_date, actual_start_date, actual_end_date, status, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, 80.0, 45.0, 1.0, '2026-08-15', '2026-09-05', '2026-08-16', NULL, 'IN_PROGRESS', 'NORMAL')
                """,
                (ord2_id, cid, plant1_id, f"WO-{code_prefix}-2026-002", req2_id, comp_item2_id, bom_asy_id)
            )

            # 8. Shop Floor Job Cards (3 for ord1)
            db.execute(
                """
                INSERT INTO prod_job_cards (order_id, routing_id, resource_id, job_card_number, operation_seq, operation_title, scheduled_hours, actual_hours, planned_qty, completed_qty, rejected_qty, operator_name, status, started_at, completed_at)
                VALUES (?, ?, ?, ?, 10, '5-Axis Precision Surface Contouring & Boring', 24.0, 23.5, 150.0, 150.0, 0.0, 'Viktor Vance (Lead Machinist)', 'COMPLETED', '2026-08-03 08:00', '2026-08-06 17:30')
                """,
                (ord1_id, rout1_id, res1_id, f"JC-{code_prefix}-1001")
            )
            db.execute(
                """
                INSERT INTO prod_job_cards (order_id, routing_id, resource_id, job_card_number, operation_seq, operation_title, scheduled_hours, actual_hours, planned_qty, completed_qty, rejected_qty, operator_name, status, started_at, completed_at)
                VALUES (?, ?, ?, ?, 20, 'Robotic Shielded Argon Enclosure Welding', 18.0, 17.0, 150.0, 149.0, 1.0, 'David Chen (Robotics Tech)', 'COMPLETED', '2026-08-07 08:00', '2026-08-10 16:00')
                """,
                (ord1_id, rout2_id, res2_id, f"JC-{code_prefix}-1002")
            )
            db.execute(
                """
                INSERT INTO prod_job_cards (order_id, routing_id, resource_id, job_card_number, operation_seq, operation_title, scheduled_hours, actual_hours, planned_qty, completed_qty, rejected_qty, operator_name, status, started_at, completed_at)
                VALUES (?, ?, ?, ?, 40, 'Zeiss 3D CMM Laser Coordinate QA & Defect Sign-off', 8.0, 7.5, 149.0, 148.0, 1.0, 'Rachel Adams (Metrologist)', 'COMPLETED', '2026-08-15 09:00', '2026-08-16 17:00')
                """,
                (ord1_id, rout4_id, res4_id, f"JC-{code_prefix}-1003")
            )

            # 9. Materials Requisitions & Issues to WIP
            db.execute(
                """
                INSERT INTO prod_material_issues (company_id, order_id, warehouse_id, issue_number, issue_date, item_id, required_qty, issued_qty, unit_cost, total_cost, issued_by, status)
                VALUES (?, ?, ?, ?, '2026-08-02', ?, 300.0, 300.0, 48.50, 14550.00, 'Warehouse Custodian Jack Miller', 'ISSUED_TO_WIP')
                """,
                (cid, ord1_id, wh_id, f"MRQ-ISS-{code_prefix}-001", comp_item1_id)
            )
            db.execute(
                """
                INSERT INTO prod_material_issues (company_id, order_id, warehouse_id, issue_number, issue_date, item_id, required_qty, issued_qty, unit_cost, total_cost, issued_by, status)
                VALUES (?, ?, ?, ?, '2026-08-02', ?, 150.0, 150.0, 800.00, 120000.00, 'Warehouse Custodian Jack Miller', 'ISSUED_TO_WIP')
                """,
                (cid, ord1_id, wh_id, f"MRQ-ISS-{code_prefix}-002", comp_item2_id)
            )

            # 10. Material-to-Material Conversions & Reversals (2 per company)
            db.execute(
                """
                INSERT INTO prod_conversions (company_id, conversion_number, conversion_type, source_item_id, target_item_id, input_qty, output_qty, conversion_date, unit_cost, total_value, operator_name, remarks, status)
                VALUES (?, ?, 'ASSEMBLY_CONVERSION', ?, ?, 40.0, 10.0, '2026-08-18', 380.00, 3800.00, 'Lead Tech Robert Gray', 'Direct kitted sub-assembly conversion batch for client delivery', 'POSTED')
                """,
                (cid, f"CONV-{code_prefix}-2026-01", comp_item1_id, fg_item_id)
            )
            db.execute(
                """
                INSERT INTO prod_conversions (company_id, conversion_number, conversion_type, source_item_id, target_item_id, input_qty, output_qty, conversion_date, unit_cost, total_value, operator_name, remarks, status)
                VALUES (?, ?, 'ASSEMBLY_REVERSAL_DEKIT', ?, ?, 2.0, 8.0, '2026-08-20', 380.00, 760.00, 'Lead Tech Robert Gray', 'Disassembly of excess test units returning raw hardware to stock', 'POSTED')
                """,
                (cid, f"REV-{code_prefix}-2026-01", fg_item_id, comp_item1_id)
            )

            # 11. Quality Inspections (2 per company)
            db.execute(
                """
                INSERT INTO prod_qc_inspections (company_id, order_id, inspection_number, inspection_stage, sample_size_qty, passed_qty, rejected_qty, defect_category, inspection_date, inspector_name, disposition, status)
                VALUES (?, ?, ?, 'IN_PROCESS', 15.0, 15.0, 0.0, 'NONE_ZERO_DEFECT', '2026-08-08', 'Senior QA Inspector Michael Wu', 'PASSED_TO_NEXT_STAGE', 'APPROVED')
                """,
                (cid, ord1_id, f"QC-{code_prefix}-2026-01")
            )
            db.execute(
                """
                INSERT INTO prod_qc_inspections (company_id, order_id, inspection_number, inspection_stage, sample_size_qty, passed_qty, rejected_qty, defect_category, inspection_date, inspector_name, disposition, status)
                VALUES (?, ?, ?, 'FINAL_INSPECTION', 148.0, 146.0, 2.0, 'MICRO_SURFACE_BLEMISH', '2026-08-17', 'Quality Director Rebecca Vance', 'ACCEPTED_FOR_DISPATCH', 'APPROVED')
                """,
                (cid, ord1_id, f"QC-{code_prefix}-2026-02")
            )

            # 12. Machine Downtime Logs (2 per company)
            db.execute(
                """
                INSERT INTO prod_downtime_logs (company_id, resource_id, log_number, downtime_date, duration_mins, downtime_category, root_cause, technician_name, estimated_cost_loss, status)
                VALUES (?, ?, ?, '2026-08-05', 45, 'TOOLING_CHANGE', 'Scheduled ceramic insert tip replacement and laser recalibration', 'Senior Tech Tom Novak', 108.75, 'RESOLVED')
                """,
                (cid, res1_id, f"DT-{code_prefix}-2026-01")
            )
            db.execute(
                """
                INSERT INTO prod_downtime_logs (company_id, resource_id, log_number, downtime_date, duration_mins, downtime_category, root_cause, technician_name, estimated_cost_loss, status)
                VALUES (?, ?, ?, '2026-08-12', 30, 'PREVENTIVE_MAINT', 'Robot hydraulic actuator fluid flush and seal inspection', 'Field Service Eng. Lucas Brandt', 47.50, 'RESOLVED')
                """,
                (cid, res2_id, f"DT-{code_prefix}-2026-02")
            )

            # 13. Standard vs Actual Cost Records (1 per completed order)
            db.execute(
                """
                INSERT INTO prod_cost_records (company_id, order_id, raw_material_cost, direct_labor_cost, machine_overhead_cost, scrap_variance_cost, total_actual_cost, standard_cost, variance_amount, variance_pct, cost_date, status)
                VALUES (?, ?, 134550.00, 7200.00, 6850.00, 760.00, 149360.00, 148000.00, 1360.00, 0.92, '2026-08-20', 'COMMITTED')
                """,
                (cid, ord1_id)
            )

        logger.info("Seeded Production Master Plants, Resources, Routings, BOMs, Orders, Job Cards & QC.")

def seed_admin_master_and_transactions():
    print("Starting System Administration & Governance seeding...")

    # 1. Global Countries
    existing_countries = db.query("SELECT COUNT(*) AS cnt FROM admin_countries")[0]["cnt"]
    if existing_countries == 0:
        countries_data = [
            ("US", "United States", "+1", "USD", "North America"),
            ("GB", "United Kingdom", "+44", "GBP", "Europe"),
            ("DE", "Germany", "+49", "EUR", "Europe"),
            ("JP", "Japan", "+81", "JPY", "Asia-Pacific"),
            ("SG", "Singapore", "+65", "SGD", "Asia-Pacific"),
            ("BD", "Bangladesh", "+880", "BDT", "South Asia"),
            ("CA", "Canada", "+1", "CAD", "North America"),
            ("AU", "Australia", "+61", "AUD", "Oceania"),
            ("AE", "United Arab Emirates", "+971", "AED", "Middle East"),
        ]
        for code, name, dial, cur, region in countries_data:
            db.execute(
                """
                INSERT INTO admin_countries (id, country_code, country_name, dial_code, currency_code, region, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (str(uuid.uuid4()), code, name, dial, cur, region)
            )
        print("Seeded Global Countries.")

    # 2. Global States
    existing_states = db.query("SELECT COUNT(*) AS cnt FROM admin_states")[0]["cnt"]
    if existing_states == 0:
        states_data = [
            ("US", "CA", "California", "US_WEST_TAX_ZONE"),
            ("US", "NY", "New York", "US_EAST_TAX_ZONE"),
            ("US", "TX", "Texas", "US_SOUTH_TAX_ZONE"),
            ("US", "IL", "Illinois", "US_MIDWEST_TAX_ZONE"),
            ("GB", "ENG", "England", "UK_VAT_STANDARD"),
            ("DE", "BY", "Bavaria", "EU_DE_VAT_19"),
            ("BD", "DH", "Dhaka Division", "BD_NBR_CENTRAL"),
            ("SG", "SG-01", "Central Singapore", "SG_GST_9"),
        ]
        for country_code, state_code, state_name, tax_zone in states_data:
            db.execute(
                """
                INSERT INTO admin_states (id, country_code, state_code, state_name, tax_zone, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (str(uuid.uuid4()), country_code, state_code, state_name, tax_zone)
            )
        print("Seeded Global States.")

    # 3. Global Currencies
    existing_currencies = db.query("SELECT COUNT(*) AS cnt FROM admin_currencies")[0]["cnt"]
    if existing_currencies == 0:
        currencies_data = [
            ("USD", "US Dollar", "$", 2, 1),
            ("EUR", "Euro", "€", 2, 0),
            ("GBP", "British Pound", "£", 2, 0),
            ("JPY", "Japanese Yen", "¥", 0, 0),
            ("SGD", "Singapore Dollar", "S$", 2, 0),
            ("BDT", "Bangladeshi Taka", "৳", 2, 0),
            ("CAD", "Canadian Dollar", "C$", 2, 0),
            ("AUD", "Australian Dollar", "A$", 2, 0),
            ("AED", "UAE Dirham", "AED", 2, 0),
        ]
        for cur_code, name, sym, dec, is_base in currencies_data:
            db.execute(
                """
                INSERT INTO admin_currencies (id, currency_code, currency_name, symbol, decimal_places, is_base_currency, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (str(uuid.uuid4()), cur_code, name, sym, dec, is_base)
            )
        print("Seeded Global Currencies.")

    # 4. Global Roles & Permissions
    existing_roles = db.query("SELECT COUNT(*) AS cnt FROM admin_roles")[0]["cnt"]
    role_map = {}
    if existing_roles == 0:
        roles_data = [
            ("ROLE_SUPER_ADMIN", "Enterprise Super Administrator", "Full unconstrained administrative privileges across all modules", 10, 1),
            ("ROLE_FIN_CONTROLLER", "Chief Financial Controller", "Full authority over General Ledger, AR, AP, Fixed Assets and Period Closures", 8, 1),
            ("ROLE_OPERATIONS_DIR", "Operations & Supply Chain Director", "Executive access to Inventory, Sourcing, and Production Manufacturing", 7, 1),
            ("ROLE_HR_DIRECTOR", "Human Resources Director", "Authority over Employee Profiles, Payroll Runs, and Attendance Records", 6, 1),
            ("ROLE_INTERNAL_AUDITOR", "Statutory Compliance Auditor", "Read-only ledger audit, log inspection, and verification access", 5, 1),
        ]
        for r_code, r_name, desc, level, is_sys in roles_data:
            r_id = str(uuid.uuid4())
            role_map[r_code] = r_id
            db.execute(
                """
                INSERT INTO admin_roles (id, role_code, role_name, description, security_level, is_system_role, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (r_id, r_code, r_name, desc, level, is_sys)
            )

        # Permissions Matrix for Roles
        modules = [
            "system-admin", "general-ledger", "accounts-receivable", "accounts-payable",
            "sales", "inventory", "fixed-assets", "human-resources", "production"
        ]
        for mod in modules:
            # Super Admin: all permissions
            db.execute(
                """
                INSERT INTO admin_role_permissions (id, role_id, module_code, sub_area_code, can_view, can_create, can_edit, can_delete, can_approve, can_export)
                VALUES (?, ?, ?, '*', 1, 1, 1, 1, 1, 1)
                """,
                (str(uuid.uuid4()), role_map["ROLE_SUPER_ADMIN"], mod)
            )
            # Fin Controller: view/edit/approve on financial
            is_fin = mod in ("general-ledger", "accounts-receivable", "accounts-payable", "fixed-assets", "system-admin")
            db.execute(
                """
                INSERT INTO admin_role_permissions (id, role_id, module_code, sub_area_code, can_view, can_create, can_edit, can_delete, can_approve, can_export)
                VALUES (?, ?, ?, '*', 1, ?, ?, 0, ?, 1)
                """,
                (str(uuid.uuid4()), role_map["ROLE_FIN_CONTROLLER"], mod, 1 if is_fin else 0, 1 if is_fin else 0, 1 if is_fin else 0)
            )
            # Auditor: read-only everywhere
            db.execute(
                """
                INSERT INTO admin_role_permissions (id, role_id, module_code, sub_area_code, can_view, can_create, can_edit, can_delete, can_approve, can_export)
                VALUES (?, ?, ?, '*', 1, 0, 0, 0, 0, 1)
                """,
                (str(uuid.uuid4()), role_map["ROLE_INTERNAL_AUDITOR"], mod)
            )
        print("Seeded Global Roles and Permissions Matrix.")
    else:
        for r in db.query("SELECT id, role_code FROM admin_roles"):
            role_map[r["role_code"]] = r["id"]

    # 5. Global Tax Categories
    existing_tax_cat = db.query("SELECT COUNT(*) AS cnt FROM admin_tax_categories")[0]["cnt"]
    tax_cat_map = {}
    if existing_tax_cat == 0:
        tax_categories = [
            ("STANDARD_VAT", "Standard Value Added Tax", "VALUE_ADDED_TAX", 15.00, "Standard rate applied on taxable supplies of goods and services"),
            ("REDUCED_RATE", "Reduced Essential Goods Tax", "VALUE_ADDED_TAX", 5.00, "Concession rate on foodstuffs, medical equipment and basic essentials"),
            ("ZERO_RATED", "Zero-Rated Export Supplies", "ZERO_RATED_TAX", 0.00, "International export supplies and eligible customs free trade zones"),
            ("WITHHOLDING_CORP", "Corporate Vendor Withholding Tax", "WITHHOLDING_TAX", 7.50, "Statutory withholding at source on vendor procurement invoices"),
            ("SERVICE_SALES_TAX", "State / Provincial Sales Tax", "SALES_TAX", 8.25, "State-level consumption and point-of-sale municipal transactions"),
        ]
        for cat_code, cat_name, tax_type, def_rate, desc in tax_categories:
            tc_id = str(uuid.uuid4())
            tax_cat_map[cat_code] = tc_id
            db.execute(
                """
                INSERT INTO admin_tax_categories (id, category_code, category_name, tax_type, default_rate, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (tc_id, cat_code, cat_name, tax_type, def_rate, desc)
            )
        print("Seeded Global Tax Categories.")
    else:
        for tc in db.query("SELECT id, category_code FROM admin_tax_categories"):
            tax_cat_map[tc["category_code"]] = tc["id"]

    # 6. Multi-Company Scoped Data
    companies = db.query("SELECT id, name, short_code, currency FROM companies")
    for comp in companies:
        cid = comp["id"]
        cname = comp["name"]
        c_code = comp["short_code"]
        base_cur = comp["currency"] or "USD"

        # Check if already seeded
        chk = db.query("SELECT COUNT(*) AS cnt FROM admin_company_configs WHERE company_id = ?", (cid,))[0]["cnt"]
        if chk > 0:
            continue

        # 6a. Company Configuration Profile
        db.execute(
            """
            INSERT INTO admin_company_configs (
                id, company_id, registration_no, tax_id, base_currency, fiscal_start_month,
                multi_currency_enabled, address_line1, city, state, postal_code, country,
                phone, email, website, logo_path, default_locale, status
            ) VALUES (
                ?, ?, ?, ?, ?, 4,
                1, ?, 'Metro City', 'CA', '90210', 'United States',
                '+1 (800) 555-0199', ?, ?, '/static/img/brand/logo.svg', 'en_US', 'ACTIVE'
            )
            """,
            (
                str(uuid.uuid4()), cid, f"REG-{c_code}-2024-9988", f"TIN-{c_code}-88776655",
                base_cur, f"Corporate Boulevard, Tech Tower #{c_code}",
                f"admin@{c_code.lower()}-corp.com", f"https://www.{c_code.lower()}-corp.com"
            )
        )

        # 6b. Business Units (3 per company)
        bu1_id = str(uuid.uuid4())
        bu2_id = str(uuid.uuid4())
        bu3_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO admin_business_units (id, company_id, unit_code, unit_name, unit_type, manager_name, location, cost_center_count, is_active)
            VALUES (?, ?, ?, 'Corporate Headquarters & Executive Offices', 'EXECUTIVE_DIVISION', 'Arthur Vance, VP Operations', 'Floor 32, Horizon Plaza', 2, 1)
            """,
            (bu1_id, cid, f"BU-{c_code}-HQ")
        )
        db.execute(
            """
            INSERT INTO admin_business_units (id, company_id, unit_code, unit_name, unit_type, manager_name, location, cost_center_count, is_active)
            VALUES (?, ?, ?, 'Manufacturing & Engineering Operations', 'OPERATING_DIVISION', 'Marcus Vance, Plant Director', 'Industrial Park Bay 4', 3, 1)
            """,
            (bu2_id, cid, f"BU-{c_code}-ENG")
        )
        db.execute(
            """
            INSERT INTO admin_business_units (id, company_id, unit_code, unit_name, unit_type, manager_name, location, cost_center_count, is_active)
            VALUES (?, ?, ?, 'Commercial Sales & Distribution Logistics', 'COMMERCIAL_DIVISION', 'Elena Rostova, Commercial Lead', 'Logistics Terminal Berth 2', 2, 1)
            """,
            (bu3_id, cid, f"BU-{c_code}-SLS")
        )

        # 6c. Cost Centers (linking to business units)
        cc1_id = str(uuid.uuid4())
        cc2_id = str(uuid.uuid4())
        cc3_id = str(uuid.uuid4())
        cc4_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO admin_cost_centers (id, company_id, business_unit_id, cost_center_code, name, department, manager_name, is_profit_center, budget_allocation, is_active)
            VALUES (?, ?, ?, ?, 'Executive Administration & Legal', 'Executive Office', 'Arthur Vance', 0, 450000.00, 1)
            """,
            (cc1_id, cid, bu1_id, f"CC-{c_code}-101")
        )
        db.execute(
            """
            INSERT INTO admin_cost_centers (id, company_id, business_unit_id, cost_center_code, name, department, manager_name, is_profit_center, budget_allocation, is_active)
            VALUES (?, ?, ?, ?, 'Precision CNC & Machining Cell', 'Production Machining', 'Marcus Vance', 1, 1250000.00, 1)
            """,
            (cc2_id, cid, bu2_id, f"CC-{c_code}-201")
        )
        db.execute(
            """
            INSERT INTO admin_cost_centers (id, company_id, business_unit_id, cost_center_code, name, department, manager_name, is_profit_center, budget_allocation, is_active)
            VALUES (?, ?, ?, ?, 'Cleanroom Electronics Assembly', 'SMT Assembly', 'Dr. Aris Thorne', 1, 980000.00, 1)
            """,
            (cc3_id, cid, bu2_id, f"CC-{c_code}-202")
        )
        db.execute(
            """
            INSERT INTO admin_cost_centers (id, company_id, business_unit_id, cost_center_code, name, department, manager_name, is_profit_center, budget_allocation, is_active)
            VALUES (?, ?, ?, ?, 'Global Key Accounts & Dispatch', 'Direct Sales', 'Elena Rostova', 1, 620000.00, 1)
            """,
            (cc4_id, cid, bu3_id, f"CC-{c_code}-301")
        )

        # 6d. Multi-Currency Daily Exchange Rates (USD base)
        exchange_rates = [
            ("EUR", 0.920000, "SPOT_RATE"),
            ("GBP", 0.785000, "SPOT_RATE"),
            ("JPY", 154.250000, "SPOT_RATE"),
            ("SGD", 1.342000, "SPOT_RATE"),
            ("BDT", 119.500000, "SPOT_RATE"),
            ("CAD", 1.365000, "SPOT_RATE"),
            ("AUD", 1.512000, "SPOT_RATE"),
        ]
        for cur, rate, r_type in exchange_rates:
            db.execute(
                """
                INSERT INTO admin_exchange_rates (id, company_id, currency_code, target_currency, exchange_rate, effective_date, rate_type, entered_by)
                VALUES (?, ?, ?, 'USD', ?, '2026-08-01', ?, 'Global Treasury Engine')
                """,
                (str(uuid.uuid4()), cid, cur, rate, r_type)
            )

        # 6e. Fiscal Calendar & 12 Periods (FY 2026-2027)
        cal_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO admin_fiscal_calendars (id, company_id, fiscal_year_name, start_date, end_date, total_periods, is_closed, opening_balance_locked)
            VALUES (?, ?, 'FY 2026-2027', '2026-04-01', '2027-03-31', 12, 0, 1)
            """,
            (cal_id, cid)
        )
        periods = [
            (1, "Period 01 - Apr 2026", "2026-04-01", "2026-04-30", "HARD_CLOSED", "2026-05-02 18:00:00", "Chief Financial Controller"),
            (2, "Period 02 - May 2026", "2026-05-01", "2026-05-31", "HARD_CLOSED", "2026-06-02 17:30:00", "Chief Financial Controller"),
            (3, "Period 03 - Jun 2026", "2026-06-01", "2026-06-30", "HARD_CLOSED", "2026-07-03 19:15:00", "Chief Financial Controller"),
            (4, "Period 04 - Jul 2026", "2026-07-01", "2026-07-31", "SOFT_LOCKED", "2026-08-03 16:45:00", "Chief Financial Controller"),
            (5, "Period 05 - Aug 2026", "2026-08-01", "2026-08-31", "OPEN", None, None),
            (6, "Period 06 - Sep 2026", "2026-09-01", "2026-09-30", "OPEN", None, None),
            (7, "Period 07 - Oct 2026", "2026-10-01", "2026-10-31", "OPEN", None, None),
            (8, "Period 08 - Nov 2026", "2026-11-01", "2026-11-30", "OPEN", None, None),
            (9, "Period 09 - Dec 2026", "2026-12-01", "2026-12-31", "OPEN", None, None),
            (10, "Period 10 - Jan 2027", "2027-01-01", "2027-01-31", "OPEN", None, None),
            (11, "Period 11 - Feb 2027", "2027-02-01", "2027-02-28", "OPEN", None, None),
            (12, "Period 12 - Mar 2027", "2027-03-01", "2027-03-31", "OPEN", None, None),
        ]
        period_ids = []
        for p_num, p_name, s_date, e_date, status, c_at, c_by in periods:
            p_id = str(uuid.uuid4())
            period_ids.append(p_id)
            db.execute(
                """
                INSERT INTO admin_fiscal_periods (id, calendar_id, period_number, period_name, start_date, end_date, status, closed_at, closed_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (p_id, cal_id, p_num, p_name, s_date, e_date, status, c_at, c_by)
            )

        # 6f. Network Print Servers & Letterhead Setup
        db.execute(
            """
            INSERT INTO admin_printers (id, company_id, printer_name, printer_type, ip_address, port, paper_size, default_tray, is_default, is_active)
            VALUES (?, ?, 'Central HP LaserJet Enterprise MFP M725', 'NETWORK_PRINT_SERVER', '192.168.1.180', 9100, 'A4', 'Tray 2 (Letterhead)', 1, 1)
            """,
            (str(uuid.uuid4()), cid)
        )
        db.execute(
            """
            INSERT INTO admin_printers (id, company_id, printer_name, printer_type, ip_address, port, paper_size, default_tray, is_default, is_active)
            VALUES (?, ?, 'Warehouse Zebra ZT411 Thermal Slip Printer', 'THERMAL_RECEIPT_SLIP', '192.168.1.182', 9100, 'ROLL_4INCH', 'Roll Feeder', 0, 1)
            """,
            (str(uuid.uuid4()), cid)
        )
        db.execute(
            """
            INSERT INTO admin_printers (id, company_id, printer_name, printer_type, ip_address, port, paper_size, default_tray, is_default, is_active)
            VALUES (?, ?, 'Pyrix High-Res PDF Virtual Spooler', 'PDF_VIRTUAL_SPOOLER', '127.0.0.1', 631, 'A4', 'Auto-Select', 0, 1)
            """,
            (str(uuid.uuid4()), cid)
        )

        # 6g. Enterprise Users Directory & Data Access Scopes
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())
        user3_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO admin_user_profiles (id, company_id, user_code, full_name, email, phone, role_id, business_unit_id, cost_center_id, avatar_url, mfa_enabled, status, last_login_at)
            VALUES (?, ?, ?, 'Alexander Wright', ?, '+1 (555) 234-5678', ?, ?, ?, '/static/img/avatars/alexander.jpg', 1, 'ACTIVE', '2026-08-25 09:14:22')
            """,
            (user1_id, cid, f"USR-{c_code}-01", f"awright@{c_code.lower()}.com", role_map["ROLE_SUPER_ADMIN"], bu1_id, cc1_id)
        )
        db.execute(
            """
            INSERT INTO admin_user_profiles (id, company_id, user_code, full_name, email, phone, role_id, business_unit_id, cost_center_id, avatar_url, mfa_enabled, status, last_login_at)
            VALUES (?, ?, ?, 'Claire Sterling', ?, '+1 (555) 345-6789', ?, ?, ?, '/static/img/avatars/claire.jpg', 1, 'ACTIVE', '2026-08-24 16:40:11')
            """,
            (user2_id, cid, f"USR-{c_code}-02", f"csterling@{c_code.lower()}.com", role_map["ROLE_FIN_CONTROLLER"], bu1_id, cc1_id)
        )
        db.execute(
            """
            INSERT INTO admin_user_profiles (id, company_id, user_code, full_name, email, phone, role_id, business_unit_id, cost_center_id, avatar_url, mfa_enabled, status, last_login_at)
            VALUES (?, ?, ?, 'Marcus Vance', ?, '+1 (555) 456-7890', ?, ?, ?, '/static/img/avatars/marcus.jpg', 0, 'ACTIVE', '2026-08-25 08:30:00')
            """,
            (user3_id, cid, f"USR-{c_code}-03", f"mvance@{c_code.lower()}.com", role_map["ROLE_OPERATIONS_DIR"], bu2_id, cc2_id)
        )

        # Scopes for Alexander (All units), Claire (HQ & Finance), Marcus (Engineering)
        db.execute(
            """
            INSERT INTO admin_user_data_scopes (id, user_id, scope_type, entity_id, entity_name, access_mode)
            VALUES (?, ?, 'SUBSIDIARY_ALL', ?, ?, 'READ_WRITE')
            """,
            (str(uuid.uuid4()), user1_id, cid, cname)
        )
        db.execute(
            """
            INSERT INTO admin_user_data_scopes (id, user_id, scope_type, entity_id, entity_name, access_mode)
            VALUES (?, ?, 'BUSINESS_UNIT', ?, 'Corporate Headquarters & Executive Offices', 'READ_WRITE')
            """,
            (str(uuid.uuid4()), user2_id, bu1_id)
        )
        db.execute(
            """
            INSERT INTO admin_user_data_scopes (id, user_id, scope_type, entity_id, entity_name, access_mode)
            VALUES (?, ?, 'COST_CENTER', ?, 'Precision CNC & Machining Cell', 'READ_WRITE')
            """,
            (str(uuid.uuid4()), user3_id, cc2_id)
        )

        # 6h. Tax Authorities & Tax Profiles
        auth1_id = str(uuid.uuid4())
        auth2_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO admin_tax_authorities (id, company_id, authority_code, authority_name, jurisdiction, tax_office, contact_person, phone, reporting_cycle, is_active)
            VALUES (?, ?, ?, 'Internal Revenue Service (Federal Large Business Division)', 'Federal Jurisdiction', 'Ogden Service Center, UT 84201', 'Tax Compliance Officer', '+1 (800) 829-4933', 'QUARTERLY', 1)
            """,
            (auth1_id, cid, f"TAX-AUTH-{c_code}-FED")
        )
        db.execute(
            """
            INSERT INTO admin_tax_authorities (id, company_id, authority_code, authority_name, jurisdiction, tax_office, contact_person, phone, reporting_cycle, is_active)
            VALUES (?, ?, ?, 'State Department of Revenue & Taxation', 'State Jurisdiction', 'Sacramento District Office', 'Revenue Inspector', '+1 (800) 400-7115', 'MONTHLY', 1)
            """,
            (auth2_id, cid, f"TAX-AUTH-{c_code}-STE")
        )

        # Tax Profiles
        db.execute(
            """
            INSERT INTO admin_tax_profiles (id, company_id, profile_code, profile_name, category_id, authority_id, rate_percent, gl_account_code, is_recoverable, effective_date, status)
            VALUES (?, ?, ?, 'Standard Enterprise Goods VAT 15%', ?, ?, 15.00, '2150-TAX-PAYABLE-VAT', 1, '2026-04-01', 'ACTIVE')
            """,
            (str(uuid.uuid4()), cid, f"TP-{c_code}-VAT15", tax_cat_map["STANDARD_VAT"], auth1_id)
        )
        db.execute(
            """
            INSERT INTO admin_tax_profiles (id, company_id, profile_code, profile_name, category_id, authority_id, rate_percent, gl_account_code, is_recoverable, effective_date, status)
            VALUES (?, ?, ?, 'Commercial Procurement Withholding 7.5%', ?, ?, 7.50, '2160-TAX-WITHHOLDING', 0, '2026-04-01', 'ACTIVE')
            """,
            (str(uuid.uuid4()), cid, f"TP-{c_code}-WHT75", tax_cat_map["WITHHOLDING_CORP"], auth1_id)
        )
        db.execute(
            """
            INSERT INTO admin_tax_profiles (id, company_id, profile_code, profile_name, category_id, authority_id, rate_percent, gl_account_code, is_recoverable, effective_date, status)
            VALUES (?, ?, ?, 'Zero-Rated Export Sales & Free Trade Zone', ?, ?, 0.00, '2170-TAX-EXEMPT-SALES', 1, '2026-04-01', 'ACTIVE')
            """,
            (str(uuid.uuid4()), cid, f"TP-{c_code}-ZERO", tax_cat_map["ZERO_RATED"], auth2_id)
        )

        # 6i. Periodic Closures (Month-end closures for Period 1, 2, 3)
        close_modules = [
            ("CASH", "Cash & Bank Sub-Ledger Reconciliation", 1845200.50),
            ("AR", "Accounts Receivable Customer Ledger Close", 3420800.00),
            ("AP", "Accounts Payable Supplier Ledger Close", 2980450.00),
            ("INVENTORY", "Sales & Inventory Perpetual Valuation Close", 5460200.00),
            ("PAYROLL", "Gross Payroll, Statutory Deductions & Net Disbursals", 420500.00),
            ("FIXED_ASSETS", "Fixed Assets Monthly Depreciation Amortization Run", 168400.00),
        ]
        for m_code, m_name, bal in close_modules:
            db.execute(
                """
                INSERT INTO admin_periodic_closures (id, company_id, fiscal_period_id, module_code, module_name, closing_date, closed_by, status, reconciliation_notes, verified_balance)
                VALUES (?, ?, ?, ?, ?, '2026-06-30', 'Claire Sterling, Financial Controller', 'CLOSED_VERIFIED', 'All sub-ledger control accounts matched 100% against General Ledger trial balance.', ?)
                """,
                (str(uuid.uuid4()), cid, period_ids[2], m_code, m_name, bal)
            )

        # 6j. Database Integrity Scans
        db.execute(
            """
            INSERT INTO admin_integrity_scans (id, company_id, scan_type, scan_title, items_checked, anomalies_found, auto_repaired, scan_status, scan_duration_ms, log_details)
            VALUES (?, ?, 'FULL_DATABASE_INTEGRITY', 'Weekly Automated Database Integrity & Parity Scan', 18420, 0, 0, 'CLEAN_VERIFIED', 1420, 'Checked 18,420 relational integrity constraints across GL, AR, AP, Inventory, Assets and HR. 0 orphan records found. 100% foreign key parity.')
            """,
            (str(uuid.uuid4()), cid)
        )
        db.execute(
            """
            INSERT INTO admin_integrity_scans (id, company_id, scan_type, scan_title, items_checked, anomalies_found, auto_repaired, scan_status, scan_duration_ms, log_details)
            VALUES (?, ?, 'BALANCE_RECALCULATION', 'General Ledger & Sub-Ledger Balance Recalculation', 4210, 0, 0, 'CLEAN_VERIFIED', 850, 'Recalculated customer AR balances, vendor AP open vouchers and perpetual inventory FIFO lots. Ledgers in perfect equilibrium.')
            """,
            (str(uuid.uuid4()), cid)
        )

        # 6k. Tamper-Evident Audit Vault
        db.execute(
            """
            INSERT INTO admin_audit_vault (id, company_id, event_timestamp, user_name, user_ip, event_action, module_code, entity_name, record_ref, change_details, security_severity)
            VALUES (?, ?, '2026-08-25 09:15:04', 'Alexander Wright', '192.168.1.10', 'AUTHENTICATION', 'system-admin', 'UserSession', 'SES-98214', 'Multi-factor biometric MFA token validated for Enterprise Super Admin.', 'INFO')
            """,
            (str(uuid.uuid4()), cid)
        )
        db.execute(
            """
            INSERT INTO admin_audit_vault (id, company_id, event_timestamp, user_name, user_ip, event_action, module_code, entity_name, record_ref, change_details, security_severity)
            VALUES (?, ?, '2026-08-24 17:02:11', 'Claire Sterling', '192.168.1.15', 'PERIOD_LOCK', 'system-admin', 'FiscalPeriod', 'Period 03 - Jun 2026', 'Soft lock applied to Period 03 pending final external auditor signoff.', 'WARNING')
            """,
            (str(uuid.uuid4()), cid)
        )
        db.execute(
            """
            INSERT INTO admin_audit_vault (id, company_id, event_timestamp, user_name, user_ip, event_action, module_code, entity_name, record_ref, change_details, security_severity)
            VALUES (?, ?, '2026-08-20 11:45:30', 'Alexander Wright', '192.168.1.10', 'EXCHANGE_RATE_UPDATE', 'system-admin', 'ExchangeRate', 'USD/EUR', 'Spot rate updated to 0.920000 by Treasury feed.', 'INFO')
            """,
            (str(uuid.uuid4()), cid)
        )

        # 6l. Backup Points
        db.execute(
            """
            INSERT INTO admin_backup_points (id, company_id, backup_number, backup_type, file_path, file_size_mb, status, verified_at, verified_by)
            VALUES (?, ?, ?, 'FULL_DATABASE_BACKUP', 'D:\\PyrixDB_Backups\\PyrixDB_Full_20260824_230000.bak', 1420.50, 'VERIFIED_HEALTHY', '2026-08-24 23:45:00', 'Automated SQL Server Agent')
            """,
            (str(uuid.uuid4()), cid, f"BAK-{c_code}-20260824-01")
        )
        db.execute(
            """
            INSERT INTO admin_backup_points (id, company_id, backup_number, backup_type, file_path, file_size_mb, status, verified_at, verified_by)
            VALUES (?, ?, ?, 'TRANSACTION_LOG_BACKUP', 'D:\\PyrixDB_Backups\\PyrixDB_Log_20260825_120000.trn', 85.20, 'VERIFIED_HEALTHY', '2026-08-25 12:15:00', 'Automated SQL Server Agent')
            """,
            (str(uuid.uuid4()), cid, f"BAK-{c_code}-20260825-02")
        )

    print("Completed System Administration & Governance seeding across all companies.")

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
    seed_sales_master_and_transactions()
    seed_inventory_master_and_transactions()
    seed_fixed_assets_master_and_transactions()
    seed_appearance()
    seed_prod_master_and_transactions()
    seed_admin_master_and_transactions()
    logger.info("PyrixDB multi-company initialization and seed complete.")

if __name__ == "__main__":
    setup_database()
