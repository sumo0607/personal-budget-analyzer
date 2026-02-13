"""
db.py - SQLite 데이터베이스 연결 및 CRUD 함수 모음
==================================================
이 파일은 가계부 앱의 모든 데이터베이스 작업을 담당합니다.
- 사용자 인증 (회원가입, 로그인, role 관리)
- 테이블 생성 (users, transactions, categories, budgets)
- 거래 추가/조회/수정/삭제
- 카테고리 관리
- 예산 관리
- 관리자 전용 조회/관리 함수
- 샘플 데이터 생성

모든 데이터는 user_id로 구분되어 사용자별로 관리됩니다.
"""

import sqlite3
import os
import bcrypt
from datetime import datetime, date, timedelta
import random

# ============================================================
# 데이터베이스 파일 경로 설정
# ============================================================
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget.db")

# ============================================================
# 기본 카테고리 정의
# ============================================================
DEFAULT_EXPENSE_CATEGORIES = [
    "식비", "교통", "주거/통신", "쇼핑", "문화/여가",
    "의료/건강", "교육", "경조사", "보험", "기타지출"
]

DEFAULT_INCOME_CATEGORIES = [
    "급여", "부수입", "용돈", "투자수익", "기타수입"
]

DEFAULT_PAYMENT_METHODS = ["현금", "카드", "이체", "기타"]


# ============================================================
# 비밀번호 해시 유틸리티 (bcrypt)
# ============================================================

def hash_password(password):
    """비밀번호를 bcrypt로 해시합니다."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, stored_hash):
    """비밀번호가 저장된 bcrypt 해시와 일치하는지 확인합니다."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        return False


# ============================================================
# DB 연결 및 초기화
# ============================================================

def get_connection():
    """SQLite 데이터베이스에 연결합니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _raw_connection():
    """row_factory 없는 원시 연결 (PRAGMA 조회용)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _get_table_columns(table_name):
    """테이블의 컬럼 이름 목록을 반환합니다."""
    raw = _raw_connection()
    cur = raw.cursor()
    cur.execute(f"PRAGMA table_info({table_name})")
    cols = [row[1] for row in cur.fetchall()]
    raw.close()
    return cols


def init_db():
    """
    데이터베이스 테이블을 생성합니다.
    기존 구 스키마 → 신 스키마 마이그레이션을 자동 수행합니다.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── foreign_keys를 잠시 끄고 마이그레이션 수행 ──
    cursor.execute("PRAGMA foreign_keys=OFF")

    try:
        # (1) 기존 transactions에 user_id가 없으면 구 스키마 → DROP 재생성
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        )
        if cursor.fetchone() is not None:
            cols = _get_table_columns("transactions")
            if "user_id" not in cols:
                cursor.execute("DROP TABLE IF EXISTS transactions")
                cursor.execute("DROP TABLE IF EXISTS categories")
                cursor.execute("DROP TABLE IF EXISTS budgets")
                conn.commit()
    except Exception:
        pass

    # ── 사용자 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user','admin')) DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    """)

    # users 테이블에 role 컬럼이 없으면 추가 (이전 버전 마이그레이션)
    try:
        user_cols = _get_table_columns("users")
        if "role" not in user_cols:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
            conn.commit()
    except Exception:
        pass

    # ── 거래 내역 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            payment_method TEXT DEFAULT '카드',
            memo TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── 카테고리 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(user_id, type, name),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── 예산 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            category TEXT DEFAULT '',
            budget_amount REAL NOT NULL,
            UNIQUE(user_id, month, category),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("PRAGMA foreign_keys=ON")
    conn.commit()

    # ── 관리자 시드 ──
    _seed_admin(conn)

    conn.close()


def _seed_admin(conn):
    """
    관리자 계정이 없으면 자동 생성합니다.
    환경변수 ADMIN_ID / ADMIN_PW 로 커스터마이징 가능합니다.
    """
    cursor = conn.cursor()
    admin_username = os.environ.get("ADMIN_ID", "admin")

    cursor.execute("SELECT id FROM users WHERE username = ?", (admin_username,))
    if cursor.fetchone() is not None:
        # 이미 존재하면 role만 admin으로 보장
        cursor.execute(
            "UPDATE users SET role='admin' WHERE username=?", (admin_username,)
        )
        conn.commit()
        return

    admin_password = os.environ.get("ADMIN_PW", "dkms3498!")
    pw_hash = hash_password(admin_password)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, 'admin', ?)",
            (admin_username, pw_hash, now),
        )
        conn.commit()
        admin_id = cursor.lastrowid
        _insert_default_categories(conn, admin_id)
    except sqlite3.IntegrityError:
        pass


# ============================================================
# 사용자 인증
# ============================================================

