import sys

# Add project root to path
sys.path.insert(0, r"d:\InteAcc\Dev\Projects\pyrix")

from starlette.testclient import TestClient
from app.main import app

def test_view_company_switch():
    client = TestClient(app, follow_redirects=False)

    USER_ID = "00000000-0000-0000-0000-000000000001"
    DELTA_ID = "8FA78A26-658B-445B-A90E-C82FF3128C2D"
    APEX_ID = "0586B60D-705D-4232-9F47-40C838717BCB"
    TITAN_ID = "3B5A7898-82A2-49D3-8C87-3BA0C47B0630"
    HORIZON_ID = "D1CE255D-A541-41EC-81DF-D68EA3FBD6F4"

    DELTA_MAP_ID = "D6FB7279-FBFC-41F5-890B-2F6B46D7912C"
    APEX_MAP_ID = "9ECD7BCE-3CC9-4EBD-8E11-A85709FECD48"
    TITAN_MAP_ID = "4A725253-0BE5-4412-8FBD-3696117C4CCE"
    HORIZON_MAP_ID = "9CC91F76-B1A3-43E2-9B5E-BE2E01069C82"

    print("=== TEST 1: DELTA view with DELTA active cookie (same company) ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{DELTA_MAP_ID}/view",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": DELTA_ID}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "DELTA" in res.text, "Expected DELTA in body"
    assert "Current Mapping" in res.text, "Expected Current Mapping badge in body"
    print(f"PASS: Status {res.status_code}, DELTA record displayed with CURRENT MAPPING")

    print("\n=== TEST 2: DELTA view URL with APEX active cookie (user switched company to APEX) ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{DELTA_MAP_ID}/view",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": APEX_ID}
    )
    assert res.status_code == 303, f"Expected 303 redirect, got {res.status_code}"
    expected_location = f"/modules/general-ledger/master/company-mappings/{APEX_MAP_ID}/view"
    assert res.headers.get("location") == expected_location, f"Expected {expected_location}, got {res.headers.get('location')}"
    print(f"PASS: Status {res.status_code}, automatically redirected to APEX mapping view: {res.headers.get('location')}")

    print("\n=== TEST 3: Accessing APEX mapping view directly ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{APEX_MAP_ID}/view",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": APEX_ID}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "APEX" in res.text, "Expected APEX in body"
    assert "Apex Precision Manufacturing Group Ltd" in res.text
    assert "Current Mapping" in res.text
    print(f"PASS: Status {res.status_code}, APEX mapping view renders APEX company and mapping profile")

    print("\n=== TEST 4: DELTA view URL with TITAN active cookie ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{DELTA_MAP_ID}/view",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": TITAN_ID}
    )
    assert res.status_code == 303, f"Expected 303 redirect, got {res.status_code}"
    expected_location = f"/modules/general-ledger/master/company-mappings/{TITAN_MAP_ID}/view"
    assert res.headers.get("location") == expected_location, f"Expected {expected_location}, got {res.headers.get('location')}"
    print(f"PASS: Status {res.status_code}, automatically redirected to TITAN mapping view: {res.headers.get('location')}")

    print("\n=== TEST 5: DELTA view URL with HORIZON active cookie ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{DELTA_MAP_ID}/view",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": HORIZON_ID}
    )
    assert res.status_code == 303, f"Expected 303 redirect, got {res.status_code}"
    expected_location = f"/modules/general-ledger/master/company-mappings/{HORIZON_MAP_ID}/view"
    assert res.headers.get("location") == expected_location, f"Expected {expected_location}, got {res.headers.get('location')}"
    print(f"PASS: Status {res.status_code}, automatically redirected to HORIZON mapping view: {res.headers.get('location')}")

    print("\n=== TEST 6: Mismatched company in edit mode guards data integrity ===")
    res = client.get(
        f"/modules/general-ledger/master/company-mappings/{DELTA_MAP_ID}/edit",
        cookies={"pyrix_user_id": USER_ID, "pyrix_active_company_id": APEX_ID}
    )
    assert res.status_code == 303, f"Expected 303 redirect, got {res.status_code}"
    assert res.headers.get("location") == "/modules/general-ledger?tab=mapping"
    print(f"PASS: Status {res.status_code}, Cross-company edit access guarded and redirected to company tab list")

    print("\n=======================================================")
    print("ALL 6 TESTS PASSED SUCCESSFULLY! FULL SYNCHRONIZATION CONFIRMED.")
    print("=======================================================")

if __name__ == "__main__":
    test_view_company_switch()
