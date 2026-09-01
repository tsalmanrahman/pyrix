from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.core.db import db
from app.core.company_service import CompanyService
from app.monographs.appearance.service import AppearanceService
from app.monographs.dynamic_builder.service import DynamicOptionService
from app.monographs.enterprise_modules.service import EnterpriseModuleService
from app.monographs.enterprise_modules.gl_master_service import GLMasterService
from app.monographs.enterprise_modules.gl_journal_service import GLJournalService
from app.monographs.enterprise_modules.gl_process_service import GLProcessService
from app.monographs.enterprise_modules.gl_analysis_service import GLAnalysisService
from app.monographs.enterprise_modules.gl_report_service import GLReportService
from app.monographs.enterprise_modules.cash_book_service import CashBookService
from app.monographs.enterprise_modules.ar_master_service import ARMasterService
from app.monographs.enterprise_modules.ar_transaction_service import ARTransactionService
from app.monographs.enterprise_modules.ar_process_service import ARProcessService
from app.monographs.enterprise_modules.ar_report_service import ARReportService
from app.monographs.enterprise_modules.sourcing_master_service import SourcingMasterService
from app.monographs.enterprise_modules.sourcing_transaction_service import SourcingTransactionService
from app.monographs.enterprise_modules.sourcing_process_service import SourcingProcessService
from app.monographs.enterprise_modules.sourcing_analytics_service import SourcingAnalyticsService
from app.monographs.enterprise_modules.sourcing_report_service import SourcingReportService
from app.monographs.enterprise_modules.sales_master_service import SalesMasterService
from app.monographs.enterprise_modules.sales_transaction_service import SalesTransactionService
from app.monographs.enterprise_modules.sales_process_service import SalesProcessService
from app.monographs.enterprise_modules.sales_analysis_service import SalesAnalysisService
from app.monographs.enterprise_modules.sales_report_service import SalesReportService
from app.monographs.enterprise_modules.inv_master_service import InvMasterService
from app.monographs.enterprise_modules.inv_transaction_service import InvTransactionService
from app.monographs.enterprise_modules.inv_process_service import InvProcessService
from app.monographs.enterprise_modules.inv_warranty_service import InvWarrantyService
from app.monographs.enterprise_modules.inv_analysis_service import InvAnalysisService
from app.monographs.enterprise_modules.inv_report_service import InvReportService
from app.monographs.enterprise_modules.fa_master_service import FAMasterService
from app.monographs.enterprise_modules.fa_asset_service import FAAssetService
from app.monographs.enterprise_modules.fa_depreciation_service import FADepreciationService
from app.monographs.enterprise_modules.fa_verification_service import FAVerificationService
from app.monographs.enterprise_modules.fa_report_service import FAReportService
from app.monographs.enterprise_modules.hr_master_service import HRMasterService
from app.monographs.enterprise_modules.hr_employee_service import HREmployeeService
from app.monographs.enterprise_modules.hr_recruitment_service import HRRecruitmentService
from app.monographs.enterprise_modules.hr_attendance_service import HRAttendanceService
from app.monographs.enterprise_modules.hr_payroll_service import HRPayrollService
from app.monographs.enterprise_modules.hr_report_service import HRReportService
from app.monographs.enterprise_modules.registry import get_module_suites_registry, get_active_suite_context
from app.core.user_service import UserService

router = APIRouter(tags=["Enterprise Modules"])
templates = Jinja2Templates(directory="app/templates")


HR_SUB_AREAS = {
    # 1. Personnel & Organization Master Setup Suite (7 Sub-Areas)
    "hr-grades": {"title": "Employee Grades & Bands", "icon": "award", "entity": "hr-grades"},
    "hr-departments": {"title": "Departments Master", "icon": "building-2", "entity": "hr-departments"},
    "hr-designations": {"title": "Designations & Titles", "icon": "badge-check", "entity": "hr-designations"},
    "hr-shifts": {"title": "Work-Shifts & Roster", "icon": "clock", "entity": "hr-shifts"},
    "hr-holidays": {"title": "Annual Holiday Calendar", "icon": "calendar", "entity": "hr-holidays"},
    "hr-leave-types": {"title": "Leave Policies & Types", "icon": "file-heart", "entity": "hr-leave-types"},
    "hr-bank-accounts": {"title": "Corporate Bank Accounts", "icon": "landmark", "entity": "hr-bank-accounts"},

    # 2. Talent Acquisition & Employee Lifecycle Suite (6 Sub-Areas)
    "hr-employees": {"title": "Master Employee Profiles", "icon": "user-check", "entity": "hr-employees"},
    "hr-contract-workers": {"title": "Temporary & Casual Workers", "icon": "hard-hat", "entity": "hr-contract-workers"},
    "hr-documents": {"title": "Digital Document Vault", "icon": "folder-lock", "entity": "hr-documents"},
    "hr-transfers": {"title": "Transfers & Promotions Log", "icon": "repeat", "entity": "hr-transfers"},
    "hr-requisitions": {"title": "Manpower Job Requisitions", "icon": "briefcase", "entity": "hr-requisitions"},
    "hr-candidates": {"title": "CV Bank & Interview Scoring", "icon": "user-plus", "entity": "hr-candidates"},

    # 3. Time, Attendance & Leave Management Suite (3 Sub-Areas)
    "hr-attendance-log": {"title": "Biometric Punch Logs", "icon": "fingerprint", "entity": "hr-attendance-log"},
    "hr-leaves": {"title": "Leave Applications & Ledger", "icon": "calendar-heart", "entity": "hr-leaves"},
    "hr-overtime": {"title": "Overtime (OT) Engine Matrix", "icon": "timer", "entity": "hr-overtime"},

    # 4. Payroll, Loans, Income Tax & GL Processing Suite (5 Sub-Areas)
    "hr-payroll-runs": {"title": "Monthly Payroll Runs", "icon": "wallet", "entity": "hr-payroll-runs"},
    "hr-payslips": {"title": "Itemized Payslips Register", "icon": "receipt", "entity": "hr-payslips"},
    "hr-loans": {"title": "Employee Loans & Advances", "icon": "coins", "entity": "hr-loans"},
    "hr-tax-slabs": {"title": "Income Tax Slabs & Rebates", "icon": "scale", "entity": "hr-tax-slabs"},
    "hr-tax-deposits": {"title": "Treasury Tax Deposit Log", "icon": "landmark", "entity": "hr-tax-deposits"},

    # 5. Statements, Statutory Reports & Print Studio Suite (5 Sub-Areas)
    "hr-summary": {"title": "Executive Workforce KPIs", "icon": "pie-chart", "entity": "hr-summary"},
    "hr-salary-register": {"title": "Consolidated Salary Register", "icon": "file-spreadsheet", "entity": "hr-salary-register"},
    "hr-bank-advice": {"title": "Corporate Bank Advice", "icon": "credit-card", "entity": "hr-bank-advice"},
    "hr-pf-ledger": {"title": "Provident Fund (PF) Ledger", "icon": "shield-dollar", "entity": "hr-pf-ledger"},
    "hr-print-studio": {"title": "HR Official Print Studio", "icon": "printer", "entity": "hr-print-studio"},
}

GL_SUB_AREAS = {
    # 1. Master Setup Suite (6 Sub-Areas)
    "coa": {"title": "GL Account (COA) List", "icon": "book-open", "entity": "gl-accounts"},
    "mapping": {"title": "GL Account Mapping Matrix", "icon": "building-2", "entity": "company-mappings"},
    "subaccounts": {"title": "GL Sub Accounts List", "icon": "folder-tree", "entity": "sub-accounts"},
    "departments": {"title": "Organizational Departments", "icon": "users", "entity": "departments"},
    "costcentres": {"title": "Cost Centres Master", "icon": "target", "entity": "cost-centres"},
    "categories": {"title": "Account Categories & Segments", "icon": "tags", "entity": None},

    # 2. Transaction Processing & Automation Suite (8 Operations from Legacy ERP)
    "journals": {"title": "Journal Vouchers (JV)", "icon": "file-spread", "entity": "journal-vouchers"},
    "auto-batch-gen": {"title": "Generate Batch from Auto Journals", "icon": "sparkles", "entity": None},
    "template-batch-gen": {"title": "Generate Batch from Template", "icon": "copy-check", "entity": None},
    "auto-batch-profiles": {"title": "Automatic Batch Profiles", "icon": "clock-4", "entity": "gl-auto-profiles"},
    "batch-templates": {"title": "Batch Templates", "icon": "copy", "entity": "batch-templates"},
    "batches": {"title": "Batch Status & Processing", "icon": "package-check", "entity": "journal-batches"},
    "budgets": {"title": "Budget Data & Variances", "icon": "pie-chart", "entity": "budget-sets"},
    "print-vouchers": {"title": "Print Journal Vouchers", "icon": "printer", "entity": None},

    # 3. Financial Process & Closing Suite (2 Operations)
    "post-batch": {"title": "Post Batch (Bulk Ledger Commitment)", "icon": "check-circle", "entity": None},
    "data-integrity": {"title": "Check Data Integrity of GL Transactions", "icon": "shield-check", "entity": None},

    # 4. Financial Analysis & Cost Control Suite (2 Operations)
    "cost-analysis": {"title": "Cost Analysis by Cost Centre", "icon": "bar-chart-3", "entity": None},
    "account-balances": {"title": "Real-Time Account Balance Inquiry", "icon": "activity", "entity": None},

    # 5. Financial Reporting & Statements Suite (7 Specialized Reports)
    "financial-statements": {"title": "Balance Sheet & Income Statement (P&L)", "icon": "file-text", "entity": None},
    "trial-balance": {"title": "Trial Balance Suite", "icon": "scale", "entity": None},
    "gl-transaction-details": {"title": "General Ledger Transaction Details", "icon": "list-filter", "entity": None},
    "cost-centre-pnl": {"title": "Cost-Centre wise Profit & Loss", "icon": "layers", "entity": None},
    "notes-to-accounts": {"title": "Notes to the Accounts", "icon": "file-code-2", "entity": None},
}

CB_SUB_AREAS = {
    # 1. Master Setup
    "cashiers": {"title": "Cashier Stations Master", "icon": "user-check", "entity": "cashiers"},
    "banks": {"title": "Bank Master Setup", "icon": "landmark", "entity": "banks"},
    "branches": {"title": "Bank Branches Master", "icon": "building-2", "entity": "branches"},
    "accounts": {"title": "Bank Accounts Master", "icon": "credit-card", "entity": "accounts"},
    # 2. Transaction & Receipts Suite (Legacy ERP parity)
    "receipts": {"title": "Money Receipts (MR)", "icon": "receipt", "entity": "receipts"},
    "transfers": {"title": "Inter Bank-Cash Contra Transfers", "icon": "arrow-left-right", "entity": "transfers"},
}

AR_SUB_AREAS = {
    # 1. Master Setup Suite (10 Options)
    "customers": {"title": "Customer Profile", "icon": "users", "entity": "ar-customers"},
    "ar-customer-groups": {"title": "AR Customer Group", "icon": "folder-cog", "entity": "ar-customer-groups"},
    "customer-groups": {"title": "Customer Group", "icon": "building-2", "entity": "ar-commercial-groups"},
    "group-categories": {"title": "Customer Group Category", "icon": "tags", "entity": "ar-group-categories"},
    "company-mappings": {"title": "Customer Mapping with Company", "icon": "network", "entity": "ar-company-mappings"},
    "ship-to-addresses": {"title": "Customers' Ship to Address", "icon": "truck", "entity": "ar-ship-addresses"},
    "control-accounts": {"title": "A/R Control Account Sets", "icon": "scale", "entity": "ar-control-accounts"},
    "reminder-criteria": {"title": "Customers Reminder Letter Criteria Setup", "icon": "mail-warning", "entity": "ar-reminder-criteria"},
    "aging-profiles": {"title": "Accounts Receivable Aging Profile", "icon": "clock-3", "entity": "ar-aging-profiles"},
    "adjustment-types": {"title": "A/R Adjustment Type", "icon": "sliders-horizontal", "entity": "ar-adjustment-types"},
    # 2. Transaction Processing Suite (8 Options from Legacy ERP)
    "advance-adjustments": {"title": "Adjustment of Advance with bills", "icon": "layers-2", "entity": "ar-advance-adjustments"},
    "ar-adjustments": {"title": "Adjustment of Accounts Receivable", "icon": "file-check-2", "entity": "ar-general-adjustments"},
    "debit-notes-ref": {"title": "Debit Note with Invoice Ref", "icon": "file-plus-2", "entity": "ar-debit-notes-ref"},
    "debit-notes-direct": {"title": "Debit Note without Invoice Ref", "icon": "file-plus", "entity": "ar-debit-notes-direct"},
    "credit-notes-ref": {"title": "Credit Note with Invoice Ref", "icon": "file-minus-2", "entity": "ar-credit-notes-ref"},
    "credit-notes-direct": {"title": "Credit Note without Invoice Ref", "icon": "file-minus", "entity": "ar-credit-notes-direct"},
    "issue-receipts": {"title": "Issue Money Receipt", "icon": "receipt", "entity": "ar-money-receipts"},
    "cancel-receipts": {"title": "Cancel Money Receipts", "icon": "receipt-x", "entity": "ar-cancelled-receipts"},
    # 3. Credit Management & Process Suite (From Process Menu)
    "reminder-letters": {"title": "Automatic Reminder Letter to Customer", "icon": "mail-warning", "entity": "ar-reminder-letters"},
    "due-overdue-status": {"title": "Due, Overdue Status Monitor", "icon": "shield-alert", "entity": "ar-due-overdue"},
    # 4. Financial Reporting & Analytics Suite (From Report Menu)
    "ar-schedule": {"title": "Accounts Receivable Schedule", "icon": "calendar-range", "entity": "ar-schedule"},
    "customer-statement": {"title": "Customer Account Statement", "icon": "file-spread", "entity": "customer-statement"},
    "sales-collection": {"title": "Customer Sales, Collection and Outstanding", "icon": "trending-up", "entity": "sales-collection"},
    "aged-trial-balance": {"title": "Aged Trial Balance of Accounts Receivables", "icon": "scale", "entity": "aged-trial-balance"},
    "collections-register": {"title": "Collection from Customers Report", "icon": "receipt", "entity": "collections-register"},
    "notes-summary": {"title": "Debit Note / Credit Note Summary Report", "icon": "file-minus-2", "entity": "notes-summary"},
}




FIXED_ASSETS_SUB_AREAS = {
    # 1. Master Setup Suite (5 Sub-Areas)
    "fa-groups": {"title": "Asset Groups & Classes", "icon": "layers", "entity": "fa-groups"},
    "fa-locations": {"title": "Physical Locations", "icon": "building-2", "entity": "fa-locations"},
    "fa-sub-locations": {"title": "Sub-Locations & Machine Bays", "icon": "grid", "entity": "fa-sub-locations"},
    "fa-policies": {"title": "Depreciation Policies", "icon": "percent", "entity": "fa-policies"},
    "fa-gl-control": {"title": "GL Control Account Sets", "icon": "landmark", "entity": "fa-gl-control"},

    # 2. Asset Register & Lifecycle Suite (6 Sub-Areas)
    "fa-assets": {"title": "Master Asset Register", "icon": "file-text", "entity": "fa-assets"},
    "fa-grn": {"title": "Capital Asset Receipts (Asset GRN)", "icon": "inbox", "entity": "fa-grn"},
    "fa-leased": {"title": "Leased & Low-Value Assets", "icon": "clock-4", "entity": "fa-leased"},
    "fa-transfers": {"title": "Asset Transfers Log", "icon": "repeat", "entity": "fa-transfers"},
    "fa-disposals": {"title": "Disposals & Write-Offs", "icon": "trash-2", "entity": "fa-disposals"},
    "fa-spares": {"title": "Machine-Spares Mapping", "icon": "cpu", "entity": "fa-spares"},

    # 3. Depreciation Engine & GL Automation Suite (3 Sub-Areas)
    "fa-depr-runs": {"title": "Depreciation Execution Runs", "icon": "history", "entity": "fa-depr-runs"},
    "fa-depr-simulation": {"title": "Depreciation Live Simulator", "icon": "play-circle", "entity": "fa-depr-simulation"},
    "fa-approvals": {"title": "Digital e-Approvals Hub", "icon": "shield-check", "entity": "fa-approvals"},

    # 4. Physical Verification & Barcode Studio Suite (2 Sub-Areas)
    "fa-audits": {"title": "Physical Verification Audits", "icon": "check-circle-2", "entity": "fa-audits"},
    "fa-scanner": {"title": "Barcode & Tag Scanner Studio", "icon": "scan", "entity": "fa-scanner"},

    # 5. Statutory Asset Schedules & Reporting Suite (4 Sub-Areas)
    "fa-summary": {"title": "Executive Summary of Fixed Assets", "icon": "pie-chart", "entity": "fa-summary"},
    "fa-statutory-schedule": {"title": "Statutory Asset Schedule (IAS 16)", "icon": "table", "entity": "fa-statutory-schedule"},
    "fa-movement-report": {"title": "Asset Movement Audit Statement", "icon": "navigation", "entity": "fa-movement-report"},
    "fa-print-studio": {"title": "Fixed Asset Print Studio", "icon": "printer", "entity": "fa-print-studio"},
}

