import uuid
from typing import Dict, Any, List, Optional, Tuple
from app.core.db import db
from app.monographs.audit_logs.service import AuditService

class DynamicCrudService:
    """
    Centralized, enterprise-grade dynamic CRUD service for Pyrix ERP.
    Provides schema reflection, pre-flight relational safety checks, 
    instant JSON-based entity updates, and safe deletion.
    """

    # Comprehensive Registry of ERP Entities
    ENTITY_REGISTRY = {
        # General Ledger
        "gl_accounts": {
            "table": "gl_accounts",
            "title": "GL Account",
            "id_col": "id",
            "display_col": "account_name",
            "editable_fields": [
                {"field": "account_number", "label": "Account Code", "type": "text", "required": True},
                {"field": "account_name", "label": "Account Title", "type": "text", "required": True},
                {"field": "account_type", "label": "Account Type", "type": "select", "options": ["ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"], "required": True},
                {"field": "normal_balance", "label": "Normal Balance", "type": "select", "options": ["DEBIT", "CREDIT"], "required": True},
                {"field": "is_active", "label": "Active Status", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "gl_journal_voucher_lines", "col": "gl_account_id", "label": "Journal Lines"}
            ]
        },
        "gl_vouchers": {
            "table": "gl_journal_vouchers",
            "title": "Journal Voucher",
            "id_col": "id",
            "display_col": "voucher_number",
            "editable_fields": [
                {"field": "voucher_number", "label": "Voucher Number", "type": "text", "required": True},
                {"field": "voucher_date", "label": "Voucher Date", "type": "date", "required": True},
                {"field": "reference_number", "label": "Reference / Memo", "type": "text"},
                {"field": "narration", "label": "Narration / Description", "type": "text"},
                {"field": "status", "label": "Voucher Status", "type": "select", "options": ["DRAFT", "UNPOSTED", "POSTED", "VOID"], "required": True}
            ],
            "dep_checks": [
                {"table": "gl_journal_voucher_lines", "col": "voucher_id", "label": "Voucher Lines"}
            ]
        },
        "gl_auto_profiles": {
            "table": "gl_automatic_profiles",
            "title": "Automatic Batch Profile",
            "id_col": "id",
            "display_col": "profile_name",
            "editable_fields": [
                {"field": "profile_code", "label": "Profile Code", "type": "text", "required": True},
                {"field": "profile_name", "label": "Profile Name", "type": "text", "required": True},
                {"field": "frequency", "label": "Frequency", "type": "select", "options": ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY"], "required": True},
                {"field": "day_of_period", "label": "Day of Period", "type": "number", "required": True},
                {"field": "default_amount", "label": "Default Amount ($)", "type": "number", "step": "0.01", "required": True},
                {"field": "is_auto_trigger", "label": "Automatic Trigger Active", "type": "checkbox"}
            ]
        },
        "gl_templates": {
            "table": "gl_batch_templates",
            "title": "Batch Template",
            "id_col": "id",
            "display_col": "template_name",
            "editable_fields": [
                {"field": "template_code", "label": "Template Code", "type": "text", "required": True},
                {"field": "template_name", "label": "Template Name", "type": "text", "required": True},
                {"field": "description", "label": "Description", "type": "text"},
                {"field": "is_active", "label": "Active Status", "type": "checkbox"}
            ]
        },
        "gl_budget_sets": {
            "table": "gl_budget_sets",
            "title": "GL Budget Allocation",
            "id_col": "id",
            "display_col": "budget_title",
            "editable_fields": [
                {"field": "budget_code", "label": "Budget Code", "type": "text", "required": True},
                {"field": "budget_title", "label": "Budget Title", "type": "text", "required": True},
                {"field": "fiscal_year", "label": "Fiscal Year", "type": "text", "required": True},
                {"field": "allocated_amount", "label": "Allocated Amount ($)", "type": "number", "step": "0.01", "required": True},
                {"field": "status", "label": "Approval Status", "type": "select", "options": ["DRAFT", "PENDING", "APPROVED", "REVISED"], "required": True}
            ]
        },

        # Sourcing
        "sourcing_vendors": {
            "table": "sourcing_vendors",
            "title": "Supplier / Vendor",
            "id_col": "id",
            "display_col": "vendor_name",
            "editable_fields": [
                {"field": "vendor_code", "label": "Vendor Code", "type": "text", "required": True},
                {"field": "vendor_name", "label": "Vendor Name", "type": "text", "required": True},
                {"field": "contact_person", "label": "Primary Contact", "type": "text"},
                {"field": "email", "label": "Official Email", "type": "text"},
                {"field": "phone", "label": "Phone Number", "type": "text"},
                {"field": "credit_limit", "label": "Credit Limit ($)", "type": "number", "step": "0.01"},
                {"field": "rating", "label": "Vendor Rating (1-5)", "type": "number", "step": "0.1"},
                {"field": "is_active", "label": "Active Vendor", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "sourcing_purchase_orders", "col": "vendor_id", "label": "Purchase Orders"}
            ]
        },
        "sourcing_requisitions": {
            "table": "sourcing_requisitions",
            "title": "Purchase Requisition",
            "id_col": "id",
            "display_col": "req_number",
            "editable_fields": [
                {"field": "req_number", "label": "PR Number", "type": "text", "required": True},
                {"field": "title", "label": "Requisition Title", "type": "text", "required": True},
                {"field": "requester_name", "label": "Requester Name", "type": "text", "required": True},
                {"field": "priority", "label": "Priority", "type": "select", "options": ["LOW", "MEDIUM", "HIGH", "URGENT"], "required": True},
                {"field": "total_estimated_amount", "label": "Est. Total ($)", "type": "number", "step": "0.01"},
                {"field": "status", "label": "Status", "type": "select", "options": ["DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED"], "required": True}
            ]
        },
        "sourcing_purchase_orders": {
            "table": "sourcing_purchase_orders",
            "title": "Purchase Order",
            "id_col": "id",
            "display_col": "po_number",
            "editable_fields": [
                {"field": "po_number", "label": "PO Number", "type": "text", "required": True},
                {"field": "payment_terms", "label": "Payment Terms", "type": "text"},
                {"field": "incoterm", "label": "Incoterm", "type": "select", "options": ["FOB", "CIF", "EXW", "DDP", "CFR"]},
                {"field": "shipping_address", "label": "Delivery / Shipping Address", "type": "text"},
                {"field": "status", "label": "Status", "type": "select", "options": ["DRAFT", "APPROVED", "DISPATCHED", "RECEIVED", "CLOSED"], "required": True}
            ],
            "dep_checks": [
                {"table": "inv_grn_headers", "col": "po_id", "label": "Goods Receipt Notes (GRN)"}
            ]
        },

        # Sales
        "sales_quotes": {
            "table": "sales_quotes",
            "title": "Commercial Quotation",
            "id_col": "id",
            "display_col": "quote_number",
            "editable_fields": [
                {"field": "quote_number", "label": "Quote Number", "type": "text", "required": True},
                {"field": "customer_name", "label": "Customer Name", "type": "text", "required": True},
                {"field": "valid_until", "label": "Valid Until Date", "type": "date"},
                {"field": "payment_terms", "label": "Payment Terms", "type": "text"},
                {"field": "total_amount", "label": "Total Amount ($)", "type": "number", "step": "0.01"},
                {"field": "status", "label": "Status", "type": "select", "options": ["DRAFT", "ISSUED", "ACCEPTED", "EXPIRED", "CONVERTED"], "required": True}
            ]
        },
        "sales_orders": {
            "table": "sales_orders",
            "title": "Sales Order",
            "id_col": "id",
            "display_col": "order_number",
            "editable_fields": [
                {"field": "order_number", "label": "Order Number", "type": "text", "required": True},
                {"field": "customer_name", "label": "Customer Name", "type": "text", "required": True},
                {"field": "expected_delivery_date", "label": "Expected Delivery Date", "type": "date"},
                {"field": "shipping_address", "label": "Shipping Destination", "type": "text"},
                {"field": "status", "label": "Status", "type": "select", "options": ["PENDING", "CONFIRMED", "PROCESSING", "DISPATCHED", "DELIVERED", "COMPLETED"], "required": True}
            ],
            "dep_checks": [
                {"table": "sales_invoices", "col": "order_id", "label": "Sales Invoices"},
                {"table": "sales_delivery_orders", "col": "order_id", "label": "Delivery Orders"}
            ]
        },
        "sales_invoices": {
            "table": "sales_invoices",
            "title": "Sales Invoice",
            "id_col": "id",
            "display_col": "invoice_number",
            "editable_fields": [
                {"field": "invoice_number", "label": "Invoice Number", "type": "text", "required": True},
                {"field": "customer_name", "label": "Customer Name", "type": "text", "required": True},
                {"field": "invoice_date", "label": "Invoice Date", "type": "date", "required": True},
                {"field": "due_date", "label": "Due Date", "type": "date", "required": True},
                {"field": "total_amount", "label": "Invoice Amount ($)", "type": "number", "step": "0.01"},
                {"field": "status", "label": "Payment Status", "type": "select", "options": ["ISSUED", "PAID", "PARTIALLY_PAID", "OVERDUE", "VOID"], "required": True}
            ]
        },

        # Inventory
        "inv_warehouses": {
            "table": "inv_warehouses",
            "title": "Warehouse Facility",
            "id_col": "id",
            "display_col": "warehouse_name",
            "editable_fields": [
                {"field": "warehouse_code", "label": "Warehouse Code", "type": "text", "required": True},
                {"field": "warehouse_name", "label": "Warehouse Name", "type": "text", "required": True},
                {"field": "location_address", "label": "Location Address", "type": "text"},
                {"field": "manager_name", "label": "Facility Manager", "type": "text"},
                {"field": "is_active", "label": "Active Facility", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "inv_locations", "col": "warehouse_id", "label": "Warehouse Stock Locations"}
            ]
        },
        "inv_items": {
            "table": "inv_items",
            "title": "Inventory SKU Item",
            "id_col": "id",
            "display_col": "item_name",
            "editable_fields": [
                {"field": "item_code", "label": "Item Code / SKU", "type": "text", "required": True},
                {"field": "item_name", "label": "Item Name", "type": "text", "required": True},
                {"field": "category", "label": "Item Category", "type": "text"},
                {"field": "uom", "label": "Unit of Measure (UOM)", "type": "text", "required": True},
                {"field": "standard_cost", "label": "Standard Cost ($)", "type": "number", "step": "0.01"},
                {"field": "selling_price", "label": "Selling Price ($)", "type": "number", "step": "0.01"},
                {"field": "is_active", "label": "Active Item", "type": "checkbox"}
            ]
        },

        # Production
        "prod_plants": {
            "table": "prod_plants",
            "title": "Manufacturing Plant",
            "id_col": "id",
            "display_col": "plant_name",
            "editable_fields": [
                {"field": "plant_code", "label": "Plant Code", "type": "text", "required": True},
                {"field": "plant_name", "label": "Plant Name", "type": "text", "required": True},
                {"field": "plant_manager", "label": "Plant Manager", "type": "text"},
                {"field": "location", "label": "Geographic Location", "type": "text"},
                {"field": "capacity_index", "label": "Capacity Index (PPM)", "type": "number"},
                {"field": "is_active", "label": "Plant Active", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "prod_orders", "col": "plant_id", "label": "Production Orders"}
            ]
        },
        "prod_work_centers": {
            "table": "prod_work_centers",
            "title": "Work Center Cell",
            "id_col": "id",
            "display_col": "work_center_name",
            "editable_fields": [
                {"field": "work_center_code", "label": "Center Code", "type": "text", "required": True},
                {"field": "work_center_name", "label": "Work Center Name", "type": "text", "required": True},
                {"field": "hourly_rate", "label": "Standard Hourly Rate ($)", "type": "number", "step": "0.01"},
                {"field": "capacity_hours_day", "label": "Capacity Hours / Day", "type": "number"},
                {"field": "is_active", "label": "Active Center", "type": "checkbox"}
            ]
        },
        "prod_orders": {
            "table": "prod_orders",
            "title": "Production Order",
            "id_col": "id",
            "display_col": "order_number",
            "editable_fields": [
                {"field": "order_number", "label": "Production Order #", "type": "text", "required": True},
                {"field": "planned_qty", "label": "Planned Quantity", "type": "number", "step": "0.01", "required": True},
                {"field": "start_date", "label": "Scheduled Start Date", "type": "date"},
                {"field": "due_date", "label": "Due Date", "type": "date"},
                {"field": "status", "label": "Order Status", "type": "select", "options": ["PLANNED", "RELEASED", "IN_PROGRESS", "COMPLETED", "CLOSED"], "required": True}
            ],
            "dep_checks": [
                {"table": "prod_job_cards", "col": "order_id", "label": "Shop Floor Job Cards"}
            ]
        },

        # Fixed Assets
        "fa_assets": {
            "table": "fa_assets",
            "title": "Fixed Asset Capital Item",
            "id_col": "id",
            "display_col": "asset_name",
            "editable_fields": [
                {"field": "asset_tag", "label": "Asset Tag / Barcode", "type": "text", "required": True},
                {"field": "asset_name", "label": "Asset Name", "type": "text", "required": True},
                {"field": "acquisition_date", "label": "Acquisition Date", "type": "date"},
                {"field": "acquisition_cost", "label": "Acquisition Cost ($)", "type": "number", "step": "0.01", "required": True},
                {"field": "useful_life_years", "label": "Useful Life (Years)", "type": "number"},
                {"field": "depreciation_method", "label": "Method", "type": "select", "options": ["STRAIGHT_LINE", "DECLINING_BALANCE", "SUM_OF_YEARS", "MACRS"]},
                {"field": "status", "label": "Asset Status", "type": "select", "options": ["ACTIVE", "MAINTENANCE", "DISPOSED", "WRITTEN_OFF"], "required": True}
            ]
        },

        # Human Resources
        "hr_employees": {
            "table": "hr_employees",
            "title": "Employee Personnel File",
            "id_col": "id",
            "display_col": "first_name",
            "editable_fields": [
                {"field": "employee_code", "label": "Employee Code", "type": "text", "required": True},
                {"field": "first_name", "label": "First Name", "type": "text", "required": True},
                {"field": "last_name", "label": "Last Name", "type": "text", "required": True},
                {"field": "email", "label": "Official Email", "type": "text", "required": True},
                {"field": "phone", "label": "Phone", "type": "text"},
                {"field": "employment_status", "label": "Employment Status", "type": "select", "options": ["PERMANENT", "PROBATION", "CONTRACT", "INTERN", "RESIGNED"], "required": True},
                {"field": "basic_salary", "label": "Basic Salary ($)", "type": "number", "step": "0.01"},
                {"field": "gross_salary", "label": "Gross Salary ($)", "type": "number", "step": "0.01"},
                {"field": "is_active", "label": "Active Employee", "type": "checkbox"}
            ]
        },
        "hr_departments": {
            "table": "hr_departments",
            "title": "HR Department",
            "id_col": "id",
            "display_col": "dept_name",
            "editable_fields": [
                {"field": "dept_code", "label": "Department Code", "type": "text", "required": True},
                {"field": "dept_name", "label": "Department Name", "type": "text", "required": True},
                {"field": "cost_center_code", "label": "Assigned Cost Center", "type": "text"},
                {"field": "head_of_dept", "label": "Department Head", "type": "text"},
                {"field": "location_name", "label": "Location", "type": "text"},
                {"field": "is_active", "label": "Active Department", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "hr_employees", "col": "department_id", "label": "Department Employees"}
            ]
        },

        # Accounts Receivable
        "ar_customers": {
            "table": "ar_customers",
            "title": "Customer Account",
            "id_col": "id",
            "display_col": "customer_name",
            "editable_fields": [
                {"field": "customer_code", "label": "Customer Code", "type": "text", "required": True},
                {"field": "customer_name", "label": "Customer Name", "type": "text", "required": True},
                {"field": "contact_person", "label": "Primary Contact", "type": "text"},
                {"field": "email", "label": "Official Email", "type": "text"},
                {"field": "phone", "label": "Telephone", "type": "text"},
                {"field": "credit_limit", "label": "Credit Limit ($)", "type": "number", "step": "0.01"},
                {"field": "is_active", "label": "Active Customer", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "sales_orders", "col": "customer_id", "label": "Sales Orders"}
            ]
        },

        # System Administration
        "admin_cost_centers": {
            "table": "admin_cost_centers",
            "title": "Enterprise Cost Center",
            "id_col": "id",
            "display_col": "name",
            "editable_fields": [
                {"field": "cost_center_code", "label": "Cost Center Code", "type": "text", "required": True},
                {"field": "name", "label": "Cost Center Name", "type": "text", "required": True},
                {"field": "department", "label": "Department Scope", "type": "text"},
                {"field": "manager_name", "label": "Manager / Lead", "type": "text"},
                {"field": "budget_allocation", "label": "Budget Allocation ($)", "type": "number", "step": "0.01"},
                {"field": "is_profit_center", "label": "Profit Center", "type": "checkbox"},
                {"field": "is_active", "label": "Active Cost Center", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "gl_journal_voucher_lines", "col": "cost_centre_id", "label": "Journal Lines"},
                {"table": "admin_user_profiles", "col": "cost_center_id", "label": "Assigned Users"}
            ]
        },
        "admin_business_units": {
            "table": "admin_business_units",
            "title": "Business Unit",
            "id_col": "id",
            "display_col": "unit_name",
            "editable_fields": [
                {"field": "unit_code", "label": "Unit Code", "type": "text", "required": True},
                {"field": "unit_name", "label": "Unit Name", "type": "text", "required": True},
                {"field": "unit_type", "label": "Unit Type", "type": "select", "options": ["DIVISION", "PLANT", "SUBSIDIARY", "REGIONAL_HUB"]},
                {"field": "manager_name", "label": "Unit Director", "type": "text"},
                {"field": "location", "label": "Location", "type": "text"},
                {"field": "is_active", "label": "Active Unit", "type": "checkbox"}
            ],
            "dep_checks": [
                {"table": "admin_cost_centers", "col": "business_unit_id", "label": "Child Cost Centers"}
            ]
        },
        "admin_currencies": {
            "table": "admin_currencies",
            "title": "Treasury Currency",
            "id_col": "id",
            "display_col": "currency_code",
            "editable_fields": [
                {"field": "currency_code", "label": "ISO Currency Code", "type": "text", "required": True},
                {"field": "currency_name", "label": "Currency Name", "type": "text", "required": True},
                {"field": "symbol", "label": "Currency Symbol", "type": "text", "required": True},
                {"field": "decimal_places", "label": "Decimal Precision", "type": "number"},
                {"field": "is_active", "label": "Active Currency", "type": "checkbox"}
            ]
        },
        "admin_exchange_rates": {
            "table": "admin_exchange_rates",
            "title": "Currency Exchange Rate",
            "id_col": "id",
            "display_col": "currency_code",
            "editable_fields": [
                {"field": "currency_code", "label": "Foreign Currency", "type": "text", "required": True},
                {"field": "target_currency", "label": "Base Currency", "type": "text", "required": True},
                {"field": "exchange_rate", "label": "Exchange Rate", "type": "number", "step": "0.000001", "required": True},
                {"field": "effective_date", "label": "Effective Date", "type": "date", "required": True},
                {"field": "rate_type", "label": "Rate Type", "type": "select", "options": ["SPOT_RATE", "MONTH_END_AVERAGE", "BUDGET_STANDARD", "TREASURY_SYNC"]}
            ]
        },
        "admin_tax_profiles": {
            "table": "admin_tax_profiles",
            "title": "Tax Compliance Profile",
            "id_col": "id",
            "display_col": "profile_name",
            "editable_fields": [
                {"field": "profile_code", "label": "Profile Code", "type": "text", "required": True},
                {"field": "profile_name", "label": "Profile Name", "type": "text", "required": True},
                {"field": "effective_rate", "label": "Effective Tax Rate (%)", "type": "number", "step": "0.01", "required": True},
                {"field": "tax_type", "label": "Tax Type", "type": "select", "options": ["VAT", "SALES_TAX", "WITHHOLDING", "EXCISE"]},
                {"field": "is_active", "label": "Active Profile", "type": "checkbox"}
            ]
        },
        "admin_printers": {
            "table": "admin_printers",
            "title": "Network Enterprise Printer",
            "id_col": "id",
            "display_col": "printer_name",
            "editable_fields": [
                {"field": "printer_name", "label": "Printer Name", "type": "text", "required": True},
                {"field": "printer_type", "label": "Printer Type", "type": "select", "options": ["NETWORK_PRINT_SERVER", "ZEBRA_THERMAL_BARCODE", "COLOR_LASER_VOUCHER"]},
                {"field": "ip_address", "label": "IP Address", "type": "text", "required": True},
                {"field": "port", "label": "Network Port", "type": "number"},
                {"field": "is_active", "label": "Online Status", "type": "checkbox"}
            ]
        }
    }

    @staticmethod
    def get_entity_config(entity_slug: str) -> Optional[Dict[str, Any]]:
        return DynamicCrudService.ENTITY_REGISTRY.get(entity_slug)

    @staticmethod
    def get_record(entity_slug: str, record_id: str) -> Optional[Dict[str, Any]]:
        cfg = DynamicCrudService.get_entity_config(entity_slug)
        if not cfg:
            return None

        table = cfg["table"]
        id_col = cfg["id_col"]

        row = db.query_one(f"SELECT * FROM {table} WHERE {id_col} = ?", (record_id,))
        if not row:
            return None

        clean_row = {}
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                clean_row[k] = v.isoformat()
            elif hasattr(v, "__float__"):
                clean_row[k] = float(v)
            else:
                clean_row[k] = v

        return {
            "entity": entity_slug,
            "title": cfg["title"],
            "fields": cfg["editable_fields"],
            "data": clean_row
        }

    @staticmethod
    def update_record(entity_slug: str, record_id: str, form_data: Dict[str, Any], user: str = "System Admin") -> Dict[str, Any]:
        cfg = DynamicCrudService.get_entity_config(entity_slug)
        if not cfg:
            return {"success": False, "error": f"Unknown entity: {entity_slug}"}

        table = cfg["table"]
        id_col = cfg["id_col"]

        set_clauses = []
        params = []

        allowed_fields = {f["field"]: f for f in cfg["editable_fields"]}

        for field_name, value in form_data.items():
            if field_name in allowed_fields:
                f_meta = allowed_fields[field_name]
                f_type = f_meta.get("type")
                
                if f_type == "checkbox":
                    val = 1 if value in (True, "true", "1", 1, "on") else 0
                elif f_type == "number":
                    val = float(value) if value not in (None, "", "null") else 0.0
                elif f_type == "date":
                    val = str(value).strip() if value else None
                else:
                    val = str(value).strip() if value is not None else None

                set_clauses.append(f"{field_name} = ?")
                params.append(val)

        if not set_clauses:
            return {"success": False, "error": "No valid fields provided for update"}

        params.append(record_id)
        sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {id_col} = ?"

        try:
            affected = db.execute(sql, tuple(params))
            if affected > 0:
                AuditService.log_event(
                    company_id="3B5A7898-82A2-49D3-8C87-3BA0C47B0630",
                    action_type="DYNAMIC_UPDATE",
                    module_code="crud",
                    entity_name=table,
                    record_ref=str(record_id),
                    change_details=f"Updated {len(set_clauses)} fields in {cfg['title']}",
                    user_name=user
                )
                return {"success": True, "message": f"{cfg['title']} updated successfully", "record_id": record_id}
            return {"success": False, "error": "Record not found or unchanged"}
        except Exception as e:
            return {"success": False, "error": f"Database error: {str(e)}"}

    @staticmethod
    def check_dependencies(entity_slug: str, record_id: str) -> Dict[str, Any]:
        cfg = DynamicCrudService.get_entity_config(entity_slug)
        if not cfg:
            return {"can_delete": False, "reason": "Unknown entity"}

        dep_checks = cfg.get("dep_checks", [])
        blocking_deps = []

        for dep in dep_checks:
            dep_table = dep["table"]
            dep_col = dep["col"]
            dep_label = dep.get("label", dep_table)

            try:
                cnt = db.query_one(
                    f"SELECT COUNT(*) AS cnt FROM {dep_table} WHERE {dep_col} = ?", 
                    (record_id,)
                )["cnt"]
                if cnt > 0:
                    blocking_deps.append(f"{cnt} active {dep_label}")
            except Exception:
                pass

        if blocking_deps:
            return {
                "can_delete": False,
                "reason": f"Cannot delete {cfg['title']} because it is referenced by: {', '.join(blocking_deps)}. Reassign or archive the record instead."
            }

        return {"can_delete": True}

    @staticmethod
    def delete_record(entity_slug: str, record_id: str, user: str = "System Admin") -> Dict[str, Any]:
        pre_check = DynamicCrudService.check_dependencies(entity_slug, record_id)
        if not pre_check["can_delete"]:
            return {"success": False, "error": pre_check["reason"]}

        cfg = DynamicCrudService.get_entity_config(entity_slug)
        table = cfg["table"]
        id_col = cfg["id_col"]

        has_is_delete = db.query_one("""
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ? AND COLUMN_NAME = 'isDelete'
        """, (table,))

        has_is_active = db.query_one("""
            SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = ? AND COLUMN_NAME = 'is_active'
        """, (table,))

        try:
            if has_is_delete:
                sql = f"UPDATE {table} SET isDelete = 1, isDeleteDate = GETDATE() WHERE {id_col} = ?"
            elif has_is_active:
                sql = f"UPDATE {table} SET is_active = 0 WHERE {id_col} = ?"
            else:
                sql = f"DELETE FROM {table} WHERE {id_col} = ?"

            affected = db.execute(sql, (record_id,))
            if affected > 0:
                AuditService.log_event(
                    company_id="3B5A7898-82A2-49D3-8C87-3BA0C47B0630",
                    action_type="DYNAMIC_DELETE",
                    module_code="crud",
                    entity_name=table,
                    record_ref=str(record_id),
                    change_details=f"Deleted / archived {cfg['title']} record {record_id}",
                    user_name=user,
                    severity="WARNING"
                )
                return {"success": True, "message": f"{cfg['title']} deleted successfully", "record_id": record_id}
            return {"success": False, "error": "Record not found"}
        except Exception as e:
            return {"success": False, "error": f"Database error during deletion: {str(e)}"}
