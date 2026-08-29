from typing import List, Dict, Any, Optional
import uuid
import datetime
from app.core.db import db

class SourcingProcessService:

    # =========================================================================
    # 1. MULTI-TIER DIGITAL E-APPROVALS
    # =========================================================================
    @staticmethod
    def get_pending_approvals(company_id: Optional[str] = None, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        # Fetch pending PO approvals
        sql_po = """
            SELECT a.*, po.po_number AS ref_code, po.total_amount, po.currency, po.created_by AS requester,
                   v.vendor_name AS party_name, c.short_code AS company_code, c.name AS company_name
            FROM sourcing_approvals a
            JOIN sourcing_purchase_orders po ON a.entity_id = po.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            JOIN companies c ON po.company_id = c.id
            WHERE a.action = 'PENDING' AND a.entity_type = 'PO'
        """
        params_po = []
        if company_id:
            sql_po += " AND po.company_id = ?"
            params_po.append(company_id)

        # Fetch pending PR approvals
        sql_pr = """
            SELECT a.*, r.req_number AS ref_code, r.total_estimated_amount AS total_amount, r.currency, r.requester_name AS requester,
                   r.title AS party_name, c.short_code AS company_code, c.name AS company_name
            FROM sourcing_approvals a
            JOIN sourcing_requisitions r ON a.entity_id = r.id
            JOIN companies c ON r.company_id = c.id
            WHERE a.action = 'PENDING' AND a.entity_type = 'PR'
        """
        params_pr = []
        if company_id:
            sql_pr += " AND r.company_id = ?"
            params_pr.append(company_id)

        results = []
        if not entity_type or entity_type == "PO":
            results.extend(db.query(sql_po, tuple(params_po) if params_po else ()))
        if not entity_type or entity_type == "PR":
            results.extend(db.query(sql_pr, tuple(params_pr) if params_pr else ()))

        return sorted(results, key=lambda x: x.get("created_at") or "", reverse=True)

    @staticmethod
    def get_approval_audit_trail(entity_id: str) -> List[Dict[str, Any]]:
        return db.query(
            "SELECT * FROM sourcing_approvals WHERE entity_id = ? ORDER BY tier_level ASC",
            (entity_id,)
        )

    @staticmethod
    def execute_approval_action(
        entity_type: str,
        entity_id: str,
        tier_level: int,
        approver_name: str,
        approver_role: str,
        action: str,  # 'APPROVED' or 'REJECTED'
        comments: Optional[str] = None
    ) -> bool:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update current tier approval record
        db.execute(
            """
            UPDATE sourcing_approvals
            SET action = ?, comments = ?, action_date = ?, approver_name = ?, approver_role = ?
            WHERE entity_type = ? AND entity_id = ? AND tier_level = ?
            """,
            (action, comments or f"{action} by {approver_name}", now_str, approver_name, approver_role, entity_type, entity_id, tier_level)
        )

        if action == "REJECTED":
            if entity_type == "PO":
                db.execute("UPDATE sourcing_purchase_orders SET status = 'REJECTED' WHERE id = ?", (entity_id,))
            elif entity_type == "PR":
                db.execute("UPDATE sourcing_requisitions SET status = 'REJECTED' WHERE id = ?", (entity_id,))
            return True

        # If approved, check if next tier exists
        if entity_type == "PO":
            po = db.query_one("SELECT * FROM sourcing_purchase_orders WHERE id = ?", (entity_id,))
            if po:
                cur_tier = int(po.get("current_approval_tier") or 1)
                max_tier = int(po.get("max_approval_tier") or 3)

                if cur_tier >= max_tier:
                    # Final Tier Reached: Mark PO Approved
                    db.execute("UPDATE sourcing_purchase_orders SET status = 'APPROVED' WHERE id = ?", (entity_id,))
                else:
                    next_tier = cur_tier + 1
                    tier_names = {2: "Tier 2: Procurement Head Verification", 3: "Tier 3: CFO / Finance Controller Authorization", 4: "Tier 4: Managing Director Executive Board"}
                    next_name = tier_names.get(next_tier, f"Tier {next_tier} Executive Sign-off")
                    next_role = "Procurement Head" if next_tier == 2 else ("Chief Financial Officer" if next_tier == 3 else "Managing Director")

                    # Advance PO current tier
                    db.execute("UPDATE sourcing_purchase_orders SET current_approval_tier = ? WHERE id = ?", (next_tier, entity_id))

                    # Insert next tier pending record
                    db.execute(
                        """
                        INSERT INTO sourcing_approvals 
                        (id, entity_type, entity_id, tier_level, tier_name, approver_name, approver_role, action, comments)
                        VALUES (?, 'PO', ?, ?, ?, 'Pending Approver', ?, 'PENDING', 'Awaiting next level sign-off')
                        """,
                        (str(uuid.uuid4()), entity_id, next_tier, next_name, next_role)
                    )

        elif entity_type == "PR":
            # For PR, mark as Approved
            db.execute("UPDATE sourcing_requisitions SET status = 'APPROVED' WHERE id = ?", (entity_id,))

        return True

    @staticmethod
    def batch_approve_all(approver_name: str, approver_role: str = "Executive Approver") -> int:
        pendings = db.query("SELECT * FROM sourcing_approvals WHERE action = 'PENDING'")
        count = 0
        for p in pendings:
            SourcingProcessService.execute_approval_action(
                entity_type=p["entity_type"],
                entity_id=p["entity_id"],
                tier_level=p["tier_level"],
                approver_name=approver_name,
                approver_role=approver_role,
                action="APPROVED",
                comments="Batch approved from Executive e-Approval Hub"
            )
            count += 1
        return count

    # =========================================================================
    # 2. LETTERS OF CREDIT (LC) OPERATIONS
    # =========================================================================
    @staticmethod
    def get_letters_of_credit(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT lc.*, po.po_number, po.currency AS po_currency, po.total_amount AS po_total,
                   v.vendor_name, v.vendor_code, c.short_code AS company_code, c.name AS company_name
            FROM sourcing_letters_of_credit lc
            JOIN sourcing_purchase_orders po ON lc.po_id = po.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            JOIN companies c ON po.company_id = c.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY lc.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def create_letter_of_credit(
        po_id: str,
        lc_number: str,
        issuing_bank: str,
        branch_name: str,
        lc_amount: float,
        margin_pct: float,
        issue_date: str,
        expiry_date: str,
        shipment_deadline: str,
        currency: str = "USD"
    ) -> str:
        lc_id = str(uuid.uuid4())
        margin_amount = lc_amount * (margin_pct / 100.0)
        db.execute(
            """
            INSERT INTO sourcing_letters_of_credit 
            (id, lc_number, po_id, issuing_bank, branch_name, lc_amount, currency, margin_pct, margin_amount, issue_date, expiry_date, shipment_deadline, status, forwarding_letter_ref)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPENED', 'FWD-LC-PENDING')
            """,
            (lc_id, lc_number.strip(), po_id, issuing_bank.strip(), branch_name.strip(), lc_amount, currency, margin_pct, margin_amount, issue_date, expiry_date, shipment_deadline)
        )
        return lc_id

    @staticmethod
    def issue_lc_forwarding_letter(lc_id: str, forwarding_letter_ref: str) -> None:
        db.execute(
            "UPDATE sourcing_letters_of_credit SET forwarding_letter_ref = ?, status = 'FORWARDED_TO_VENDOR' WHERE id = ?",
            (forwarding_letter_ref.strip(), lc_id)
        )

    # =========================================================================
    # 3. C&F SHIPPING DOCUMENTS FORWARDING
    # =========================================================================
    @staticmethod
    def get_cnf_dispatches(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT d.*, po.po_number, po.currency AS po_currency,
                   cnf.agent_name, cnf.agent_code, cnf.port_location,
                   v.vendor_name, c.short_code AS company_code
            FROM sourcing_cnf_dispatches d
            JOIN sourcing_purchase_orders po ON d.po_id = po.id
            JOIN sourcing_cnf_agents cnf ON d.cnf_agent_id = cnf.id
            JOIN sourcing_vendors v ON po.vendor_id = v.id
            JOIN companies c ON po.company_id = c.id
            WHERE 1=1
        """
        params = []
        if company_id:
            sql += " AND po.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY d.code DESC"
        return db.query(sql, tuple(params) if params else ())

    @staticmethod
    def create_cnf_dispatch(
        po_id: str,
        cnf_agent_id: str,
        dispatch_number: str,
        bl_number: str,
        vessel_name: str,
        port_of_discharge: str,
        dispatch_date: str,
        eta_date: Optional[str] = None,
        forwarding_text: Optional[str] = None,
        lc_id: Optional[str] = None
    ) -> str:
        disp_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO sourcing_cnf_dispatches 
            (id, dispatch_number, lc_id, po_id, cnf_agent_id, bl_number, vessel_name, port_of_discharge, dispatch_date, eta_date, status, forwarding_letter_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DISPATCHED', ?)
            """,
            (disp_id, dispatch_number.strip(), lc_id or None, po_id, cnf_agent_id, bl_number.strip(), vessel_name.strip(), port_of_discharge.strip(), dispatch_date, eta_date, forwarding_text)
        )
        return disp_id