INVENTORY_SUB_AREAS = {
    # 1. Master Setup Suite
    "warehouses": {"title": "Warehouses Master", "icon": "warehouse", "entity": "warehouses"},
    "bins": {"title": "Multi-Bin Storage Map", "icon": "grid", "entity": "bins"},
    "product-groups": {"title": "Product Groups & Classes", "icon": "folder-tree", "entity": "product-groups"},
    "uom": {"title": "UOM & Conversion Matrix", "icon": "scale", "entity": "uom"},
    "items": {"title": "Master Items Catalog", "icon": "package", "entity": "items"},
    # 2. Transaction Processing & Movement Suite
    "grn": {"title": "Goods Receiving Notes (GRN)", "icon": "arrow-down-left", "entity": "grn"},
    "issues": {"title": "Goods Issue Challans", "icon": "arrow-up-right", "entity": "issues"},
    "stock-transfers": {"title": "Stock Transfer Orders (STO)", "icon": "truck", "entity": "stock-transfers"},
    "assembly": {"title": "Material Kitting & Assembly", "icon": "layers", "entity": "assembly"},
    "adjustments": {"title": "Physical Cycle Adjustments", "icon": "sliders-horizontal", "entity": "adjustments"},
    # 3. Process, e-Approval & Closing Suite
    "e-approvals": {"title": "e-Approval Hub", "icon": "check-check", "entity": "e-approvals"},
    "picking-lists": {"title": "Wave Picking Lists", "icon": "list-checks", "entity": "picking-lists"},
    "day-end-closing": {"title": "Day-End Inventory Closing", "icon": "clock-4", "entity": "day-end-closing"},
    # 4. Warranty, Serialization & Barcode Suite
    "warranties": {"title": "Serial & Warranty Registry", "icon": "barcode", "entity": "warranties"},
    "barcode-inquiry": {"title": "Barcode Scanner Inquiry", "icon": "scan", "entity": "barcode-inquiry"},
    # 5. Reporting, Statements & Valuation Analysis Suite
    "product-ledger": {"title": "Product Ledger (Stock Card)", "icon": "file-text", "entity": "product-ledger"},
    "inventory-valuation": {"title": "Inventory Valuation Report", "icon": "calculator", "entity": "inventory-valuation"},
    "do-vs-dispatch": {"title": "DO vs Dispatch Reconciliation", "icon": "clock-4", "entity": "do-vs-dispatch"},
    "production-costing": {"title": "WIP Production Costing", "icon": "layers", "entity": "production-costing"},
    "plant-consumption": {"title": "Plant-Wise Consumption", "icon": "building-2", "entity": "plant-consumption"},
    "sto-reports": {"title": "Inter-Warehouse STO Statement", "icon": "truck", "entity": "sto-reports"},
    "stock-balances": {"title": "Live Stock Balance Matrix", "icon": "bar-chart-3", "entity": "stock-balances"},
    "goods-in-transit": {"title": "Goods in Transit (GIT)", "icon": "navigation", "entity": "goods-in-transit"},
    "abc-analysis": {"title": "ABC & Reorder Analytics", "icon": "pie-chart", "entity": "abc-analysis"},
    "warehouse-print-studio": {"title": "Warehouse Print Studio", "icon": "printer", "entity": "warehouse-print-studio"},
}

SALES_SUB_AREAS = {
    # 1. Master Setup Suite
    "sales-teams": {"title": "Sales Teams (MM/ZM/TSM)", "icon": "network", "entity": "sales-teams"},
    "salespersons": {"title": "Salespersons Master", "icon": "users", "entity": "salespersons"},
    "sales-areas": {"title": "Sales Areas & Territories", "icon": "map-pin", "entity": "sales-areas"},
    "price-profiles": {"title": "Price Profiles & Lists", "icon": "tag", "entity": "price-profiles"},
    "product-prices": {"title": "Product Catalog Prices", "icon": "layers", "entity": "product-prices"},
    "discount-limits": {"title": "Discount Limit Matrix", "icon": "sliders", "entity": "discount-limits"},
    # 2. Transaction Processing Suite
    "quotes": {"title": "Sales Quotes & Proformas", "icon": "file-text", "entity": "quotes"},
    "sales-orders": {"title": "Sales Orders (SO)", "icon": "shopping-cart", "entity": "sales-orders"},
    "delivery-orders": {"title": "Delivery Orders (DO)", "icon": "truck", "entity": "delivery-orders"},
    "invoices": {"title": "Sales Invoices", "icon": "receipt", "entity": "invoices"},
    "returns": {"title": "Sales Returns & Credits", "icon": "rotate-ccw", "entity": "returns"},
    "budgets": {"title": "Sales Target Budgets", "icon": "pie-chart", "entity": "budgets"},
    # 3. Process, e-Approval & DSS Suite
    "document-flow": {"title": "Document Flow Studio", "icon": "git-merge", "entity": "document-flow"},
    "e-approvals": {"title": "e-Approval Hub", "icon": "check-check", "entity": "e-approvals"},
    "dss-simulator": {"title": "DSS Margin Simulator", "icon": "calculator", "entity": "dss-simulator"},
    "on-hold-orders": {"title": "On-Hold Orders Queue", "icon": "pause-circle", "entity": "on-hold-orders"},
    # 4. Analytical & Dynamic Pivot Suite
    "sales-collection-pivot": {"title": "Sales, Collection & AR Pivot", "icon": "bar-chart-3", "entity": "sales-collection-pivot"},
    "hierarchy-performance": {"title": "MM > ZM > TSM Performance", "icon": "trending-up", "entity": "hierarchy-performance"},
    "target-achievement": {"title": "Target vs Achievement", "icon": "target", "entity": "target-achievement"},
    # 5. Reporting & Statements Suite
    "do-invoice-pending": {"title": "DO-GI-Invoice Pending", "icon": "clock-4", "entity": "do-invoice-pending"},
    "consolidated-statement": {"title": "Consolidated Statement", "icon": "file-spreadsheet", "entity": "consolidated-statement"},
    "profitability-report": {"title": "Profitability Analysis", "icon": "file-text", "entity": "profitability-report"},
    "sales-print-studio": {"title": "Sales Print Studio", "icon": "printer", "entity": "sales-print-studio"},
}

SOURCING_SUB_AREAS = {
    # 1. Master Setup Suite
    "vendors": {"title": "Vendor Master Profile", "icon": "users", "entity": "vendors"},
    "enlistment": {"title": "Vendor Enlistment & Classification", "icon": "award", "entity": "enlistment"},
    "buyers": {"title": "Sourcing Buyers Master", "icon": "user-check", "entity": "buyers"},
    "purchasing-orgs": {"title": "Purchasing Organizations", "icon": "building-2", "entity": "purchasing-orgs"},
    "price-terms": {"title": "Price Terms & Incoterms Profile", "icon": "file-check", "entity": "price-terms"},
    "cnf-agents": {"title": "C&F Agents & Indentors", "icon": "ship", "entity": "cnf-agents"},
    "exchange-rates": {"title": "Multi-Currency Exchange Rates", "icon": "coins", "entity": "exchange-rates"},
    "vendor-mappings": {"title": "Vendor Company Mappings Matrix", "icon": "network", "entity": "vendor-mappings"},

    # 2. Transaction Processing Suite
    "requisitions": {"title": "Purchase Requisitions (PR)", "icon": "file-text", "entity": "requisitions"},
    "rfqs": {"title": "Request For Quotation (RFQ)", "icon": "send", "entity": "rfqs"},
    "comparative-statements": {"title": "Comparative Statement (CS) Matrix", "icon": "scale", "entity": "comparative-statements"},
    "purchase-orders": {"title": "Purchase Orders (PO)", "icon": "shopping-cart", "entity": "purchase-orders"},
    "goods-returns": {"title": "Goods Return Notes (GRN Return)", "icon": "rotate-ccw", "entity": "goods-returns"},

    # 3. Process, Batch & e-Approval Suite
    "e-approvals": {"title": "Digital e-Approval Hub", "icon": "check-check", "entity": "e-approvals"},
    "lc-operations": {"title": "Letter of Credit (LC) & Forwarding", "icon": "landmark", "entity": "lc-operations"},
    "cnf-dispatches": {"title": "C&F Shipping Document Forwarding", "icon": "container", "entity": "cnf-dispatches"},
    "po-lifecycle": {"title": "PO Lifecycle & Close/Open Management", "icon": "lock", "entity": "po-lifecycle"},

    # 4. Financial & Operational Analysis Suite
    "lc-analysis": {"title": "LC Exposure & Margin Register", "icon": "bar-chart-3", "entity": "lc-analysis"},
    "vendor-scorecards": {"title": "Vendor Performance Scorecard", "icon": "trending-up", "entity": "vendor-scorecards"},
    "spend-analytics": {"title": "Category Spend Analytics", "icon": "pie-chart", "entity": "spend-analytics"},

    # 5. Reporting & Statements Suite
    "three-way-match": {"title": "PR vs PO vs GRN 3-Way Reconciliation", "icon": "check-circle-2", "entity": "three-way-match"},
    "purchase-register": {"title": "Purchase Tax & VAT Register", "icon": "file-spreadsheet", "entity": "purchase-register"},
    "lc-maturity": {"title": "LC Settlement & Maturity Schedule", "icon": "calendar-clock", "entity": "lc-maturity"},
}

