"""
db.py - SQLite 데이터베이스 연결 및 CRUD 함수 모음
==================================================
이 파일은 가계부 앱의 모든 데이터베이스 작업을 담당합니다.
- 테이블 생성 (transactions, categories, budgets)
- 거래 추가/조회/수정/삭제
- 카테고리 관리
- 예산 관리
- 샘플 데이터 생성

[초보자 안내]
SQLite는 파일 하나(budget.db)에 데이터를 저장하는 경량 데이터베이스입니다.
별도의 서버 설치 없이 Python 기본 라이브러리로 사용할 수 있어요.
"""

import sqlite3
import os
from datetime import datetime, date, timedelta
import random

# ============================================================
# 데이터베이스 파일 경로 설정
# ============================================================
# 이 파일과 같은 폴더에 budget.db 파일을 생성합니다.
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget.db")


# ============================================================
# 기본 카테고리 정의
# ============================================================
# 앱을 처음 실행할 때 이 카테고리들이 자동으로 생성됩니다.
DEFAULT_EXPENSE_CATEGORIES = [
    "식비", "교통", "주거/통신", "쇼핑", "문화/여가",
    "의료/건강", "교육", "경조사", "보험", "기타지출"
]

DEFAULT_INCOME_CATEGORIES = [
    "급여", "부수입", "용돈", "투자수익", "기타수입"
]

DEFAULT_PAYMENT_METHODS = ["현금", "카드", "이체", "기타"]


def get_connection():
    """
    SQLite 데이터베이스에 연결합니다.
    
    Returns:
        sqlite3.Connection: 데이터베이스 연결 객체
    
    [초보자 안내]
    sqlite3.connect()는 DB 파일이 없으면 자동으로 생성합니다.
    Row 팩토리를 설정하면 결과를 딕셔너리처럼 사용할 수 있습니다.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리처럼 접근 가능
    conn.execute("PRAGMA journal_mode=WAL")  # 동시 접근 성능 향상
    return conn


def init_db():
    """
    데이터베이스 테이블을 생성합니다.
    이미 테이블이 있으면 건너뜁니다 (IF NOT EXISTS).
    
    생성되는 테이블:
    1. transactions - 수입/지출 거래 내역
    2. categories - 카테고리 목록
    3. budgets - 예산 설정
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── 거래 내역 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,            -- 거래 날짜 (YYYY-MM-DD)
            type TEXT NOT NULL,            -- 'income' 또는 'expense'
            amount REAL NOT NULL,          -- 금액 (양수)
            category TEXT NOT NULL,        -- 카테고리명
            payment_method TEXT DEFAULT '카드',  -- 결제수단
            memo TEXT DEFAULT '',          -- 메모 (선택)
            created_at TEXT NOT NULL       -- 생성 시각
        )
    """)

    # ── 카테고리 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,            -- 'income' 또는 'expense'
            name TEXT NOT NULL,            -- 카테고리명
            UNIQUE(type, name)             -- 같은 타입에 중복 이름 방지
        )
    """)

    # ── 예산 테이블 ──
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,           -- 예산 월 (YYYY-MM)
            category TEXT DEFAULT '',      -- 카테고리 (빈 문자열이면 전체 예산)
            budget_amount REAL NOT NULL,   -- 예산 금액
            UNIQUE(month, category)        -- 같은 월+카테고리 중복 방지
        )
    """)

    conn.commit()

    # 카테고리가 비어있으면 기본 카테고리 삽입
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    if count == 0:
        _insert_default_categories(conn)

    conn.close()


def _insert_default_categories(conn):
    """기본 카테고리를 DB에 삽입합니다."""
    cursor = conn.cursor()
    for cat in DEFAULT_EXPENSE_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (type, name) VALUES (?, ?)",
            ("expense", cat)
        )
    for cat in DEFAULT_INCOME_CATEGORIES:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (type, name) VALUES (?, ?)",
            ("income", cat)
        )
    conn.commit()


# ============================================================
# 거래(Transaction) CRUD
# ============================================================

def add_transaction(date_str, tx_type, amount, category, payment_method, memo=""):
    """
    새 거래를 추가합니다.
    
    Args:
        date_str (str): 날짜 (YYYY-MM-DD)
        tx_type (str): 'income' 또는 'expense'
        amount (float): 금액 (양수)
        category (str): 카테고리명
        payment_method (str): 결제수단
        memo (str): 메모 (선택)
    
    Returns:
        int: 새로 생성된 거래 ID
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO transactions (date, type, amount, category, payment_method, memo, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date_str, tx_type, amount, category, payment_method, memo, now))
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_transactions(start_date=None, end_date=None, tx_type=None,
                     categories=None, payment_method=None, keyword=None,
                     sort_by="date", sort_order="DESC"):
    """
    조건에 맞는 거래 목록을 조회합니다.
    
    Args:
        start_date (str): 시작 날짜 (YYYY-MM-DD)
        end_date (str): 종료 날짜 (YYYY-MM-DD)
        tx_type (str): 'income', 'expense', 또는 None(전체)
        categories (list): 카테고리 목록 (멀티 선택)
        payment_method (str): 결제수단 필터
        keyword (str): 메모 검색 키워드
        sort_by (str): 정렬 기준 ('date', 'amount')
        sort_order (str): 정렬 방향 ('ASC', 'DESC')
    
    Returns:
        list[dict]: 거래 목록
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

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

    # 정렬
    allowed_sort = {"date": "date", "amount": "amount", "created_at": "created_at"}
    sort_col = allowed_sort.get(sort_by, "date")
    order = "DESC" if sort_order == "DESC" else "ASC"
    query += f" ORDER BY {sort_col} {order}"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_transaction(tx_id, date_str, tx_type, amount, category, payment_method, memo):
    """
    기존 거래를 수정합니다.
    
    Args:
        tx_id (int): 거래 ID
        이하 필드: add_transaction과 동일
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET date=?, type=?, amount=?, category=?, payment_method=?, memo=?
        WHERE id=?
    """, (date_str, tx_type, amount, category, payment_method, memo, tx_id))
    conn.commit()
    conn.close()


def delete_transaction(tx_id):
    """거래를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    conn.commit()
    conn.close()


