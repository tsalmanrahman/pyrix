import sys

# Add project root to path
sys.path.insert(0, r"d:\InteAcc\Dev\Projects\pyrix")

from starlette.testclient import TestClient
from app.main import app

def test_sub_accounts():
    client = TestClient(app, follow_redirects=False)

    USER_ID = "00000000-0000-0000-0000-000000000001"
    DELTA_ID = "8FA78A26-658B-445B-A90E-C82FF3128C2D"
    TARGET_ID = "4F83D116-0FC9-46DF-8B33-4B843F51E076"

    cookies = {
        "pyrix_user_id": USER_ID,
        "pyrix_active_company_id": DELTA_ID
    }

    print("=== TEST 1: Sub-Account VIEW Mode ===")
    res = client.get(
        f"/modules/general-ledger/master/sub-accounts/{TARGET_ID}/view",
        cookies=cookies
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.text
    assert "SUB-001" in html, "Expected SUB-001 in view mode"
    assert "High-Precision Export Contracts" in html, "Expected sub-account name in view mode"
    assert "GL-AC-1008" in html, "Expected parent account number in view mode"
    assert "Gross Commercial Operating Revenue" in html, "Expected parent account name in view mode"
    assert "Parent GL Account Card" not in html, "Muddy 'Parent GL Account Card' must be gone!"
    assert "bg-black/40" not in html, "Legacy black box must be gone!"
    assert "Sub-Account Profile" in html, "Expected new Sub-Account Profile header"
    print("PASS: View mode rendered cleanly with hierarchy profile and no muddy card!")

    print("\n=== TEST 2: Sub-Account EDIT Mode ===")
    res = client.get(
        f"/modules/general-ledger/master/sub-accounts/{TARGET_ID}/edit",
        cookies=cookies
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.text
    assert "SUB-001" in html, "Expected SUB-001 in edit mode"
    assert "Master Account Hierarchy" in html, "Expected Master Account Hierarchy header"
    assert "Controlling Parent GL Account" not in html, "Marked area 'Controlling Parent GL Account' must not be shown!"
    assert "dim-type-btn" in html, "Expected dimension type chips"
    assert "Parent GL Account Card" not in html, "Muddy card must not be in edit mode"
    print("PASS: Edit mode rendered with Master Account Hierarchy and marked area removed!")

    print("\n=== TEST 3: Sub-Account NEW Mode ===")
    res = client.get(
        "/modules/general-ledger/master/sub-accounts/new",
        cookies=cookies
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.text
    assert "Master Account Hierarchy" in html
    assert "Controlling Parent GL Account" not in html, "Marked area must not be shown in new mode!"
    assert "dim-type-btn" in html
    assert "Active for Postings" in html
    print("PASS: New record mode rendered cleanly!")

    print("\n=== TEST 4: Sub-Account Edit POST / Save ===")
    res = client.post(
        f"/modules/general-ledger/master/sub-accounts/{TARGET_ID}/edit",
        data={
            "gl_account_id": "C1D02B3E-3268-4B45-89FC-C089684AC6FD",
            "sub_account_code": "SUB-001",
            "sub_account_name": "High-Precision Export Contracts",
            "sub_account_type": "PRODUCT_LINE",
            "description": "Contracts for precision avionics parts"
        },
        cookies=cookies
    )
    assert res.status_code == 303, f"Expected 303 redirect, got {res.status_code}"
    assert res.headers["location"] == "/modules/general-ledger?tab=subaccounts"
    print("PASS: Sub-account updated and redirected to tab=subaccounts!")

    print("\n=======================================================")
    print("ALL SUB-ACCOUNT TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    test_sub_accounts()