@router.get("/modules/{slug}", response_class=HTMLResponse)
async def module_workspace_page(request: Request, slug: str, tab: Optional[str] = Query(None)):
    module = EnterpriseModuleService.get_module_by_slug(slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    active_company = CompanyService.resolve_active_company(request)
    active_cid = str(active_company["id"]) if active_company else None
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    categories = DynamicOptionService.get_categories()
    all_modules = EnterpriseModuleService.get_all_modules()
    grouped_modules = EnterpriseModuleService.get_modules_by_domain()
    
    # Filter transactional records by the globally active company GUID
    records = EnterpriseModuleService.get_module_records(module["module_code"], company_id=str(active_company["id"]))
    db_health = db.check_health()

    # GL Master & Transaction Collections
    gl_coa = []
    gl_mappings = []
    gl_subaccounts = []
    gl_departments = []
    gl_costcentres = []
    gl_budgets = []
    gl_vouchers = []
    gl_batches = []
    gl_templates = []
    gl_auto_profiles = []
    gl_integrity = {"is_healthy": True, "issues": []}
    gl_cost_analysis = {"records": [], "kpis": {}}
    gl_account_balances = {"records": [], "kpis": {}}
    gl_financial_statements = {"balance_sheet": {}, "income_statement": {}}
    gl_trial_balance = {"records": [], "totals": {}}
    gl_transaction_details = []
    gl_cost_centre_pnl = []
    gl_notes_to_accounts = []

    # Cash Book Collections
    cb_cashiers = []
    cb_banks = []
    cb_branches = []
    cb_accounts = []
    cb_receipts = []
    cb_transfers = []

    # Accounts Receivable Collections (Master Setup)
    ar_customers = []
    ar_customer_groups = []
    ar_commercial_groups = []
    ar_group_categories = []
    ar_mappings = []
    ar_ship_addresses = []
    ar_control_sets = []
    ar_reminder_criteria = []
    ar_aging_profiles = []
    ar_adjustment_types = []
    gl_accounts = []

    # Accounts Receivable Collections (Transaction Suite)
    ar_advance_adjustments = []
    ar_general_adjustments = []
    ar_debit_notes_ref = []
    ar_debit_notes_direct = []
    ar_credit_notes_ref = []
    ar_credit_notes_direct = []
    ar_receipts = []
    ar_cancelled_receipts = []

    # Accounts Receivable Collections (Credit Management Process Suite)
    ar_reminder_letters = []
    ar_credit_status = {"records": [], "kpis": {}}

    # Accounts Receivable Collections (Financial Reporting Suite)
    ar_schedule = {"rows": [], "totals": {}}
    ar_statement = {"customer": None, "lines": [], "totals": {}}
    ar_sales_collection = {"rows": [], "totals": {}}
    ar_atb = {"rows": [], "totals": {}}
    ar_collections_register = {"receipts": [], "totals": {}, "mode_breakdown": {}}
    ar_notes_summary = {"notes": [], "totals": {}}
    selected_customer_id = request.query_params.get("customer_id", "")

    # Sourcing & Procurement Collections
    src_vendors = []
    src_enlistments = []
    src_buyers = []
    src_purchasing_orgs = []
    src_price_terms = []
    src_cnf_agents = []
    src_exchange_rates = []
    src_vendor_mappings = []
    src_requisitions = []
    src_rfqs = []
    src_cs_list = []
    src_purchase_orders = []
    src_goods_returns = []
    src_pending_approvals = []
    src_lc_list = []
    src_cnf_dispatches = []
    src_scorecards = []
    src_match_matrix = []
    src_purchase_register = []
    src_kpi_summary = {}

    # Sales Management Collections
    sls_areas = []
    sls_teams = []
    sls_reps = []
    sls_profiles = []
    sls_prices = []
    sls_discount_limits = []
    sls_quotes = []
    sls_orders = []
    sls_do_list = []
    sls_invoices = []
    sls_returns = []
    sls_budgets = []
    sls_doc_flow = []
    sls_approvals = []
    sls_pivot_data = {"monthly_data": [], "total_billed": 0, "total_collected": 0, "total_ar": 0, "collection_efficiency_pct": 100}
    sls_hierarchy_data = []
    sls_target_variance = []
    sls_do_pending_report = []
    sls_consolidated_statement = []
    sls_profitability_report = []
    # Inventory Management Collections
    inv_warehouses = []
    inv_bins = []
    inv_groups = []
    inv_uom_list = []
    inv_items = []
    inv_grn_list = []
    inv_issues = []
    inv_transfers = []
    inv_adjustments = []
    inv_approvals = []
    inv_picking_lists = []
    inv_eod_data = {}
    inv_warranties = []
    inv_stock_matrix = []
    inv_git_list = []
    inv_abc_data = []
    inv_abc_data = []
    inv_product_ledger = []
    inv_valuation_report = {"items": [], "grand_total_valuation": 0, "grand_total_units": 0, "total_skus": 0}
    inv_do_dispatch_report = []
    inv_prod_costing_report = []
    inv_plant_consumption = []
    inv_sto_reports = []
    # Fixed Assets Collections
    fa_groups = []
    fa_locations = []
    fa_sub_locations = []
    fa_policies = []
    fa_gl_control = []
    fa_assets = []
    fa_grn_list = []
    fa_transfers_list = []
    fa_disposals_list = []
    fa_spares_list = []
    fa_depr_runs = []
    fa_depr_sim = {"lines": [], "total_monthly_depr": 0, "total_annual_depr": 0, "eligible_assets_count": 0}
    fa_approvals = []
    fa_audits = []
    fa_summary = {}
    fa_statutory_sched = []

    # HR Master, Employee, Attendance, Payroll & Report Collections
    hr_grades = []
    hr_departments = []
    hr_designations = []
    hr_shifts = []
    hr_holidays = []
    hr_leave_types = []
    hr_bank_accounts = []
    hr_employees = []
    hr_contract_workers = []
    hr_documents = []
    hr_transfers = []
    hr_requisitions = []
    hr_candidates = []
    hr_attendance_logs = []
    hr_leave_applications = []
    hr_overtime_records = []
    hr_payroll_runs = []
    hr_payslips = []
    hr_loan_types = []
    hr_loans = []
    hr_tax_slabs = []
    hr_tax_deposits = []
    hr_summary = {}
    hr_salary_register = []
    hr_bank_advice = []
    hr_pf_ledger = []

    fa_movement_log = []

    if slug == "general-ledger":
        gl_coa = GLMasterService.get_all_accounts()
        gl_mappings = GLMasterService.get_mappings_for_company(str(active_company["id"]))
        gl_subaccounts = GLMasterService.get_all_sub_accounts()
        gl_departments = GLMasterService.get_all_departments()
        gl_costcentres = GLMasterService.get_cost_centres_for_company(str(active_company["id"]))
        gl_budgets = GLMasterService.get_budgets_for_company(str(active_company["id"]))
        gl_vouchers = GLJournalService.get_vouchers_for_company(str(active_company["id"]))
        gl_batches = GLJournalService.get_batches_for_company(str(active_company["id"]))
        gl_templates = GLJournalService.get_templates_for_company(str(active_company["id"]))
        gl_auto_profiles = GLJournalService.get_auto_profiles_for_company(str(active_company["id"]))
        gl_integrity = GLProcessService.check_data_integrity(str(active_company["id"]))
        gl_cost_analysis = GLAnalysisService.get_cost_analysis(str(active_company["id"]))
        gl_account_balances = GLAnalysisService.get_account_balance_inquiry(str(active_company["id"]))
        gl_financial_statements = GLReportService.get_financial_statements(str(active_company["id"]))
        gl_trial_balance = GLReportService.get_trial_balance_suite(str(active_company["id"]))
        gl_transaction_details = GLReportService.get_transaction_details_report(str(active_company["id"]))
        gl_cost_centre_pnl = GLReportService.get_cost_centre_pnl(str(active_company["id"]))
        gl_notes_to_accounts = GLReportService.get_notes_to_accounts(str(active_company["id"]))

    elif slug == "cash-book":
        cb_cashiers = CashBookService.get_cashiers(str(active_company["id"]))
        cb_banks = CashBookService.get_banks()
        cb_branches = CashBookService.get_branches()
        cb_accounts = CashBookService.get_bank_accounts(str(active_company["id"]))
        cb_receipts = CashBookService.get_money_receipts(str(active_company["id"]))
        cb_transfers = CashBookService.get_contra_transfers(str(active_company["id"]))

    elif slug == "accounts-receivable":
        ar_customers = ARMasterService.get_all_customers()
        ar_customer_groups = ARMasterService.get_ar_customer_groups()
        ar_commercial_groups = ARMasterService.get_commercial_groups()
        ar_group_categories = ARMasterService.get_group_categories()
        ar_mappings = ARMasterService.get_customer_company_mappings(str(active_company["id"]))
        ar_ship_addresses = ARMasterService.get_ship_to_addresses()
        ar_control_sets = ARMasterService.get_control_account_sets(str(active_company["id"]))
        ar_reminder_criteria = ARMasterService.get_reminder_criteria()
        ar_aging_profiles = ARMasterService.get_aging_profiles()
        ar_adjustment_types = ARMasterService.get_adjustment_types()
        gl_accounts = GLMasterService.get_all_accounts()

        # Load Transaction Collections
        ar_advance_adjustments = ARTransactionService.get_advance_adjustments(str(active_company["id"]))
        ar_general_adjustments = ARTransactionService.get_general_adjustments(str(active_company["id"]))
        ar_debit_notes_ref = ARTransactionService.get_debit_notes_with_ref(str(active_company["id"]))
        ar_debit_notes_direct = ARTransactionService.get_debit_notes_direct(str(active_company["id"]))
        ar_credit_notes_ref = ARTransactionService.get_credit_notes_with_ref(str(active_company["id"]))
        ar_credit_notes_direct = ARTransactionService.get_credit_notes_direct(str(active_company["id"]))
        ar_receipts = ARTransactionService.get_active_money_receipts(str(active_company["id"]))
        ar_cancelled_receipts = ARTransactionService.get_cancelled_money_receipts(str(active_company["id"]))

        # Load Credit Management Process Collections
        ar_reminder_letters = ARProcessService.get_reminder_letters(str(active_company["id"]))
        ar_credit_status = ARProcessService.get_due_overdue_status(str(active_company["id"]))

        # Load Financial Reporting Collections
        if not selected_customer_id and ar_customers:
            selected_customer_id = str(ar_customers[0]["id"])
        
        ar_schedule = ARReportService.get_ar_schedule_report(str(active_company["id"]))
        if selected_customer_id:
            ar_statement = ARReportService.get_customer_statement(selected_customer_id, company_id=str(active_company["id"]))
        ar_sales_collection = ARReportService.get_sales_collection_outstanding(str(active_company["id"]))
        ar_atb = ARReportService.get_aged_trial_balance(str(active_company["id"]))
        ar_collections_register = ARReportService.get_collections_register(str(active_company["id"]))
        ar_notes_summary = ARReportService.get_notes_summary_report(str(active_company["id"]))

    elif slug == "sourcing":
        src_vendors = SourcingMasterService.get_all_vendors()
        src_enlistments = SourcingMasterService.get_all_enlistments()
        src_buyers = SourcingMasterService.get_all_buyers()
        src_purchasing_orgs = SourcingMasterService.get_purchasing_orgs()
        src_price_terms = SourcingMasterService.get_price_terms()
        src_cnf_agents = SourcingMasterService.get_cnf_agents()
        src_exchange_rates = SourcingMasterService.get_exchange_rates()
        src_vendor_mappings = SourcingMasterService.get_vendor_company_mappings(str(active_company["id"]))

        src_requisitions = SourcingTransactionService.get_requisitions(company_id=str(active_company["id"]))
        src_rfqs = SourcingTransactionService.get_rfqs(company_id=str(active_company["id"]))
        src_cs_list = SourcingTransactionService.get_comparative_statements(company_id=str(active_company["id"]))
        src_purchase_orders = SourcingTransactionService.get_purchase_orders(company_id=str(active_company["id"]))
        src_goods_returns = SourcingTransactionService.get_goods_returns(company_id=str(active_company["id"]))

        src_pending_approvals = SourcingProcessService.get_pending_approvals(company_id=str(active_company["id"]))
        src_lc_list = SourcingProcessService.get_letters_of_credit(company_id=str(active_company["id"]))
        src_cnf_dispatches = SourcingProcessService.get_cnf_dispatches(company_id=str(active_company["id"]))

        src_kpi_summary = SourcingAnalyticsService.get_sourcing_kpi_summary(company_id=str(active_company["id"]))
        src_scorecards = SourcingAnalyticsService.get_vendor_scorecards()

        src_match_matrix = SourcingReportService.get_three_way_reconciliation_matrix(company_id=str(active_company["id"]))
        src_purchase_register = SourcingReportService.get_purchase_register(company_id=str(active_company["id"]))


    elif slug in ("inventory", "inventory-management"):
        active_cid = str(active_company["id"]) if active_company else None
        inv_warehouses = InvMasterService.get_warehouses(active_cid)
        inv_bins = InvMasterService.get_bins()
        inv_groups = InvMasterService.get_product_groups(active_cid)
        inv_uom_list = InvMasterService.get_uom_list(active_cid)
        inv_items = InvMasterService.get_items(active_cid)

        inv_grn_list = InvTransactionService.get_grn_list(active_cid)
        inv_issues = InvTransactionService.get_issues(active_cid)
        inv_transfers = InvTransactionService.get_stock_transfers(active_cid)
        inv_adjustments = InvTransactionService.get_adjustments(active_cid)

        inv_approvals = InvProcessService.get_pending_approvals(active_cid)
        inv_picking_lists = InvProcessService.get_active_picking_lists(active_cid)
        inv_eod_data = InvProcessService.execute_day_end_closing()

        inv_warranties = InvWarrantyService.get_warranties(active_cid)

        inv_stock_matrix = InvAnalysisService.get_stock_balance_matrix(active_cid)
        inv_git_list = InvAnalysisService.get_goods_in_transit(active_cid)
        inv_abc_data = InvAnalysisService.get_abc_analysis(active_cid)

        inv_product_ledger = InvReportService.get_product_ledger(active_cid)
        inv_valuation_report = InvReportService.get_inventory_valuation_report(active_cid)
        inv_do_dispatch_report = InvReportService.get_do_vs_actual_delivery_report(active_cid)
        inv_prod_costing_report = InvReportService.get_production_costing_report(active_cid)
        inv_plant_consumption = InvReportService.get_plant_wise_consumption(active_cid)
        inv_sto_reports = InvReportService.get_sto_transfer_statement(active_cid)

    elif module["route_slug"] in ("hris", "hr", "human-resources", "human-capital"):
        hr_grades = HRMasterService.get_grades(active_cid)
        hr_departments = HRMasterService.get_departments(active_cid)
        hr_designations = HRMasterService.get_designations(active_cid)
        hr_shifts = HRMasterService.get_shifts(active_cid)
        hr_holidays = HRMasterService.get_holidays(active_cid)
        hr_leave_types = HRMasterService.get_leave_types(active_cid)
        hr_bank_accounts = HRMasterService.get_bank_accounts(active_cid)

        hr_employees = HREmployeeService.get_employees(active_cid)
        hr_contract_workers = HREmployeeService.get_contract_workers(active_cid)
        hr_documents = HREmployeeService.get_documents()
        hr_transfers = HREmployeeService.get_transfers(active_cid)
        hr_requisitions = HRRecruitmentService.get_job_requisitions(active_cid)
        hr_candidates = HRRecruitmentService.get_candidates()

        hr_attendance_logs = HRAttendanceService.get_attendance_logs(active_cid)
        hr_leave_applications = HRAttendanceService.get_leave_applications(active_cid)
        hr_overtime_records = HRAttendanceService.get_overtime_records(active_cid)

        hr_payroll_runs = HRPayrollService.get_payroll_runs(active_cid)
        hr_payslips = HRPayrollService.get_payslips(company_id=active_cid)
        hr_loan_types = HRPayrollService.get_loan_types(active_cid)
        hr_loans = HRPayrollService.get_loans(active_cid)
        hr_tax_slabs = HRPayrollService.get_tax_slabs(active_cid)
        hr_tax_deposits = HRPayrollService.get_tax_deposits(active_cid)

        hr_summary = HRReportService.get_executive_summary(active_cid)
        hr_salary_register = HRReportService.get_salary_register(active_cid)
        hr_bank_advice = HRReportService.get_bank_advice(active_cid)
        hr_pf_ledger = HRReportService.get_pf_ledger(active_cid)

    elif module["route_slug"] in ("fixed-assets", "fixed-asset-management"):
        fa_groups = FAMasterService.get_asset_groups(active_cid)
        fa_locations = FAMasterService.get_locations(active_cid)
        fa_sub_locations = FAMasterService.get_sub_locations()
        fa_policies = FAMasterService.get_depreciation_policies(active_cid)
        fa_gl_control = FAMasterService.get_gl_control_sets(active_cid)

        fa_assets = FAAssetService.get_assets(active_cid)
        fa_grn_list = FAAssetService.get_asset_grns(active_cid)
        fa_transfers_list = FAAssetService.get_transfers(active_cid)
        fa_disposals_list = FAAssetService.get_disposals(active_cid)
        fa_spares_list = FAAssetService.get_spares_mapping(active_cid)

        fa_depr_runs = FADepreciationService.get_depreciation_runs(active_cid)
        fa_depr_sim = FADepreciationService.get_depreciation_simulation(active_cid)
        fa_approvals = FADepreciationService.get_approvals(active_cid)

        fa_audits = FAVerificationService.get_physical_audits(active_cid)

        fa_summary = FAReportService.get_summary_of_fixed_assets(active_cid)
        fa_statutory_sched = FAReportService.get_statutory_asset_schedule(active_cid)
        fa_movement_log = FAReportService.get_asset_movement_report(active_cid)

    elif slug in ("sales", "sales-management"):
        sls_areas = SalesMasterService.get_sales_areas(company_id=str(active_company["id"]))
        sls_teams = SalesMasterService.get_sales_teams(company_id=str(active_company["id"]))
        sls_reps = SalesMasterService.get_salespersons(company_id=str(active_company["id"]))
        sls_profiles = SalesMasterService.get_price_profiles(company_id=str(active_company["id"]))
        sls_prices = SalesMasterService.get_product_prices()
        sls_discount_limits = SalesMasterService.get_discount_limits()

        sls_quotes = SalesTransactionService.get_quotes(company_id=str(active_company["id"]))
        sls_orders = SalesTransactionService.get_orders(company_id=str(active_company["id"]))
        sls_do_list = SalesTransactionService.get_delivery_orders(company_id=str(active_company["id"]))
        sls_invoices = SalesTransactionService.get_invoices(company_id=str(active_company["id"]))
        sls_returns = db.query("SELECT * FROM sales_returns WHERE company_id = ? ORDER BY code DESC", (str(active_company["id"]),))
        sls_budgets = db.query("SELECT b.*, sp.full_name AS salesperson_name FROM sales_budgets b LEFT JOIN salespersons sp ON b.salesperson_id = sp.id WHERE b.company_id = ? ORDER BY b.code ASC", (str(active_company["id"]),))

        sls_doc_flow = SalesProcessService.get_document_flow()
        sls_approvals = db.query("SELECT * FROM sales_approvals WHERE entity_type = 'SO' ORDER BY code DESC")

        sls_pivot_data = SalesAnalysisService.get_sales_collection_pivot(company_id=str(active_company["id"]))
        sls_hierarchy_data = SalesAnalysisService.get_hierarchical_performance(company_id=str(active_company["id"]))
        sls_target_variance = SalesAnalysisService.get_target_vs_achievement(company_id=str(active_company["id"]))

        sls_do_pending_report = SalesReportService.get_do_invoice_pending_report(company_id=str(active_company["id"]))
        sls_consolidated_statement = SalesReportService.get_consolidated_statement()
        sls_profitability_report = SalesReportService.get_profitability_report()

    current_tab = tab if tab else "overview"

    # Multi-level dynamic title, icon, breadcrumbs, and back navigation
    all_sub_areas = {**GL_SUB_AREAS, **CB_SUB_AREAS, **AR_SUB_AREAS, **SOURCING_SUB_AREAS, **SALES_SUB_AREAS}
    if current_tab in all_sub_areas and current_tab != "overview":
        sub_info = all_sub_areas[current_tab]
        current_page_title = sub_info["title"]
        current_page_icon = sub_info["icon"]
        is_sub_page = True
        back_url = f"/modules/{slug}"
        back_title = f"Back to {module['name']} Master Hub"
        breadcrumbs = [
            {"title": "Home", "url": "/"},
            {"title": module["domain_group"], "url": "/"},
            {"title": module["name"], "url": f"/modules/{slug}"},
            {"title": sub_info["title"], "url": None}
        ]
    else:
        current_page_title = module["name"]
        current_page_icon = module["icon"]
        is_sub_page = False
        back_url = "/"
        back_title = "Back to Home"
        breadcrumbs = [
            {"title": "Home", "url": "/"},
            {"title": module["domain_group"], "url": "/"},
            {"title": module["name"], "url": None}
        ]

    context_counts = {
        "gl_coa_count": len(gl_coa),
        "gl_mapping_count": len(gl_mappings),
        "gl_subaccount_count": len(gl_subaccounts),
        "gl_dept_count": len(gl_departments),
        "gl_costcentre_count": len(gl_costcentres),
        "gl_voucher_count": len(gl_vouchers),
        "gl_auto_profile_count": len(gl_auto_profiles),
        "gl_template_count": len(gl_templates),
        "gl_batch_count": len(gl_batches),
        "gl_budget_count": len(gl_budgets),
        "gl_integrity_label": gl_integrity.get("status_label", "100% HEALTHY"),
        "gl_cost_spent": f"${gl_cost_analysis.get('kpis', {}).get('total_actual_spent', 0.0):,.0f}",
        "ar_customers_count": len(ar_customers),
        "ar_customer_groups_count": len(ar_customer_groups),
        "ar_commercial_groups_count": len(ar_commercial_groups),
        "ar_group_categories_count": len(ar_group_categories),
        "ar_mappings_count": len(ar_mappings),
        "ar_ship_addresses_count": len(ar_ship_addresses),
        "ar_control_sets_count": len(ar_control_sets),
        "ar_reminder_criteria_count": len(ar_reminder_criteria),
        "ar_aging_profiles_count": len(ar_aging_profiles),
        "ar_adjustment_types_count": len(ar_adjustment_types),
        "ar_dunning_count": len(ar_reminder_letters),
        "cb_cashier_count": len(cb_cashiers),
        "cb_bank_count": len(cb_banks),
        "cb_branch_count": len(cb_branches),
        "cb_account_count": len(cb_accounts),
        "cb_receipt_count": len(cb_receipts),
        "src_vendors_count": len(src_vendors),
        "src_enlistments_count": len(src_enlistments),
        "src_buyers_count": len(src_buyers),
        "src_orgs_count": len(src_purchasing_orgs),
        "src_terms_count": len(src_price_terms),
        "src_cnf_count": len(src_cnf_agents),
        "src_pr_count": len(src_requisitions),
        "src_rfq_count": len(src_rfqs),
        "src_po_count": len(src_purchase_orders),
        "sls_teams_count": len(sls_teams),
        "sls_reps_count": len(sls_reps),
        "sls_areas_count": len(sls_areas),
        "sls_profiles_count": len(sls_profiles),
        "sls_prices_count": len(sls_prices),
        "sls_quotes_count": len(sls_quotes),
        "sls_orders_count": len(sls_orders),
        "sls_do_count": len(sls_do_list),
        "sls_inv_count": len(sls_invoices),
        "sls_returns_count": len(sls_returns),
        "sls_budgets_count": len(sls_budgets),
        "sls_on_hold_count": len([o for o in sls_orders if o.get("is_on_hold") or o.get("status") == "ON_HOLD"]),
        "inv_wh_count": len(inv_warehouses),
        "inv_bin_count": len(inv_bins),
        "inv_group_count": len(inv_groups),
        "inv_uom_count": len(inv_uom_list),
        "inv_item_count": len(inv_items),
        "inv_grn_count": len(inv_grn_list),
        "inv_issue_count": len(inv_issues),
        "inv_sto_count": len(inv_transfers),
        "inv_adj_count": len(inv_adjustments),
        "inv_warranty_count": len(inv_warranties),
        "inv_git_count": len(inv_git_list),
        "src_returns_count": len(src_goods_returns),
        "src_pending_approvals": len(src_pending_approvals),
        "src_lc_count": len(src_lc_list),
        "src_dispatches_count": len(src_cnf_dispatches),
        "src_lc_total": f"${src_kpi_summary.get('total_lc_amount', 0):,.0f}",
    }
    module_suites = get_module_suites_registry(slug, context_counts)
    active_suite = get_active_suite_context(slug, current_tab, module_suites)

    return templates.TemplateResponse(
        request=request,
        name="pages/module_workspace.html",
        context={
            "module": module,
            "module_suites": module_suites,
            "active_suite": active_suite,
            "records": records,
            "current_tab": current_tab,
            "current_page_title": current_page_title,
            "current_page_icon": current_page_icon,
            "is_sub_page": is_sub_page,
            "back_url": back_url,
            "back_title": back_title,
            "gl_coa": gl_coa,
            "gl_mappings": gl_mappings,
            "gl_subaccounts": gl_subaccounts,
            "gl_departments": gl_departments,
            "gl_costcentres": gl_costcentres,
            "gl_budgets": gl_budgets,
            "gl_vouchers": gl_vouchers,
            "gl_batches": gl_batches,
            "gl_templates": gl_templates,
            "gl_auto_profiles": gl_auto_profiles,
            "gl_integrity": gl_integrity,
            "gl_cost_analysis": gl_cost_analysis,
            "gl_account_balances": gl_account_balances,
            "gl_financial_statements": gl_financial_statements,
            "gl_trial_balance": gl_trial_balance,
            "gl_transaction_details": gl_transaction_details,
            "gl_cost_centre_pnl": gl_cost_centre_pnl,
            "gl_notes_to_accounts": gl_notes_to_accounts,
            "cb_cashiers": cb_cashiers,
            "cb_banks": cb_banks,
            "cb_branches": cb_branches,
            "cb_accounts": cb_accounts,
            "cb_receipts": cb_receipts,
            "cb_transfers": cb_transfers,
            "ar_customers": ar_customers,
            "ar_customer_groups": ar_customer_groups,
            "ar_commercial_groups": ar_commercial_groups,
            "ar_group_categories": ar_group_categories,
            "ar_mappings": ar_mappings,
            "ar_ship_addresses": ar_ship_addresses,
            "ar_control_sets": ar_control_sets,
            "ar_reminder_criteria": ar_reminder_criteria,
            "ar_aging_profiles": ar_aging_profiles,
            "ar_adjustment_types": ar_adjustment_types,
            "ar_advance_adjustments": ar_advance_adjustments,
            "ar_general_adjustments": ar_general_adjustments,
            "ar_debit_notes_ref": ar_debit_notes_ref,
            "ar_debit_notes_direct": ar_debit_notes_direct,
            "ar_credit_notes_ref": ar_credit_notes_ref,
            "ar_credit_notes_direct": ar_credit_notes_direct,
            "ar_receipts": ar_receipts,
            "ar_cancelled_receipts": ar_cancelled_receipts,
            "ar_reminder_letters": ar_reminder_letters,
            "ar_credit_status": ar_credit_status,
            "ar_schedule": ar_schedule,
            "ar_statement": ar_statement,
            "ar_sales_collection": ar_sales_collection,
            "ar_atb": ar_atb,
            "ar_collections_register": ar_collections_register,
            "ar_notes_summary": ar_notes_summary,
            "selected_customer_id": selected_customer_id,
            "gl_accounts": gl_accounts,
            "src_vendors": src_vendors,
            "src_enlistments": src_enlistments,
            "src_buyers": src_buyers,
            "src_purchasing_orgs": src_purchasing_orgs,
            "src_price_terms": src_price_terms,
            "src_cnf_agents": src_cnf_agents,
            "src_exchange_rates": src_exchange_rates,
            "src_vendor_mappings": src_vendor_mappings,
            "src_requisitions": src_requisitions,
            "src_rfqs": src_rfqs,
            "src_cs_list": src_cs_list,
            "src_purchase_orders": src_purchase_orders,
            "src_goods_returns": src_goods_returns,
            "src_pending_approvals": src_pending_approvals,
            "src_lc_list": src_lc_list,
            "src_cnf_dispatches": src_cnf_dispatches,
            "src_scorecards": src_scorecards,
            "src_match_matrix": src_match_matrix,
        "sls_areas": sls_areas,
        "sls_teams": sls_teams,
        "sls_reps": sls_reps,
        "sls_profiles": sls_profiles,
        "sls_prices": sls_prices,
        "sls_discount_limits": sls_discount_limits,
        "sls_quotes": sls_quotes,
        "sls_orders": sls_orders,
        "sls_do_list": sls_do_list,
        "sls_invoices": sls_invoices,
        "sls_returns": sls_returns,
        "sls_budgets": sls_budgets,
        "sls_doc_flow": sls_doc_flow,
        "sls_approvals": sls_approvals,
        "sls_pivot_data": sls_pivot_data,
        "sls_hierarchy_data": sls_hierarchy_data,
        "sls_target_variance": sls_target_variance,
        "sls_do_pending_report": sls_do_pending_report,
        "sls_consolidated_statement": sls_consolidated_statement,
        "sls_profitability_report": sls_profitability_report,
            "inv_warehouses": inv_warehouses,
            "inv_bins": inv_bins,
            "inv_groups": inv_groups,
            "inv_uom_list": inv_uom_list,
            "inv_items": inv_items,
            "inv_grn_list": inv_grn_list,
            "inv_issues": inv_issues,
            "inv_transfers": inv_transfers,
            "inv_adjustments": inv_adjustments,
            "inv_approvals": inv_approvals,
            "inv_picking_lists": inv_picking_lists,
            "inv_eod_data": inv_eod_data,
            "inv_warranties": inv_warranties,
            "inv_stock_matrix": inv_stock_matrix,
            "inv_git_list": inv_git_list,
            "inv_abc_data": inv_abc_data,
            "inv_product_ledger": inv_product_ledger,
            "inv_valuation_report": inv_valuation_report,
            "inv_do_dispatch_report": inv_do_dispatch_report,
            "inv_prod_costing_report": inv_prod_costing_report,
            "inv_plant_consumption": inv_plant_consumption,
            "inv_sto_reports": inv_sto_reports,
            "fa_groups": fa_groups,
            "fa_locations": fa_locations,
            "fa_sub_locations": fa_sub_locations,
            "fa_policies": fa_policies,
            "fa_gl_control": fa_gl_control,
            "fa_assets": fa_assets,
            "fa_grn_list": fa_grn_list,
            "fa_transfers_list": fa_transfers_list,
            "fa_disposals_list": fa_disposals_list,
            "fa_spares_list": fa_spares_list,
            "fa_depr_runs": fa_depr_runs,
            "fa_depr_sim": fa_depr_sim,
            "fa_approvals": fa_approvals,
            "fa_audits": fa_audits,
            "fa_summary": fa_summary,
            "fa_statutory_sched": fa_statutory_sched,
            "fa_movement_log": fa_movement_log,
            "hr_grades": hr_grades,
            "hr_departments": hr_departments,
            "hr_designations": hr_designations,
            "hr_shifts": hr_shifts,
            "hr_holidays": hr_holidays,
            "hr_leave_types": hr_leave_types,
            "hr_bank_accounts": hr_bank_accounts,
            "hr_employees": hr_employees,
            "hr_contract_workers": hr_contract_workers,
            "hr_documents": hr_documents,
            "hr_transfers": hr_transfers,
            "hr_requisitions": hr_requisitions,
            "hr_candidates": hr_candidates,
            "hr_attendance_logs": hr_attendance_logs,
            "hr_leave_applications": hr_leave_applications,
            "hr_overtime_records": hr_overtime_records,
            "hr_payroll_runs": hr_payroll_runs,
            "hr_payslips": hr_payslips,
            "hr_loan_types": hr_loan_types,
            "hr_loans": hr_loans,
            "hr_tax_slabs": hr_tax_slabs,
            "hr_tax_deposits": hr_tax_deposits,
            "hr_summary": hr_summary,
            "hr_salary_register": hr_salary_register,
            "hr_bank_advice": hr_bank_advice,
            "hr_pf_ledger": hr_pf_ledger,
            "src_purchase_register": src_purchase_register,
            "src_kpi_summary": src_kpi_summary,
            "current_user": UserService.resolve_current_user(request),
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "categories": categories,
            "all_modules": all_modules,
            "grouped_modules": grouped_modules,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": f"module_{slug}"
        }
    )

# =========================================================================
# Solid Transaction Entry Pages
# =========================================================================
@router.get("/modules/{slug}/new", response_class=HTMLResponse)
async def new_module_record_page(request: Request, slug: str):
    module = EnterpriseModuleService.get_module_by_slug(slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": module["domain_group"], "url": "/"},
        {"title": module["name"], "url": f"/modules/{slug}"},
        {"title": "New Transaction Entry", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/record_create.html",
        context={
            "module": module,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": f"module_{slug}"
        }
    )

@router.post("/modules/{slug}/new")
async def handle_new_record_submit(
    request: Request,
    slug: str,
    module_code: str = Form(...),
    record_type: str = Form("ENTRY"),
    ref_number: str = Form(...),
    title: str = Form(...),
    status: str = Form("COMPLETED"),
    amount: float = Form(0.0),
    party_name: str = Form(""),
    created_by: str = Form("Operator Admin")
):
    active_company = CompanyService.resolve_active_company(request)
    EnterpriseModuleService.add_module_record(
        company_id=str(active_company["id"]),
        module_code=module_code,
        record_type=record_type,
        ref_number=ref_number,
        title=title,
        status=status,
        amount=amount,
        party_name=party_name,
        created_by=created_by
    )
    return RedirectResponse(url=f"/modules/{slug}", status_code=303)

# =========================================================================
# Solid GL Master Data Creation Pages (/modules/general-ledger/master/{entity}/new)
# =========================================================================
@router.get("/modules/general-ledger/master/{entity}/new", response_class=HTMLResponse)
async def new_gl_master_record_page(request: Request, entity: str):
    module = EnterpriseModuleService.get_module_by_slug("general-ledger")
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    entity_titles = {
        "gl-accounts": "GL Account (Chart of Accounts)",
        "company-mappings": "GL Account Mapping with Company",
        "sub-accounts": "GL Sub Account",
        "departments": "Department",
        "cost-centres": "Cost Centre",
        "budget-sets": "Budget Set"
    }

    if entity not in entity_titles:
        raise HTTPException(status_code=404, detail="Master Data entity not found")

    # Options needed for selects
    all_accounts = GLMasterService.get_all_accounts()
    all_departments = GLMasterService.get_all_departments()
    all_cost_centres = GLMasterService.get_cost_centres_for_company(str(active_company["id"]))
    all_companies = CompanyService.get_all_companies()

    entity_to_tab = {
        "gl-accounts": "coa",
        "company-mappings": "mapping",
        "sub-accounts": "subaccounts",
        "departments": "departments",
        "cost-centres": "costcentres",
        "budget-sets": "budgets"
    }
    sub_tab = entity_to_tab.get(entity, "overview")
    sub_title = GL_SUB_AREAS.get(sub_tab, {}).get("title", entity_titles.get(entity, "List"))

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "General Ledger", "url": "/modules/general-ledger"},
        {"title": sub_title, "url": f"/modules/general-ledger?tab={sub_tab}"},
        {"title": f"New {entity_titles[entity]}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/gl_master_create.html",
        context={
            "module": module,
            "entity": entity,
            "sub_tab": sub_tab,
            "entity_title": entity_titles[entity],
            "all_accounts": all_accounts,
            "all_departments": all_departments,
            "all_cost_centres": all_cost_centres,
            "all_companies": all_companies,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_general-ledger"
        }
    )

@router.post("/modules/general-ledger/master/{entity}/new")
async def handle_new_gl_master_submit(
    request: Request,
    entity: str,
    # GL Account fields
    account_number: Optional[str] = Form(None),
    account_name: Optional[str] = Form(None),
    account_type: Optional[str] = Form(None),
    financial_statement: Optional[str] = Form(None),
    normal_balance: Optional[str] = Form(None),
    # Company Mapping fields
    gl_account_id: Optional[str] = Form(None),
    company_id: Optional[str] = Form(None),
    company_account_alias: Optional[str] = Form(None),
    posting_currency: Optional[str] = Form("USD"),
    # Sub Account fields
    sub_account_code: Optional[str] = Form(None),
    sub_account_name: Optional[str] = Form(None),
    sub_account_type: Optional[str] = Form(None),
    # Department fields
    dept_code: Optional[str] = Form(None),
    dept_name: Optional[str] = Form(None),
    head_of_dept: Optional[str] = Form(None),
    # Cost Centre fields
    cost_centre_code: Optional[str] = Form(None),
    cost_centre_name: Optional[str] = Form(None),
    department_id: Optional[str] = Form(None),
    # Budget Set fields
    budget_code: Optional[str] = Form(None),
    budget_title: Optional[str] = Form(None),
    fiscal_year: Optional[str] = Form(None),
    cost_centre_id: Optional[str] = Form(None),
    allocated_amount: Optional[float] = Form(0.0),
    budget_status: Optional[str] = Form("APPROVED")
):
    active_company = CompanyService.resolve_active_company(request)
    target_tab = "transactions"

    if entity == "gl-accounts" and account_number and account_name:
        GLMasterService.create_account(account_number, account_name, account_type or "ASSET", financial_statement or "BALANCE_SHEET", normal_balance or "DEBIT")
        target_tab = "coa"
    elif entity == "company-mappings" and gl_account_id:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.create_company_mapping(gl_account_id, target_comp, company_account_alias or "", posting_currency or "USD")
        target_tab = "mapping"
    elif entity == "sub-accounts" and gl_account_id and sub_account_code and sub_account_name:
        GLMasterService.create_sub_account(gl_account_id, sub_account_code, sub_account_name, sub_account_type or "DEPARTMENTAL")
        target_tab = "subaccounts"
    elif entity == "departments" and dept_code and dept_name:
        GLMasterService.create_department(dept_code, dept_name, head_of_dept or "")
        target_tab = "departments"
    elif entity == "cost-centres" and cost_centre_code and cost_centre_name:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.create_cost_centre(cost_centre_code, cost_centre_name, department_id, target_comp)
        target_tab = "costcentres"
    elif entity == "budget-sets" and budget_code and budget_title and gl_account_id:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.create_budget_set(
            budget_code, budget_title, fiscal_year or active_company["fiscal_year"], target_comp, cost_centre_id, gl_account_id, allocated_amount or 0.0, budget_status or "APPROVED"
        )
        target_tab = "budgets"

    return RedirectResponse(url=f"/modules/general-ledger?tab={target_tab}", status_code=303)

# =========================================================================
# Solid GL Master Data Edit Pages (/modules/general-ledger/master/{entity}/{record_id}/edit)
# =========================================================================
@router.get("/modules/general-ledger/master/{entity}/{record_id}/edit", response_class=HTMLResponse)
async def edit_gl_master_record_page(request: Request, entity: str, record_id: str):
    module = EnterpriseModuleService.get_module_by_slug("general-ledger")
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    entity_titles = {
        "gl-accounts": "GL Account (Chart of Accounts)",
        "company-mappings": "GL Account Mapping with Company",
        "sub-accounts": "GL Sub Account",
        "departments": "Department",
        "cost-centres": "Cost Centre",
        "budget-sets": "Budget Set"
    }

    if entity not in entity_titles:
        raise HTTPException(status_code=404, detail="Master Data entity not found")

    record = None
    if entity == "gl-accounts":
        record = GLMasterService.get_account_by_id(record_id)
    elif entity == "company-mappings":
        record = GLMasterService.get_mapping_by_id(record_id)
    elif entity == "sub-accounts":
        record = GLMasterService.get_sub_account_by_id(record_id)
    elif entity == "departments":
        record = GLMasterService.get_department_by_id(record_id)
    elif entity == "cost-centres":
        record = GLMasterService.get_cost_centre_by_id(record_id)
    elif entity == "budget-sets":
        record = GLMasterService.get_budget_set_by_id(record_id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    all_accounts = GLMasterService.get_all_accounts()
    all_departments = GLMasterService.get_all_departments()
    all_cost_centres = GLMasterService.get_cost_centres_for_company(str(active_company["id"]))
    all_companies = CompanyService.get_all_companies()

    entity_to_tab = {
        "gl-accounts": "coa",
        "company-mappings": "mapping",
        "sub-accounts": "subaccounts",
        "departments": "departments",
        "cost-centres": "costcentres",
        "budget-sets": "budgets"
    }
    sub_tab = entity_to_tab.get(entity, "overview")
    sub_title = GL_SUB_AREAS.get(sub_tab, {}).get("title", entity_titles.get(entity, "List"))

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "General Ledger", "url": "/modules/general-ledger"},
        {"title": sub_title, "url": f"/modules/general-ledger?tab={sub_tab}"},
        {"title": f"Edit {entity_titles[entity]}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/gl_master_create.html",
        context={
            "module": module,
            "entity": entity,
            "sub_tab": sub_tab,
            "entity_title": entity_titles[entity],
            "record": record,
            "record_id": record_id,
            "is_edit_mode": True,
            "all_accounts": all_accounts,
            "all_departments": all_departments,
            "all_cost_centres": all_cost_centres,
            "all_companies": all_companies,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_general-ledger"
        }
    )

@router.post("/modules/general-ledger/master/{entity}/{record_id}/edit")
async def handle_edit_gl_master_submit(
    request: Request,
    entity: str,
    record_id: str,
    # GL Account fields
    account_number: Optional[str] = Form(None),
    account_name: Optional[str] = Form(None),
    account_type: Optional[str] = Form(None),
    financial_statement: Optional[str] = Form(None),
    normal_balance: Optional[str] = Form(None),
    # Company Mapping fields
    gl_account_id: Optional[str] = Form(None),
    company_id: Optional[str] = Form(None),
    company_account_alias: Optional[str] = Form(None),
    posting_currency: Optional[str] = Form("USD"),
    # Sub Account fields
    sub_account_code: Optional[str] = Form(None),
    sub_account_name: Optional[str] = Form(None),
    sub_account_type: Optional[str] = Form(None),
    # Department fields
    dept_code: Optional[str] = Form(None),
    dept_name: Optional[str] = Form(None),
    head_of_dept: Optional[str] = Form(None),
    # Cost Centre fields
    cost_centre_code: Optional[str] = Form(None),
    cost_centre_name: Optional[str] = Form(None),
    department_id: Optional[str] = Form(None),
    # Budget Set fields
    budget_code: Optional[str] = Form(None),
    budget_title: Optional[str] = Form(None),
    fiscal_year: Optional[str] = Form(None),
    cost_centre_id: Optional[str] = Form(None),
    allocated_amount: Optional[float] = Form(0.0),
    budget_status: Optional[str] = Form("APPROVED")
):
    active_company = CompanyService.resolve_active_company(request)
    target_tab = "transactions"

    if entity == "gl-accounts" and account_number and account_name:
        GLMasterService.update_account(record_id, account_number, account_name, account_type or "ASSET", financial_statement or "BALANCE_SHEET", normal_balance or "DEBIT")
        target_tab = "coa"
    elif entity == "company-mappings" and gl_account_id:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.update_company_mapping(record_id, gl_account_id, target_comp, company_account_alias or "", posting_currency or "USD")
        target_tab = "mapping"
    elif entity == "sub-accounts" and gl_account_id and sub_account_code and sub_account_name:
        GLMasterService.update_sub_account(record_id, gl_account_id, sub_account_code, sub_account_name, sub_account_type or "DEPARTMENTAL")
        target_tab = "subaccounts"
    elif entity == "departments" and dept_code and dept_name:
        GLMasterService.update_department(record_id, dept_code, dept_name, head_of_dept or "")
        target_tab = "departments"
    elif entity == "cost-centres" and cost_centre_code and cost_centre_name:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.update_cost_centre(record_id, cost_centre_code, cost_centre_name, department_id, target_comp)
        target_tab = "costcentres"
    elif entity == "budget-sets" and budget_title and gl_account_id:
        target_comp = company_id or str(active_company["id"])
        GLMasterService.update_budget_set(
            record_id, budget_title, fiscal_year or active_company["fiscal_year"], target_comp, cost_centre_id, gl_account_id, allocated_amount or 0.0, budget_status or "APPROVED"
        )
        target_tab = "budgets"

    return RedirectResponse(url=f"/modules/general-ledger?tab={target_tab}", status_code=303)

# =========================================================================
# Solid Transaction Entry Edit Pages (/modules/{slug}/records/{record_id}/edit)
# =========================================================================
@router.get("/modules/{slug}/records/{record_id}/edit", response_class=HTMLResponse)
async def edit_module_record_page(request: Request, slug: str, record_id: str):
    module = EnterpriseModuleService.get_module_by_slug(slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    record = EnterpriseModuleService.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Transaction record not found")

    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": module["domain_group"], "url": "/"},
        {"title": module["name"], "url": f"/modules/{slug}"},
        {"title": f"Edit Entry #{record['code']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/record_create.html",
        context={
            "module": module,
            "record": record,
            "record_id": record_id,
            "is_edit_mode": True,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": f"module_{slug}"
        }
    )

@router.post("/modules/{slug}/records/{record_id}/edit")
async def handle_edit_record_submit(
    request: Request,
    slug: str,
    record_id: str,
    record_type: str = Form("ENTRY"),
    title: str = Form(...),
    status: str = Form("COMPLETED"),
    amount: float = Form(0.0),
    party_name: str = Form("")
):
    EnterpriseModuleService.update_module_record(
        record_id=record_id,
        record_type=record_type,
        title=title,
        status=status,
        amount=amount,
        party_name=party_name
    )
    return RedirectResponse(url=f"/modules/{slug}", status_code=303)

# =========================================================================
# Dynamic Record Delete API Endpoints (Soft Delete with isDelete)
# =========================================================================
@router.post("/api/modules/master/{entity}/{record_id}/delete")
async def delete_gl_master_record(entity: str, record_id: str):
    GLMasterService.delete_entity_record(entity, record_id)
    return {"success": True, "entity": entity, "record_id": record_id}

@router.post("/api/modules/records/{record_id}/delete")
async def delete_module_record(record_id: str):
    EnterpriseModuleService.delete_record(record_id)
    return {"success": True, "record_id": record_id}

# =========================================================================
# Double-Entry Journal Voucher Studio Routes
# =========================================================================
@router.get("/modules/general-ledger/journals/new", response_class=HTMLResponse)
async def new_journal_voucher_page(request: Request):
    module = EnterpriseModuleService.get_module_by_slug("general-ledger")
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()
    all_accounts = GLMasterService.get_all_accounts()
    all_cost_centres = GLMasterService.get_cost_centres_for_company(str(active_company["id"]))

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "General Ledger", "url": "/modules/general-ledger"},
        {"title": "Journal Vouchers", "url": "/modules/general-ledger?tab=journals"},
        {"title": "New Journal Entry", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/gl_journal_entry.html",
        context={
            "module": module,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "all_accounts": all_accounts,
            "all_cost_centres": all_cost_centres,
            "breadcrumbs": breadcrumbs,
            "is_edit_mode": False,
            "voucher": None,
            "lines": [],
            "active_tab": "module_general-ledger"
        }
    )

@router.post("/modules/general-ledger/journals/new")
async def handle_new_journal_submit(
    request: Request,
    voucher_number: str = Form(...),
    voucher_date: str = Form(...),
    reference_number: Optional[str] = Form(None),
    narration: str = Form(...)
):
    form_data = await request.form()
    account_ids = form_data.getlist("line_account_id[]")
    cost_centre_ids = form_data.getlist("line_cost_centre_id[]")
    narrations = form_data.getlist("line_narration[]")
    debits = form_data.getlist("line_debit[]")
    credits = form_data.getlist("line_credit[]")

    lines = []
    for i in range(len(account_ids)):
        lines.append({
            "gl_account_id": account_ids[i],
            "cost_centre_id": cost_centre_ids[i] if i < len(cost_centre_ids) and cost_centre_ids[i] else None,
            "line_narration": narrations[i] if i < len(narrations) else "",
            "debit_amount": float(debits[i]) if i < len(debits) and debits[i] else 0.0,
            "credit_amount": float(credits[i]) if i < len(credits) and credits[i] else 0.0
        })

    active_company = CompanyService.resolve_active_company(request)
    GLJournalService.create_journal_voucher(
        company_id=str(active_company["id"]),
        voucher_number=voucher_number,
        voucher_date=voucher_date,
        reference_number=reference_number or "",
        narration=narration,
        lines=lines
    )
    return RedirectResponse(url="/modules/general-ledger?tab=journals", status_code=303)

@router.get("/modules/general-ledger/journals/{voucher_id}/edit", response_class=HTMLResponse)
async def edit_journal_voucher_page(request: Request, voucher_id: str):
    module = EnterpriseModuleService.get_module_by_slug("general-ledger")
    voucher = GLJournalService.get_voucher_by_id(voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Journal voucher not found")
    
    lines = GLJournalService.get_voucher_lines(voucher_id)
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()
    all_accounts = GLMasterService.get_all_accounts()
    all_cost_centres = GLMasterService.get_cost_centres_for_company(str(active_company["id"]))

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "General Ledger", "url": "/modules/general-ledger"},
        {"title": "Journal Vouchers", "url": "/modules/general-ledger?tab=journals"},
        {"title": f"Edit {voucher['voucher_number']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/gl_journal_entry.html",
        context={
            "module": module,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "all_accounts": all_accounts,
            "all_cost_centres": all_cost_centres,
            "breadcrumbs": breadcrumbs,
            "is_edit_mode": True,
            "voucher": voucher,
            "lines": lines,
            "active_tab": "module_general-ledger"
        }
    )

@router.post("/modules/general-ledger/journals/{voucher_id}/edit")
async def handle_edit_journal_submit(
    request: Request,
    voucher_id: str,
    voucher_date: str = Form(...),
    reference_number: Optional[str] = Form(None),
    narration: str = Form(...)
):
    form_data = await request.form()
    account_ids = form_data.getlist("line_account_id[]")
    cost_centre_ids = form_data.getlist("line_cost_centre_id[]")
    narrations = form_data.getlist("line_narration[]")
    debits = form_data.getlist("line_debit[]")
    credits = form_data.getlist("line_credit[]")

    lines = []
    for i in range(len(account_ids)):
        lines.append({
            "gl_account_id": account_ids[i],
            "cost_centre_id": cost_centre_ids[i] if i < len(cost_centre_ids) and cost_centre_ids[i] else None,
            "line_narration": narrations[i] if i < len(narrations) else "",
            "debit_amount": float(debits[i]) if i < len(debits) and debits[i] else 0.0,
            "credit_amount": float(credits[i]) if i < len(credits) and credits[i] else 0.0
        })

    GLJournalService.update_journal_voucher(
        voucher_id=voucher_id,
        voucher_date=voucher_date,
        reference_number=reference_number or "",
        narration=narration,
        lines=lines
    )
    return RedirectResponse(url="/modules/general-ledger?tab=journals", status_code=303)

@router.get("/modules/general-ledger/vouchers/{voucher_id}/print", response_class=HTMLResponse)
async def print_journal_voucher_page(request: Request, voucher_id: str):
    module = EnterpriseModuleService.get_module_by_slug("general-ledger")
    voucher = GLJournalService.get_voucher_by_id(voucher_id)
    if not voucher:
        raise HTTPException(status_code=404, detail="Journal voucher not found")
    
    lines = GLJournalService.get_voucher_lines(voucher_id)
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "General Ledger", "url": "/modules/general-ledger"},
        {"title": "Journal Vouchers", "url": "/modules/general-ledger?tab=journals"},
        {"title": f"Print Slip #{voucher['voucher_number']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/gl_voucher_print.html",
        context={
            "module": module,
            "voucher": voucher,
            "lines": lines,
            "active_company": active_company,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_general-ledger"
        }
    )

