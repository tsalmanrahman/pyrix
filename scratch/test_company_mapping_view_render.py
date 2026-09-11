import sys

# Add project root to path
sys.path.insert(0, r"d:\InteAcc\Dev\Projects\pyrix")

from starlette.testclient import TestClient
from app.main import app

def test_company_mapping_view_clean_casing():
    client = TestClient(app, follow_redirects=False)

    USER_ID = "00000000-0000-0000-0000-000000000001"
    APEX_ID = "0586B60D-705D-4232-9F47-40C838717BCB"
    APEX_MAP_ID = "9ECD7BCE-3CC9-4EBD-8E11-A85709FECD48"

    cookies = {
        "pyrix_user_id": USER_ID,
        "pyrix_active_company_id": APEX_ID
    }

    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{APEX_MAP_ID}/view",
        cookies=cookies
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.text

    print("=== Checking Removed Elements (Red Box Areas) ===")
    assert "ACTIVE & SYNCHRONIZED" not in html, "ACTIVE & SYNCHRONIZED badge must be removed!"
    assert "ACTIVE &amp; SYNCHRONIZED" not in html, "ACTIVE &amp; SYNCHRONIZED badge must be removed!"
    assert "Read-only global status across conglomerate entities" not in html, "Redundant table subtitle must be removed!"
    print("PASS: Red box elements successfully removed!")

    print("\n=== Checking Natural Casing (Yellow Marked Areas) ===")
    assert "Mapping Profile: Apex Precision Manufacturing Group Ltd" in html or "Mapping Profile:" in html
    assert "Global Master Account" in html
    assert "Assigned Subsidiary Scope" in html
    assert "Corporate Legal Entity" in html
    assert "Account Code &amp; Title" in html or "Account Code & Title" in html
    assert "Local Alias" in html
    assert "Direct Posting" in html
    assert "Current Mapping" in html, "Expected 'Current Mapping' in title/sentence case"
    assert "CURRENT MAPPING" not in html, "Legacy 'CURRENT MAPPING' must not be present"
    assert "Allowed" in html, "Expected 'Allowed' in title/sentence case"
    assert "ALLOWED" not in html, "Legacy 'ALLOWED' must not be present"
    print("PASS: Natural casing verified across all target labels and badges!")

    print("\n=======================================================")
    print("ALL COMPANY MAPPING VIEW TESTS PASSED!")
    print("=======================================================")

if __name__ == "__main__":
    test_company_mapping_view_clean_casing()