def get_transaction_by_id(tx_id):
    """ID로 단일 거래를 조회합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id=?", (tx_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# ============================================================
# 카테고리 CRUD
# ============================================================

def get_categories(tx_type=None):
    """
    카테고리 목록을 조회합니다.
    
    Args:
        tx_type (str): 'income', 'expense', 또는 None(전체)
    
    Returns:
        list[str]: 카테고리명 목록
    """
    conn = get_connection()
    cursor = conn.cursor()
    if tx_type:
        cursor.execute("SELECT name FROM categories WHERE type=? ORDER BY id", (tx_type,))
    else:
        cursor.execute("SELECT name FROM categories ORDER BY type, id")
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]


def add_category(tx_type, name):
    """새 카테고리를 추가합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (type, name) VALUES (?, ?)",
            (tx_type, name)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # 중복 카테고리


def delete_category(tx_type, name):
    """카테고리를 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE type=? AND name=?", (tx_type, name))
    conn.commit()
    conn.close()


# ============================================================
# 예산(Budget) CRUD
# ============================================================

def get_budgets(month=None):
    """
    예산 목록을 조회합니다.
    
    Args:
        month (str): 'YYYY-MM' 형식. None이면 전체 조회
    
    Returns:
        list[dict]: 예산 목록
    """
    conn = get_connection()
    cursor = conn.cursor()
    if month:
        cursor.execute("SELECT * FROM budgets WHERE month=?", (month,))
    else:
        cursor.execute("SELECT * FROM budgets ORDER BY month DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_budget(month, category, amount):
    """
    예산을 설정(추가 또는 업데이트)합니다.
    
    Args:
        month (str): 'YYYY-MM'
        category (str): 카테고리명 (빈 문자열이면 전체 예산)
        amount (float): 예산 금액
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (month, category, budget_amount)
        VALUES (?, ?, ?)
        ON CONFLICT(month, category) DO UPDATE SET budget_amount=?
    """, (month, category, amount, amount))
    conn.commit()
    conn.close()


def delete_budget(budget_id):
    """예산을 삭제합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE id=?", (budget_id,))
    conn.commit()
    conn.close()


# ============================================================
# 유틸리티
# ============================================================

def clear_all_data():
    """모든 거래 데이터를 삭제합니다. (카테고리/예산은 유지)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()


def clear_everything():
    """모든 데이터를 삭제하고 기본 카테고리를 다시 생성합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    cursor.execute("DELETE FROM categories")
    conn.commit()
    _insert_default_categories(conn)
    conn.close()


def generate_sample_data(num_months=3):
    """
    데모용 샘플 데이터를 생성합니다.
    
    Args:
        num_months (int): 몇 개월치 데이터를 생성할지
    
    [초보자 안내]
    이 함수는 앱을 처음 사용할 때 데모 목적으로 가짜 데이터를 넣어줍니다.
    실제 사용 시에는 직접 입력하면 됩니다.
    """
    today = date.today()
    expense_cats = DEFAULT_EXPENSE_CATEGORIES
    income_cats = DEFAULT_INCOME_CATEGORIES
    methods = DEFAULT_PAYMENT_METHODS

    # 지출 샘플 패턴 (카테고리: (최소금액, 최대금액, 월 평균 건수))
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

    # 수입 샘플 패턴
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
        # 현재 달에서 m개월 전
        target_month = today.month - m
        target_year = today.year
        while target_month <= 0:
            target_month += 12
            target_year -= 1

        # 지출 생성
        for cat, (min_amt, max_amt, avg_count) in expense_patterns.items():
            n = random.randint(max(1, avg_count - 1), avg_count + 1)
            for _ in range(n):
                day = random.randint(1, 28)
                d = f"{target_year}-{target_month:02d}-{day:02d}"
                amt = round(random.randint(min_amt, max_amt) / 100) * 100
                method = random.choice(methods)
                memo = random.choice(memos_expense)
                add_transaction(d, "expense", amt, cat, method, memo)
                count += 1

        # 수입 생성
        for cat, (min_amt, max_amt, avg_count) in income_patterns.items():
            n = avg_count
            for _ in range(n):
                day = random.randint(1, 28)
                d = f"{target_year}-{target_month:02d}-{day:02d}"
                amt = round(random.randint(min_amt, max_amt) / 1000) * 1000
                memo = random.choice(memos_income)
                add_transaction(d, "income", amt, cat, "이체", memo)
                count += 1

    return count


def export_transactions_csv(start_date=None, end_date=None):
    """
    거래 내역을 CSV 문자열로 내보냅니다.
    
    Returns:
        str: CSV 형식 문자열
    """
    import io
    import csv

    transactions = get_transactions(start_date=start_date, end_date=end_date,
                                     sort_by="date", sort_order="ASC")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 헤더
    writer.writerow(["날짜", "유형", "금액", "카테고리", "결제수단", "메모"])
    
    type_map = {"income": "수입", "expense": "지출"}
    for tx in transactions:
        writer.writerow([
            tx["date"],
            type_map.get(tx["type"], tx["type"]),
            tx["amount"],
            tx["category"],
            tx["payment_method"],
            tx["memo"]
        ])
    
    return output.getvalue()