# =========================================================================
# Batch Operations & Automation API Endpoints
# =========================================================================
@router.post("/api/modules/general-ledger/batches/generate-auto")
async def api_generate_auto_batch(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    batch_id = GLJournalService.generate_auto_journals_batch(str(active_company["id"]))
    return {"success": True, "batch_id": batch_id, "message": "Automated Batch generated successfully."}

@router.post("/api/modules/general-ledger/batches/generate-from-template")
async def api_generate_from_template(request: Request, template_id: str = Form(...), amount: float = Form(50000.0)):
    active_company = CompanyService.resolve_active_company(request)
    batch_id = GLJournalService.generate_batch_from_template(str(active_company["id"]), template_id, "", amount=amount)
    return {"success": True, "batch_id": batch_id, "message": "Batch generated from Template."}

@router.post("/api/modules/general-ledger/batches/{batch_id}/post")
async def api_post_batch(batch_id: str):
    GLJournalService.post_batch(batch_id)
    return {"success": True, "batch_id": batch_id}

@router.post("/api/modules/general-ledger/batches/{batch_id}/delete")
async def api_delete_batch(batch_id: str):
    GLJournalService.delete_batch(batch_id)
    return {"success": True, "batch_id": batch_id}

@router.post("/api/modules/general-ledger/vouchers/{voucher_id}/delete")
async def api_delete_voucher(voucher_id: str):
    GLJournalService.delete_journal_voucher(voucher_id)
    return {"success": True, "voucher_id": voucher_id}

# =========================================================================
# CASH BOOK & TREASURY SUITE ROUTES
# =========================================================================

# 1. Money Receipts (MR)
@router.get("/modules/cash-book/receipts/new", response_class=HTMLResponse)
async def new_money_receipt_page(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    bank_accounts = CashBookService.get_bank_accounts(str(active_company["id"]))
    cashiers = CashBookService.get_cashiers(str(active_company["id"]))
    gl_accounts = GLMasterService.get_all_accounts()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": "Money Receipts", "url": "/modules/cash-book?tab=receipts"},
        {"title": "Issue Money Receipt", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_receipt_entry.html",
        context={
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "bank_accounts": bank_accounts,
            "cashiers": cashiers,
            "gl_accounts": gl_accounts,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.post("/modules/cash-book/receipts/new")
async def create_money_receipt_post(
    request: Request,
    receipt_type: str = Form(...),
    receipt_date: str = Form(...),
    party_name: str = Form(...),
    amount: float = Form(...),
    payment_mode: str = Form(...),
    narration: str = Form(""),
    cashier_id: Optional[str] = Form(None),
    bank_account_id: Optional[str] = Form(None),
    cheque_no: Optional[str] = Form(None),
    cheque_date: Optional[str] = Form(None),
    drawn_on_bank: Optional[str] = Form(None),
    gl_account_id: Optional[str] = Form(None)
):
    active_company = CompanyService.resolve_active_company(request)
    current_user = UserService.resolve_current_user(request)
    user_name = current_user.get("full_name", "Alexander Vance") if current_user else "Alexander Vance"

    CashBookService.create_money_receipt(
        company_id=str(active_company["id"]),
        receipt_type=receipt_type,
        receipt_date=receipt_date,
        party_name=party_name,
        payment_mode=payment_mode,
        amount=amount,
        narration=narration,
        cashier_id=cashier_id or None,
        bank_account_id=bank_account_id or None,
        cheque_no=cheque_no or None,
        cheque_date=cheque_date or None,
        drawn_on_bank=drawn_on_bank or None,
        gl_account_id=gl_account_id or None,
        created_by=user_name
    )
    return RedirectResponse(url="/modules/cash-book?tab=receipts", status_code=303)

@router.get("/modules/cash-book/receipts/{receipt_id}/print", response_class=HTMLResponse)
async def print_money_receipt(request: Request, receipt_id: str):
    receipt = CashBookService.get_money_receipt_by_id(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Money receipt not found")
    
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": "Money Receipts", "url": "/modules/cash-book?tab=receipts"},
        {"title": f"Print Receipt #{receipt['receipt_number']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_receipt_print.html",
        context={
            "receipt": receipt,
            "active_company": active_company,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.post("/api/modules/cash-book/receipts/{receipt_id}/delete")
async def api_delete_money_receipt(receipt_id: str):
    CashBookService.delete_money_receipt(receipt_id)
    return {"success": True, "receipt_id": receipt_id}

@router.post("/api/modules/cash-book/receipts/{receipt_id}/cancel")
async def api_cancel_money_receipt(receipt_id: str, reason: str = Form("User Cancelled")):
    CashBookService.cancel_money_receipt(receipt_id, reason)
    return {"success": True, "receipt_id": receipt_id}

# 2. Inter Bank-Cash Contra Transfers
@router.get("/modules/cash-book/transfers/new", response_class=HTMLResponse)
async def new_contra_transfer_page(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    bank_accounts = CashBookService.get_bank_accounts(str(active_company["id"]))
    cashiers = CashBookService.get_cashiers(str(active_company["id"]))

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": "Contra Transfers", "url": "/modules/cash-book?tab=transfers"},
        {"title": "Post Contra Transfer", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_contra_entry.html",
        context={
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "bank_accounts": bank_accounts,
            "cashiers": cashiers,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.post("/modules/cash-book/transfers/new")
async def create_contra_transfer_post(
    request: Request,
    transfer_type: str = Form(...),
    transfer_date: str = Form(...),
    amount: float = Form(...),
    reference_number: str = Form(...),
    narration: str = Form(""),
    from_cashier_id: Optional[str] = Form(None),
    from_bank_account_id: Optional[str] = Form(None),
    to_cashier_id: Optional[str] = Form(None),
    to_bank_account_id: Optional[str] = Form(None)
):
    active_company = CompanyService.resolve_active_company(request)
    current_user = UserService.resolve_current_user(request)
    user_name = current_user.get("full_name", "Alexander Vance") if current_user else "Alexander Vance"

    CashBookService.create_contra_transfer(
        company_id=str(active_company["id"]),
        transfer_date=transfer_date,
        transfer_type=transfer_type,
        amount=amount,
        reference_number=reference_number,
        narration=narration,
        from_cashier_id=from_cashier_id or None,
        from_bank_account_id=from_bank_account_id or None,
        to_cashier_id=to_cashier_id or None,
        to_bank_account_id=to_bank_account_id or None,
        created_by=user_name
    )
    return RedirectResponse(url="/modules/cash-book?tab=transfers", status_code=303)

@router.get("/modules/cash-book/transfers/{transfer_id}/print", response_class=HTMLResponse)
async def print_contra_voucher(request: Request, transfer_id: str):
    transfer = CashBookService.get_contra_transfer_by_id(transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Contra transfer not found")
    
    active_company = CompanyService.resolve_active_company(request)
    appearance = AppearanceService.get_appearance()

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": "Contra Transfers", "url": "/modules/cash-book?tab=transfers"},
        {"title": f"Print Voucher #{transfer['transfer_number']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_voucher_print.html",
        context={
            "transfer": transfer,
            "active_company": active_company,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.post("/api/modules/cash-book/transfers/{transfer_id}/delete")
async def api_delete_contra_transfer(transfer_id: str):
    CashBookService.delete_contra_transfer(transfer_id)
    return {"success": True, "transfer_id": transfer_id}

# 3. Master Setup Create & Edit (Cashiers, Banks, Branches, Accounts)
CB_MASTER_ENTITIES = {
    "cashiers": {"title": "Cashier Station", "tab": "cashiers"},
    "banks": {"title": "Bank Partner", "tab": "banks"},
    "branches": {"title": "Bank Branch", "tab": "branches"},
    "accounts": {"title": "Bank Account", "tab": "accounts"}
}

@router.get("/modules/cash-book/master/{entity}/new", response_class=HTMLResponse)
async def new_cb_master_record_page(request: Request, entity: str):
    if entity not in CB_MASTER_ENTITIES:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    banks_list = CashBookService.get_banks()
    branches_list = CashBookService.get_branches()
    gl_accounts = GLMasterService.get_all_accounts()

    ent_meta = CB_MASTER_ENTITIES[entity]
    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": ent_meta["title"], "url": f"/modules/cash-book?tab={ent_meta['tab']}"},
        {"title": f"New {ent_meta['title']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_master_create.html",
        context={
            "entity": entity,
            "entity_title": ent_meta["title"],
            "sub_tab": ent_meta["tab"],
            "is_edit_mode": False,
            "record": None,
            "active_company": active_company,
            "companies_list": companies_list,
            "banks_list": banks_list,
            "branches_list": branches_list,
            "gl_accounts": gl_accounts,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.get("/modules/cash-book/master/{entity}/{record_id}/edit", response_class=HTMLResponse)
async def edit_cb_master_record_page(request: Request, entity: str, record_id: str):
    if entity not in CB_MASTER_ENTITIES:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    record = None
    if entity == "cashiers":
        record = CashBookService.get_cashier_by_id(record_id)
    elif entity == "banks":
        record = CashBookService.get_bank_by_id(record_id)
    elif entity == "branches":
        record = CashBookService.get_branch_by_id(record_id)
    elif entity == "accounts":
        record = CashBookService.get_bank_account_by_id(record_id)

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    banks_list = CashBookService.get_banks()
    branches_list = CashBookService.get_branches()
    gl_accounts = GLMasterService.get_all_accounts()

    ent_meta = CB_MASTER_ENTITIES[entity]
    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Cash Book", "url": "/modules/cash-book"},
        {"title": ent_meta["title"], "url": f"/modules/cash-book?tab={ent_meta['tab']}"},
        {"title": f"Edit {ent_meta['title']}", "url": None}
    ]

    return templates.TemplateResponse(
        request=request,
        name="pages/cb_master_create.html",
        context={
            "entity": entity,
            "entity_title": ent_meta["title"],
            "sub_tab": ent_meta["tab"],
            "is_edit_mode": True,
            "record": record,
            "record_id": record_id,
            "active_company": active_company,
            "companies_list": companies_list,
            "banks_list": banks_list,
            "branches_list": branches_list,
            "gl_accounts": gl_accounts,
            "appearance": appearance,
            "breadcrumbs": breadcrumbs,
            "active_tab": "module_cash-book"
        }
    )

@router.post("/modules/cash-book/master/{entity}/new")
async def create_cb_master_record(request: Request, entity: str):
    form_data = await request.form()
    tab = CB_MASTER_ENTITIES[entity]["tab"]

    if entity == "cashiers":
        CashBookService.create_cashier(
            cashier_code=form_data.get("cashier_code", ""),
            cashier_name=form_data.get("cashier_name", ""),
            company_id=form_data.get("company_id", ""),
            counter_station=form_data.get("counter_station", ""),
            daily_cash_limit=float(form_data.get("daily_cash_limit", 50000.0)),
            gl_account_id=form_data.get("gl_account_id") or None
        )
    elif entity == "banks":
        CashBookService.create_bank(
            bank_code=form_data.get("bank_code", ""),
            bank_name=form_data.get("bank_name", ""),
            swift_code=form_data.get("swift_code") or None,
            country=form_data.get("country", "United States")
        )
    elif entity == "branches":
        CashBookService.create_branch(
            bank_id=form_data.get("bank_id", ""),
            branch_code=form_data.get("branch_code", ""),
            branch_name=form_data.get("branch_name", ""),
            routing_number=form_data.get("routing_number") or None,
            branch_address=form_data.get("branch_address") or None,
            contact_phone=form_data.get("contact_phone") or None
        )
    elif entity == "accounts":
        CashBookService.create_bank_account(
            company_id=form_data.get("company_id", ""),
            branch_id=form_data.get("branch_id", ""),
            account_number=form_data.get("account_number", ""),
            account_title=form_data.get("account_title", ""),
            account_type=form_data.get("account_type", "CURRENT"),
            currency=form_data.get("currency", "USD"),
            gl_account_id=form_data.get("gl_account_id", ""),
            opening_balance=float(form_data.get("opening_balance", 0.0)),
            overdraft_limit=float(form_data.get("overdraft_limit", 0.0))
        )

    return RedirectResponse(url=f"/modules/cash-book?tab={tab}", status_code=303)

@router.post("/modules/cash-book/master/{entity}/{record_id}/edit")
async def update_cb_master_record(request: Request, entity: str, record_id: str):
    form_data = await request.form()
    tab = CB_MASTER_ENTITIES[entity]["tab"]

    if entity == "cashiers":
        CashBookService.update_cashier(
            cashier_id=record_id,
            cashier_code=form_data.get("cashier_code", ""),
            cashier_name=form_data.get("cashier_name", ""),
            company_id=form_data.get("company_id", ""),
            counter_station=form_data.get("counter_station", ""),
            daily_cash_limit=float(form_data.get("daily_cash_limit", 50000.0)),
            gl_account_id=form_data.get("gl_account_id") or None
        )
    elif entity == "banks":
        CashBookService.update_bank(
            bank_id=record_id,
            bank_code=form_data.get("bank_code", ""),
            bank_name=form_data.get("bank_name", ""),
            swift_code=form_data.get("swift_code") or None,
            country=form_data.get("country", "United States")
        )
    elif entity == "branches":
        CashBookService.update_branch(
            branch_id=record_id,
            bank_id=form_data.get("bank_id", ""),
            branch_code=form_data.get("branch_code", ""),
            branch_name=form_data.get("branch_name", ""),
            routing_number=form_data.get("routing_number") or None,
            branch_address=form_data.get("branch_address") or None,
            contact_phone=form_data.get("contact_phone") or None
        )
    elif entity == "accounts":
        CashBookService.update_bank_account(
            account_id=record_id,
            company_id=form_data.get("company_id", ""),
            branch_id=form_data.get("branch_id", ""),
            account_number=form_data.get("account_number", ""),
            account_title=form_data.get("account_title", ""),
            account_type=form_data.get("account_type", "CURRENT"),
            currency=form_data.get("currency", "USD"),
            gl_account_id=form_data.get("gl_account_id", ""),
            opening_balance=float(form_data.get("opening_balance", 0.0)),
            overdraft_limit=float(form_data.get("overdraft_limit", 0.0))
        )

    return RedirectResponse(url=f"/modules/cash-book?tab={tab}", status_code=303)

@router.post("/api/modules/cash-book/master/{entity}/{record_id}/delete")
async def api_delete_cb_master_record(entity: str, record_id: str):
    if entity == "cashiers":
        CashBookService.delete_cashier(record_id)
    elif entity == "banks":
        CashBookService.delete_bank(record_id)
    elif entity == "branches":
        CashBookService.delete_branch(record_id)
    elif entity == "accounts":
        CashBookService.delete_bank_account(record_id)
    return {"success": True, "entity": entity, "record_id": record_id}

# =========================================================================
# Accounts Receivable Master Setup Dedicated Full-Page Routes (Zero-Modal)
# =========================================================================
AR_MASTER_ENTITIES = {
    "customers": {"title": "Customer Master Profile", "tab": "customers"},
    "ar-customer-groups": {"title": "AR Customer Group", "tab": "ar-customer-groups"},
    "customer-groups": {"title": "Commercial Customer Group", "tab": "customer-groups"},
    "group-categories": {"title": "Tier Group Category", "tab": "group-categories"},
    "company-mappings": {"title": "Customer Company Mapping", "tab": "company-mappings"},
    "ship-to-addresses": {"title": "Customer Ship to Address", "tab": "ship-to-addresses"},
    "control-accounts": {"title": "A/R Control Account Set", "tab": "control-accounts"},
    "reminder-criteria": {"title": "Reminder Criteria Setup", "tab": "reminder-criteria"},
    "aging-profiles": {"title": "AR Aging Profile", "tab": "aging-profiles"},
    "adjustment-types": {"title": "A/R Adjustment Type", "tab": "adjustment-types"}
}

@router.get("/modules/accounts-receivable/master/{entity}/new", response_class=HTMLResponse)
async def new_ar_master_page(request: Request, entity: str):
    if entity not in AR_MASTER_ENTITIES:
        raise HTTPException(status_code=404, detail="AR Master entity not found")

    module = EnterpriseModuleService.get_module_by_slug("accounts-receivable")
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    ent_meta = AR_MASTER_ENTITIES[entity]
    sub_tab = ent_meta["tab"]
    sub_title = AR_SUB_AREAS.get(sub_tab, {}).get("title", ent_meta["title"])

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Accounts Receivable", "url": "/modules/accounts-receivable"},
        {"title": sub_title, "url": f"/modules/accounts-receivable?tab={sub_tab}"},
        {"title": f"New {ent_meta['title']}", "url": None}
    ]

    ar_customers = ARMasterService.get_all_customers()
    ar_customer_groups = ARMasterService.get_ar_customer_groups()
    ar_commercial_groups = ARMasterService.get_commercial_groups()
    ar_group_categories = ARMasterService.get_group_categories()
    ar_control_sets = ARMasterService.get_control_account_sets(str(active_company["id"]))
    gl_accounts = GLMasterService.get_all_accounts()

    return templates.TemplateResponse(
        request=request,
        name="pages/ar_master_create.html",
        context={
            "module": module,
            "entity": entity,
            "entity_title": ent_meta["title"],
            "sub_tab": sub_tab,
            "is_edit_mode": False,
            "record": None,
            "record_id": None,
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "ar_customers": ar_customers,
            "ar_customer_groups": ar_customer_groups,
            "ar_commercial_groups": ar_commercial_groups,
            "ar_group_categories": ar_group_categories,
            "ar_control_sets": ar_control_sets,
            "gl_accounts": gl_accounts,
            "active_tab": "module_accounts-receivable"
        }
    )

@router.get("/modules/accounts-receivable/master/{entity}/{record_id}/edit", response_class=HTMLResponse)
async def edit_ar_master_page(request: Request, entity: str, record_id: str):
    if entity not in AR_MASTER_ENTITIES:
        raise HTTPException(status_code=404, detail="AR Master entity not found")

    record = None
    if entity == "customers":
        record = ARMasterService.get_customer_by_id(record_id)
    elif entity == "ar-customer-groups":
        record = ARMasterService.get_ar_customer_group_by_id(record_id)
    elif entity == "customer-groups":
        record = ARMasterService.get_commercial_group_by_id(record_id)
    elif entity == "group-categories":
        record = ARMasterService.get_group_category_by_id(record_id)
    elif entity == "company-mappings":
        record = ARMasterService.get_customer_company_mapping_by_id(record_id)
    elif entity == "ship-to-addresses":
        record = ARMasterService.get_ship_to_address_by_id(record_id)
    elif entity == "control-accounts":
        record = ARMasterService.get_control_account_set_by_id(record_id)
    elif entity == "reminder-criteria":
        record = ARMasterService.get_reminder_criteria_by_id(record_id)
    elif entity == "aging-profiles":
        record = ARMasterService.get_aging_profile_by_id(record_id)
    elif entity == "adjustment-types":
        record = ARMasterService.get_adjustment_type_by_id(record_id)

    if not record:
        raise HTTPException(status_code=404, detail="AR record not found")

    module = EnterpriseModuleService.get_module_by_slug("accounts-receivable")
    active_company = CompanyService.resolve_active_company(request)
    companies_list = CompanyService.get_all_companies()
    appearance = AppearanceService.get_appearance()
    db_health = db.check_health()

    ent_meta = AR_MASTER_ENTITIES[entity]
    sub_tab = ent_meta["tab"]
    sub_title = AR_SUB_AREAS.get(sub_tab, {}).get("title", ent_meta["title"])

    breadcrumbs = [
        {"title": "Home", "url": "/"},
        {"title": "Financial & Treasury", "url": "/"},
        {"title": "Accounts Receivable", "url": "/modules/accounts-receivable"},
        {"title": sub_title, "url": f"/modules/accounts-receivable?tab={sub_tab}"},
        {"title": f"Edit {ent_meta['title']}", "url": None}
    ]

    ar_customers = ARMasterService.get_all_customers()
    ar_customer_groups = ARMasterService.get_ar_customer_groups()
    ar_commercial_groups = ARMasterService.get_commercial_groups()
    ar_group_categories = ARMasterService.get_group_categories()
    ar_control_sets = ARMasterService.get_control_account_sets(str(active_company["id"]))
    gl_accounts = GLMasterService.get_all_accounts()

    return templates.TemplateResponse(
        request=request,
        name="pages/ar_master_create.html",
        context={
            "module": module,
            "entity": entity,
            "entity_title": ent_meta["title"],
            "sub_tab": sub_tab,
            "is_edit_mode": True,
            "record": record,
            "record_id": record_id,
            "active_company": active_company,
            "companies_list": companies_list,
            "appearance": appearance,
            "db_health": db_health,
            "breadcrumbs": breadcrumbs,
            "ar_customers": ar_customers,
            "ar_customer_groups": ar_customer_groups,
            "ar_commercial_groups": ar_commercial_groups,
            "ar_group_categories": ar_group_categories,
            "ar_control_sets": ar_control_sets,
            "gl_accounts": gl_accounts,
            "active_tab": "module_accounts-receivable"
        }
    )

# =========================================================================
# Accounts Receivable Master Setup Actions & CRUD
# =========================================================================
@router.post("/modules/accounts-receivable/master/customers")
@router.post("/modules/accounts-receivable/master/customers/new")
async def create_ar_customer_action(request: Request):
    form = await request.form()
    ARMasterService.create_customer(
        customer_code=form.get("customer_code", ""),
        customer_name=form.get("customer_name", ""),
        ar_customer_group_id=form.get("ar_customer_group_id") or None,
        commercial_group_id=form.get("commercial_group_id") or None,
        group_category_id=form.get("group_category_id") or None,
        contact_person=form.get("contact_person") or None,
        email=form.get("email") or None,
        phone=form.get("phone") or None,
        tax_bin_number=form.get("tax_bin_number") or None,
        credit_limit=float(form.get("credit_limit", 1000000.0)),
        payment_terms_days=int(form.get("payment_terms_days", 30)),
        discount_percentage=float(form.get("discount_percentage", 0.0)),
        currency=form.get("currency", "USD"),
        billing_address=form.get("billing_address") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=customers", status_code=303)

@router.post("/modules/accounts-receivable/master/customers/{customer_id}/edit")
async def update_ar_customer_action(customer_id: str, request: Request):
    form = await request.form()
    ARMasterService.update_customer(
        customer_id=customer_id,
        customer_code=form.get("customer_code", ""),
        customer_name=form.get("customer_name", ""),
        ar_customer_group_id=form.get("ar_customer_group_id") or None,
        commercial_group_id=form.get("commercial_group_id") or None,
        group_category_id=form.get("group_category_id") or None,
        contact_person=form.get("contact_person") or None,
        email=form.get("email") or None,
        phone=form.get("phone") or None,
        tax_bin_number=form.get("tax_bin_number") or None,
        credit_limit=float(form.get("credit_limit", 1000000.0)),
        payment_terms_days=int(form.get("payment_terms_days", 30)),
        discount_percentage=float(form.get("discount_percentage", 0.0)),
        currency=form.get("currency", "USD"),
        billing_address=form.get("billing_address") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=customers", status_code=303)

@router.post("/modules/accounts-receivable/master/{entity}")
async def create_ar_master_record(entity: str, request: Request):
    form = await request.form()
    tab = entity
    if entity == "ar-customer-groups":
        ARMasterService.create_ar_customer_group(
            group_code=form.get("group_code", ""),
            group_name=form.get("group_name", ""),
            control_account_set_id=form.get("control_account_set_id") or None,
            default_credit_limit=float(form.get("default_credit_limit", 500000.0)),
            grace_period_days=int(form.get("grace_period_days", 30))
        )
    elif entity == "customer-groups":
        ARMasterService.create_commercial_group(
            group_code=form.get("group_code", ""),
            group_name=form.get("group_name", ""),
            region=form.get("region") or None,
            description=form.get("description") or None
        )
    elif entity == "group-categories":
        ARMasterService.create_group_category(
            category_code=form.get("category_code", ""),
            category_name=form.get("category_name", ""),
            tier_level=form.get("tier_level", "Standard"),
            min_turnover=float(form.get("min_turnover", 0.0)),
            priority_level=int(form.get("priority_level", 1))
        )
    elif entity == "company-mappings":
        ARMasterService.create_customer_company_mapping(
            customer_id=form.get("customer_id", ""),
            company_id=form.get("company_id", ""),
            subsidiary_account_code=form.get("subsidiary_account_code") or None,
            allocated_credit_limit=float(form.get("allocated_credit_limit", 500000.0)),
            assigned_sales_rep=form.get("assigned_sales_rep") or None
        )
    elif entity == "ship-to-addresses":
        ARMasterService.create_ship_to_address(
            customer_id=form.get("customer_id", ""),
            location_name=form.get("location_name", ""),
            ship_address=form.get("ship_address", ""),
            city=form.get("city") or None,
            division_state=form.get("division_state") or None,
            contact_person=form.get("contact_person") or None,
            contact_phone=form.get("contact_phone") or None,
            is_default=bool(form.get("is_default"))
        )
    elif entity == "control-accounts":
        ARMasterService.create_control_account_set(
            set_code=form.get("set_code", ""),
            set_name=form.get("set_name", ""),
            company_id=form.get("company_id") or None,
            ar_control_gl_id=form.get("ar_control_gl_id") or None,
            sales_discount_gl_id=form.get("sales_discount_gl_id") or None,
            bad_debt_provision_gl_id=form.get("bad_debt_provision_gl_id") or None,
            advance_received_gl_id=form.get("advance_received_gl_id") or None
        )
    elif entity == "reminder-criteria":
        ARMasterService.create_reminder_criteria(
            criteria_code=form.get("criteria_code", ""),
            criteria_name=form.get("criteria_name", ""),
            reminder_level=form.get("reminder_level", "Level 1 (Gentle)"),
            overdue_days_threshold=int(form.get("overdue_days_threshold", 15)),
            min_overdue_amount=float(form.get("min_overdue_amount", 1000.0)),
            penalty_interest_pct=float(form.get("penalty_interest_pct", 0.0)),
            auto_email_enabled=bool(form.get("auto_email_enabled", True)),
            email_subject_template=form.get("email_subject_template") or None
        )
    elif entity == "aging-profiles":
        ARMasterService.create_aging_profile(
            profile_code=form.get("profile_code", ""),
            profile_name=form.get("profile_name", ""),
            bucket_1_label=form.get("bucket_1_label", "Current (0-30 Days)"),
            bucket_2_label=form.get("bucket_2_label", "31-60 Days"),
            bucket_3_label=form.get("bucket_3_label", "61-90 Days"),
            bucket_4_label=form.get("bucket_4_label", "91-120 Days"),
            bucket_5_label=form.get("bucket_5_label", "120+ Days (Doubtful)"),
            bad_debt_provision_pct=float(form.get("bad_debt_provision_pct", 5.0))
        )
    elif entity == "adjustment-types":
        ARMasterService.create_adjustment_type(
            adjustment_code=form.get("adjustment_code", ""),
            adjustment_name=form.get("adjustment_name", ""),
            adjustment_category=form.get("adjustment_category", "CREDIT"),
            default_offset_gl_id=form.get("default_offset_gl_id") or None,
            is_tax_applicable=bool(form.get("is_tax_applicable")),
            requires_manager_approval=bool(form.get("requires_manager_approval", True))
        )

    return RedirectResponse(url=f"/modules/accounts-receivable?tab={tab}", status_code=303)

@router.post("/modules/accounts-receivable/master/{entity}/{record_id}/edit")
async def update_ar_master_record(entity: str, record_id: str, request: Request):
    form = await request.form()
    tab = entity
    if entity == "customers":
        ARMasterService.update_customer(
            customer_id=record_id,
            customer_code=form.get("customer_code", ""),
            customer_name=form.get("customer_name", ""),
            ar_customer_group_id=form.get("ar_customer_group_id") or None,
            commercial_group_id=form.get("commercial_group_id") or None,
            group_category_id=form.get("group_category_id") or None,
            contact_person=form.get("contact_person") or None,
            email=form.get("email") or None,
            phone=form.get("phone") or None,
            tax_bin_number=form.get("tax_bin_number") or None,
            credit_limit=float(form.get("credit_limit", 1000000.0)),
            payment_terms_days=int(form.get("payment_terms_days", 30)),
            discount_percentage=float(form.get("discount_percentage", 0.0)),
            currency=form.get("currency", "USD"),
            billing_address=form.get("billing_address") or None
        )
    elif entity == "ar-customer-groups":
        ARMasterService.update_ar_customer_group(
            group_id=record_id,
            group_code=form.get("group_code", ""),
            group_name=form.get("group_name", ""),
            control_account_set_id=form.get("control_account_set_id") or None,
            default_credit_limit=float(form.get("default_credit_limit", 500000.0)),
            grace_period_days=int(form.get("grace_period_days", 30))
        )
    elif entity == "customer-groups":
        ARMasterService.update_commercial_group(
            group_id=record_id,
            group_code=form.get("group_code", ""),
            group_name=form.get("group_name", ""),
            region=form.get("region") or None,
            description=form.get("description") or None
        )
    elif entity == "group-categories":
        ARMasterService.update_group_category(
            category_id=record_id,
            category_code=form.get("category_code", ""),
            category_name=form.get("category_name", ""),
            tier_level=form.get("tier_level", "Standard"),
            min_turnover=float(form.get("min_turnover", 0.0)),
            priority_level=int(form.get("priority_level", 1))
        )
    elif entity == "company-mappings":
        ARMasterService.update_customer_company_mapping(
            mapping_id=record_id,
            customer_id=form.get("customer_id", ""),
            company_id=form.get("company_id", ""),
            subsidiary_account_code=form.get("subsidiary_account_code") or None,
            allocated_credit_limit=float(form.get("allocated_credit_limit", 500000.0)),
            assigned_sales_rep=form.get("assigned_sales_rep") or None
        )
    elif entity == "ship-to-addresses":
        ARMasterService.update_ship_to_address(
            address_id=record_id,
            customer_id=form.get("customer_id", ""),
            location_name=form.get("location_name", ""),
            ship_address=form.get("ship_address", ""),
            city=form.get("city") or None,
            division_state=form.get("division_state") or None,
            contact_person=form.get("contact_person") or None,
            contact_phone=form.get("contact_phone") or None,
            is_default=bool(form.get("is_default"))
        )
    elif entity == "control-accounts":
        ARMasterService.update_control_account_set(
            set_id=record_id,
            set_code=form.get("set_code", ""),
            set_name=form.get("set_name", ""),
            company_id=form.get("company_id") or None,
            ar_control_gl_id=form.get("ar_control_gl_id") or None,
            sales_discount_gl_id=form.get("sales_discount_gl_id") or None,
            bad_debt_provision_gl_id=form.get("bad_debt_provision_gl_id") or None,
            advance_received_gl_id=form.get("advance_received_gl_id") or None
        )
    elif entity == "reminder-criteria":
        ARMasterService.update_reminder_criteria(
            criteria_id=record_id,
            criteria_code=form.get("criteria_code", ""),
            criteria_name=form.get("criteria_name", ""),
            reminder_level=form.get("reminder_level", "Level 1 (Gentle)"),
            overdue_days_threshold=int(form.get("overdue_days_threshold", 15)),
            min_overdue_amount=float(form.get("min_overdue_amount", 1000.0)),
            penalty_interest_pct=float(form.get("penalty_interest_pct", 0.0)),
            auto_email_enabled=bool(form.get("auto_email_enabled", True)),
            email_subject_template=form.get("email_subject_template") or None
        )
    elif entity == "aging-profiles":
        ARMasterService.update_aging_profile(
            profile_id=record_id,
            profile_code=form.get("profile_code", ""),
            profile_name=form.get("profile_name", ""),
            bucket_1_label=form.get("bucket_1_label", "Current (0-30 Days)"),
            bucket_2_label=form.get("bucket_2_label", "31-60 Days"),
            bucket_3_label=form.get("bucket_3_label", "61-90 Days"),
            bucket_4_label=form.get("bucket_4_label", "91-120 Days"),
            bucket_5_label=form.get("bucket_5_label", "120+ Days (Doubtful)"),
            bad_debt_provision_pct=float(form.get("bad_debt_provision_pct", 5.0))
        )
    elif entity == "adjustment-types":
        ARMasterService.update_adjustment_type(
            adjustment_id=record_id,
            adjustment_code=form.get("adjustment_code", ""),
            adjustment_name=form.get("adjustment_name", ""),
            adjustment_category=form.get("adjustment_category", "CREDIT"),
            default_offset_gl_id=form.get("default_offset_gl_id") or None,
            is_tax_applicable=bool(form.get("is_tax_applicable")),
            requires_manager_approval=bool(form.get("requires_manager_approval", True))
        )

    return RedirectResponse(url=f"/modules/accounts-receivable?tab={tab}", status_code=303)

@router.post("/api/modules/accounts-receivable/master/{entity}/{record_id}/delete")
async def api_delete_ar_master_record(entity: str, record_id: str):
    if entity == "customers":
        ARMasterService.delete_customer(record_id)
    elif entity == "ar-customer-groups":
        ARMasterService.delete_ar_customer_group(record_id)
    elif entity == "customer-groups":
        ARMasterService.delete_commercial_group(record_id)
    elif entity == "group-categories":
        ARMasterService.delete_group_category(record_id)
    elif entity == "company-mappings":
        ARMasterService.delete_customer_company_mapping(record_id)
    elif entity == "ship-to-addresses":
        ARMasterService.delete_ship_to_address(record_id)
    elif entity == "control-accounts":
        ARMasterService.delete_control_account_set(record_id)
    elif entity == "reminder-criteria":
        ARMasterService.delete_reminder_criteria(record_id)
    elif entity == "aging-profiles":
        ARMasterService.delete_aging_profile(record_id)
    elif entity == "adjustment-types":
        ARMasterService.delete_adjustment_type(record_id)
    return {"success": True, "entity": entity, "record_id": record_id}

# =========================================================================
# Accounts Receivable Transaction Processing Suite Actions & CRUD
# =========================================================================
@router.post("/modules/accounts-receivable/transactions/advance-adjustments")
async def create_ar_advance_adj_action(request: Request):
    form = await request.form()
    ARTransactionService.create_advance_adjustment(
        voucher_number=form.get("voucher_number", ""),
        adjustment_date=form.get("adjustment_date", ""),
        company_id=form.get("company_id", ""),
        customer_id=form.get("customer_id", ""),
        advance_ref_number=form.get("advance_ref_number", ""),
        invoice_number=form.get("invoice_number", ""),
        original_advance_amount=float(form.get("original_advance_amount", 0.0)),
        adjusted_amount=float(form.get("adjusted_amount", 0.0)),
        unadjusted_balance=float(form.get("unadjusted_balance", 0.0)),
        narration=form.get("narration") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=advance-adjustments", status_code=303)

@router.post("/modules/accounts-receivable/transactions/general-adjustments")
async def create_ar_general_adj_action(request: Request):
    form = await request.form()
    ARTransactionService.create_general_adjustment(
        voucher_number=form.get("voucher_number", ""),
        adjustment_date=form.get("adjustment_date", ""),
        company_id=form.get("company_id", ""),
        customer_id=form.get("customer_id", ""),
        adjustment_type_id=form.get("adjustment_type_id", ""),
        adjustment_category=form.get("adjustment_category", "CREDIT"),
        amount=float(form.get("amount", 0.0)),
        reason_description=form.get("reason_description", ""),
        offset_gl_account_id=form.get("offset_gl_account_id") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=ar-adjustments", status_code=303)

@router.post("/modules/accounts-receivable/transactions/notes")
async def create_ar_note_action(request: Request):
    form = await request.form()
    note_type = form.get("note_type", "DEBIT_WITH_REF")
    
    # Determine redirect tab based on note type
    tab_map = {
        "DEBIT_WITH_REF": "debit-notes-ref",
        "DEBIT_DIRECT": "debit-notes-direct",
        "CREDIT_WITH_REF": "credit-notes-ref",
        "CREDIT_DIRECT": "credit-notes-direct",
    }
    redirect_tab = tab_map.get(note_type, "debit-notes-ref")

    ARTransactionService.create_note(
        note_number=form.get("note_number", ""),
        note_type=note_type,
        note_date=form.get("note_date", ""),
        company_id=form.get("company_id", ""),
        customer_id=form.get("customer_id", ""),
        note_amount=float(form.get("note_amount", 0.0)),
        tax_amount=float(form.get("tax_amount", 0.0)),
        reason=form.get("reason", ""),
        invoice_ref_number=form.get("invoice_ref_number") or None,
        original_invoice_amount=float(form.get("original_invoice_amount")) if form.get("original_invoice_amount") else None,
        gl_account_id=form.get("gl_account_id") or None
    )
    return RedirectResponse(url=f"/modules/accounts-receivable?tab={redirect_tab}", status_code=303)

@router.post("/modules/accounts-receivable/transactions/receipts")
async def issue_ar_receipt_action(request: Request):
    form = await request.form()
    ARTransactionService.issue_money_receipt(
        receipt_number=form.get("receipt_number", ""),
        receipt_date=form.get("receipt_date", ""),
        company_id=form.get("company_id", ""),
        customer_id=form.get("customer_id", ""),
        payment_mode=form.get("payment_mode", "WIRE"),
        receipt_amount=float(form.get("receipt_amount", 0.0)),
        instrument_ref=form.get("instrument_ref") or None,
        instrument_date=form.get("instrument_date") or None,
        allocated_invoices=form.get("allocated_invoices") or None,
        remarks=form.get("remarks") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=issue-receipts", status_code=303)

@router.post("/api/modules/accounts-receivable/transactions/receipts/{record_id}/cancel")
async def cancel_ar_receipt_api(record_id: str, request: Request):
    payload = await request.json() if request.headers.get("content-type") == "application/json" else {}
    reason = payload.get("reason", "Cancelled by financial operator")
    ARTransactionService.cancel_money_receipt(record_id, reason)
    return {"success": True, "record_id": record_id, "action": "cancelled"}

@router.post("/api/modules/accounts-receivable/transactions/{entity}/{record_id}/delete")
async def api_delete_ar_transaction(entity: str, record_id: str):
    if entity in ["advance-adjustments", "ar-advance-adjustments"]:
        ARTransactionService.delete_advance_adjustment(record_id)
    elif entity in ["ar-adjustments", "general-adjustments", "ar-general-adjustments"]:
        ARTransactionService.delete_general_adjustment(record_id)
    elif entity in ["notes", "debit-notes-ref", "debit-notes-direct", "credit-notes-ref", "credit-notes-direct"]:
        ARTransactionService.delete_note(record_id)
    return {"success": True, "entity": entity, "record_id": record_id}

# =========================================================================
# Accounts Receivable Credit Management Process Operations
# =========================================================================
@router.post("/modules/accounts-receivable/process/generate-reminders")
async def generate_batch_reminders_action(request: Request):
    form = await request.form()
    company_id = form.get("company_id", "")
    criteria_id = form.get("criteria_id", "")
    min_days = int(form.get("min_overdue_days", 15))
    count = ARProcessService.generate_batch_reminders(company_id, criteria_id, min_days)
    return RedirectResponse(url="/modules/accounts-receivable?tab=reminder-letters", status_code=303)

@router.post("/modules/accounts-receivable/process/create-reminder")
async def create_single_reminder_action(request: Request):
    form = await request.form()
    ARProcessService.create_manual_reminder_letter(
        letter_number=form.get("letter_number", ""),
        letter_date=form.get("letter_date", ""),
        company_id=form.get("company_id", ""),
        customer_id=form.get("customer_id", ""),
        reminder_criteria_id=form.get("reminder_criteria_id") or None,
        reminder_level=form.get("reminder_level", "Level 1 (Gentle)"),
        overdue_days=int(form.get("overdue_days", 15)),
        overdue_amount=float(form.get("overdue_amount", 0.0)),
        penalty_amount=float(form.get("penalty_amount", 0.0)),
        delivery_channel=form.get("delivery_channel", "EMAIL"),
        letter_subject=form.get("letter_subject") or None,
        letter_content=form.get("letter_content") or None
    )
    return RedirectResponse(url="/modules/accounts-receivable?tab=reminder-letters", status_code=303)

@router.post("/api/modules/accounts-receivable/process/reminder-letters/{record_id}/dispatch")
async def dispatch_reminder_api(record_id: str, request: Request):
    payload = await request.json() if request.headers.get("content-type") == "application/json" else {}
    channel = payload.get("channel", "EMAIL")
    ARProcessService.dispatch_reminder_letter(record_id, channel)
    return {"success": True, "record_id": record_id, "status": "SENT", "channel": channel}

@router.post("/api/modules/accounts-receivable/process/reminder-letters/{record_id}/delete")
async def delete_reminder_api(record_id: str):
    ARProcessService.delete_reminder_letter(record_id)
    return {"success": True, "record_id": record_id}

# =========================================================================
# Accounts Receivable Financial Reporting Operations
# =========================================================================
@router.get("/api/modules/accounts-receivable/reports/voucher/{voucher_type}/{voucher_id}")
async def get_printable_voucher_api(voucher_type: str, voucher_id: str):
    doc = ARReportService.get_voucher_document(voucher_type, voucher_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Voucher document not found")
    return {"success": True, "document": doc}

@router.get("/api/modules/accounts-receivable/reports/statement/{customer_id}")
async def get_customer_statement_api(
    customer_id: str,
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    statement_type: str = "STANDARD"
):
    active_company = CompanyService.resolve_active_company(request)
    company_id = str(active_company["id"]) if active_company else None
    stmt = ARReportService.get_customer_statement(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        statement_type=statement_type,
        company_id=company_id
    )
    return {"success": True, "statement": stmt}

# =========================================================================
# General Ledger Transaction & Batch Automation Operations
# =========================================================================
@router.post("/api/modules/general-ledger/transactions/auto-batch/generate")
async def generate_auto_batch_api(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    company_id = str(active_company["id"]) if active_company else None
    batch_id = GLJournalService.generate_auto_journals_batch(company_id)
    return {"success": True, "batch_id": batch_id, "message": "Automated recurring accruals batch generated successfully."}

@router.post("/api/modules/general-ledger/transactions/template-batch/generate")
async def generate_template_batch_api(request: Request):
    payload = await request.json() if request.headers.get("content-type") == "application/json" else {}
    template_id = payload.get("template_id", "")
    batch_title = payload.get("batch_title", "Template Generated Batch")
    amount = float(payload.get("amount", 50000.0))
    active_company = CompanyService.resolve_active_company(request)
    company_id = str(active_company["id"]) if active_company else None
    batch_id = GLJournalService.generate_batch_from_template(company_id, template_id, batch_title, amount)
    return {"success": True, "batch_id": batch_id, "message": "Template batch compiled and staged successfully."}

@router.post("/api/modules/general-ledger/transactions/auto-profiles/create")
async def create_auto_profile_api(request: Request):
    form = await request.form()
    active_company = CompanyService.resolve_active_company(request)
    company_id = str(active_company["id"]) if active_company else None
    profile_id = GLJournalService.create_auto_profile(
        profile_code=form.get("profile_code", ""),
        profile_name=form.get("profile_name", ""),
        frequency=form.get("frequency", "MONTHLY"),
        day_of_period=int(form.get("day_of_period", 1)),
        company_id=company_id,
        template_id=form.get("template_id") or None,
        default_amount=float(form.get("default_amount", 0.0)),
        is_auto_trigger=bool(form.get("is_auto_trigger")),
        description=form.get("description", "")
    )
    return RedirectResponse(url="/modules/general-ledger?tab=auto-batch-profiles", status_code=303)

@router.post("/api/modules/general-ledger/transactions/auto-profiles/{profile_id}/delete")
async def delete_auto_profile_api(profile_id: str):
    GLJournalService.delete_auto_profile(profile_id)
    return {"success": True, "profile_id": profile_id}

@router.post("/api/modules/general-ledger/transactions/batches/{batch_id}/post")
async def post_gl_batch_api(batch_id: str, request: Request):
    active_company = CompanyService.resolve_active_company(request)
    res = GLProcessService.post_batch_engine(batch_id, str(active_company["id"]) if active_company else None)
    return res

@router.post("/api/modules/general-ledger/transactions/batches/{batch_id}/unpost")
async def unpost_gl_batch_api(batch_id: str):
    GLJournalService.unpost_batch(batch_id)
    return {"success": True, "batch_id": batch_id, "status": "UNPOSTED"}

@router.post("/api/modules/general-ledger/process/data-integrity/run")
async def run_data_integrity_check_api(request: Request):
    active_company = CompanyService.resolve_active_company(request)
    res = GLProcessService.check_data_integrity(str(active_company["id"]) if active_company else None)
    return res

@router.get("/api/modules/general-ledger/reports/voucher/{voucher_id}/print-data")
async def get_gl_printable_voucher_api(voucher_id: str):
    doc = GLJournalService.get_printable_journal_voucher(voucher_id)
    return {"success": True, "document": doc}

# =========================================================================
# Sourcing & Procurement Actions & Print Routes
# =========================================================================
@router.post("/modules/sourcing/actions/vendors/create")
async def create_sourcing_vendor_action(request: Request):
    form = await request.form()
    SourcingMasterService.create_vendor(
        vendor_code=form.get("vendor_code", "VND-NEW"),
        vendor_name=form.get("vendor_name", ""),
        vendor_group=form.get("vendor_group", "MANUFACTURER_OEM"),
        contact_person=form.get("contact_person"),
        email=form.get("email"),
        phone=form.get("phone"),
        address=form.get("address"),
        credit_terms_days=int(form.get("credit_terms_days", 30)),
        currency=form.get("currency", "USD")
    )
    return RedirectResponse(url="/modules/sourcing?tab=vendors", status_code=303)

@router.post("/modules/sourcing/actions/requisitions/create")
async def create_sourcing_requisition_action(request: Request):
    form = await request.form()
    active_company = CompanyService.resolve_active_company(request)
    SourcingTransactionService.create_requisition(
        company_id=str(active_company["id"]),
        req_number=form.get("req_number", "REQ-NEW"),
        req_type=form.get("req_type", "SPARES"),
        title=form.get("title", ""),
        priority=form.get("priority", "MEDIUM"),
        requester_name=form.get("requester_name", "Procurement Lead"),
        notes=form.get("notes")
    )
    return RedirectResponse(url="/modules/sourcing?tab=requisitions", status_code=303)

@router.post("/modules/sourcing/actions/cs/generate-po")
async def generate_po_from_cs_action(request: Request):
    form = await request.form()
    cs_id = form.get("cs_id")
    if not cs_id:
        raise HTTPException(status_code=400, detail="Missing cs_id")
    import random
    po_num = f"PO-APX-{random.randint(1100, 9999)}"
    SourcingTransactionService.generate_po_from_cs_winner(cs_id=cs_id, po_number=po_num)
    return RedirectResponse(url="/modules/sourcing?tab=purchase-orders", status_code=303)

@router.post("/modules/sourcing/actions/approvals/process")
async def process_sourcing_approval_action(request: Request):
    form = await request.form()
    entity_type = form.get("entity_type", "PO")
    entity_id = form.get("entity_id")
    tier_level = int(form.get("tier_level", 1))
    action = form.get("action", "APPROVED")
    current_user = UserService.resolve_current_user(request)
    approver_name = current_user.get("full_name", "Executive Approver") if current_user else "Executive Approver"

    SourcingProcessService.execute_approval_action(
        entity_type=entity_type,
        entity_id=entity_id,
        tier_level=tier_level,
        approver_name=approver_name,
        approver_role="Authorized Executive Signatory",
        action=action
    )
    return RedirectResponse(url="/modules/sourcing?tab=e-approvals", status_code=303)

@router.post("/modules/sourcing/actions/approvals/batch-approve")
async def batch_approve_sourcing_action(request: Request):
    current_user = UserService.resolve_current_user(request)
    approver_name = current_user.get("full_name", "Executive Director") if current_user else "Executive Director"
    SourcingProcessService.batch_approve_all(approver_name=approver_name)
    return RedirectResponse(url="/modules/sourcing?tab=e-approvals", status_code=303)

@router.get("/modules/sourcing/po/print/{po_id}", response_class=HTMLResponse)
async def print_purchase_order_page(request: Request, po_id: str):
    po = SourcingTransactionService.get_purchase_order_by_id(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase Order not found")
    return templates.TemplateResponse(
        request=request,
        name="pages/sourcing_po_print.html",
        context={"po": po}
    )





# =========================================================================
# SALES DOCUMENT PRINT STUDIO ROUTES
# =========================================================================
@router.get("/modules/sales/print/quote/{quote_id}", response_class=HTMLResponse)
async def print_sales_quote_page(request: Request, quote_id: str):
    active_company = CompanyService.resolve_active_company(request)
    quote = SalesTransactionService.get_quote_by_id(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
    return templates.TemplateResponse(
        request=request,
        name="pages/sales_print_document.html",
        context={
            "active_company": active_company,
            "doc_type_title": f"Official Sales Quotation (Rev {quote.get('revision_no', 1)})",
            "doc_number": quote["quote_number"],
            "doc_date": str(quote["quote_date"]),
            "doc_status": quote["status"],
            "customer_name": quote["customer_name"],
            "billing_address": "Corporate Address on File",
            "shipping_address": "Destination Port / Facility",
            "payment_terms": "As per quotation agreement",
            "delivery_terms": "FOB Factory Gate",
            "carrier_name": None,
            "vehicle_no": None,
            "items": quote.get("items", []),
            "total_amount": quote["total_amount"]
        }
    )

@router.get("/modules/sales/print/order/{order_id}", response_class=HTMLResponse)
async def print_sales_order_page(request: Request, order_id: str):
    active_company = CompanyService.resolve_active_company(request)
    order = SalesTransactionService.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Sales Order not found")
    return templates.TemplateResponse(
        request=request,
        name="pages/sales_print_document.html",
        context={
            "active_company": active_company,
            "doc_type_title": "Confirmed Sales Order (Confirmation Sheet)",
            "doc_number": order["order_number"],
            "doc_date": str(order["order_date"]),
            "doc_status": order["status"],
            "customer_name": order["customer_name"],
            "billing_address": order.get("billing_address"),
            "shipping_address": order.get("shipping_address"),
            "payment_terms": order.get("payment_terms"),
            "delivery_terms": order.get("delivery_terms"),
            "carrier_name": None,
            "vehicle_no": None,
            "items": order.get("items", []),
            "total_amount": order["total_amount"]
        }
    )

@router.get("/modules/sales/print/do/{do_id}", response_class=HTMLResponse)
async def print_delivery_order_page(request: Request, do_id: str):
    active_company = CompanyService.resolve_active_company(request)
    do_row = db.query_one(
        """
        SELECT do.*, so.order_number, so.customer_name, so.total_amount AS order_total
        FROM sales_delivery_orders do
        JOIN sales_orders so ON do.order_id = so.id
        WHERE do.id = ?
        """,
        (do_id,)
    )
    if not do_row:
        raise HTTPException(status_code=404, detail="Delivery Order not found")
    items = db.query("SELECT * FROM sales_do_items WHERE do_id = ? ORDER BY code ASC", (do_id,))
    return templates.TemplateResponse(
        request=request,
        name="pages/sales_print_document.html",
        context={
            "active_company": active_company,
            "doc_type_title": "Delivery Order (DO) & Gate Pass Challan",
            "doc_number": do_row["do_number"],
            "doc_date": str(do_row["do_date"]),
            "doc_status": do_row["status"],
            "customer_name": do_row["customer_name"],
            "billing_address": f"Gate Pass Ref: {do_row.get('gate_pass_ref', 'N/A')}",
            "shipping_address": do_row.get("delivery_address"),
            "payment_terms": "Pre-Dispatched Delivery Challan",
            "delivery_terms": "Official Outbound Gate Pass",
            "carrier_name": do_row.get("carrier_name"),
            "vehicle_no": do_row.get("vehicle_no"),
            "items": items,
            "total_amount": do_row.get("order_total", 0.0)
        }
    )

@router.get("/modules/sales/print/invoice/{invoice_id}", response_class=HTMLResponse)
async def print_sales_invoice_page(request: Request, invoice_id: str):
    active_company = CompanyService.resolve_active_company(request)
    inv = db.query_one("SELECT * FROM sales_invoices WHERE id = ?", (invoice_id,))
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    items = db.query("SELECT * FROM sales_invoice_items WHERE invoice_id = ? ORDER BY code ASC", (invoice_id,))
    return templates.TemplateResponse(
        request=request,
        name="pages/sales_print_document.html",
        context={
            "active_company": active_company,
            "doc_type_title": "Commercial Tax Invoice (GL-Integrated)",
            "doc_number": inv["invoice_number"],
            "doc_date": str(inv["invoice_date"]),
            "doc_status": inv["status"],
            "customer_name": inv["customer_name"],
            "billing_address": f"GL Journal Reference: {inv.get('gl_journal_ref', 'Auto-Posted')}",
            "shipping_address": f"Payment Due Date: {inv.get('due_date')}",
            "payment_terms": "Tax Invoice Settlement",
            "delivery_terms": "Commercial Billing",
            "carrier_name": None,
            "vehicle_no": None,
            "items": items,
            "total_amount": inv["total_amount"]
        }
    )


# =========================================================================
# INVENTORY OFFICIAL DOCUMENT PRINT STUDIO ROUTES
# =========================================================================
@router.get("/modules/inventory/print/{doc_type}/{doc_id}", response_class=HTMLResponse)
async def inventory_print_document(request: Request, doc_type: str, doc_id: str):
    active_company = CompanyService.resolve_active_company(request)
    all_companies = CompanyService.get_all_companies()
    user_id = request.cookies.get(UserService.COOKIE_USER_ID)
    user = UserService.get_user_by_id(user_id) if user_id else None

    doc_type_clean = doc_type.lower()
    doc_type_title = "Warehouse Official Document"
    doc_number = "N/A"
    doc_date = "2026-08-31"
    doc_status = "POSTED"
    warehouse_name = "Central Plant Storage Facility"
    entity_name = "Enterprise Logistics Partner"
    order_po_ref = "N/A"
    gate_pass_ref = "GP-2026-ENTRY-001"
    carrier_name = ""
    vehicle_no = ""
    items = []
    total_amount = 0.0

    if doc_type_clean == "grn":
        grn = InvTransactionService.get_grn_by_id(doc_id)
        if not grn:
            return HTMLResponse("Goods Receiving Note (GRN) record not found.", status_code=404)
        doc_type_title = "Goods Receiving Note (GRN / MRR)"
        doc_number = grn["grn_number"]
        doc_date = str(grn["grn_date"])
        doc_status = grn["status"]
        warehouse_name = grn["warehouse_name"]
        entity_name = grn["supplier_name"]
        order_po_ref = grn.get("po_ref", "Direct PO Receipt")
        gate_pass_ref = grn.get("challan_ref", "GP-IN-0818")
        items = grn.get("items", [])
        total_amount = float(grn.get("total_received_value", 0.0))

    elif doc_type_clean in ("issue", "challan"):
        iss = InvTransactionService.get_issue_by_id(doc_id)
        if not iss:
            return HTMLResponse("Goods Issue Challan record not found.", status_code=404)
        doc_type_title = "Goods Issue Delivery Challan"
        doc_number = iss["issue_number"]
        doc_date = str(iss["issue_date"])
        doc_status = iss["status"]
        warehouse_name = iss["warehouse_name"]
        entity_name = iss["recipient_name"]
        order_po_ref = iss.get("order_ref", "Direct Delivery Challan")
        gate_pass_ref = iss.get("gate_pass_ref", "GP-OUT-0820")
        items = iss.get("items", [])
        total_amount = float(iss.get("total_issue_value", 0.0))

    elif doc_type_clean == "sto":
        sto = InvTransactionService.get_transfer_by_id(doc_id)
        if not sto:
            return HTMLResponse("Stock Transfer Order (STO) record not found.", status_code=404)
        doc_type_title = "Stock Transfer Note (STO)"
        doc_number = sto["transfer_number"]
        doc_date = str(sto["transfer_date"])
        doc_status = sto["status"]
        warehouse_name = f"{sto['from_warehouse']} -> {sto['to_warehouse']}"
        entity_name = f"Destination: {sto['to_warehouse']}"
        order_po_ref = f"STO Shuttling Ref: {sto['transfer_number']}"
        gate_pass_ref = sto.get("tracking_ref", "TRACK-STO-9912")
        carrier_name = sto.get("carrier_name", "Internal Shuttling Fleet")
        vehicle_no = sto.get("vehicle_no", "TRK-01")
        items = sto.get("items", [])
        total_amount = float(sto.get("total_transfer_value", 0.0))

    elif doc_type_clean == "warranty":
        warr_list = InvWarrantyService.get_warranties()
        warr = next((w for w in warr_list if str(w["id"]) == doc_id or w["serial_number"] == doc_id), None)
        if not warr:
            return HTMLResponse("Warranty Certificate record not found.", status_code=404)
        doc_type_title = "Official Product Warranty Certificate"
        doc_number = f"WARR-{warr['serial_number']}"
        doc_date = str(warr["warranty_start_date"])
        doc_status = warr["status"]
        warehouse_name = "Quality Assurance & Warranty Division"
        entity_name = warr["customer_name"]
        order_po_ref = f"Invoice Ref: {warr.get('invoice_ref', 'INV-DIRECT')}"
        gate_pass_ref = f"Serial Number: {warr['serial_number']}"
        items = [{
            "item_code": warr["item_code"],
            "item_name": warr["item_name"],
            "remarks": f"Valid until {warr['warranty_end_date']} ({warr['warranty_months']} Months Full Coverage)",
            "bin_code": "QA-CERT",
            "received_qty": 1,
            "uom_code": "PCS",
            "unit_cost": 0.0,
            "line_total": 0.0
        }]
        total_amount = 0.0

    return templates.TemplateResponse(
        request=request,
        name="pages/inv_print_document.html",
        context={
            "user": user,
            "active_company": active_company,
            "all_companies": all_companies,
            "doc_type_title": doc_type_title,
            "doc_number": doc_number,
            "doc_date": doc_date,
            "doc_status": doc_status,
            "warehouse_name": warehouse_name,
            "entity_name": entity_name,
            "order_po_ref": order_po_ref,
            "gate_pass_ref": gate_pass_ref,
            "carrier_name": carrier_name,
            "vehicle_no": vehicle_no,
            "items": items,
            "total_amount": total_amount,
        }
    )


# =========================================================================
# FIXED ASSETS OFFICIAL DOCUMENT PRINT STUDIO ROUTES
# =========================================================================
@router.get("/modules/fixed-assets/print/{doc_type}/{doc_id}", response_class=HTMLResponse)
async def fixed_assets_print_document(request: Request, doc_type: str, doc_id: str):
    active_company = CompanyService.resolve_active_company(request)
    all_companies = CompanyService.get_all_companies()
    user_id = request.cookies.get(UserService.COOKIE_USER_ID)
    user = UserService.get_user_by_id(user_id) if user_id else None

    doc_type_clean = doc_type.lower()
    doc_type_title = "Capital Asset Official Document"
    doc_number = "N/A"
    doc_date = "2026-08-31"
    doc_status = "POSTED"
    facility_name = "Primary Manufacturing Facility"
    entity_name = "Enterprise Asset Management"
    po_ref = "N/A"
    custodian_name = "Asset Custodian"
    department_name = "Precision Engineering"
    asset_tag = "N/A"
    serial_number = "N/A"
    manufacturer = "N/A"
    model_number = "N/A"
    items = []
    total_amount = 0.0

    if doc_type_clean == "grn":
        grn = db.query_one("SELECT * FROM fa_grn_headers WHERE id = ?", (doc_id,))
        if grn:
            doc_type_title = "Capital Asset Receiving Note (Asset GRN)"
            doc_number = grn["grn_number"]
            doc_date = str(grn["grn_date"])
            doc_status = grn["status"]
            entity_name = grn["supplier_name"]
            po_ref = grn.get("po_ref", "CAPEX-PO-2026-0041")
            total_amount = float(grn.get("total_cost", 0.0))
            items = [{
                "code": 1,
                "asset_tag": "AST-CAP-001",
                "asset_name": "High-Precision Capital Machinery (QA Laser Certified)",
                "serial_number": "DMG-2024-88421",
                "capital_cost": total_amount
            }]
    elif doc_type_clean == "transfer":
        tr = db.query_one("SELECT * FROM fa_transfers WHERE id = ?", (doc_id,))
        if tr:
            doc_type_title = "Capital Asset Inter-Plant Transfer Note"
            doc_number = tr["transfer_number"]
            doc_date = str(tr["transfer_date"])
            doc_status = tr["status"]
            custodian_name = tr.get("to_custodian", "Engr. Kevin Vance")
            entity_name = f"Origin: Plant 01 -> Destination: Plant 02"
            po_ref = tr.get("reason", "Operational Bay Reallocation")
            asset = db.query_one("SELECT * FROM fa_assets WHERE id = ?", (str(tr["asset_id"]),))
            if asset:
                asset_tag = asset["asset_tag"]
                serial_number = asset.get("serial_number", "N/A")
                manufacturer = asset.get("manufacturer", "N/A")
                total_amount = float(asset.get("purchase_cost", 0.0))
                items = [{
                    "code": 1,
                    "asset_tag": asset["asset_tag"],
                    "asset_name": asset["asset_name"],
                    "serial_number": asset.get("serial_number", "N/A"),
                    "capital_cost": total_amount
                }]
    elif doc_type_clean == "disposal":
        disp = db.query_one("SELECT * FROM fa_disposals WHERE id = ?", (doc_id,))
        if disp:
            doc_type_title = "Capital Asset Disposal & Scrapping Certificate"
            doc_number = disp["disposal_number"]
            doc_date = str(disp["disposal_date"])
            doc_status = disp["status"]
            entity_name = disp.get("buyer_name", "Global Salvage & Recovery LLC")
            po_ref = f"Disposal Type: {disp.get('disposal_type', 'SALE')}"
            total_amount = float(disp.get("disposal_proceeds", 0.0))
            asset = db.query_one("SELECT * FROM fa_assets WHERE id = ?", (str(disp["asset_id"]),))
            items = [{
                "code": 1,
                "asset_tag": asset["asset_tag"] if asset else "AST-DISP-001",
                "asset_name": asset["asset_name"] if asset else "Retired Commercial Fleet Vehicle",
                "serial_number": f"Gain/Loss: ${float(disp.get('gain_loss_amount', 0.0)):,.2f}",
                "capital_cost": float(disp.get("original_cost", 0.0))
            }]
    elif doc_type_clean == "tag":
        asset = db.query_one("SELECT * FROM fa_assets WHERE id = ?", (doc_id,))
        if asset:
            doc_type_title = "Official Asset Identification & Barcode Tag"
            doc_number = asset["asset_tag"]
            doc_date = str(asset["purchase_date"])
            doc_status = asset["status"]
            custodian_name = asset.get("custodian_name", "Asset Custodian")
            department_name = asset.get("department_name", "Plant Engineering")
            asset_tag = asset["asset_tag"]
            serial_number = asset.get("serial_number", "N/A")
            manufacturer = asset.get("manufacturer", "N/A")
            model_number = asset.get("model_number", "N/A")
            total_amount = float(asset.get("purchase_cost", 0.0))
            items = [{
                "code": 1,
                "asset_tag": asset["asset_tag"],
                "asset_name": asset["asset_name"],
                "serial_number": serial_number,
                "capital_cost": total_amount
            }]

    return templates.TemplateResponse(
        request=request,
        name="pages/fa_print_document.html",
        context={
            "user": user,
            "active_company": active_company,
            "all_companies": all_companies,
            "doc_type_title": doc_type_title,
            "doc_number": doc_number,
            "doc_date": doc_date,
            "doc_status": doc_status,
            "facility_name": facility_name,
            "entity_name": entity_name,
            "po_ref": po_ref,
            "custodian_name": custodian_name,
            "department_name": department_name,
            "asset_tag": asset_tag,
            "serial_number": serial_number,
            "manufacturer": manufacturer,
            "model_number": model_number,
            "items": items,
            "total_amount": total_amount,
        }
    )


# =========================================================================
# OFFICIAL HRIS & PAYROLL DOCUMENT PRINT STUDIO ROUTE
# =========================================================================
@router.get("/modules/hris/print/{doc_type}/{doc_id}", response_class=HTMLResponse)
async def print_hr_document(request: Request, doc_type: str, doc_id: str):
    """
    Renders standardized, printable corporate letterhead documents for:
    - payslip: Official Monthly Salary Pay Slip
    - appointment: Formal Employment Appointment Letter (Offer Letter)
    - transfer: Inter-Plant / Department Transfer Order
    - certificate: Official Experience & Service Certificate
    - bank-advice: Corporate Bank Salary Disbursement Advice
    """
    active_company = CompanyService.resolve_active_company(request)
    doc_type = doc_type.strip().lower()

    if doc_type == "payslip":
        ps = HRPayrollService.get_payslip_by_id(doc_id)
        if not ps:
            raise HTTPException(status_code=404, detail="Payslip record not found")
        
        return templates.TemplateResponse(
            request=request,
            name="pages/hr_print_document.html",
            context={
                "doc_type": "payslip",
                "doc_type_title": "OFFICIAL MONTHLY SALARY PAYSLIP",
                "doc_number": ps["payslip_number"],
                "doc_date": str(ps["run_date"]),
                "employee": ps,
                "active_company": active_company
            }
        )

    elif doc_type == "appointment":
        cand = HRRecruitmentService.get_candidate_by_id(doc_id)
        if not cand:
            raise HTTPException(status_code=404, detail="Candidate record not found")
        
        return templates.TemplateResponse(
            request=request,
            name="pages/hr_print_document.html",
            context={
                "doc_type": "appointment",
                "doc_type_title": "FORMAL EMPLOYMENT APPOINTMENT LETTER",
                "doc_number": f"OFF-{cand['requisition_number']}-01",
                "doc_date": "2026-09-01",
                "candidate": cand,
                "active_company": active_company
            }
        )

    elif doc_type == "transfer":
        tr = HREmployeeService.get_transfer_by_id(doc_id)
        if not tr:
            raise HTTPException(status_code=404, detail="Transfer record not found")
        
        return templates.TemplateResponse(
            request=request,
            name="pages/hr_print_document.html",
            context={
                "doc_type": "transfer",
                "doc_type_title": "OFFICIAL EMPLOYEE TRANSFER & PROMOTION ORDER",
                "doc_number": tr["transfer_number"],
                "doc_date": str(tr["transfer_date"]),
                "transfer": tr,
                "active_company": active_company
            }
        )

    elif doc_type in ("certificate", "bank-advice"):
        emp = HREmployeeService.get_employee_by_id(doc_id)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee record not found")
        
        return templates.TemplateResponse(
            request=request,
            name="pages/hr_print_document.html",
            context={
                "doc_type": doc_type,
                "doc_type_title": "CERTIFICATE OF EMPLOYMENT & SERVICE EXPERIENCE" if doc_type == "certificate" else "CORPORATE BANK SALARY DISBURSEMENT ADVICE",
                "doc_number": f"EXP-{emp['employee_code']}-2026" if doc_type == "certificate" else f"BNK-ADV-{emp['employee_code']}-2026",
                "doc_date": "2026-09-01",
                "employee": emp,
                "active_company": active_company
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid HR document print type")