def register_user(username, password):
    """
    새 사용자를 등록합니다 (role='user').

    Returns:
        int|None: 새 사용자 ID. 중복 아이디면 None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pw_hash = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, 'user', ?)",
            (username, pw_hash, now),
        )
        conn.commit()
        user_id = cursor.lastrowid
        _insert_default_categories(conn, user_id)
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def authenticate_user(username, password):
    """
    사용자를 인증합니다.

    Returns:
        dict|None: {'id', 'username', 'role'} 또는 None
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and verify_password(password, row["password_hash"]):
        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
        }
    return None


# ============================================================
# 관리자 전용: 사용자 관리
# ============================================================

def get_all_users():
    """
    모든 사용자 목록을 조회합니다 (관리자용).

    Returns:
        list[dict]: 사용자 목록 (id, username, role, created_at, tx_count)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.username, u.role, u.created_at,
               COALESCE(t.cnt, 0) AS tx_count
        FROM users u
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS cnt FROM transactions GROUP BY user_id
        ) t ON u.id = t.user_id
        ORDER BY u.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_user_role(user_id, new_role):
    """사용자 role을 변경합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()


def admin_get_transactions(
    target_user_id,
    start_date=None,
    end_date=None,
    tx_type=None,
    categories=None,
    payment_method=None,
    keyword=None,
    sort_by="date",
    sort_order="DESC",
):
    """
    관리자가 특정 사용자의 거래를 조회합니다.
    get_transactions와 동일하지만 명시적으로 admin 용도임을 나타냅니다.
    """
    return get_transactions(
        target_user_id,
        start_date=start_date,
        end_date=end_date,
        tx_type=tx_type,
        categories=categories,
        payment_method=payment_method,
        keyword=keyword,
        sort_by=sort_by,
        sort_order=sort_order,
    )


def admin_delete_transaction(tx_id):
    """관리자가 임의의 거래를 삭제합니다 (user_id 체크 없음)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    conn.commit()
    conn.close()


# ============================================================
# 기본 카테고리 삽입
# ============================================================

def _insert_default_categories(conn, user_id):
    """지정된 사용자에게 기본 카테고리를 삽입합니다."""
    cursor = conn.cursor()
    for cat in DEFAULT_EXPENSE_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (user_id, type, name) VALUES (?, ?, ?)",
            (user_id, "expense", cat),
        )
    for cat in DEFAULT_INCOME_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (user_id, type, name) VALUES (?, ?, ?)",
            (user_id, "income", cat),
        )
    conn.commit()


# ============================================================
# 거래(Transaction) CRUD
# ============================================================

def add_transaction(user_id, date_str, tx_type, amount, category, payment_method, memo=""):
    """새 거래를 추가합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """INSERT INTO transactions (user_id, date, type, amount, category, payment_method, memo, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, date_str, tx_type, amount, category, payment_method, memo, now),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_transactions(
    user_id,
    start_date=None,
    end_date=None,
    tx_type=None,
    categories=None,
    payment_method=None,
    keyword=None,
    sort_by="date",
    sort_order="DESC",
):
    """조건에 맞는 거래 목록을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if tx_type and tx_type != "전체":
        type_map = {"수입": "income", "지출": "expense"}
        query += " AND type = ?"
        params.append(type_map.get(tx_type, tx_type))
    if categories:
        placeholders = ",".join(["?" for _ in categories])
        query += f" AND category IN ({placeholders})"
        params.extend(categories)
    if payment_method and payment_method != "전체":
        query += " AND payment_method = ?"
        params.append(payment_method)
    if keyword:
        query += " AND memo LIKE ?"
        params.append(f"%{keyword}%")

    allowed_sort = {"date": "date", "amount": "amount", "created_at": "created_at"}
    sort_col = allowed_sort.get(sort_by, "date")
    order = "DESC" if sort_order == "DESC" else "ASC"
    query += f" ORDER BY {sort_col} {order}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_transaction(user_id, tx_id, date_str, tx_type, amount, category, payment_method, memo):
    """기존 거래를 수정합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE transactions
           SET date=?, type=?, amount=?, category=?, payment_method=?, memo=?
           WHERE id=? AND user_id=?""",
        (date_str, tx_type, amount, category, payment_method, memo, tx_id, user_id),
    )
    conn.commit()
    conn.close()


def delete_transaction(user_id, tx_id):
    """거래를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (tx_id, user_id))
    conn.commit()
    conn.close()


def get_transaction_by_id(user_id, tx_id):
    """ID로 단일 거래를 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id=? AND user_id=?", (tx_id, user_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================================
# 카테고리 CRUD
# ============================================================

