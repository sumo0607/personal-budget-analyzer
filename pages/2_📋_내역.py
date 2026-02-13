"""
2_📋_내역.py - 거래 목록/관리 페이지
=====================================
저장된 거래 내역을 조회, 필터링, 검색, 수정, 삭제할 수 있습니다.

[기능]
- 기간/타입/카테고리/결제수단 필터
- 메모 키워드 검색
- 날짜/금액 정렬
- 행 선택 후 수정/삭제
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth
from ui_components import (
    format_currency,
    type_to_korean,
    type_to_english,
    show_empty_state,
)

# ============================================================
# 페이지 설정
# ============================================================
# 인증 확인
user_id = auth.check_auth()

st.title("📋 거래 내역")
st.caption("저장된 거래를 조회하고, 수정하거나 삭제할 수 있습니다.")

# ============================================================
# 사이드바 필터
# ============================================================
st.sidebar.subheader("🔍 필터 설정")

# 기간 필터
period = st.sidebar.selectbox(
    "📅 기간",
    ["이번 달", "지난 달", "최근 3개월", "전체", "사용자 지정"],
    key="history_period"
)

today = date.today()
first_of_month = today.replace(day=1)

if period == "이번 달":
    start_date = first_of_month
    end_date = today
elif period == "지난 달":
    last_month_end = first_of_month - timedelta(days=1)
    start_date = last_month_end.replace(day=1)
    end_date = last_month_end
elif period == "최근 3개월":
    start_date = today - timedelta(days=90)
    end_date = today
elif period == "사용자 지정":
    start_date = st.sidebar.date_input("시작일", first_of_month - timedelta(days=30))
    end_date = st.sidebar.date_input("종료일", today)
else:  # 전체
    start_date = None
    end_date = None

# 타입 필터
tx_type_filter = st.sidebar.radio("📌 유형", ["전체", "수입", "지출"], horizontal=True)

# 카테고리 필터
all_cats = db.get_categories(user_id)
selected_cats = st.sidebar.multiselect("🏷️ 카테고리", all_cats, default=[])

# 결제수단 필터
payment_filter = st.sidebar.selectbox(
    "💳 결제수단",
    ["전체"] + db.DEFAULT_PAYMENT_METHODS
)

# 검색어
keyword = st.sidebar.text_input("🔎 메모 검색", placeholder="키워드 입력")

# 정렬
sort_col = st.sidebar.selectbox("정렬 기준", ["날짜", "금액"])
sort_dir = st.sidebar.radio("정렬 방향", ["최신순/큰순", "오래된순/작은순"], horizontal=True)

sort_map = {"날짜": "date", "금액": "amount"}
dir_map = {"최신순/큰순": "DESC", "오래된순/작은순": "ASC"}

# ============================================================
# 데이터 조회
# ============================================================
transactions = db.get_transactions(
    user_id,
    start_date=str(start_date) if start_date else None,
    end_date=str(end_date) if end_date else None,
    tx_type=tx_type_filter if tx_type_filter != "전체" else None,
    categories=selected_cats if selected_cats else None,
    payment_method=payment_filter if payment_filter != "전체" else None,
    keyword=keyword if keyword else None,
    sort_by=sort_map[sort_col],
    sort_order=dir_map[sort_dir]
)

# ============================================================
# 결과 표시
# ============================================================
st.markdown("---")

if not transactions:
    show_empty_state(
        "조건에 맞는 거래가 없습니다",
        "필터 조건을 변경하거나, '입력' 페이지에서 새 거래를 추가해보세요."
    )
else:
    # 건수 및 합계 표시
    df = pd.DataFrame(transactions)
    income_sum = df[df["type"] == "income"]["amount"].sum()
    expense_sum = df[df["type"] == "expense"]["amount"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 조회 건수", f"{len(df)}건")
    col2.metric("💰 수입 합계", format_currency(income_sum))
    col3.metric("💸 지출 합계", format_currency(expense_sum))
    
    st.markdown("---")
    
    # 데이터프레임 표시
    display_df = df.copy()
    type_map = {"income": "🟢 수입", "expense": "🔴 지출"}
    display_df["유형"] = display_df["type"].map(type_map)
    display_df["금액"] = display_df["amount"].apply(lambda x: f"{x:,.0f}원")
    display_df["ID"] = display_df["id"]
    
    show_df = display_df[["ID", "date", "유형", "금액", "category", "payment_method", "memo"]].copy()
    show_df.columns = ["ID", "날짜", "유형", "금액", "카테고리", "결제수단", "메모"]
    
    st.dataframe(show_df, use_container_width=True, hide_index=True, height=400)
    
    # ============================================================
    # 수정/삭제 기능
    # ============================================================
    st.markdown("---")
    st.subheader("✏️ 거래 수정/삭제")
    
    # 수정할 거래 ID 선택
    tx_ids = [tx["id"] for tx in transactions]
    
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    
    def _fmt_tx_id(x):
        for t in transactions:
            if t['id'] == x:
                return "ID {} | {} | {} | {} | {}".format(
                    x, t['date'], type_to_korean(t['type']),
                    format_currency(t['amount']), t['category']
                )
        return "ID {}".format(x)

    selected_id = st.selectbox(
        "수정/삭제할 거래 ID 선택",
        options=tx_ids,
        format_func=_fmt_tx_id
    )
    
    if selected_id:
        tx = db.get_transaction_by_id(user_id, selected_id)
        
        if tx:
            col_edit, col_delete = st.columns(2)
            
            # ── 수정 폼 ──
            with col_edit:
                st.markdown("#### ✏️ 수정")
                with st.form(f"edit_form_{selected_id}"):
                    edit_date = st.date_input("날짜", value=date.fromisoformat(tx["date"]))
                    edit_type = st.radio("유형", ["지출", "수입"],
                                         index=0 if tx["type"] == "expense" else 1,
                                         horizontal=True)
                    edit_amount = st.number_input("금액", min_value=0,
                                                   value=int(tx["amount"]), step=1000)
                    
                    edit_type_en = type_to_english(edit_type)
                    edit_cats = db.get_categories(user_id, edit_type_en)
                    cat_idx = edit_cats.index(tx["category"]) if tx["category"] in edit_cats else 0
                    edit_category = st.selectbox("카테고리", edit_cats, index=cat_idx)
                    
                    pm_idx = db.DEFAULT_PAYMENT_METHODS.index(tx["payment_method"]) \
                        if tx["payment_method"] in db.DEFAULT_PAYMENT_METHODS else 0
                    edit_payment = st.selectbox("결제수단", db.DEFAULT_PAYMENT_METHODS, index=pm_idx)
                    edit_memo = st.text_input("메모", value=tx["memo"] or "")
                    
                    if st.form_submit_button("💾 수정 저장", type="primary", use_container_width=True):
                        if edit_amount <= 0:
                            st.error("금액은 0보다 커야 합니다.")
                        else:
                            db.update_transaction(
                                user_id,
                                selected_id,
                                str(edit_date),
                                edit_type_en,
                                float(edit_amount),
                                edit_category,
                                edit_payment,
                                edit_memo
                            )
                            st.success("✅ 수정 완료!")
                            st.rerun()
            
            # ── 삭제 ──
            with col_delete:
                st.markdown("#### 🗑️ 삭제")
                st.warning(f"**ID {selected_id}** 거래를 삭제하시겠습니까?")
                st.markdown(f"""
                - 날짜: {tx['date']}
                - 유형: {type_to_korean(tx['type'])}
                - 금액: {format_currency(tx['amount'])}
                - 카테고리: {tx['category']}
                """)
                
                # 삭제 확인 체크박스 (실수 방지)
                confirm = st.checkbox("삭제를 확인합니다", key=f"del_confirm_{selected_id}")
                if st.button("🗑️ 삭제 실행", type="secondary", 
                             use_container_width=True, disabled=not confirm):
                    db.delete_transaction(user_id, selected_id)
                    st.success("✅ 삭제 완료!")
                    st.rerun()
