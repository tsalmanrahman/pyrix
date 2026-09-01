"""
Pyrix Enterprise Modules Sub-Area Registry
Centralized, dynamic metadata for all 20 enterprise modules structured into the standard 5 Enterprise Suites.
"""

from typing import Dict, Any, List, Optional
from app.core.db import db

# Color mapping per suite
SUITE_THEMES = {
    1: {"color": "blue", "icon": "settings-2", "title": "Master Setup Suite"},
    2: {"color": "emerald", "icon": "arrow-left-right", "title": "Transaction Processing & Automation Suite"},
    3: {"color": "purple", "icon": "check-check", "title": "Process, Batch & Closing Suite"},
    4: {"color": "amber", "icon": "bar-chart-2", "title": "Financial & Operational Analysis Suite"},
    5: {"color": "rose", "icon": "file-pie-chart", "title": "Reporting & Statements Suite"},
}

def get_module_suites_registry(slug: str, context_counts: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Returns the standardized 5 suites with their sub-areas for any module slug.
    Injects live badge counts from context if available.
    """
    counts = context_counts or {}

    # 1. GENERAL LEDGER
    if slug == "general-ledger":
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Chart of Accounts, Mappings & Cost Dimensions",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "6 Sub-Areas",
                "cards": [
                    {"title": "Chart of Accounts", "subtitle": "Hierarchical accounts & normal balances", "badge": str(counts.get("gl_coa_count", 12)), "url": "/modules/general-ledger?tab=coa", "icon": "book-open", "color": "blue"},
                    {"title": "GL Mapping Matrix", "subtitle": "Multi-company allocation rules", "badge": str(counts.get("gl_mapping_count", 12)), "url": "/modules/general-ledger?tab=mapping", "icon": "building-2", "color": "indigo"},
                    {"title": "GL Sub Accounts", "subtitle": "Sub-ledgers & party dimensions", "badge": str(counts.get("gl_subaccount_count", 4)), "url": "/modules/general-ledger?tab=subaccounts", "icon": "folder-tree", "color": "emerald"},
                    {"title": "Departments", "subtitle": "Corporate & plant cost divisions", "badge": str(counts.get("gl_dept_count", 4)), "url": "/modules/general-ledger?tab=departments", "icon": "users", "color": "purple"},
                    {"title": "Cost Centres", "subtitle": "Operating units & cost pools", "badge": str(counts.get("gl_costcentre_count", 1)), "url": "/modules/general-ledger?tab=costcentres", "icon": "target", "color": "teal"},
                    {"title": "Categories & Segments", "subtitle": "Statutory groupings & reporting tags", "badge": "5", "url": "/modules/general-ledger?tab=categories", "icon": "tags", "color": "amber"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing & Automation Suite",
                "subtitle": "Double-Entry Journals, Recurring Engines & Vouchers",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "8 Operations",
                "cards": [
                    {"title": "Journal Entry", "subtitle": "Balanced double-entry journal vouchers", "badge": str(counts.get("gl_voucher_count", 2)), "url": "/modules/general-ledger?tab=journals", "icon": "file-spread", "color": "emerald"},
                    {"title": "Auto Journals Batch", "subtitle": "Automated periodic accruals engine", "badge": "Auto", "url": "/modules/general-ledger?tab=auto-batch-gen", "icon": "sparkles", "color": "cyan"},
                    {"title": "Batch from Template", "subtitle": "Standardized recurring batch wizard", "badge": "Wizard", "url": "/modules/general-ledger?tab=template-batch-gen", "icon": "copy-check", "color": "blue"},
                    {"title": "Auto Batch Profiles", "subtitle": "Monthly/Quarterly schedule triggers", "badge": str(counts.get("gl_auto_profile_count", 4)), "url": "/modules/general-ledger?tab=auto-batch-profiles", "icon": "clock-4", "color": "indigo"},
                    {"title": "Batch Templates", "subtitle": "Reusable multi-line distribution designs", "badge": str(counts.get("gl_template_count", 1)), "url": "/modules/general-ledger?tab=batch-templates", "icon": "copy", "color": "violet"},
                    {"title": "Batch Status", "subtitle": "Batch processing & lifecycle monitor", "badge": str(counts.get("gl_batch_count", 1)), "url": "/modules/general-ledger?tab=batches", "icon": "package-check", "color": "amber"},
                    {"title": "Budget Data", "subtitle": "Fiscal allocations & variance tracking", "badge": str(counts.get("gl_budget_count", 0)), "url": "/modules/general-ledger?tab=budgets", "icon": "pie-chart", "color": "teal"},
                    {"title": "Print Vouchers", "subtitle": "Formal letterhead & 4-tier sign-off", "badge": "Print", "url": "/modules/general-ledger?tab=print-vouchers", "icon": "printer", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Financial Process & Closing Suite",
                "subtitle": "Bulk Staging, Ledger Commitment & Data Diagnostics",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Post Batch", "subtitle": "Bulk commit unposted batches directly into master general ledger", "badge": "Bulk Post", "url": "/modules/general-ledger?tab=post-batch", "icon": "check-circle", "color": "purple"},
                    {"title": "Check Data Integrity", "subtitle": "Diagnostic scanner for Debit=Credit equality, orphans & missing mappings", "badge": counts.get("gl_integrity_label", "100% HEALTHY"), "url": "/modules/general-ledger?tab=data-integrity", "icon": "shield-check", "color": "indigo"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Financial Analysis & Cost Control Suite",
                "subtitle": "Departmental Spending & Real-Time Account Inquiry",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Cost Analysis", "subtitle": "Cost centre spending breakdown, budget utilization & variances", "badge": counts.get("gl_cost_spent", "$450,000"), "url": "/modules/general-ledger?tab=cost-analysis", "icon": "bar-chart-3", "color": "amber"},
                    {"title": "Account Balance Inquiry", "subtitle": "Real-time ledger lookup with Opening, Debits, Credits & Net Activity", "badge": "Live Inquiry", "url": "/modules/general-ledger?tab=account-balances", "icon": "activity", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Financial Reporting & Statements Suite",
                "subtitle": "Balance Sheet, Income Statement, Trial Balance & Cost Centre P&L",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "5 Sub-Areas",
                "cards": [
                    {"title": "Financial Statements", "subtitle": "Balance Sheet & Income Statement (P&L)", "badge": "P&L / BS", "url": "/modules/general-ledger?tab=financial-statements", "icon": "file-text", "color": "rose"},
                    {"title": "Trial Balance", "subtitle": "Opening, Period Movement & Closing TB", "badge": "100% Balanced", "url": "/modules/general-ledger?tab=trial-balance", "icon": "scale", "color": "indigo"},
                    {"title": "Transaction Details", "subtitle": "Itemized audit register by cost centre", "badge": "Register", "url": "/modules/general-ledger?tab=gl-transaction-details", "icon": "list-filter", "color": "purple"},
                    {"title": "Cost-Centre P&L", "subtitle": "Segmented revenue & direct margins", "badge": "Margins", "url": "/modules/general-ledger?tab=cost-centre-pnl", "icon": "layers", "color": "emerald"},
                    {"title": "Notes to Accounts", "subtitle": "Statutory disclosures & policy notes", "badge": "IFRS", "url": "/modules/general-ledger?tab=notes-to-accounts", "icon": "file-code-2", "color": "amber"},
                ]
            }
        ]

    # 2. ACCOUNTS RECEIVABLE
    if slug == "accounts-receivable":
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Customer Profiles, Credit Limits & Group Classifications",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "10 Sub-Areas",
                "cards": [
                    {"title": "Customer Profile", "subtitle": "Directory, credit limits & balances", "badge": str(counts.get("ar_customers_count", 4)), "url": "/modules/accounts-receivable?tab=customers", "icon": "users", "color": "blue"},
                    {"title": "AR Customer Group", "subtitle": "AR accounting classifications & terms", "badge": str(counts.get("ar_customer_groups_count", 3)), "url": "/modules/accounts-receivable?tab=ar-customer-groups", "icon": "folder-cog", "color": "indigo"},
                    {"title": "Customer Group", "subtitle": "Commercial wholesale, retail & export", "badge": str(counts.get("ar_commercial_groups_count", 3)), "url": "/modules/accounts-receivable?tab=customer-groups", "icon": "building-2", "color": "cyan"},
                    {"title": "Group Category", "subtitle": "Tier rankings & minimum turnover", "badge": str(counts.get("ar_group_categories_count", 3)), "url": "/modules/accounts-receivable?tab=group-categories", "icon": "tags", "color": "emerald"},
                    {"title": "Customer Mapping", "subtitle": "Multi-subsidiary allocations & sales reps", "badge": str(counts.get("ar_mappings_count", 4)), "url": "/modules/accounts-receivable?tab=company-mappings", "icon": "network", "color": "violet"},
                    {"title": "Ship to Address", "subtitle": "Delivery docks, depots & plant gates", "badge": str(counts.get("ar_ship_addresses_count", 3)), "url": "/modules/accounts-receivable?tab=ship-to-addresses", "icon": "truck", "color": "amber"},
                    {"title": "Control Account Sets", "subtitle": "GL receivables, discount & bad debt sets", "badge": str(counts.get("ar_control_sets_count", 2)), "url": "/modules/accounts-receivable?tab=control-accounts", "icon": "scale", "color": "rose"},
                    {"title": "Reminder Criteria", "subtitle": "Dunning escalation & overdue penalties", "badge": str(counts.get("ar_reminder_criteria_count", 3)), "url": "/modules/accounts-receivable?tab=reminder-criteria", "icon": "mail-warning", "color": "orange"},
                    {"title": "AR Aging Profile", "subtitle": "Multi-bracket aging & bad debt risk %", "badge": str(counts.get("ar_aging_profiles_count", 2)), "url": "/modules/accounts-receivable?tab=aging-profiles", "icon": "clock-3", "color": "teal"},
                    {"title": "A/R Adjustment Type", "subtitle": "Debit/Credit adjustment reason codes", "badge": str(counts.get("ar_adjustment_types_count", 4)), "url": "/modules/accounts-receivable?tab=adjustment-types", "icon": "sliders-horizontal", "color": "purple"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing & Automation Suite",
                "subtitle": "Adjustments, Invoices, Debit/Credit Notes & Money Receipts",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "8 Operations",
                "cards": [
                    {"title": "Advance Adjustments", "subtitle": "Match advances against bills", "badge": str(counts.get("ar_advance_count", 0)), "url": "/modules/accounts-receivable?tab=advance-adjustments", "icon": "layers-2", "color": "emerald"},
                    {"title": "AR Adjustments", "subtitle": "Debit/Credit ledger reclassifications", "badge": str(counts.get("ar_adjustments_count", 0)), "url": "/modules/accounts-receivable?tab=ar-adjustments", "icon": "file-check-2", "color": "emerald"},
                    {"title": "Debit Note (Ref)", "subtitle": "Linked to invoice number", "badge": str(counts.get("ar_dn_ref_count", 0)), "url": "/modules/accounts-receivable?tab=debit-notes-ref", "icon": "file-plus-2", "color": "rose"},
                    {"title": "Debit Note (Direct)", "subtitle": "Direct interest / detention charges", "badge": str(counts.get("ar_dn_dir_count", 0)), "url": "/modules/accounts-receivable?tab=debit-notes-direct", "icon": "file-plus", "color": "rose"},
                    {"title": "Credit Note (Ref)", "subtitle": "Sales returns & billing deductions", "badge": str(counts.get("ar_cn_ref_count", 0)), "url": "/modules/accounts-receivable?tab=credit-notes-ref", "icon": "file-minus-2", "color": "blue"},
                    {"title": "Credit Note (Direct)", "subtitle": "Direct volume rebates & incentives", "badge": str(counts.get("ar_cn_dir_count", 0)), "url": "/modules/accounts-receivable?tab=credit-notes-direct", "icon": "file-minus", "color": "blue"},
                    {"title": "Issue Money Receipts", "subtitle": "Cheque, bank & cash collection entry", "badge": str(counts.get("ar_mr_count", 2)), "url": "/modules/accounts-receivable?tab=issue-money-receipts", "icon": "receipt", "color": "amber"},
                    {"title": "Cancel Money Receipts", "subtitle": "Bounced cheque & reversal audit trail", "badge": "Audit", "url": "/modules/accounts-receivable?tab=cancel-money-receipts", "icon": "rotate-ccw", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Credit Management Process Suite",
                "subtitle": "Overdue Tracking, Dunning Escalation & Reminder Generation",
                "icon": "shield-alert",
                "theme_color": "purple",
                "count_label": "1 Operation",
                "cards": [
                    {"title": "Reminder Letters", "subtitle": "Auto-dunning generation & dispatched notices", "badge": str(counts.get("ar_dunning_count", 6)), "url": "/modules/accounts-receivable?tab=reminder-letters", "icon": "mail-warning", "color": "purple"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Financial & Operational Analysis Suite",
                "subtitle": "Real-Time Aging Matrix, Credit Limits & Portfolio Utilization",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "1 Operation",
                "cards": [
                    {"title": "Due, Overdue Status", "subtitle": "Real-time aging matrix & credit utilization monitor", "badge": "Live Monitor", "url": "/modules/accounts-receivable?tab=due-overdue-status", "icon": "clock", "color": "amber"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Financial Reporting & Statements Suite",
                "subtitle": "Statements, Aging Schedules, Real-Time Turnover & Registers",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "6 Sub-Areas",
                "cards": [
                    {"title": "A/R Schedule", "subtitle": "Opening, Invoiced, Received & Closing balances", "badge": "Schedule", "url": "/modules/accounts-receivable?tab=ar-schedule", "icon": "calendar-range", "color": "rose"},
                    {"title": "Customer Statements", "subtitle": "Periodic ledger statement with running balance", "badge": "Statement", "url": "/modules/accounts-receivable?tab=customer-statement", "icon": "file-text", "color": "blue"},
                    {"title": "Sales & Collection Matrix", "subtitle": "Monthly billed vs collected matrix", "badge": "Matrix", "url": "/modules/accounts-receivable?tab=sales-collection", "icon": "pie-chart", "color": "emerald"},
                    {"title": "Aged Trial Balance (ATB)", "subtitle": "Standard aged receivables trial balance", "badge": "ATB", "url": "/modules/accounts-receivable?tab=aged-trial-balance", "icon": "scale", "color": "indigo"},
                    {"title": "Collection Register", "subtitle": "Itemized cash, cheque & transfer receipts", "badge": "Register", "url": "/modules/accounts-receivable?tab=collections-register", "icon": "receipt", "color": "amber"},
                    {"title": "Notes Summary & Reprints", "subtitle": "Debit & Credit notes summary & document reprint", "badge": "Reprint", "url": "/modules/accounts-receivable?tab=notes-summary", "icon": "file-spread", "color": "teal"},
                ]
            }
        ]

    # 3. CASH BOOK
    if slug == "cash-book":
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Cashier Stations, Bank Accounts & Currency Rules",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "5 Sub-Areas",
                "cards": [
                    {"title": "Cashier Stations", "subtitle": "Counter desks & daily cash limits", "badge": str(counts.get("cb_cashier_count", 2)), "url": "/modules/cash-book?tab=cashiers", "icon": "user-check", "color": "blue"},
                    {"title": "Bank Master", "subtitle": "Corporate banking partners", "badge": str(counts.get("cb_bank_count", 3)), "url": "/modules/cash-book?tab=banks", "icon": "landmark", "color": "indigo"},
                    {"title": "Bank Branches", "subtitle": "Routing numbers & SWIFT codes", "badge": str(counts.get("cb_branch_count", 3)), "url": "/modules/cash-book?tab=branches", "icon": "building-2", "color": "cyan"},
                    {"title": "Bank Accounts", "subtitle": "Treasury & settlement accounts", "badge": str(counts.get("cb_account_count", 3)), "url": "/modules/cash-book?tab=accounts", "icon": "credit-card", "color": "emerald"},
                    {"title": "Cheque Books", "subtitle": "Cheque leaf inventory & serial ranges", "badge": "Active", "url": "/modules/cash-book?tab=cheques", "icon": "book-marked", "color": "purple"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing Suite",
                "subtitle": "Receipts, Payments & Contra Transfers",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "4 Operations",
                "cards": [
                    {"title": "Money Receipts (MR)", "subtitle": "Customer & vendor cash/cheque inflows", "badge": str(counts.get("cb_receipt_count", 2)), "url": "/modules/cash-book?tab=receipts", "icon": "receipt", "color": "emerald"},
                    {"title": "Payment Vouchers (BPV)", "subtitle": "Vendor, tax & operational cash/cheque disbursements", "badge": "Disburse", "url": "/modules/cash-book?tab=payments", "icon": "wallet", "color": "rose"},
                    {"title": "Contra Transfers", "subtitle": "Cash-to-bank & bank-to-cash routing", "badge": "Contra", "url": "/modules/cash-book?tab=transfers", "icon": "arrow-left-right", "color": "cyan"},
                    {"title": "Petty Cash Expenses", "subtitle": "Daily office floats & imprest vouchers", "badge": "Float", "url": "/modules/cash-book?tab=petty-cash", "icon": "coins", "color": "amber"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Treasury Process & Reconciliation",
                "subtitle": "Bank Reconciliation & Daily Cash Drawer Closings",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Bank Reconciliation", "subtitle": "Match statement lines with ledger transactions", "badge": "Reconcile", "url": "/modules/cash-book?tab=bank-recon", "icon": "scale", "color": "purple"},
                    {"title": "Daily Cash Closing", "subtitle": "Cashier drawer physical count verification", "badge": "Closing", "url": "/modules/cash-book?tab=cash-closing", "icon": "lock", "color": "indigo"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Liquidity & Cash Flow Analysis",
                "subtitle": "Live Treasury Balances & Cash Velocity",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Liquidity Position", "subtitle": "Real-time bank balances & available liquid funds", "badge": "Live Pool", "url": "/modules/cash-book?tab=liquidity", "icon": "activity", "color": "amber"},
                    {"title": "Account Velocity", "subtitle": "Bank turnover, inflow rates & deposit speeds", "badge": "Velocity", "url": "/modules/cash-book?tab=velocity", "icon": "zap", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Treasury Reporting Suite",
                "subtitle": "Daily Cash Sheet, Bank Registers & Cheque Status",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "4 Reports",
                "cards": [
                    {"title": "Daily Cash Sheet", "subtitle": "Cashier opening, receipts, payments & closing", "badge": "Daily", "url": "/modules/cash-book?tab=daily-cash-sheet", "icon": "file-spreadsheet", "color": "rose"},
                    {"title": "Bank Book Register", "subtitle": "Itemized transaction register by bank account", "badge": "Register", "url": "/modules/cash-book?tab=bank-book", "icon": "file-text", "color": "indigo"},
                    {"title": "Cheque Register", "subtitle": "Issued, cleared, pending & dishonored cheques", "badge": "Cheques", "url": "/modules/cash-book?tab=cheque-register", "icon": "check-square", "color": "emerald"},
                    {"title": "Reconciliation Report", "subtitle": "Formal Bank Reconciliation Statement (BRS)", "badge": "BRS", "url": "/modules/cash-book?tab=brs-report", "icon": "file-check", "color": "teal"},
                ]
            }
        ]

    # 4. ACCOUNTS PAYABLE
    if slug == "accounts-payable":
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Vendor Master, AP Groups & Payment Terms",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "5 Sub-Areas",
                "cards": [
                    {"title": "Vendor Profile", "subtitle": "Supplier directory, bank info & credit terms", "badge": "Vendors", "url": "/modules/accounts-payable?tab=vendors", "icon": "users", "color": "blue"},
                    {"title": "AP Vendor Groups", "subtitle": "Payable accounting classes & default accounts", "badge": "Groups", "url": "/modules/accounts-payable?tab=vendor-groups", "icon": "folder-cog", "color": "indigo"},
                    {"title": "Payment Terms", "subtitle": "Net-30, discounts & early settlement rules", "badge": "Terms", "url": "/modules/accounts-payable?tab=payment-terms", "icon": "calendar-clock", "color": "cyan"},
                    {"title": "AP Control Accounts", "subtitle": "GL accounts payable, accruals & tax sets", "badge": "GL Sets", "url": "/modules/accounts-payable?tab=control-accounts", "icon": "scale", "color": "emerald"},
                    {"title": "Adjustment Types", "subtitle": "Debit/Credit adjustment reason codes", "badge": "Codes", "url": "/modules/accounts-payable?tab=adjustment-types", "icon": "sliders-horizontal", "color": "purple"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing Suite",
                "subtitle": "Invoices, Payment Vouchers & Debit/Credit Notes",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "6 Operations",
                "cards": [
                    {"title": "Purchase Invoices", "subtitle": "Direct & PO-linked vendor bills", "badge": "Invoices", "url": "/modules/accounts-payable?tab=invoices", "icon": "file-text", "color": "emerald"},
                    {"title": "Payment Vouchers", "subtitle": "Bank & cheque payments to vendors", "badge": "Disburse", "url": "/modules/accounts-payable?tab=payments", "icon": "wallet", "color": "blue"},
                    {"title": "Advance Adjustments", "subtitle": "Match vendor advance prepayments against bills", "badge": "Match", "url": "/modules/accounts-payable?tab=advance-adjustments", "icon": "layers-2", "color": "cyan"},
                    {"title": "AP Debit Note (Return)", "subtitle": "Purchase returns & vendor debit memos", "badge": "Return", "url": "/modules/accounts-payable?tab=debit-notes", "icon": "file-plus-2", "color": "rose"},
                    {"title": "AP Credit Note", "subtitle": "Vendor price adjustments & late fee billings", "badge": "Credit", "url": "/modules/accounts-payable?tab=credit-notes", "icon": "file-minus-2", "color": "amber"},
                    {"title": "Cancel Payment", "subtitle": "Void payment voucher & restore open invoices", "badge": "Void", "url": "/modules/accounts-payable?tab=cancel-payment", "icon": "rotate-ccw", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Payment Run & AP Process Suite",
                "subtitle": "Batch Payment Runs & AP Data Diagnostics",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Batch Payment Run", "subtitle": "Automated multi-vendor disbursement generation", "badge": "Run Batch", "url": "/modules/accounts-payable?tab=payment-run", "icon": "play-circle", "color": "purple"},
                    {"title": "AP Data Integrity", "subtitle": "Verify invoice-payment matching & foreign key links", "badge": "Diagnostic", "url": "/modules/accounts-payable?tab=ap-integrity", "icon": "shield-check", "color": "indigo"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Payable Aging & Cash Outflow Analysis",
                "subtitle": "DPO Metrics & Projected Cash Requirements",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Vendor Aging Matrix", "subtitle": "Current, 30, 60, 90+ days payable distribution", "badge": "Aging", "url": "/modules/accounts-payable?tab=vendor-aging", "icon": "clock-3", "color": "amber"},
                    {"title": "Cash Outflow Forecast", "subtitle": "Upcoming due dates & mandatory disbursements", "badge": "Forecast", "url": "/modules/accounts-payable?tab=cash-outflow", "icon": "trending-down", "color": "rose"},
                ]
            },
            {
                "suite_id": 5,
                "title": "AP Reporting & 1099 Disclosures",
                "subtitle": "AP Schedule, Vendor Statements & Tax Filings",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "5 Reports",
                "cards": [
                    {"title": "AP Schedule", "subtitle": "Opening, Invoiced, Paid & Closing balances", "badge": "Schedule", "url": "/modules/accounts-payable?tab=ap-schedule", "icon": "calendar-range", "color": "rose"},
                    {"title": "Vendor Statement", "subtitle": "Periodic ledger statement with running balance", "badge": "Statement", "url": "/modules/accounts-payable?tab=vendor-statement", "icon": "file-text", "color": "blue"},
                    {"title": "Purchases & Payments Summary", "subtitle": "Monthly supplier invoice vs disbursement matrix", "badge": "Summary", "url": "/modules/accounts-payable?tab=summary", "icon": "pie-chart", "color": "emerald"},
                    {"title": "Aged AP Trial Balance", "subtitle": "Itemized vendor open balances by aging bracket", "badge": "ATB", "url": "/modules/accounts-payable?tab=aged-trial-balance", "icon": "scale", "color": "indigo"},
                    {"title": "Tax & 1099 Disclosures", "subtitle": "Statutory withholding tax & 1099 reporting", "badge": "1099", "url": "/modules/accounts-payable?tab=tax-1099", "icon": "file-code-2", "color": "teal"},
                ]
            }
        ]

    # 5. SOURCING & PROCUREMENT MODERN 5-SUITE REGISTRY
    if slug == "sourcing":
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Vendor Profiles, Enlistment Tiers, Buyer Governance & Incoterms",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "8 Sub-Areas",
                "cards": [
                    {"title": "Vendor Profile", "subtitle": "Directory, credit terms, bank & VAT/TIN info", "badge": str(counts.get("src_vendors_count", 8)), "url": "/modules/sourcing?tab=vendors", "icon": "users", "color": "blue"},
                    {"title": "Vendor Enlistment", "subtitle": "Qualification categories & renewal tiers", "badge": str(counts.get("src_enlistments_count", 4)), "url": "/modules/sourcing?tab=enlistment", "icon": "award", "color": "emerald"},
                    {"title": "Buyer Master", "subtitle": "Assigned product categories & delegated limits", "badge": str(counts.get("src_buyers_count", 4)), "url": "/modules/sourcing?tab=buyers", "icon": "user-check", "color": "indigo"},
                    {"title": "Purchasing Orgs", "subtitle": "Central vs plant-specific procurement units", "badge": str(counts.get("src_orgs_count", 3)), "url": "/modules/sourcing?tab=purchasing-orgs", "icon": "building-2", "color": "cyan"},
                    {"title": "Price Terms & Incoterms", "subtitle": "FOB, CIF, CFR, Ex-Works & validity profiles", "badge": str(counts.get("src_terms_count", 5)), "url": "/modules/sourcing?tab=price-terms", "icon": "file-check", "color": "purple"},
                    {"title": "C&F Agents & Ports", "subtitle": "Clearing & forwarding agents & port terminals", "badge": str(counts.get("src_cnf_count", 2)), "url": "/modules/sourcing?tab=cnf-agents", "icon": "ship", "color": "amber"},
                    {"title": "Exchange Rates", "subtitle": "Multi-currency rates (USD, EUR, GBP, BDT)", "badge": "FX Live", "url": "/modules/sourcing?tab=exchange-rates", "icon": "coins", "color": "rose"},
                    {"title": "Vendor Allocations", "subtitle": "Multi-company cross-entity vendor matrix", "badge": "Matrix", "url": "/modules/sourcing?tab=vendor-mappings", "icon": "network", "color": "violet"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing & Automation Suite",
                "subtitle": "Multi-Type PR, RFQ Tenders, Dynamic CS Matrix & Purchase Orders",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "5 Operations",
                "cards": [
                    {"title": "Purchase Requisitions", "subtitle": "Spares, Services, Stationery & Decision forms", "badge": str(counts.get("src_pr_count", 4)), "url": "/modules/sourcing?tab=requisitions", "icon": "file-text", "color": "emerald"},
                    {"title": "Request For Quotation", "subtitle": "Broadcast RFQ tenders & collect vendor bids", "badge": str(counts.get("src_rfq_count", 1)), "url": "/modules/sourcing?tab=rfqs", "icon": "send", "color": "blue"},
                    {"title": "Comparative Statement", "subtitle": "Dynamic commercial & technical evaluation matrix", "badge": "Live Matrix", "url": "/modules/sourcing?tab=comparative-statements", "icon": "scale", "color": "amber"},
                    {"title": "Purchase Orders (PO)", "subtitle": "Import & Local POs with/without PR reference", "badge": str(counts.get("src_po_count", 4)), "url": "/modules/sourcing?tab=purchase-orders", "icon": "shopping-cart", "color": "indigo"},
                    {"title": "Goods Return Notes", "subtitle": "Return-to-vendor memos for rejected goods", "badge": str(counts.get("src_returns_count", 1)), "url": "/modules/sourcing?tab=goods-returns", "icon": "rotate-ccw", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Process, Batch & e-Approval Suite",
                "subtitle": "Multi-Tier Approval Chains, LC Operations & C&F Dispatch",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "4 Operations",
                "cards": [
                    {"title": "e-Approval Hub", "subtitle": "Executive multi-tier digital sign-off queue", "badge": str(counts.get("src_pending_approvals", 2)) + " Pending", "url": "/modules/sourcing?tab=e-approvals", "icon": "check-check", "color": "purple"},
                    {"title": "Letter of Credit (LC)", "subtitle": "Import LC opening, margin allocation & bank letters", "badge": str(counts.get("src_lc_count", 2)), "url": "/modules/sourcing?tab=lc-operations", "icon": "landmark", "color": "indigo"},
                    {"title": "C&F Shipping Dispatch", "subtitle": "Forward Bill of Lading & shipping docs to agents", "badge": str(counts.get("src_dispatches_count", 1)), "url": "/modules/sourcing?tab=cnf-dispatches", "icon": "container", "color": "cyan"},
                    {"title": "PO Lifecycle Control", "subtitle": "Force close, reopen or cancel purchase orders", "badge": "Lifecycle", "url": "/modules/sourcing?tab=po-lifecycle", "icon": "lock", "color": "rose"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Financial & Operational Analysis Suite",
                "subtitle": "LC Exposure, Vendor Scorecards & Spend Analytics",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "3 Operations",
                "cards": [
                    {"title": "LC Exposure Register", "subtitle": "Bank-wise LC exposure, margin pool & maturity", "badge": counts.get("src_lc_total", "$223,500"), "url": "/modules/sourcing?tab=lc-analysis", "icon": "bar-chart-3", "color": "amber"},
                    {"title": "Vendor Scorecards", "subtitle": "On-time delivery (OTD), quality & price index", "badge": "96.5% OTD", "url": "/modules/sourcing?tab=vendor-scorecards", "icon": "trending-up", "color": "emerald"},
                    {"title": "Spend Analytics", "subtitle": "Category-wise procurement spend breakdown", "badge": "Analytics", "url": "/modules/sourcing?tab=spend-analytics", "icon": "pie-chart", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Sourcing Reporting & 3-Way Audit Suite",
                "subtitle": "PR-PO-GRN Reconciliation, Purchase Registers & Schedules",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "3 Reports",
                "cards": [
                    {"title": "3-Way Match Engine", "subtitle": "PR vs PO vs GRN vs Invoice line-item audit", "badge": "Audit", "url": "/modules/sourcing?tab=three-way-match", "icon": "check-circle-2", "color": "rose"},
                    {"title": "Purchase Tax Register", "subtitle": "Period-wise procurement register & VAT books", "badge": "Register", "url": "/modules/sourcing?tab=purchase-register", "icon": "file-spreadsheet", "color": "indigo"},
                    {"title": "LC Maturity Schedule", "subtitle": "Bank liabilities & upcoming settlement calendar", "badge": "Schedule", "url": "/modules/sourcing?tab=lc-maturity", "icon": "calendar-clock", "color": "purple"},
                ]
            }
        ]


    # 6. SALES MANAGEMENT MODERN 5-SUITE REGISTRY
    if slug in ("sales", "sales-management"):
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Sales Teams Hierarchy, Pricing Matrices & Discount Limits",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "6 Sub-Areas",
                "cards": [
                    {"title": "Sales Teams (MM/ZM/TSM)", "subtitle": "Territory hierarchy & team targets", "badge": str(counts.get("sls_teams_count", 6)), "url": "/modules/sales?tab=sales-teams", "icon": "network", "color": "blue"},
                    {"title": "Salespersons Master", "subtitle": "Reps, commission rates & monthly quotas", "badge": str(counts.get("sls_reps_count", 5)), "url": "/modules/sales?tab=salespersons", "icon": "users", "color": "indigo"},
                    {"title": "Sales Areas & Zones", "subtitle": "Territories, distribution centers & depots", "badge": str(counts.get("sls_areas_count", 5)), "url": "/modules/sales?tab=sales-areas", "icon": "map-pin", "color": "cyan"},
                    {"title": "Price Profiles & Lists", "subtitle": "Base, Wholesale, Retail & OEM contracts", "badge": str(counts.get("sls_profiles_count", 5)), "url": "/modules/sales?tab=price-profiles", "icon": "tag", "color": "emerald"},
                    {"title": "Product Catalog Prices", "subtitle": "Item pricing, min floor prices & UOMs", "badge": str(counts.get("sls_prices_count", 6)), "url": "/modules/sales?tab=product-prices", "icon": "layers", "color": "amber"},
                    {"title": "Discount Limit Matrix", "subtitle": "Role-based discount limits & sign-off rules", "badge": "4 Tiers", "url": "/modules/sales?tab=discount-limits", "icon": "sliders", "color": "rose"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing & Automation Suite",
                "subtitle": "Quotes, Proformas, Sales Orders, DOs, Invoices & Returns",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "6 Operations",
                "cards": [
                    {"title": "Sales Quotes & Proformas", "subtitle": "Formal quotations, revisions & 1-click SO conversion", "badge": str(counts.get("sls_quotes_count", 5)), "url": "/modules/sales?tab=quotes", "icon": "file-text", "color": "blue"},
                    {"title": "Sales Orders (SO)", "subtitle": "Multi-item orders, packing specs & stock reservations", "badge": str(counts.get("sls_orders_count", 6)), "url": "/modules/sales?tab=sales-orders", "icon": "shopping-cart", "color": "emerald"},
                    {"title": "Delivery Orders (DO)", "subtitle": "Delivery orders, fleet dispatch & gate passes", "badge": str(counts.get("sls_do_count", 2)), "url": "/modules/sales?tab=delivery-orders", "icon": "truck", "color": "cyan"},
                    {"title": "Sales Invoices", "subtitle": "Commercial tax invoices & export documentation", "badge": str(counts.get("sls_inv_count", 2)), "url": "/modules/sales?tab=invoices", "icon": "receipt", "color": "indigo"},
                    {"title": "Sales Returns & Credits", "subtitle": "Goods return memos & reverse credit invoices", "badge": str(counts.get("sls_returns_count", 1)), "url": "/modules/sales?tab=returns", "icon": "rotate-ccw", "color": "rose"},
                    {"title": "Sales Target Budgets", "subtitle": "Annual/Quarterly targets by rep and customer", "badge": str(counts.get("sls_budgets_count", 4)), "url": "/modules/sales?tab=budgets", "icon": "pie-chart", "color": "amber"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Process, e-Approval & DSS Suite",
                "subtitle": "Document Flow, Multi-Tier e-Approval & Margin Simulator",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "4 Operations",
                "cards": [
                    {"title": "Document Flow Studio", "subtitle": "Visual lifecycle trace (Quote -> SO -> DO -> Invoice -> GL)", "badge": "Visual Flow", "url": "/modules/sales?tab=document-flow", "icon": "git-merge", "color": "purple"},
                    {"title": "e-Approval Hub", "subtitle": "Executive validation for credit & discount limit breaches", "badge": "e-Sign Queue", "url": "/modules/sales?tab=e-approvals", "icon": "check-check", "color": "indigo"},
                    {"title": "DSS Margin Simulator", "subtitle": "Decision Support: Gross profit & floor price checking", "badge": "DSS Engine", "url": "/modules/sales?tab=dss-simulator", "icon": "calculator", "color": "amber"},
                    {"title": "On-Hold Orders Queue", "subtitle": "Manage orders blocked for credit or stock shortage", "badge": str(counts.get("sls_on_hold_count", 1)) + " On Hold", "url": "/modules/sales?tab=on-hold-orders", "icon": "pause-circle", "color": "rose"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Analytical & Dynamic Pivot Suite",
                "subtitle": "Sales, Collection & AR Pivots, MM-ZM-TSM Drilldown",
                "icon": "bar-chart-2",
                "theme_color": "amber",
                "count_label": "3 Operations",
                "cards": [
                    {"title": "Sales, Collection & AR Pivot", "subtitle": "Monthly & yearly billed vs collected analytics", "badge": "Live Matrix", "url": "/modules/sales?tab=sales-collection-pivot", "icon": "bar-chart-3", "color": "amber"},
                    {"title": "MM > ZM > TSM Performance", "subtitle": "Hierarchical drilldown by management structure", "badge": "Hierarchy", "url": "/modules/sales?tab=hierarchy-performance", "icon": "trending-up", "color": "emerald"},
                    {"title": "Target vs Achievement", "subtitle": "Rep-wise budget vs actual billing variance matrix", "badge": "Variance", "url": "/modules/sales?tab=target-achievement", "icon": "target", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Reporting & Document Print Studio",
                "subtitle": "DO Pending Reconciliation, Profitability & Formal Printouts",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "4 Sub-Areas",
                "cards": [
                    {"title": "DO-GI-Invoice Pending", "subtitle": "Reconciliation audit of uninvoiced delivery orders", "badge": "Reconcile", "url": "/modules/sales?tab=do-invoice-pending", "icon": "clock-4", "color": "rose"},
                    {"title": "Consolidated Statement", "subtitle": "Multi-company gross turnover & net outstanding", "badge": "Consolidated", "url": "/modules/sales?tab=consolidated-statement", "icon": "file-spreadsheet", "color": "indigo"},
                    {"title": "Profitability Analysis", "subtitle": "Item-wise gross margins & discount audit", "badge": "Margins", "url": "/modules/sales?tab=profitability-report", "icon": "file-text", "color": "emerald"},
                    {"title": "Sales Print Studio", "subtitle": "Formal letterhead printouts for Quotes, SO, DO & Invoices", "badge": "Print Hub", "url": "/modules/sales?tab=sales-print-studio", "icon": "printer", "color": "teal"},
                ]
            }
        ]

    # 6. DEFAULT DYNAMIC SUITE BUILDER FOR ALL OTHER 15 ENTERPRISE MODULES
    # Automatically generates the standardized 5 enterprise suites based on module domain!
    return _generate_default_enterprise_suites(slug)

def _generate_default_enterprise_suites(slug: str) -> List[Dict[str, Any]]:
    """
    Generates standard 5-tier enterprise suite for any operational, supply chain,
    manufacturing, property, HR, or admin module.
    """
    # Look up human-friendly names
    module_row = db.query_one("SELECT name, domain_group FROM enterprise_modules WHERE route_slug = ?", (slug,))
    mod_name = module_row["name"] if module_row else slug.replace("-", " ").title()
    domain = module_row["domain_group"] if module_row else "Enterprise Operations"

    return [
        {
            "suite_id": 1,
            "title": "Master Setup Suite",
            "subtitle": f"Core Master Catalogs, Policies & System Parameters for {mod_name}",
            "icon": "settings-2",
            "theme_color": "blue",
            "count_label": "Master Setup",
            "cards": [
                {"title": f"{mod_name} Master", "subtitle": "Primary entities, definitions & specifications", "badge": "Master", "url": f"/modules/{slug}?tab=master", "icon": "layers", "color": "blue"},
                {"title": "Categories & Groups", "subtitle": "Classifications, hierarchies & structural tags", "badge": "Hierarchy", "url": f"/modules/{slug}?tab=categories", "icon": "tags", "color": "indigo"},
                {"title": "Company Allocation", "subtitle": "Operating subsidiary & multi-entity rules", "badge": "Multi-Org", "url": f"/modules/{slug}?tab=mapping", "icon": "building-2", "color": "cyan"},
                {"title": "Policies & Parameters", "subtitle": "System workflows, default values & thresholds", "badge": "Config", "url": f"/modules/{slug}?tab=policies", "icon": "sliders", "color": "emerald"},
            ]
        },
        {
            "suite_id": 2,
            "title": "Transaction Processing & Automation Suite",
            "subtitle": f"Operational Vouchers, Workflow Documents & Processing Engine",
            "icon": "arrow-left-right",
            "theme_color": "emerald",
            "count_label": "Transactions",
            "cards": [
                {"title": f"New {mod_name} Transaction", "subtitle": "Create operational entry & distribution lines", "badge": "New Entry", "url": f"/modules/{slug}?tab=transactions", "icon": "plus-circle", "color": "emerald"},
                {"title": "Batch Processing Engine", "subtitle": "Automated multi-record compilation & staging", "badge": "Batch", "url": f"/modules/{slug}?tab=batches", "icon": "package-check", "color": "cyan"},
                {"title": "Adjustment & Reclassification", "subtitle": "Corrective entries, adjustments & re-allocations", "badge": "Adjust", "url": f"/modules/{slug}?tab=adjustments", "icon": "file-check-2", "color": "blue"},
                {"title": "Document Print Studio", "subtitle": "Printable documents with formal sign-off blocks", "badge": "Print", "url": f"/modules/{slug}?tab=print-docs", "icon": "printer", "color": "rose"},
            ]
        },
        {
            "suite_id": 3,
            "title": "Process, Approval & Closing Suite",
            "subtitle": "Workflow Approvals, Periodic Cycles & Integrity Diagnostics",
            "icon": "check-check",
            "theme_color": "purple",
            "count_label": "Process Suite",
            "cards": [
                {"title": "Post & Commit Engine", "subtitle": "Bulk commit staged transactions to master records", "badge": "Commit", "url": f"/modules/{slug}?tab=post-process", "icon": "check-circle", "color": "purple"},
                {"title": "Data Integrity Diagnostics", "subtitle": "Diagnostic scanner verifying foreign keys & parity", "badge": "Diagnostic", "url": f"/modules/{slug}?tab=integrity", "icon": "shield-check", "color": "indigo"},
            ]
        },
        {
            "suite_id": 4,
            "title": "Analytical & Control Suite",
            "subtitle": "Performance Metrics, Variance Calculations & KPI Dashboards",
            "icon": "bar-chart-2",
            "theme_color": "amber",
            "count_label": "Analytics",
            "cards": [
                {"title": f"{mod_name} Analysis", "subtitle": "Variance analysis, budget tracking & utilization", "badge": "Analytics", "url": f"/modules/{slug}?tab=analysis", "icon": "bar-chart-3", "color": "amber"},
                {"title": "Real-Time Status Monitor", "subtitle": "Live activity lookup, queues & pipeline tracking", "badge": "Live", "url": f"/modules/{slug}?tab=status-monitor", "icon": "activity", "color": "blue"},
            ]
        },
        {
            "suite_id": 5,
            "title": "Reporting & Statements Suite",
            "subtitle": f"Statutory Registers, Periodic Schedules & Exportable Reports",
            "icon": "file-pie-chart",
            "theme_color": "rose",
            "count_label": "Reports",
            "cards": [
                {"title": f"{mod_name} Master Register", "subtitle": "Comprehensive audit register with line details", "badge": "Register", "url": f"/modules/{slug}?tab=master-register", "icon": "file-text", "color": "rose"},
                {"title": "Periodic Movement Schedule", "subtitle": "Opening balance, period activity & closing values", "badge": "Schedule", "url": f"/modules/{slug}?tab=schedule", "icon": "calendar-range", "color": "indigo"},
                {"title": "Executive Summary Report", "subtitle": "High-level summary metrics & management charts", "badge": "Executive", "url": f"/modules/{slug}?tab=executive-summary", "icon": "pie-chart", "color": "emerald"},
            ]
        }
    ]

def get_active_suite_context(slug: str, current_tab: Optional[str], module_suites: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    """
    Given the current module slug and active tab, finds which of the 5 Enterprise Suites
    the tab belongs to, and returns its sibling cards and suite theme metadata.
    Returns None if current_tab is 'overview' or None, or if the suite has <= 1 cards.
    """
    if not current_tab or current_tab == "overview":
        return None

    suites = module_suites or get_module_suites_registry(slug)
    if not suites:
        return None

    clean_tab = current_tab.strip().lower()

    for suite in suites:
        cards = suite.get("cards", [])
        for card in cards:
            url = card.get("url", "")
            if f"tab={clean_tab}" in url or url.endswith(f"/{clean_tab}") or url.endswith(f"?tab={clean_tab}"):
                return {
                    "suite_id": suite.get("suite_id"),
                    "title": suite.get("title"),
                    "subtitle": suite.get("subtitle"),
                    "icon": suite.get("icon", "layers"),
                    "theme_color": suite.get("theme_color", "blue"),
                    "cards": cards,
                    "active_tab": clean_tab
                }
    return None