def get_categories(user_id, tx_type=None):
    """해당 사용자의 카테고리 목록을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    if tx_type:
        cursor.execute(
            "SELECT name FROM categories WHERE user_id=? AND type=? ORDER BY id",
            (user_id, tx_type),
        )
    else:
        cursor.execute(
            "SELECT name FROM categories WHERE user_id=? ORDER BY type, id",
            (user_id,),
        )
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]


def add_category(user_id, tx_type, name):
    """새 카테고리를 추가합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (user_id, type, name) VALUES (?, ?, ?)",
            (user_id, tx_type, name),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def delete_category(user_id, tx_type, name):
    """카테고리를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM categories WHERE user_id=? AND type=? AND name=?",
        (user_id, tx_type, name),
    )
    conn.commit()
    conn.close()


# ============================================================
# 예산(Budget) CRUD
# ============================================================

def get_budgets(user_id, month=None):
    """해당 사용자의 예산 목록을 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    if month:
        cursor.execute("SELECT * FROM budgets WHERE user_id=? AND month=?", (user_id, month))
    else:
        cursor.execute("SELECT * FROM budgets WHERE user_id=? ORDER BY month DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_budget(user_id, month, category, amount):
    """예산을 설정(추가 또는 업데이트)합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO budgets (user_id, month, category, budget_amount)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, month, category) DO UPDATE SET budget_amount=?""",
        (user_id, month, category, amount, amount),
    )
    conn.commit()
    conn.close()


def delete_budget(user_id, budget_id):
    """예산을 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE id=? AND user_id=?", (budget_id, user_id))
    conn.commit()
    conn.close()


# ============================================================
# 유틸리티
# ============================================================

def clear_all_data(user_id):
    """해당 사용자의 모든 거래 데이터를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def clear_everything(user_id):
    """해당 사용자의 모든 데이터를 삭제하고 기본 카테고리를 다시 생성합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM budgets WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM categories WHERE user_id=?", (user_id,))
    conn.commit()
    _insert_default_categories(conn, user_id)
    conn.close()


def generate_sample_data(user_id, num_months=3):
    """데모용 샘플 데이터를 생성합니다."""
    today = date.today()
    methods = DEFAULT_PAYMENT_METHODS

    expense_patterns = {
        "식비": (5000, 30000, 15),
        "교통": (1000, 10000, 8),
        "주거/통신": (50000, 150000, 2),
        "쇼핑": (10000, 100000, 3),
        "문화/여가": (10000, 50000, 2),
        "의료/건강": (5000, 80000, 1),
        "교육": (30000, 200000, 1),
        "경조사": (30000, 100000, 1),
        "기타지출": (5000, 30000, 2),
    }
    income_patterns = {
        "급여": (2500000, 3500000, 1),
        "부수입": (100000, 500000, 1),
    }
    memos_expense = [
        "점심식사", "커피", "택시", "버스", "지하철", "마트장보기",
        "온라인쇼핑", "영화관람", "책구입", "약국", "통신비",
        "관리비", "전기요금", "친구생일선물", "운동", "간식",
    ]
    memos_income = ["월급", "프리랜서", "용돈", "배당금", "환급금"]

    count = 0
    for m in range(num_months):
        target_month = today.month - m
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        for cat, (min_amt, max_amt, avg_count) in expense_patterns.items():
            n = random.randint(max(1, avg_count - 1), avg_count + 1)
            for _ in range(n):
                day = random.randint(1, 28)
                d = f"{target_year}-{target_month:02d}-{day:02d}"
                amt = round(random.randint(min_amt, max_amt) / 100) * 100
                method = random.choice(methods)
                memo = random.choice(memos_expense)
                add_transaction(user_id, d, "expense", amt, cat, method, memo)
                count += 1

        for cat, (min_amt, max_amt, avg_count) in income_patterns.items():
            n = avg_count
            for _ in range(n):
                day = random.randint(1, 28)
                d = f"{target_year}-{target_month:02d}-{day:02d}"
                amt = round(random.randint(min_amt, max_amt) / 1000) * 1000
                memo = random.choice(memos_income)
                add_transaction(user_id, d, "income", amt, cat, "이체", memo)
                count += 1

    return count


def export_transactions_csv(user_id, start_date=None, end_date=None):
    """거래 내역을 CSV 문자열로 내보냅니다."""
    import io
    import csv

    transactions = get_transactions(
        user_id, start_date=start_date, end_date=end_date,
        sort_by="date", sort_order="ASC"
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["날짜", "유형", "금액", "카테고리", "결제수단", "메모"])

    type_map = {"income": "수입", "expense": "지출"}
    for tx in transactions:
        writer.writerow([
            tx["date"],
            type_map.get(tx["type"], tx["type"]),
            tx["amount"],
            tx["category"],
            tx["payment_method"],
            tx["memo"],
        ])
    return output.getvalue()
