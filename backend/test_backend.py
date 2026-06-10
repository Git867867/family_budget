"""
Unit tests for Family Budget backend API.
Uses a separate test database, isolated via fixtures.
Each test starts with clean tables (incomes, expenses, audit_log, balance_history).
"""

import pytest
import psycopg2
from fastapi.testclient import TestClient
import backend

TEST_DB_CONFIG = {
    "dbname": "family_budget_test",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": 5432,
}

# Tables to clean before each test
TABLES_TO_CLEAN = ["income", "expense", "audit_log", "balance_history"]

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create and initialize a dedicated test database once per session.
    The database is dropped after all tests.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user=TEST_DB_CONFIG["user"],
        password=TEST_DB_CONFIG["password"],
        host=TEST_DB_CONFIG["host"],
        port=TEST_DB_CONFIG["port"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['dbname']}")
    cur.execute(f"CREATE DATABASE {TEST_DB_CONFIG['dbname']}")
    cur.close()
    conn.close()

    original_config = backend.DB_CONFIG.copy()
    backend.DB_CONFIG = TEST_DB_CONFIG
    backend.init_db()

    yield

    # Restore original config and drop test database
    backend.DB_CONFIG = original_config
    conn = psycopg2.connect(
        dbname="postgres",
        user=TEST_DB_CONFIG["user"],
        password=TEST_DB_CONFIG["password"],
        host=TEST_DB_CONFIG["host"],
        port=TEST_DB_CONFIG["port"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['dbname']}")
    cur.close()
    conn.close()

@pytest.fixture(autouse=True)
def clean_tables():
    """
    Clean all transactional tables before each test to ensure isolation.
    Reference tables (family_members, income_types, accounts, expense_categories)
    and session data are left intact.
    """
    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cur = conn.cursor()
    for table in TABLES_TO_CLEAN:
        cur.execute(f"DELETE FROM {table}")
    # Reset sequences to keep IDs predictable
    cur.execute("ALTER SEQUENCE income_id_seq RESTART WITH 1")
    cur.execute("ALTER SEQUENCE expense_id_seq RESTART WITH 1")
    cur.execute("ALTER SEQUENCE audit_log_id_seq RESTART WITH 1")
    cur.execute("ALTER SEQUENCE balance_history_id_seq RESTART WITH 1")
    conn.commit()
    cur.close()
    conn.close()

@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    with TestClient(backend.app) as c:
        yield c

def _obtain_admin_token(client):
    resp = client.post("/login/admin", json={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    return resp.json()["token"]

def _create_member_and_activate(client, admin_token):
    """Helper: create a family member and activate session, return client token and member_id."""
    resp = client.post("/members", json={"full_name": "Тест Тестович", "kinship_type": "отец"},
                       headers={"token": admin_token})
    assert resp.status_code == 200
    member_id = resp.json()["id"]
    resp = client.post("/session/activate", json={"member_id": member_id})
    assert resp.status_code == 200
    return resp.json()["token"], member_id

class TestAuthentication:
    def test_admin_login_success(self, client):
        resp = client.post("/login/admin", json={"username": "admin", "password": "admin"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["full_name"] == "Администратор"

    def test_admin_login_wrong_password(self, client):
        resp = client.post("/login/admin", json={"username": "admin", "password": "wrong"})
        assert resp.status_code == 403

    def test_guest_login(self, client):
        resp = client.post("/login/guest")
        assert resp.status_code == 200
        assert "token" in resp.json()

class TestIncomeCRUD:
    def test_add_income_success(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        resp = client.post("/income", json={
            "income_type": "зарплата",
            "account": "основной счет",
            "amount": 5000,
            "date": "2025-01-01"
        }, headers={"token": token})
        assert resp.status_code == 200
        assert resp.json()["detail"] == "Доход добавлен"
        assert "id" in resp.json()

    def test_update_income(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        add_resp = client.post("/income", json={
            "income_type": "зарплата",
            "account": "основной счет",
            "amount": 3000,
            "date": "2025-02-01"
        }, headers={"token": token})
        income_id = add_resp.json()["id"]
        resp = client.put(f"/income/{income_id}", json={
            "income_type": "стипендия",
            "account": "накопления",
            "amount": 4500,
            "date": "2025-02-15"
        }, headers={"token": token})
        assert resp.status_code == 200
        balance = client.get("/balance", headers={"token": token}).json()
        assert balance["total_income"] == 4500

    def test_delete_income(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        add_resp = client.post("/income", json={
            "income_type": "зарплата",
            "account": "основной счет",
            "amount": 1000,
            "date": "2025-03-01"
        }, headers={"token": token})
        income_id = add_resp.json()["id"]
        resp = client.delete(f"/income/{income_id}", headers={"token": token})
        assert resp.status_code == 200
        balance = client.get("/balance", headers={"token": token}).json()
        assert balance["total_income"] == 0

class TestExpenseCRUD:
    def test_add_expense_insufficient_funds(self, client):
        """Попытка добавить расход при нулевом балансе должна быть отклонена."""
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        # Баланс изначально 0 (нет доходов)
        resp = client.post("/expense", json={
            "category": "продукты",
            "amount": 10,
            "date": "2025-01-02",
            "is_planned": False
        }, headers={"token": token})
        assert resp.status_code == 400
        assert "Расход запрещён" in resp.json()["detail"]

    def test_full_expense_lifecycle(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        # Fund the account
        client.post("/income", json={
            "income_type": "зарплата",
            "account": "основной счет",
            "amount": 500,
            "date": "2025-05-01"
        }, headers={"token": token})
        # Add a real expense
        resp = client.post("/expense", json={
            "category": "транспорт",
            "amount": 150,
            "date": "2025-05-02",
            "is_planned": False
        }, headers={"token": token})
        exp_id = resp.json()["id"]
        # Update to planned (should not affect spendable balance)
        resp = client.put(f"/expense/{exp_id}", json={
            "category": "транспорт",
            "amount": 100,
            "date": "2025-05-02",
            "is_planned": True
        }, headers={"token": token})
        assert resp.status_code == 200
        balance = client.get("/balance", headers={"token": token}).json()
        # Planned expense does not count toward total_expenses
        assert balance["total_expenses"] == 0
        # Delete the expense
        resp = client.delete(f"/expense/{exp_id}", headers={"token": token})
        assert resp.status_code == 200

class TestBalanceAndReport:
    def test_balance_calculation(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        client.post("/income", json={
            "income_type": "стипендия",
            "account": "накопления",
            "amount": 3000,
            "date": "2025-06-01"
        }, headers={"token": token})
        resp = client.get("/balance", headers={"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"] == 3000
        assert data["balance"] == 3000

    def test_report(self, client):
        admin_token = _obtain_admin_token(client)
        token, _ = _create_member_and_activate(client, admin_token)
        # Add income
        resp_inc = client.post("/income", json={
            "income_type": "зарплата",
            "account": "основной счет",
            "amount": 1000,
            "date": "2025-07-01"
        }, headers={"token": token})
        assert resp_inc.status_code == 200

        # Add expense with a valid category from ExpenseCategory
        resp_exp = client.post("/expense", json={
            "category": "продукты",
            "amount": 200,
            "date": "2025-07-01",
            "is_planned": False
        }, headers={"token": token})
        assert resp_exp.status_code == 200

        resp = client.get("/report", params={"start_date": "2025-07-01", "end_date": "2025-07-31"},
                          headers={"token": token})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"] == 1000
        assert data["total_expense"] == 200
        assert data["balance"] == 800

def test_audit_log(client):
    """Audit log should contain at least one login_admin entry."""
    _obtain_admin_token(client)
    conn = psycopg2.connect(**TEST_DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM audit_log WHERE action = 'login_admin'")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    assert count >= 1