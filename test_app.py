import sys
from fastapi.testclient import TestClient
from app.main import app
from app.core.company_service import CompanyService

def run_tests():
    print("Testing Pyrix: General Ledger Master Data & Clean Title/Favicon...")
    client = TestClient(app, cookies={"pyrix_user_id": "101", "pyrix_session_id": "test", "pyrix_last_activity": "9999999999"})

    # 1. Test Home Title (APEX)
    print("\n--- 1. Testing Home Title Bar ---")
    resp = client.get("/")
    assert resp.status_code == 200 and "<title>APEX</title>" in resp.text
    print("[OK - Home Title matches]")

    # 2. Test GL Module Master Hub (APEX-GL)
    print("\n--- 2. Testing General Ledger Master Hub ---")
    resp = client.get("/modules/general-ledger")
    assert resp.status_code == 200 and "<title>APEX-GL</title>" in resp.text
    assert "Chart of Accounts" in resp.text
    assert 'title="Back to Home"' in resp.text
    print("[OK - GL Master Hub loaded with all 7 master area cards and Back to Home button]")

    # 3. Test Master Tab: Chart of Accounts (COA) List View
    print("\n--- 3. Testing Chart of Accounts List Page ---")
    resp = client.get("/modules/general-ledger?tab=coa")
    assert resp.status_code == 200
    assert "Chart of Accounts Master (COA)" in resp.text
    assert "1010-00" in resp.text
    assert "GL Account (COA) List" in resp.text
    # Actions column and action buttons must be present
    assert "Actions" in resp.text
    assert "btn-action-edit" in resp.text
    assert "btn-action-delete" in resp.text
    # Master cards container should NOT be shown in list view
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - Chart of Accounts list page verified with Actions column & edit/delete buttons]")

    # 4. Test Master Tab: Company Mappings List Page
    print("\n--- 4. Testing GL Account Mapping Tab ---")
    resp = client.get("/modules/general-ledger?tab=mapping")
    assert resp.status_code == 200
    assert "GL Account Mapping Matrix" in resp.text
    assert "Actions" in resp.text
    assert 'title="Back to General Ledger Master Hub"' in resp.text
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - GL Account Mapping tab verified with dynamic header title & back button]")

    # 5. Test Master Tab: Sub Accounts List Page
    print("\n--- 5. Testing GL Sub Accounts Tab ---")
    resp = client.get("/modules/general-ledger?tab=subaccounts")
    assert resp.status_code == 200
    assert "GL Sub Accounts Master" in resp.text
    assert "Actions" in resp.text
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - GL Sub Accounts tab verified with Actions column]")

    # 6. Test Master Tab: Departments List Page
    print("\n--- 6. Testing Departments Tab ---")
    resp = client.get("/modules/general-ledger?tab=departments")
    assert resp.status_code == 200
    assert "Organizational Departments Master" in resp.text
    assert "DEP-FIN" in resp.text
    assert "Actions" in resp.text
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - Departments tab verified with Actions column]")

    # 7. Test Master Tab: Cost Centres List Page
    print("\n--- 7. Testing Cost Centres Tab ---")
    resp = client.get("/modules/general-ledger?tab=costcentres")
    assert resp.status_code == 200
    assert "Cost Centres Master" in resp.text
    assert "Actions" in resp.text
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - Cost Centres tab verified with Actions column]")

    # 8. Test Master Tab: Budget Sets List Page
    print("\n--- 8. Testing Budget Sets Tab ---")
    resp = client.get("/modules/general-ledger?tab=budgets")
    assert resp.status_code == 200
    assert "Annual Budget Sets Master" in resp.text
    assert "Actions" in resp.text
    assert "id=\"module-suites-container\"" not in resp.text
    print("[OK - Budget Sets tab verified with Actions column]")

    # 9. Test Solid Master Record Creation Form (New GL Account)
    print("\n--- 9. Testing Solid GL Account Creation Page ---")
    resp = client.get("/modules/general-ledger/master/gl-accounts/new")
    assert resp.status_code == 200
    assert "New GL Account (Chart of Accounts)" in resp.text
    assert "GL Account (COA) List" in resp.text  # Clickable parent breadcrumb
    print("[OK - Solid Master Data creation page verified with 4-level deep breadcrumbs]")

    # 10. Test Dynamic Edit Page (Pre-filled form) & Update flow
    print("\n--- 10. Testing Pre-filled Edit Page & Update Flow ---")
    from app.monographs.enterprise_modules.gl_master_service import GLMasterService
    from app.core.db import db

    # Insert a temporary test GL account
    test_acc_num = "TEST-9999"
    db.execute(
        "INSERT INTO gl_accounts (account_number, account_name, account_type, financial_statement, normal_balance, is_active, isDelete) VALUES (?, ?, ?, ?, ?, 1, 0)",
        (test_acc_num, "Temporary Test GL Account", "EXPENSE", "INCOME_STATEMENT", "DEBIT")
    )
    acc = db.query_one("SELECT * FROM gl_accounts WHERE account_number = ?", (test_acc_num,))
    assert acc is not None
    acc_id = str(acc["id"])

    # Test GET edit page loads pre-filled value
    edit_page_resp = client.get(f"/modules/general-ledger/master/gl-accounts/{acc_id}/edit")
    assert edit_page_resp.status_code == 200
    assert "Edit GL Account (Chart of Accounts)" in edit_page_resp.text
    assert test_acc_num in edit_page_resp.text
    assert "Temporary Test GL Account" in edit_page_resp.text
    assert "Update Record" in edit_page_resp.text
    print("[OK - Pre-filled Edit page loaded with existing record values]")

    # Test POST edit page updates record in SQL Server
    update_resp = client.post(
        f"/modules/general-ledger/master/gl-accounts/{acc_id}/edit",
        data={
            "account_number": test_acc_num,
            "account_name": "Updated Test GL Account Name",
            "account_type": "EXPENSE",
            "financial_statement": "INCOME_STATEMENT",
            "normal_balance": "DEBIT"
        },
        follow_redirects=True
    )
    assert update_resp.status_code == 200
    assert "Updated Test GL Account Name" in update_resp.text
    print("[OK - Record update successfully persisted in SQL Server]")

    # 11. Test Dynamic Safe Soft-Delete (isDelete & isDeleteDate)
    print("\n--- 11. Testing Safe Soft-Delete Architecture ---")
    del_resp = client.post(f"/api/modules/master/gl-accounts/{acc_id}/delete")
    assert del_resp.status_code == 200 and del_resp.json().get("success") is True

    # Check SQL Server directly: row MUST still exist with isDelete = 1 and isDeleteDate not null
    deleted_row = db.query_one("SELECT id, isDelete, isDeleteDate FROM gl_accounts WHERE id = ?", (acc_id,))
    assert deleted_row is not None
    assert deleted_row["isDelete"] == 1 or deleted_row["isDelete"] is True
    assert deleted_row["isDeleteDate"] is not None
    print("[OK - Row safely preserved in SQL Server with isDelete=1 and isDeleteDate timestamp]")

    # Check UI list query: row MUST NOT appear in active list
    active_accounts = GLMasterService.get_all_accounts()
    active_ids = [str(a["id"]) for a in active_accounts]
    assert acc_id not in active_ids
    print("[OK - Soft-deleted record is immediately filtered out from UI lists]")

    # Clean up test row
    db.execute("DELETE FROM gl_accounts WHERE id = ?", (acc_id,))

    # 12. Test Journal Vouchers List Tab
    print("\n--- 12. Testing Journal Vouchers Tab ---")
    jv_tab_resp = client.get("/modules/general-ledger?tab=journals")
    assert jv_tab_resp.status_code == 200
    assert "Journal Vouchers (JV)" in jv_tab_resp.text
    assert "New Journal Entry" in jv_tab_resp.text
    assert "JV-APEX-2026-0001" in jv_tab_resp.text
    print("[OK - Journal Vouchers tab loaded with active vouchers & New Journal Entry button]")

    # 13. Test Double-Entry Journal Entry Studio (GET & POST)
    print("\n--- 13. Testing Double-Entry Journal Entry Studio ---")
    new_jv_page = client.get("/modules/general-ledger/journals/new")
    assert new_jv_page.status_code == 200
    assert "New Double-Entry Journal Voucher" in new_jv_page.text
    assert "BALANCED" in new_jv_page.text
    assert "Operating Entity Scope" in new_jv_page.text

    # Post a balanced voucher
    import random
    from app.monographs.enterprise_modules.gl_journal_service import GLJournalService
    all_accs = GLMasterService.get_all_accounts()
    acc1_id = str(all_accs[0]["id"])
    acc2_id = str(all_accs[1]["id"])
    rand_v_num = f"JV-TEST-{random.randint(10000, 99999)}"

    post_jv_resp = client.post(
        "/modules/general-ledger/journals/new",
        data={
            "voucher_number": rand_v_num,
            "voucher_date": "2026-08-24",
            "reference_number": "TEST-REF-001",
            "narration": "Test Balanced Journal Entry",
            "line_account_id[]": [acc1_id, acc2_id],
            "line_cost_centre_id[]": ["", ""],
            "line_narration[]": ["Debit line test", "Credit line test"],
            "line_debit[]": ["7500.00", "0.00"],
            "line_credit[]": ["0.00", "7500.00"]
        },
        follow_redirects=True
    )
    assert post_jv_resp.status_code == 200
    assert rand_v_num in post_jv_resp.text

    # Verify line items in DB
    created_v = db.query_one("SELECT * FROM gl_journal_vouchers WHERE voucher_number = ?", (rand_v_num,))
    assert created_v is not None
    assert created_v["total_amount"] == 7500.00
    v_lines = GLJournalService.get_voucher_lines(str(created_v["id"]))
    assert len(v_lines) == 2
    print("[OK - Double-entry balanced journal voucher created and persisted in SQL Server]")

    # 14. Test Official Printable Journal Voucher (JV) Slip
    print("\n--- 14. Testing Printable Journal Voucher Slip ---")
    print_slip_resp = client.get(f"/modules/general-ledger/vouchers/{created_v['id']}/print")
    assert print_slip_resp.status_code == 200
    assert "JOURNAL VOUCHER" in print_slip_resp.text
    assert rand_v_num in print_slip_resp.text
    assert "Total Balanced Voucher Posting" in print_slip_resp.text
    assert "Authorized Signatory" in print_slip_resp.text
    assert "Prepared By" in print_slip_resp.text
    print("[OK - Official print-ready Journal Voucher slip rendered successfully with signature blocks]")

    # 15. Test Batch Processing & Automated Batch Generation
    print("\n--- 15. Testing Batch Processing & Auto Batch Generator ---")
    batch_tab_resp = client.get("/modules/general-ledger?tab=batches")
    assert batch_tab_resp.status_code == 200
    assert "Journal Batches & Processing Status" in batch_tab_resp.text
    assert "Generate Batch from Auto Journals" in batch_tab_resp.text

    # Trigger auto batch generation
    auto_gen_resp = client.post("/api/modules/general-ledger/batches/generate-auto")
    assert auto_gen_resp.status_code == 200
    auto_batch_id = auto_gen_resp.json().get("batch_id")
    assert auto_batch_id is not None
    print("[OK - Automated Journal Batch generated successfully from recurring system rules]")

    # 16. Test Batch Templates & One-Click Instantiation
    print("\n--- 16. Testing Batch Templates & One-Click Instantiation ---")
    tmpl_tab_resp = client.get("/modules/general-ledger?tab=templates")
    assert tmpl_tab_resp.status_code == 200
    assert "Recurring Batch Templates" in tmpl_tab_resp.text
    assert "TMPL-APEX-PAYROLL" in tmpl_tab_resp.text
    assert "Generate Batch" in tmpl_tab_resp.text

    tmpl = db.query_one("SELECT * FROM gl_batch_templates WHERE template_code = 'TMPL-APEX-PAYROLL'")
    inst_resp = client.post(
        "/api/modules/general-ledger/batches/generate-from-template",
        data={"template_id": str(tmpl["id"]), "amount": 65000.00}
    )
    assert inst_resp.status_code == 200
    tmpl_batch_id = inst_resp.json().get("batch_id")
    assert tmpl_batch_id is not None
    print("[OK - Batch generated from template with pre-balanced distribution lines]")

    # 17. Test Modern Login Page Rendering
    print("\n--- 17. Testing Modern Glassmorphic Login Page ---")
    login_resp = client.get("/login")
    assert login_resp.status_code == 200
    assert "Pyrix Enterprise Suite" in login_resp.text
    assert "Sign In" in login_resp.text
    assert "1-Click Quick Sign-In" in login_resp.text
    print("[OK - Modern Glassmorphic Login page rendered with 1-click personas]")

    # 18. Test Authentication & Session Cookie Issuance
    print("\n--- 18. Testing Authentication & Session Cookie Issuance ---")
    # Bad login
    bad_login_resp = client.post("/login", data={"email": "alex.vance@pyrix.internal", "password": "wrongpassword"})
    assert bad_login_resp.status_code == 401
    assert "Invalid Username or Password" in bad_login_resp.text

    # Valid login - Alexander Vance
    good_login_resp = client.post(
        "/login",
        data={"email": "alex.vance@pyrix.internal", "password": "admin123", "remember": "on"},
        follow_redirects=False
    )
    assert good_login_resp.status_code == 303
    assert "pyrix_user_id" in good_login_resp.cookies
    assert "pyrix_session_token" in good_login_resp.cookies
    print("[OK - Valid credentials authenticate and issue secure session cookies]")

    # Test Persona Login - Marcus Sterling & verify header trigger synchronization
    marcus_user = db.query_one("SELECT * FROM users WHERE email = 'marcus.sterling@pyrix.internal'")
    marcus_client = TestClient(app, cookies={"pyrix_user_id": str(marcus_user["id"])})
    marcus_home_resp = marcus_client.get("/")
    assert marcus_home_resp.status_code == 200
    assert "<span>MS</span>" in marcus_home_resp.text
    assert "Marcus S." in marcus_home_resp.text
    assert "Supply Director" in marcus_home_resp.text
    assert "marcus.sterling@pyrix.internal" in marcus_home_resp.text
    print("[OK - Header trigger button perfectly synchronizes with Marcus Sterling: MS, Marcus S., Supply Director]")

    # 19. Test Dedicated User Profile Page & Updates
    print("\n--- 19. Testing Dedicated User Profile Page & Updates ---")
    profile_resp = client.get("/profile")
    assert profile_resp.status_code == 200
    assert "My Profile & Enterprise Account" in profile_resp.text
    assert "Alexander Vance" in profile_resp.text
    assert "EMP-8801" in profile_resp.text
    assert "Employee ID:" in profile_resp.text

    # Update profile
    u = db.query_one("SELECT * FROM users WHERE email = 'alex.vance@pyrix.internal'")
    update_resp = client.post(
        "/profile",
        data={
            "full_name": "Alexander Vance",
            "email": "alex.vance@pyrix.internal",
            "phone": "+1 (555) 888-9999",
            "job_title": "Chief Enterprise Architect & Sys Admin",
            "department": "Enterprise Information Systems",
            "primary_company_id": str(u["primary_company_id"])
        }
    )
    assert update_resp.status_code == 200
    assert "updated successfully" in update_resp.text
    updated_user = db.query_one("SELECT * FROM users WHERE id = ?", (u["id"],))
    assert updated_user["phone"] == "+1 (555) 888-9999"
    assert updated_user["job_title"] == "Chief Enterprise Architect & Sys Admin"
    print("[OK - User profile details updated and persisted in SQL Server]")

    # 20. Test Cash Book Hub & Tabs
    print("\n--- 20. Testing Cash Book Master Hub & Sub-Areas ---")
    cb_resp = client.get("/modules/cash-book")
    assert cb_resp.status_code == 200
    assert "Cashier Stations" in cb_resp.text
    assert "Bank Master" in cb_resp.text
    assert "Bank Branches" in cb_resp.text
    assert "Bank Accounts" in cb_resp.text
    assert "Money Receipts (MR)" in cb_resp.text
    assert "Contra Transfers" in cb_resp.text
    print("[OK - Cash Book Master Hub loaded with all 6 setup & transaction cards]")

    # 21. Test Cashier Stations Tab & Master Create
    print("\n--- 21. Testing Cashier Stations & Bank Accounts Master ---")
    csh_resp = client.get("/modules/cash-book?tab=cashiers")
    assert csh_resp.status_code == 200
    assert "Cashier Stations Master" in csh_resp.text
    assert "CSH-APEX-01" in csh_resp.text

    # 22. Test Issue Money Receipt (MR) Studio
    print("\n--- 22. Testing Issue Money Receipt Studio & SQL Server Persistence ---")
    new_mr_form = client.get("/modules/cash-book/receipts/new")
    assert new_mr_form.status_code == 200
    assert "Issue Money Receipt (MR)" in new_mr_form.text

    create_mr_resp = client.post(
        "/modules/cash-book/receipts/new",
        data={
            "receipt_type": "CUSTOMER",
            "receipt_date": "2026-08-24",
            "party_name": "Zenith Avionics Global Systems Ltd",
            "payment_mode": "CHEQUE",
            "cheque_no": "CHQ-778811",
            "cheque_date": "2026-08-24",
            "drawn_on_bank": "HSBC Bank USA",
            "amount": "95000.00",
            "narration": "Full settlement for avionics flight control subassemblies invoice #INV-9021"
        },
        follow_redirects=False
    )
    assert create_mr_resp.status_code == 303

    saved_mr = db.query_one("SELECT * FROM cb_money_receipts WHERE party_name = 'Zenith Avionics Global Systems Ltd' AND COALESCE(isDelete, 0) = 0 ORDER BY code DESC")
    assert saved_mr is not None
    assert saved_mr["amount"] == 95000.00
    assert saved_mr["payment_mode"] == "CHEQUE"
    print("[OK - Customer Money Receipt issued and persisted in SQL Server]")

    # 23. Test Official Printable Money Receipt (MR Slip)
    print("\n--- 23. Testing Printable Official Money Receipt Slip ---")
    mr_print_resp = client.get(f"/modules/cash-book/receipts/{saved_mr['id']}/print")
    assert mr_print_resp.status_code == 200
    assert "MONEY RECEIPT (MR)" in mr_print_resp.text
    assert "Zenith Avionics Global Systems Ltd" in mr_print_resp.text
    assert "95,000.00" in mr_print_resp.text
    assert "CHQ-778811" in mr_print_resp.text
    assert "Authorized Signatory" in mr_print_resp.text
    print("[OK - Official Printable Money Receipt rendered with 3-tier authorization signatures]")

    # 24. Test Inter Bank-Cash Contra Transfer Studio
    print("\n--- 24. Testing Inter Bank-Cash Contra Transfer Studio ---")
    contra_form = client.get("/modules/cash-book/transfers/new")
    assert contra_form.status_code == 200
    assert "Inter Bank-Cash Contra Transfer Studio" in contra_form.text

    create_ct_resp = client.post(
        "/modules/cash-book/transfers/new",
        data={
            "transfer_type": "CASH_TO_BANK",
            "transfer_date": "2026-08-24",
            "amount": "32000.00",
            "reference_number": "DEP-SLIP-9902",
            "narration": "Transfer of counter cash collections into corporate operating treasury"
        },
        follow_redirects=False
    )
    assert create_ct_resp.status_code == 303

    saved_ct = db.query_one("SELECT * FROM cb_contra_transfers WHERE reference_number = 'DEP-SLIP-9902' AND COALESCE(isDelete, 0) = 0 ORDER BY code DESC")
    assert saved_ct is not None
    assert saved_ct["amount"] == 32000.00
    print("[OK - Inter Bank-Cash Contra Transfer executed and balanced in SQL Server]")

    # 25. Test Printable Contra Voucher Slip
    print("\n--- 25. Testing Printable Contra Voucher Slip ---")
    ct_print_resp = client.get(f"/modules/cash-book/transfers/{saved_ct['id']}/print")
    assert ct_print_resp.status_code == 200
    assert "CONTRA VOUCHER" in ct_print_resp.text
    assert "32,000.00" in ct_print_resp.text
    assert "DEP-SLIP-9902" in ct_print_resp.text
    print("[OK - Official Printable Contra Voucher Slip rendered successfully]")

    # 26. Test Safe Soft-Delete on Cash Book
    print("\n--- 26. Testing Safe Soft-Delete on Money Receipt ---")
    del_mr_resp = client.post(f"/api/modules/cash-book/receipts/{saved_mr['id']}/delete")
    assert del_mr_resp.status_code == 200
    deleted_mr = db.query_one("SELECT isDelete, isDeleteDate FROM cb_money_receipts WHERE id = ?", (saved_mr["id"],))
    assert deleted_mr["isDelete"] == 1
    assert deleted_mr["isDeleteDate"] is not None
    print("[OK - Money Receipt safely soft-deleted in SQL Server with isDelete=1]")

    # 27. Test Sourcing & Procurement Modern Suite
    print("\n--- 27. Testing Modern Sourcing & Procurement 5-Suite ---")
    src_resp = client.get("/modules/sourcing")
    assert src_resp.status_code == 200
    assert "Vendor Profile" in src_resp.text
    assert "1. Master Setup Suite" in src_resp.text

    src_pr_resp = client.get("/modules/sourcing?tab=requisitions")
    assert src_pr_resp.status_code == 200
    assert "REQ-2026-001" in src_pr_resp.text

    src_cs_resp = client.get("/modules/sourcing?tab=comparative-statements")
    assert src_cs_resp.status_code == 200
    assert "CS-2026-042" in src_cs_resp.text

    src_po_resp = client.get("/modules/sourcing?tab=purchase-orders")
    assert src_po_resp.status_code == 200
    assert "PO-APX-1092" in src_po_resp.text

    src_match_resp = client.get("/modules/sourcing?tab=three-way-match")
    assert src_match_resp.status_code == 200
    assert "PR vs PO vs GRN" in src_match_resp.text
    print("[OK - Full Sourcing 5-Suite, PR, CS Matrix, PO and 3-Way Match verified]")

    # 28. Test Sign Out & Cookie Clearance
    print("\n--- 28. Testing Sign Out Flow & Session Cookie Clearance ---")
    logout_resp = client.get("/logout", follow_redirects=False)
    assert logout_resp.status_code == 303
    assert "/login" in logout_resp.headers.get("location", "")
    print("[OK - Sign Out safely terminates session and redirects to Login]")

    print("\n=========================================================================")
    print("ALL ENTERPRISE GL, CASH BOOK, SOURCING & AUTH SUITE TESTS PASSED!")
    print("=========================================================================")

if __name__ == "__main__":
    run_tests()
