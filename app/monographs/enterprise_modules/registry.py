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


    # 7. INVENTORY MANAGEMENT MODERN 5-SUITE REGISTRY
    if slug in ("inventory", "inventory-management"):
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Warehouses, Bins, Product Groups & Unit of Measure Conversions",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "5 Sub-Areas",
                "cards": [
                    {"title": "Warehouses Master", "subtitle": "Storage plants, regional depots & transit hubs", "badge": str(counts.get("inv_wh_count", 6)), "url": "/modules/inventory?tab=warehouses", "icon": "warehouse", "color": "blue"},
                    {"title": "Multi-Bin Storage", "subtitle": "Aisle, rack, shelf & bin location map", "badge": str(counts.get("inv_bin_count", 5)), "url": "/modules/inventory?tab=bins", "icon": "grid", "color": "indigo"},
                    {"title": "Product Groups & Classes", "subtitle": "RM, FG, WIP, Spares & Consumables categories", "badge": str(counts.get("inv_group_count", 6)), "url": "/modules/inventory?tab=product-groups", "icon": "folder-tree", "color": "cyan"},
                    {"title": "UOM & Conversions", "subtitle": "Unit of measures & conversion multipliers", "badge": str(counts.get("inv_uom_count", 6)), "url": "/modules/inventory?tab=uom", "icon": "scale", "color": "emerald"},
                    {"title": "Master Items Catalog", "subtitle": "Item codes, specifications & reorder points", "badge": str(counts.get("inv_item_count", 4)), "url": "/modules/inventory?tab=items", "icon": "package", "color": "amber"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Transaction Processing & Movement Suite",
                "subtitle": "GRNs, Issue Challans, STO Transfers, Kitting & Adjustments",
                "icon": "arrow-left-right",
                "theme_color": "emerald",
                "count_label": "5 Operations",
                "cards": [
                    {"title": "Goods Receiving Notes (GRN)", "subtitle": "Inward receipts from vendor PO, production & returns", "badge": str(counts.get("inv_grn_count", 1)), "url": "/modules/inventory?tab=grn", "icon": "arrow-down-left", "color": "emerald"},
                    {"title": "Goods Issue Challans", "subtitle": "Outbound dispatches for DO, WIP, spares & cost centers", "badge": str(counts.get("inv_issue_count", 1)), "url": "/modules/inventory?tab=issues", "icon": "arrow-up-right", "color": "blue"},
                    {"title": "Stock Transfer Orders (STO)", "subtitle": "Inter-warehouse transfers with in-transit tracking", "badge": str(counts.get("inv_sto_count", 1)), "url": "/modules/inventory?tab=stock-transfers", "icon": "truck", "color": "cyan"},
                    {"title": "Material Kitting & Assembly", "subtitle": "BOM component conversion & bundle disassembly", "badge": "Assembly", "url": "/modules/inventory?tab=assembly", "icon": "layers", "color": "indigo"},
                    {"title": "Physical Cycle Adjustments", "subtitle": "Periodic physical count variance (+/-) adjustments", "badge": str(counts.get("inv_adj_count", 1)), "url": "/modules/inventory?tab=adjustments", "icon": "sliders-horizontal", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Process, e-Approval & Closing Suite",
                "subtitle": "Quality QA Approvals, Wave Picking Lists & Day-End Closing",
                "icon": "check-check",
                "theme_color": "purple",
                "count_label": "3 Operations",
                "cards": [
                    {"title": "e-Approval Hub", "subtitle": "QA inspection sign-offs & STO dispatch approvals", "badge": "Approval Queue", "url": "/modules/inventory?tab=e-approvals", "icon": "check-check", "color": "indigo"},
                    {"title": "Wave Picking Lists", "subtitle": "Automated warehouse pick lists by bin location", "badge": "Pick Lists", "url": "/modules/inventory?tab=picking-lists", "icon": "list-checks", "color": "purple"},
                    {"title": "Day-End Inventory Closing", "subtitle": "EOD ledger reconciliation & balance snapshots", "badge": "EOD Process", "url": "/modules/inventory?tab=day-end-closing", "icon": "clock-4", "color": "amber"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Warranty, Serialization & Barcode Suite",
                "subtitle": "Serial Number Registry, Barcode Scanner & Warranty Inquiry",
                "icon": "shield-check",
                "theme_color": "amber",
                "count_label": "2 Operations",
                "cards": [
                    {"title": "Serial & Warranty Registry", "subtitle": "Serialized tracking, warranty terms & AMC contracts", "badge": str(counts.get("inv_warranty_count", 2)), "url": "/modules/inventory?tab=warranties", "icon": "barcode", "color": "amber"},
                    {"title": "Barcode & Serial Scanner", "subtitle": "Live scanner inquiry for serial & warranty validity", "badge": "Scanner Studio", "url": "/modules/inventory?tab=barcode-inquiry", "icon": "scan", "color": "emerald"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Reporting, Statements & Valuation Analysis Suite",
                "subtitle": "Product Ledger, Valuation, DO Reconciliation, WIP Costing & Statements",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "10 Report Areas",
                "cards": [
                    {"title": "Product Ledger (Stock Card)", "subtitle": "Item-wise running balance statement with inward & outward logs", "badge": "Ledger", "url": "/modules/inventory?tab=product-ledger", "icon": "file-text", "color": "blue"},
                    {"title": "Inventory Valuation Report", "subtitle": "Group & warehouse valuation breakdown with GL asset parity", "badge": "Valuation", "url": "/modules/inventory?tab=inventory-valuation", "icon": "calculator", "color": "emerald"},
                    {"title": "DO vs Dispatch Reconciliation", "subtitle": "Delivery order confirmed vs actual dispatch challan variance", "badge": "DO Audit", "url": "/modules/inventory?tab=do-vs-dispatch", "icon": "clock-4", "color": "amber"},
                    {"title": "WIP Production Costing", "subtitle": "Raw materials and tooling issued to manufacturing job cards", "badge": "WIP Cost", "url": "/modules/inventory?tab=production-costing", "icon": "layers", "color": "purple"},
                    {"title": "Plant-Wise Consumption", "subtitle": "Multi-plant consumption breakdown and cost center split", "badge": "Plant Audit", "url": "/modules/inventory?tab=plant-consumption", "icon": "building-2", "color": "cyan"},
                    {"title": "Inter-Warehouse STO Statement", "subtitle": "Plant-to-plant transfer audit with dispatch vs receipt tracking", "badge": "STO Audit", "url": "/modules/inventory?tab=sto-reports", "icon": "truck", "color": "indigo"},
                    {"title": "Live Stock Balance Matrix", "subtitle": "On-hand, reserved, in-transit & available balances", "badge": "Live Matrix", "url": "/modules/inventory?tab=stock-balances", "icon": "bar-chart-3", "color": "blue"},
                    {"title": "Goods in Transit (GIT)", "subtitle": "Inter-plant shipments on the road with carrier tracking", "badge": str(counts.get("inv_git_count", 1)) + " In Transit", "url": "/modules/inventory?tab=goods-in-transit", "icon": "navigation", "color": "cyan"},
                    {"title": "ABC & Reorder Analytics", "subtitle": "Fast vs slow moving stock & safety stock alerts", "badge": "ABC Analysis", "url": "/modules/inventory?tab=abc-analysis", "icon": "pie-chart", "color": "indigo"},
                    {"title": "Warehouse Print Studio", "subtitle": "Printable letterheads for GRN, Challans, STO & Warranties", "badge": "Print Hub", "url": "/modules/inventory?tab=warehouse-print-studio", "icon": "printer", "color": "rose"},
                ]
            }
        ]




    # =========================================================================
    # 6. FIXED ASSETS & ASSET ACCOUNTING (5-SUITE ENTERPRISE ARCHITECTURE)
    # =========================================================================
    if slug in ("fixed-assets", "fixed-asset-management"):
        return [
            {
                "suite_id": 1,
                "title": "Master Setup Suite",
                "subtitle": "Asset Groups, Locations, Sub-Locations, Policies & GL Sets",
                "icon": "settings",
                "theme_color": "blue",
                "count_label": "5 Setup Areas",
                "cards": [
                    {"title": "Asset Groups & Classes", "subtitle": "Machinery, Buildings, Land, Vehicles, IT & Furniture", "badge": str(counts.get("fa_groups_count", 6)) + " Groups", "url": "/modules/fixed-assets?tab=fa-groups", "icon": "layers", "color": "blue"},
                    {"title": "Physical Locations", "subtitle": "Primary manufacturing plants, facilities & yards", "badge": str(counts.get("fa_locs_count", 2)) + " Plants", "url": "/modules/fixed-assets?tab=fa-locations", "icon": "building-2", "color": "emerald"},
                    {"title": "Sub-Locations & Machine Bays", "subtitle": "Production bays, server rooms & executive floors", "badge": "2D Coordinates", "url": "/modules/fixed-assets?tab=fa-sub-locations", "icon": "grid", "color": "purple"},
                    {"title": "Depreciation Policies", "subtitle": "SLM, WDV, useful life years & salvage value %", "badge": "SLM & WDV", "url": "/modules/fixed-assets?tab=fa-policies", "icon": "percent", "color": "amber"},
                    {"title": "GL Control Account Sets", "subtitle": "Direct GL mapping for Cost, Acc Depr, Expense & Gain/Loss", "badge": "GL Mapped", "url": "/modules/fixed-assets?tab=fa-gl-control", "icon": "landmark", "color": "indigo"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Asset Register & Lifecycle Suite",
                "subtitle": "Capitalization, GRN Inwarding, Transfers, Disposals & Spares",
                "icon": "box",
                "theme_color": "emerald",
                "count_label": "6 Operational Areas",
                "cards": [
                    {"title": "Master Asset Register", "subtitle": "Capital asset registry with barcode tags, serials & costs", "badge": str(counts.get("fa_assets_count", 4)) + " Active Assets", "url": "/modules/fixed-assets?tab=fa-assets", "icon": "file-text", "color": "blue"},
                    {"title": "Capital Asset Receipts (Asset GRN)", "subtitle": "PO-linked Capex inwarding with QA laser alignment sign-off", "badge": "Inwarding", "url": "/modules/fixed-assets?tab=fa-grn", "icon": "inbox", "color": "emerald"},
                    {"title": "Leased & Low-Value Assets", "subtitle": "Operating/Finance lease tracking and expensed tooling", "badge": "Leased/Expensed", "url": "/modules/fixed-assets?tab=fa-leased", "icon": "clock-4", "color": "amber"},
                    {"title": "Asset Transfers Log", "subtitle": "Inter-departmental, inter-plant & custodian reallocations", "badge": "Transfers", "url": "/modules/fixed-assets?tab=fa-transfers", "icon": "repeat", "color": "purple"},
                    {"title": "Disposals & Write-Offs", "subtitle": "Asset retirement, scrapping & sale with automated gain/loss", "badge": "Disposals", "url": "/modules/fixed-assets?tab=fa-disposals", "icon": "trash-2", "color": "rose"},
                    {"title": "Machine-Spares Mapping", "subtitle": "Linking inventory spare parts to parent capital machines", "badge": "Spares Map", "url": "/modules/fixed-assets?tab=fa-spares", "icon": "cpu", "color": "cyan"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Depreciation Engine & GL Automation Suite",
                "subtitle": "Depreciation Runs, Live Simulator, e-Approvals & GL Postings",
                "icon": "calculator",
                "theme_color": "purple",
                "count_label": "3 Process Areas",
                "cards": [
                    {"title": "Depreciation Execution Runs", "subtitle": "Monthly & annual automated depreciation posting history", "badge": "Depr Runs", "url": "/modules/fixed-assets?tab=fa-depr-runs", "icon": "history", "color": "purple"},
                    {"title": "Depreciation Live Simulator", "subtitle": "1-Click period depreciation calculation engine (SLM & WDV)", "badge": "Simulator", "url": "/modules/fixed-assets?tab=fa-depr-simulation", "icon": "play-circle", "color": "emerald"},
                    {"title": "Digital e-Approvals Hub", "subtitle": "Multi-tier engineering QA and CFO Capex authorization", "badge": "e-Approvals", "url": "/modules/fixed-assets?tab=fa-approvals", "icon": "shield-check", "color": "indigo"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Physical Verification & Barcode Studio Suite",
                "subtitle": "Field Barcode Audits, Scanner Inquiry & Tag Generator",
                "icon": "qr-code",
                "theme_color": "amber",
                "count_label": "2 Audit Areas",
                "cards": [
                    {"title": "Physical Verification Audits", "subtitle": "Field audit checklists reconciling Found vs Missing assets", "badge": "Audits", "url": "/modules/fixed-assets?tab=fa-audits", "icon": "check-circle-2", "color": "emerald"},
                    {"title": "Barcode & Tag Scanner Studio", "subtitle": "Live barcode / serial lookup and printable asset tag labels", "badge": "Barcode Hub", "url": "/modules/fixed-assets?tab=fa-scanner", "icon": "scan", "color": "amber"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Statutory Asset Schedules & Reporting Suite",
                "subtitle": "IAS 16 / IFRS Statutory Schedules, Summaries & Print Studio",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "4 Reporting Areas",
                "cards": [
                    {"title": "Executive Summary of Fixed Assets", "subtitle": "Gross Block, Accumulated Depr & Net Book Value KPIs", "badge": "Executive KPI", "url": "/modules/fixed-assets?tab=fa-summary", "icon": "pie-chart", "color": "blue"},
                    {"title": "Statutory Asset Schedule (IAS 16)", "subtitle": "IFRS statutory schedule (Opening, Additions, Depr, Closing NBV)", "badge": "IAS 16 / IFRS", "url": "/modules/fixed-assets?tab=fa-statutory-schedule", "icon": "table", "color": "emerald"},
                    {"title": "Asset Movement Audit Statement", "subtitle": "Historical plant and custodian movement statements", "badge": "Movement Log", "url": "/modules/fixed-assets?tab=fa-movement-report", "icon": "navigation", "color": "cyan"},
                    {"title": "Fixed Asset Print Studio", "subtitle": "Printable letterheads for Asset GRN, Transfer & Disposal Slips", "badge": "Print Hub", "url": "/modules/fixed-assets?tab=fa-print-studio", "icon": "printer", "color": "rose"},
                ]
            }
        ]

    # =========================================================================
    # 7. HUMAN RESOURCES, PAYROLL & TALENT (5-SUITE ENTERPRISE ARCHITECTURE)
    # =========================================================================
    if slug in ("hris", "hr", "human-resources", "human-capital"):
        return [
            {
                "suite_id": 1,
                "title": "Personnel & Organization Master Setup Suite",
                "subtitle": "Grades, Departments, Designations, Work-Shifts, Holiday Calendar & Leave Quotas",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "7 Setup Areas",
                "cards": [
                    {"title": "Employee Grades & Bands", "subtitle": "Executive, Management & Operator pay bands", "badge": str(counts.get("hr_grades_count", 6)) + " Grades", "url": "/modules/hris?tab=hr-grades", "icon": "award", "color": "blue"},
                    {"title": "Departments Master", "subtitle": "Organizational divisions & cost centers", "badge": str(counts.get("hr_depts_count", 6)) + " Depts", "url": "/modules/hris?tab=hr-departments", "icon": "building-2", "color": "indigo"},
                    {"title": "Designations & Titles", "subtitle": "Job titles, skill levels & rank hierarchy", "badge": "Designations", "url": "/modules/hris?tab=hr-designations", "icon": "badge-check", "color": "purple"},
                    {"title": "Work-Shifts & Roster", "subtitle": "Morning, Day, Night & 24/7 security schedules", "badge": "Shifts", "url": "/modules/hris?tab=hr-shifts", "icon": "clock", "color": "amber"},
                    {"title": "Annual Holiday Calendar", "subtitle": "Public holidays & corporate off days", "badge": "Calendar", "url": "/modules/hris?tab=hr-holidays", "icon": "calendar", "color": "emerald"},
                    {"title": "Leave Policies & Types", "subtitle": "Casual, Sick, Earned & Maternity quotas", "badge": "Quotas", "url": "/modules/hris?tab=hr-leave-types", "icon": "file-heart", "color": "rose"},
                    {"title": "Corporate Bank Accounts", "subtitle": "Salary disbursement accounts & routing", "badge": "Banking", "url": "/modules/hris?tab=hr-bank-accounts", "icon": "landmark", "color": "cyan"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Talent Acquisition & Employee Lifecycle Suite",
                "subtitle": "Employee Dossiers, Contract Workers, Transfers, Vault & Recruitment",
                "icon": "users",
                "theme_color": "emerald",
                "count_label": "6 Operational Areas",
                "cards": [
                    {"title": "Master Employee Profiles", "subtitle": "Comprehensive digital dossier, compensation & banking", "badge": str(counts.get("hr_employees_count", 4)) + " Staff", "url": "/modules/hris?tab=hr-employees", "icon": "user-check", "color": "emerald"},
                    {"title": "Temporary & Casual Workers", "subtitle": "Daily wage, piece-rate & contract labor rosters", "badge": "Contractors", "url": "/modules/hris?tab=hr-contract-workers", "icon": "hard-hat", "color": "amber"},
                    {"title": "Digital Document Vault", "subtitle": "Contracts, national IDs, degrees & certificates", "badge": "Vault", "url": "/modules/hris?tab=hr-documents", "icon": "folder-lock", "color": "blue"},
                    {"title": "Transfers & Promotions Log", "subtitle": "Inter-plant, departmental transfers & grade adjustments", "badge": "Transfers", "url": "/modules/hris?tab=hr-transfers", "icon": "repeat", "color": "purple"},
                    {"title": "Manpower Job Requisitions", "subtitle": "Hiring requests with multi-tier e-approvals", "badge": "Requisitions", "url": "/modules/hris?tab=hr-requisitions", "icon": "briefcase", "color": "indigo"},
                    {"title": "CV Bank & Interview Scoring", "subtitle": "Candidate talent pool & structured interview rubric", "badge": "Talent Pool", "url": "/modules/hris?tab=hr-candidates", "icon": "user-plus", "color": "cyan"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Time, Attendance & Leave Management Suite",
                "subtitle": "Biometric Sync, Leave Applications, Overtime Engine & Late Rules",
                "icon": "calendar-check",
                "theme_color": "purple",
                "count_label": "3 Time Areas",
                "cards": [
                    {"title": "Biometric Punch Logs", "subtitle": "Daily biometric clock-in, terminal sync & late detection", "badge": "Live Biometrics", "url": "/modules/hris?tab=hr-attendance-log", "icon": "fingerprint", "color": "purple"},
                    {"title": "Leave Applications & Ledger", "subtitle": "Online leave requests & approval workflow engine", "badge": "Approvals", "url": "/modules/hris?tab=hr-leaves", "icon": "calendar-heart", "color": "rose"},
                    {"title": "Overtime (OT) Engine Matrix", "subtitle": "Staff OT hours tracking with 1.5x / 2.0x rates", "badge": "Overtime", "url": "/modules/hris?tab=hr-overtime", "icon": "timer", "color": "amber"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Payroll, Loans, Income Tax & GL Processing Suite",
                "subtitle": "Gross-to-Net Engine, Loans Amortization, Tax Slabs & GL Postings",
                "icon": "calculator",
                "theme_color": "amber",
                "count_label": "5 Financial Areas",
                "cards": [
                    {"title": "Monthly Payroll Runs", "subtitle": "1-Click automated Gross-to-Net salary calculation batch", "badge": "Payroll Batch", "url": "/modules/hris?tab=hr-payroll-runs", "icon": "wallet", "color": "emerald"},
                    {"title": "Itemized Payslips Register", "subtitle": "Full earnings & deductions breakdown with net payout", "badge": "Payslips", "url": "/modules/hris?tab=hr-payslips", "icon": "receipt", "color": "blue"},
                    {"title": "Employee Loans & Advances", "subtitle": "Loan disbursement, EMI recovery & amortization schedules", "badge": "Loans", "url": "/modules/hris?tab=hr-loans", "icon": "coins", "color": "amber"},
                    {"title": "Income Tax Slabs & Rebates", "subtitle": "Statutory graduated tax slabs & investment rebates", "badge": "TIN & Slabs", "url": "/modules/hris?tab=hr-tax-slabs", "icon": "scale", "color": "indigo"},
                    {"title": "Treasury Tax Deposit Log", "subtitle": "Treasury challan remittance & GL withholding tax posting", "badge": "Treasury Challan", "url": "/modules/hris?tab=hr-tax-deposits", "icon": "landmark", "color": "purple"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Statements, Statutory Reports & Print Studio Suite",
                "subtitle": "Salary Registers, Bank Advice, Tax Statements, PF Ledger & Print Hub",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "5 Reporting Areas",
                "cards": [
                    {"title": "Executive Workforce KPIs", "subtitle": "Headcount, monthly salary budget, loan balances & PF", "badge": "Executive Hub", "url": "/modules/hris?tab=hr-summary", "icon": "pie-chart", "color": "blue"},
                    {"title": "Consolidated Salary Register", "subtitle": "Group-wide and plant-wide monthly salary matrix", "badge": "Salary Sheet", "url": "/modules/hris?tab=hr-salary-register", "icon": "file-spreadsheet", "color": "emerald"},
                    {"title": "Corporate Bank Advice", "subtitle": "Standard salary disbursement advice statement", "badge": "Bank Advice", "url": "/modules/hris?tab=hr-bank-advice", "icon": "credit-card", "color": "cyan"},
                    {"title": "Provident Fund (PF) Ledger", "subtitle": "Employee contribution, employer matching & balance", "badge": "PF Statement", "url": "/modules/hris?tab=hr-pf-ledger", "icon": "shield-dollar", "color": "purple"},
                    {"title": "HR Official Print Studio", "subtitle": "Printable Payslips, Appointment Letters & Transfer Orders", "badge": "Print Hub", "url": "/modules/hris?tab=hr-print-studio", "icon": "printer", "color": "rose"},
                ]
            }
        ]


    # =========================================================================
    # 8. PRODUCTION & MANUFACTURING MANAGEMENT (5-SUITE ENTERPRISE ARCHITECTURE)
    # =========================================================================
    if slug in ("production", "manufacturing", "production-management"):
        return [
            {
                "suite_id": 1,
                "title": "Engineering Masters, BOM & Plant Routing Setup Suite",
                "subtitle": "Manufacturing Processes, Plants, Work Centers, Multi-Step Routings, Capacity & Engineering BOMs",
                "icon": "settings-2",
                "theme_color": "blue",
                "count_label": "7 Setup Areas",
                "cards": [
                    {"title": "Manufacturing Processes", "subtitle": "Cutting, Machining, Welding, Coating & Testing stages", "badge": "Processes", "url": "/modules/production?tab=prod-processes", "icon": "layers", "color": "blue"},
                    {"title": "Production Plants & Works", "subtitle": "Fabrication plants, machine shops & bay locations", "badge": "Plants", "url": "/modules/production?tab=prod-plants", "icon": "building-2", "color": "indigo"},
                    {"title": "Work Centers & Resources", "subtitle": "5-Axis CNC, Robotic cells, Coating lines & CMM stations", "badge": "Work Centers", "url": "/modules/production?tab=prod-resources", "icon": "cpu", "color": "purple"},
                    {"title": "Operational Routings", "subtitle": "Standard sequence, setup & run times per unit", "badge": "Routings", "url": "/modules/production?tab=prod-routings", "icon": "git-commit", "color": "amber"},
                    {"title": "Plant Capacity Profiles", "subtitle": "Shift hours, monthly capacity & load utilization limits", "badge": "Capacity", "url": "/modules/production?tab=prod-capacity", "icon": "sliders", "color": "emerald"},
                    {"title": "Standard Engineering BOM", "subtitle": "Multi-level bill of materials with scrap % & revision history", "badge": "BOM Standard", "url": "/modules/production?tab=prod-bom-standard", "icon": "folder-tree", "color": "cyan"},
                    {"title": "Assembly BOM & Kitting", "subtitle": "Fast modular assembly recipes & kitted packaging sets", "badge": "Assembly BOM", "url": "/modules/production?tab=prod-bom-assembly", "icon": "box", "color": "rose"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Production Orders, Job Cards & Floor Execution Suite",
                "subtitle": "Demand Requisitions, Discrete Work Orders, Job Travelers, WIP Issues & Direct Assembly",
                "icon": "factory",
                "theme_color": "emerald",
                "count_label": "6 Operational Areas",
                "cards": [
                    {"title": "Production Requisitions", "subtitle": "Demand-driven job requests from Sales Orders & buffer stock", "badge": "Requisitions", "url": "/modules/production?tab=prod-requisitions", "icon": "file-text", "color": "blue"},
                    {"title": "Master Production Orders", "subtitle": "Discrete manufacturing work orders with planned vs completed", "badge": "Work Orders", "url": "/modules/production?tab=prod-orders", "icon": "clipboard-list", "color": "emerald"},
                    {"title": "Shop Floor Job Cards", "subtitle": "Operation-level travelers, operator clock-in & actual hours", "badge": "Job Cards", "url": "/modules/production?tab=prod-job-cards", "icon": "wrench", "color": "purple"},
                    {"title": "Material Issues to WIP", "subtitle": "Warehouse raw material and parts issue linked to BOM lines", "badge": "WIP Issues", "url": "/modules/production?tab=prod-mat-issues", "icon": "arrow-up-right", "color": "amber"},
                    {"title": "Assembly Conversions", "subtitle": "Material-to-material instant batch assembly transformation", "badge": "Conversions", "url": "/modules/production?tab=prod-conversions", "icon": "repeat", "color": "cyan"},
                    {"title": "Assembly Reversals & De-Kits", "subtitle": "Disassembly reversal returning component parts to warehouse", "badge": "Reversals", "url": "/modules/production?tab=prod-reversals", "icon": "rotate-ccw", "color": "rose"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Quality Control, Downtime & Process Suite",
                "subtitle": "In-Process QA Inspections, Machine Downtime Tracker, Data Import Hub & Year-End Process",
                "icon": "shield-check",
                "theme_color": "purple",
                "count_label": "4 Control Areas",
                "cards": [
                    {"title": "Quality Inspection Hub", "subtitle": "First-piece, in-process & final QA tolerance test sign-offs", "badge": "Quality QA", "url": "/modules/production?tab=prod-qc-inspections", "icon": "check-circle", "color": "emerald"},
                    {"title": "Machine Downtime Tracker", "subtitle": "Stoppage logging, tool change, breakdown & idle analytics", "badge": "Downtime Log", "url": "/modules/production?tab=prod-downtime", "icon": "alert-triangle", "color": "amber"},
                    {"title": "External Data Import Hub", "subtitle": "Import opening stock, monthly sales forecast & BOM profiles", "badge": "Data Import", "url": "/modules/production?tab=prod-import-data", "icon": "download", "color": "blue"},
                    {"title": "Year-End WIP Process", "subtitle": "Annual production WIP valuation rollover & cost variance close", "badge": "Year-End", "url": "/modules/production?tab=prod-year-end", "icon": "calendar-check", "color": "purple"},
                ]
            },
            {
                "suite_id": 4,
                "title": "Manufacturing Costing & Floor Analytics Suite",
                "subtitle": "Actual vs Standard Costing, OEE Cockpit & Work Center Capacity Heatmap",
                "icon": "calculator",
                "theme_color": "amber",
                "count_label": "3 Analytics Areas",
                "cards": [
                    {"title": "Manufacturing Cost Records", "subtitle": "Actual vs standard costing (Materials, Labor, Overhead, Scrap)", "badge": "Cost Engine", "url": "/modules/production?tab=prod-costing", "icon": "coins", "color": "emerald"},
                    {"title": "OEE Effectiveness Cockpit", "subtitle": "Live Availability x Performance x Quality metrics per machine", "badge": "OEE Cockpit", "url": "/modules/production?tab=prod-oee-monitor", "icon": "gauge", "color": "amber"},
                    {"title": "Capacity Load vs Availability", "subtitle": "Resource load factor, bottleneck identification & shift planning", "badge": "Capacity Load", "url": "/modules/production?tab=prod-capacity-planning", "icon": "bar-chart-2", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Statements, Statutory Registers & Production Print Studio Suite",
                "subtitle": "Executive KPIs, WIP Stage Ledger, Yield & Scrap Statements & Manufacturing Print Studio",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "4 Reporting Areas",
                "cards": [
                    {"title": "Executive Production KPIs", "subtitle": "Throughput volume, scrap rate %, average OEE & WIP valuation", "badge": "Executive Hub", "url": "/modules/production?tab=prod-summary", "icon": "pie-chart", "color": "blue"},
                    {"title": "WIP Stage Balance Ledger", "subtitle": "Stage-by-stage Work-In-Progress balance & completed ops", "badge": "WIP Ledger", "url": "/modules/production?tab=prod-wip-ledger", "icon": "layers", "color": "emerald"},
                    {"title": "Yield & Scrap Variance Report", "subtitle": "Production output yield %, scrap variance & material efficiency", "badge": "Yield Audit", "url": "/modules/production?tab=prod-yield-report", "icon": "scale", "color": "purple"},
                    {"title": "Manufacturing Print Studio", "subtitle": "Official Work Orders, BOM Explosion Sheets, Pick Slips & QA Certs", "badge": "Print Hub", "url": "/modules/production?tab=prod-print-studio", "icon": "printer", "color": "rose"},
                ]
            }
        ]


    # =========================================================================
    # 9. SYSTEM ADMINISTRATION & ENTERPRISE GOVERNANCE (5-SUITE ENTERPRISE ARCHITECTURE)
    # =========================================================================
    if slug in ("system-admin", "system_admin", "admin", "system-administration"):
        return [
            {
                "suite_id": 1,
                "title": "Global Organization, Locales & Currencies Setup Suite",
                "subtitle": "Multi-Entity Companies, Business Units, Cost Centers, Geo Locales, Multi-Currency Board & Printers",
                "icon": "globe",
                "theme_color": "blue",
                "count_label": "6 Setup Areas",
                "cards": [
                    {"title": "Company Profile & Multi-Entity Setup", "subtitle": "Subsidiaries, legal entity, registration & tax ID", "badge": "Companies", "url": "/modules/system-admin?tab=admin-companies", "icon": "building-2", "color": "blue"},
                    {"title": "Business Units & Cost Centers", "subtitle": "Divisional hierarchy, operating branches & profit centers", "badge": "Units & CC", "url": "/modules/system-admin?tab=admin-units", "icon": "network", "color": "indigo"},
                    {"title": "Countries, States & Locales", "subtitle": "ISO geographic directory, currency codes & locale formats", "badge": "Geo Locales", "url": "/modules/system-admin?tab=admin-geo", "icon": "map-pin", "color": "cyan"},
                    {"title": "Multi-Currency & Daily Rates", "subtitle": "ISO currency profiles & real-time exchange rate table", "badge": "Currencies", "url": "/modules/system-admin?tab=admin-currencies", "icon": "coins", "color": "amber"},
                    {"title": "Fiscal Calendars & Periods", "subtitle": "12-period fiscal calendar & opening balance lock", "badge": "Calendars", "url": "/modules/system-admin?tab=admin-calendars", "icon": "calendar-range", "color": "emerald"},
                    {"title": "Network Printers & Spoolers", "subtitle": "Print servers, thermal slip drivers & default trays", "badge": "Printers", "url": "/modules/system-admin?tab=admin-printers", "icon": "printer", "color": "rose"},
                ]
            },
            {
                "suite_id": 2,
                "title": "Access Control, Roles & Security Governance Suite",
                "subtitle": "User Profiles, Granular RBAC Permissions Matrix, Data Scopes, Password Policies & Live Sessions",
                "icon": "shield-check",
                "theme_color": "emerald",
                "count_label": "5 Security Areas",
                "cards": [
                    {"title": "Enterprise User Profiles", "subtitle": "User credentials directory, departments & MFA status", "badge": "Users", "url": "/modules/system-admin?tab=admin-users", "icon": "users", "color": "emerald"},
                    {"title": "Role-Based Access Control (RBAC)", "subtitle": "Function access matrix (View/Create/Edit/Delete/Approve)", "badge": "Roles & RBAC", "url": "/modules/system-admin?tab=admin-roles", "icon": "key-round", "color": "purple"},
                    {"title": "Cost & Profit Center Scopes", "subtitle": "Subsidiary, business unit & cost center data restrictions", "badge": "Data Scopes", "url": "/modules/system-admin?tab=admin-auth-scope", "icon": "lock", "color": "blue"},
                    {"title": "Password Vault & Security Policy", "subtitle": "Complexity rules, password renewal, reset & MFA keys", "badge": "Pass Vault", "url": "/modules/system-admin?tab=admin-passwords", "icon": "key", "color": "amber"},
                    {"title": "Live Sessions & Security Telemetry", "subtitle": "Real-time active logins, device IP & session management", "badge": "Live Sessions", "url": "/modules/system-admin?tab=admin-sessions", "icon": "radio", "color": "cyan"},
                ]
            },
            {
                "suite_id": 3,
                "title": "Tax Engine & Statutory Authorities Suite",
                "subtitle": "Statutory Revenue Boards, Tax Categories, VAT/GST Profiles & Standard GL Account Linkages",
                "icon": "landmark",
                "theme_color": "purple",
                "count_label": "3 Statutory Areas",
                "cards": [
                    {"title": "Statutory Tax Authorities", "subtitle": "Federal IRS, State Revenue & National Board of Revenue", "badge": "Authorities", "url": "/modules/system-admin?tab=admin-tax-authorities", "icon": "landmark", "color": "purple"},
                    {"title": "Tax Classification Categories", "subtitle": "Standard VAT, Reduced, Zero-Rated, Withholding & Sales Tax", "badge": "Categories", "url": "/modules/system-admin?tab=admin-tax-categories", "icon": "tags", "color": "blue"},
                    {"title": "Tax Rates & Profile Slabs", "subtitle": "Active calculation rates %, GL account mapping & recovery", "badge": "Tax Profiles", "url": "/modules/system-admin?tab=admin-tax-profiles", "icon": "receipt", "color": "emerald"},
                ]
            },
            {
                "suite_id": 4,
                "title": "System Diagnostics, Periodic Process & Integrity Suite",
                "subtitle": "Database Integrity Scanner, Recalculate Ledgers, Month-End Module Closures & Backup Points",
                "icon": "cpu",
                "theme_color": "amber",
                "count_label": "4 Maintenance Areas",
                "cards": [
                    {"title": "Database Integrity & Scanner", "subtitle": "Foreign key parity, orphan checks & ledger recalculation", "badge": "Integrity", "url": "/modules/system-admin?tab=admin-integrity", "icon": "activity", "color": "amber"},
                    {"title": "Consolidated Month-End Close", "subtitle": "Periodic close for Cash, AR, AP, Inventory, HR & Assets", "badge": "Month-End", "url": "/modules/system-admin?tab=admin-periodic", "icon": "check-square", "color": "emerald"},
                    {"title": "Year-End Processing & Balance Sync", "subtitle": "Retained earnings roll-forward & annual balance sync", "badge": "Year-End", "url": "/modules/system-admin?tab=admin-year-end", "icon": "calendar-check-2", "color": "purple"},
                    {"title": "Database Backup Snapshots", "subtitle": "Automated full backups, transaction logs & restore points", "badge": "Backups", "url": "/modules/system-admin?tab=admin-backups", "icon": "hard-drive", "color": "blue"},
                ]
            },
            {
                "suite_id": 5,
                "title": "Audit Vault, System Telemetry & Print Studio Suite",
                "subtitle": "Tamper-Evident System Audit Trail, IT Infrastructure KPIs, License Telemetry & Print Studio",
                "icon": "file-pie-chart",
                "theme_color": "rose",
                "count_label": "4 Telemetry Areas",
                "cards": [
                    {"title": "Tamper-Evident Audit Vault", "subtitle": "Immutable security timeline, entity mutations & IP logs", "badge": "Audit Vault", "url": "/modules/system-admin?tab=admin-audit-log", "icon": "shield-alert", "color": "rose"},
                    {"title": "Executive Administration KPIs", "subtitle": "System health, database score, active nodes & periods", "badge": "Admin KPIs", "url": "/modules/system-admin?tab=admin-kpis", "icon": "pie-chart", "color": "blue"},
                    {"title": "Enterprise Client License", "subtitle": "Autonomous Edition 2026, node limits & support SLA", "badge": "License", "url": "/modules/system-admin?tab=admin-license", "icon": "award", "color": "purple"},
                    {"title": "System Admin Print Studio", "subtitle": "Security Audit Certs, Entity Specs, Tax Schedules & Health", "badge": "Print Studio", "url": "/modules/system-admin?tab=admin-print-studio", "icon": "printer", "color": "emerald"},
                ]
            }
        ]

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
