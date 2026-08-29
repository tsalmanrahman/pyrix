from typing import List, Dict, Any, Optional
import uuid
from app.core.db import db

class CashBookService:

    # =========================================================================
    # 1. CASHIERS MASTER
    # =========================================================================
    @staticmethod
    def get_cashiers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT c.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_cashiers c
            JOIN companies cmp ON c.company_id = cmp.id
            LEFT JOIN gl_accounts g ON c.gl_account_id = g.id
            WHERE COALESCE(c.isDelete, 0) = 0
        """
        params = []
        if company_id:
            sql += " AND c.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY c.code ASC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_cashier_by_id(cashier_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT c.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_cashiers c
            JOIN companies cmp ON c.company_id = cmp.id
            LEFT JOIN gl_accounts g ON c.gl_account_id = g.id
            WHERE c.id = ? AND COALESCE(c.isDelete, 0) = 0
            """,
            (cashier_id,)
        )

    @staticmethod
    def create_cashier(
        cashier_code: str,
        cashier_name: str,
        company_id: str,
        counter_station: str,
        daily_cash_limit: float = 50000.0,
        gl_account_id: Optional[str] = None
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO cb_cashiers 
            (id, cashier_code, cashier_name, company_id, counter_station, daily_cash_limit, gl_account_id, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (new_id, cashier_code.strip(), cashier_name.strip(), company_id, counter_station.strip(), daily_cash_limit, gl_account_id or None)
        )
        return new_id

    @staticmethod
    def update_cashier(
        cashier_id: str,
        cashier_code: str,
        cashier_name: str,
        company_id: str,
        counter_station: str,
        daily_cash_limit: float,
        gl_account_id: Optional[str] = None
    ) -> bool:
        db.execute(
            """
            UPDATE cb_cashiers
            SET cashier_code = ?, cashier_name = ?, company_id = ?, counter_station = ?, daily_cash_limit = ?, gl_account_id = ?
            WHERE id = ?
            """,
            (cashier_code.strip(), cashier_name.strip(), company_id, counter_station.strip(), daily_cash_limit, gl_account_id or None, cashier_id)
        )
        return True

    @staticmethod
    def delete_cashier(cashier_id: str) -> bool:
        db.execute(
            "UPDATE cb_cashiers SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?",
            (cashier_id,)
        )
        return True

    # =========================================================================
    # 2. BANK MASTER
    # =========================================================================
    @staticmethod
    def get_banks() -> List[Dict[str, Any]]:
        return db.query(
            """
            SELECT b.*, 
                   (SELECT COUNT(*) FROM cb_bank_branches br WHERE br.bank_id = b.id AND COALESCE(br.isDelete, 0) = 0) AS branch_count
            FROM cb_banks b
            WHERE COALESCE(b.isDelete, 0) = 0
            ORDER BY b.code ASC
            """
        )

    @staticmethod
    def get_bank_by_id(bank_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            "SELECT * FROM cb_banks WHERE id = ? AND COALESCE(isDelete, 0) = 0",
            (bank_id,)
        )

    @staticmethod
    def create_bank(bank_code: str, bank_name: str, swift_code: Optional[str] = None, country: str = "United States") -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO cb_banks (id, bank_code, bank_name, swift_code, country, is_active, isDelete) VALUES (?, ?, ?, ?, ?, 1, 0)",
            (new_id, bank_code.strip(), bank_name.strip(), swift_code.strip() if swift_code else None, country.strip())
        )
        return new_id

    @staticmethod
    def update_bank(bank_id: str, bank_code: str, bank_name: str, swift_code: Optional[str] = None, country: str = "United States") -> bool:
        db.execute(
            "UPDATE cb_banks SET bank_code = ?, bank_name = ?, swift_code = ?, country = ? WHERE id = ?",
            (bank_code.strip(), bank_name.strip(), swift_code.strip() if swift_code else None, country.strip(), bank_id)
        )
        return True

    @staticmethod
    def delete_bank(bank_id: str) -> bool:
        db.execute("UPDATE cb_banks SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (bank_id,))
        return True

    # =========================================================================
    # 3. BANK BRANCHES
    # =========================================================================
    @staticmethod
    def get_branches(bank_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT br.*, b.bank_name, b.bank_code, b.swift_code
            FROM cb_bank_branches br
            JOIN cb_banks b ON br.bank_id = b.id
            WHERE COALESCE(br.isDelete, 0) = 0
        """
        params = []
        if bank_id:
            sql += " AND br.bank_id = ?"
            params.append(bank_id)
        sql += " ORDER BY br.code ASC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_branch_by_id(branch_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT br.*, b.bank_name, b.bank_code, b.swift_code
            FROM cb_bank_branches br
            JOIN cb_banks b ON br.bank_id = b.id
            WHERE br.id = ? AND COALESCE(br.isDelete, 0) = 0
            """,
            (branch_id,)
        )

    @staticmethod
    def create_branch(
        bank_id: str,
        branch_code: str,
        branch_name: str,
        routing_number: Optional[str] = None,
        branch_address: Optional[str] = None,
        contact_phone: Optional[str] = None
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO cb_bank_branches 
            (id, bank_id, branch_code, branch_name, routing_number, branch_address, contact_phone, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (new_id, bank_id, branch_code.strip(), branch_name.strip(), routing_number or None, branch_address or None, contact_phone or None)
        )
        return new_id

    @staticmethod
    def update_branch(
        branch_id: str,
        bank_id: str,
        branch_code: str,
        branch_name: str,
        routing_number: Optional[str] = None,
        branch_address: Optional[str] = None,
        contact_phone: Optional[str] = None
    ) -> bool:
        db.execute(
            """
            UPDATE cb_bank_branches
            SET bank_id = ?, branch_code = ?, branch_name = ?, routing_number = ?, branch_address = ?, contact_phone = ?
            WHERE id = ?
            """,
            (bank_id, branch_code.strip(), branch_name.strip(), routing_number or None, branch_address or None, contact_phone or None, branch_id)
        )
        return True

    @staticmethod
    def delete_branch(branch_id: str) -> bool:
        db.execute("UPDATE cb_bank_branches SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (branch_id,))
        return True

    # =========================================================================
    # 4. BANK ACCOUNTS
    # =========================================================================
    @staticmethod
    def get_bank_accounts(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT a.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   b.bank_name, b.bank_code, br.branch_name, br.branch_code, br.routing_number,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_bank_accounts a
            JOIN companies cmp ON a.company_id = cmp.id
            JOIN cb_bank_branches br ON a.branch_id = br.id
            JOIN cb_banks b ON br.bank_id = b.id
            JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE COALESCE(a.isDelete, 0) = 0
        """
        params = []
        if company_id:
            sql += " AND a.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY a.code ASC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_bank_account_by_id(account_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT a.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   b.bank_name, b.bank_code, br.branch_name, br.branch_code, br.routing_number,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_bank_accounts a
            JOIN companies cmp ON a.company_id = cmp.id
            JOIN cb_bank_branches br ON a.branch_id = br.id
            JOIN cb_banks b ON br.bank_id = b.id
            JOIN gl_accounts g ON a.gl_account_id = g.id
            WHERE a.id = ? AND COALESCE(a.isDelete, 0) = 0
            """,
            (account_id,)
        )

    @staticmethod
    def create_bank_account(
        company_id: str,
        branch_id: str,
        account_number: str,
        account_title: str,
        account_type: str = "CURRENT",
        currency: str = "USD",
        gl_account_id: str = "",
        opening_balance: float = 0.0,
        overdraft_limit: float = 0.0
    ) -> str:
        new_id = str(uuid.uuid4())
        db.execute(
            """
            INSERT INTO cb_bank_accounts 
            (id, company_id, branch_id, account_number, account_title, account_type, currency, gl_account_id, opening_balance, current_balance, overdraft_limit, is_active, isDelete)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0)
            """,
            (new_id, company_id, branch_id, account_number.strip(), account_title.strip(), account_type.upper(), currency.upper(), gl_account_id, opening_balance, opening_balance, overdraft_limit)
        )
        return new_id

    @staticmethod
    def update_bank_account(
        account_id: str,
        company_id: str,
        branch_id: str,
        account_number: str,
        account_title: str,
        account_type: str,
        currency: str,
        gl_account_id: str,
        opening_balance: float,
        overdraft_limit: float
    ) -> bool:
        db.execute(
            """
            UPDATE cb_bank_accounts
            SET company_id = ?, branch_id = ?, account_number = ?, account_title = ?, account_type = ?, currency = ?, gl_account_id = ?, opening_balance = ?, overdraft_limit = ?
            WHERE id = ?
            """,
            (company_id, branch_id, account_number.strip(), account_title.strip(), account_type.upper(), currency.upper(), gl_account_id, opening_balance, overdraft_limit, account_id)
        )
        return True

    @staticmethod
    def delete_bank_account(account_id: str) -> bool:
        db.execute("UPDATE cb_bank_accounts SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (account_id,))
        return True

    # =========================================================================
    # 5. MONEY RECEIPTS (MR)
    # =========================================================================
    @staticmethod
    def get_money_receipts(company_id: Optional[str] = None, receipt_type: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT mr.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   csh.cashier_name, csh.counter_station,
                   ba.account_number, ba.account_title, bnk.bank_name,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_money_receipts mr
            JOIN companies cmp ON mr.company_id = cmp.id
            LEFT JOIN cb_cashiers csh ON mr.cashier_id = csh.id
            LEFT JOIN cb_bank_accounts ba ON mr.bank_account_id = ba.id
            LEFT JOIN cb_bank_branches br ON ba.branch_id = br.id
            LEFT JOIN cb_banks bnk ON br.bank_id = bnk.id
            LEFT JOIN gl_accounts g ON mr.gl_account_id = g.id
            WHERE COALESCE(mr.isDelete, 0) = 0
        """
        params = []
        if company_id:
            sql += " AND mr.company_id = ?"
            params.append(company_id)
        if receipt_type:
            sql += " AND mr.receipt_type = ?"
            params.append(receipt_type)
        sql += " ORDER BY mr.receipt_date DESC, mr.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_money_receipt_by_id(receipt_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT mr.*, cmp.name AS company_name, cmp.short_code AS company_code, cmp.currency AS company_currency,
                   csh.cashier_name, csh.counter_station,
                   ba.account_number, ba.account_title, bnk.bank_name, br.branch_name,
                   g.account_number AS gl_account_number, g.account_name AS gl_account_name
            FROM cb_money_receipts mr
            JOIN companies cmp ON mr.company_id = cmp.id
            LEFT JOIN cb_cashiers csh ON mr.cashier_id = csh.id
            LEFT JOIN cb_bank_accounts ba ON mr.bank_account_id = ba.id
            LEFT JOIN cb_bank_branches br ON ba.branch_id = br.id
            LEFT JOIN cb_banks bnk ON br.bank_id = bnk.id
            LEFT JOIN gl_accounts g ON mr.gl_account_id = g.id
            WHERE mr.id = ? AND COALESCE(mr.isDelete, 0) = 0
            """,
            (receipt_id,)
        )

    @staticmethod
    def create_money_receipt(
        company_id: str,
        receipt_type: str,
        receipt_date: str,
        party_name: str,
        payment_mode: str,
        amount: float,
        narration: str,
        cashier_id: Optional[str] = None,
        bank_account_id: Optional[str] = None,
        cheque_no: Optional[str] = None,
        cheque_date: Optional[str] = None,
        drawn_on_bank: Optional[str] = None,
        gl_account_id: Optional[str] = None,
        created_by: str = "Alexander Vance"
    ) -> str:
        new_id = str(uuid.uuid4())
        
        # Generate receipt number
        count_row = db.query_one("SELECT COUNT(*) AS cnt FROM cb_money_receipts WHERE company_id = ?", (company_id,))
        seq = (count_row["cnt"] if count_row else 0) + 1
        comp = db.query_one("SELECT short_code FROM companies WHERE id = ?", (company_id,))
        comp_code = comp["short_code"] if comp else "APEX"
        receipt_number = f"MR-{comp_code}-{seq:04d}"

        db.execute(
            """
            INSERT INTO cb_money_receipts 
            (id, receipt_number, company_id, receipt_type, receipt_date, party_name, cashier_id, bank_account_id, payment_mode, cheque_no, cheque_date, drawn_on_bank, amount, narration, gl_account_id, status, isDelete, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ISSUED', 0, ?)
            """,
            (new_id, receipt_number, company_id, receipt_type.upper(), receipt_date, party_name.strip(), cashier_id or None, bank_account_id or None, payment_mode.upper(), cheque_no or None, cheque_date or None, drawn_on_bank or None, amount, narration.strip(), gl_account_id or None, created_by)
        )
        return new_id

    @staticmethod
    def cancel_money_receipt(receipt_id: str, cancel_reason: str) -> bool:
        db.execute(
            """
            UPDATE cb_money_receipts
            SET status = 'CANCELLED', cancel_reason = ?, isDelete = 1, isDeleteDate = GETDATE()
            WHERE id = ?
            """,
            (cancel_reason.strip(), receipt_id)
        )
        return True

    @staticmethod
    def delete_money_receipt(receipt_id: str) -> bool:
        db.execute("UPDATE cb_money_receipts SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (receipt_id,))
        return True

    # =========================================================================
    # 6. INTER BANK-CASH CONTRA TRANSFERS
    # =========================================================================
    @staticmethod
    def get_contra_transfers(company_id: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = """
            SELECT ct.*, cmp.name AS company_name, cmp.short_code AS company_code,
                   fcsh.cashier_name AS from_cashier_name,
                   fba.account_number AS from_bank_account_no, fba.account_title AS from_bank_account_title,
                   tcsh.cashier_name AS to_cashier_name,
                   tba.account_number AS to_bank_account_no, tba.account_title AS to_bank_account_title
            FROM cb_contra_transfers ct
            JOIN companies cmp ON ct.company_id = cmp.id
            LEFT JOIN cb_cashiers fcsh ON ct.from_cashier_id = fcsh.id
            LEFT JOIN cb_bank_accounts fba ON ct.from_bank_account_id = fba.id
            LEFT JOIN cb_cashiers tcsh ON ct.to_cashier_id = tcsh.id
            LEFT JOIN cb_bank_accounts tba ON ct.to_bank_account_id = tba.id
            WHERE COALESCE(ct.isDelete, 0) = 0
        """
        params = []
        if company_id:
            sql += " AND ct.company_id = ?"
            params.append(company_id)
        sql += " ORDER BY ct.transfer_date DESC, ct.code DESC"
        return db.query(sql, tuple(params))

    @staticmethod
    def get_contra_transfer_by_id(transfer_id: str) -> Optional[Dict[str, Any]]:
        return db.query_one(
            """
            SELECT ct.*, cmp.name AS company_name, cmp.short_code AS company_code, cmp.currency AS company_currency,
                   fcsh.cashier_name AS from_cashier_name,
                   fba.account_number AS from_bank_account_no, fba.account_title AS from_bank_account_title,
                   tcsh.cashier_name AS to_cashier_name,
                   tba.account_number AS to_bank_account_no, tba.account_title AS to_bank_account_title
            FROM cb_contra_transfers ct
            JOIN companies cmp ON ct.company_id = cmp.id
            LEFT JOIN cb_cashiers fcsh ON ct.from_cashier_id = fcsh.id
            LEFT JOIN cb_bank_accounts fba ON ct.from_bank_account_id = fba.id
            LEFT JOIN cb_cashiers tcsh ON ct.to_cashier_id = tcsh.id
            LEFT JOIN cb_bank_accounts tba ON ct.to_bank_account_id = tba.id
            WHERE ct.id = ? AND COALESCE(ct.isDelete, 0) = 0
            """,
            (transfer_id,)
        )

    @staticmethod
    def create_contra_transfer(
        company_id: str,
        transfer_date: str,
        transfer_type: str,
        amount: float,
        reference_number: str,
        narration: str,
        from_cashier_id: Optional[str] = None,
        from_bank_account_id: Optional[str] = None,
        to_cashier_id: Optional[str] = None,
        to_bank_account_id: Optional[str] = None,
        created_by: str = "Alexander Vance"
    ) -> str:
        new_id = str(uuid.uuid4())
        
        count_row = db.query_one("SELECT COUNT(*) AS cnt FROM cb_contra_transfers WHERE company_id = ?", (company_id,))
        seq = (count_row["cnt"] if count_row else 0) + 1
        comp = db.query_one("SELECT short_code FROM companies WHERE id = ?", (company_id,))
        comp_code = comp["short_code"] if comp else "APEX"
        transfer_number = f"CONTRA-{comp_code}-{seq:04d}"

        db.execute(
            """
            INSERT INTO cb_contra_transfers
            (id, transfer_number, company_id, transfer_date, transfer_type, from_cashier_id, from_bank_account_id, to_cashier_id, to_bank_account_id, amount, reference_number, narration, status, isDelete, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'POSTED', 0, ?)
            """,
            (new_id, transfer_number, company_id, transfer_date, transfer_type.upper(), from_cashier_id or None, from_bank_account_id or None, to_cashier_id or None, to_bank_account_id or None, amount, reference_number.strip(), narration.strip(), created_by)
        )
        return new_id

    @staticmethod
    def delete_contra_transfer(transfer_id: str) -> bool:
        db.execute("UPDATE cb_contra_transfers SET isDelete = 1, isDeleteDate = GETDATE() WHERE id = ?", (transfer_id,))
        return True
