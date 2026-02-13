"""
5_🔧_관리자.py - 관리자 전용 페이지
=====================================
관리자(role=admin)만 접근할 수 있는 페이지입니다.

[탭 구성]
A) 가입자 목록 / 권한 관리
B) 사용자 상세 / 거래 내역 조회·삭제
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth
import analytics
from ui_components import (
    format_currency,
    type_to_korean,
    show_empty_state,
    display_summary_cards,
    create_expense_trend_chart,
    create_category_pie_chart,
)

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(page_title="🔧 관리자", page_icon="🔧", layout="wide")
db.init_db()

# 관리자 권한 검사
admin_id = auth.require_admin()
st.title("🔧 관리자 패널")
auth.show_user_info()
st.caption("사용자 관리 및 전체 거래 내역을 관리합니다.")

# ============================================================
# 탭 구성
# ============================================================
tab_users, tab_detail = st.tabs(["👥 가입자 목록 / 권한 관리", "📋 사용자 거래 내역"])

# ============================================================
# 탭 A : 가입자 목록 / 권한 관리
# ============================================================
with tab_users:
    st.subheader("👥 가입자 목록")

    users = db.get_all_users()
    if not users:
        st.info("가입된 사용자가 없습니다.")
    else:
        # 테이블 표시
        user_df = pd.DataFrame(users)
        user_df["역할"] = user_df["role"].map({"admin": "🛡️ 관리자", "user": "👤 일반"})
        display_df = user_df[["id", "username", "역할", "created_at", "tx_count"]].copy()
        display_df.columns = ["ID", "사용자명", "역할", "가입일", "거래 건수"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🔄 권한 변경")

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            user_options = {u["id"]: f'{u["username"]} ({u["role"]})' for u in users}
            selected_uid = st.selectbox(
                "사용자 선택",
                options=list(user_options.keys()),
                format_func=lambda x: user_options[x],
                key="role_sel_user",
            )
        with col2:
            new_role = st.selectbox("변경할 역할", ["user", "admin"], key="role_sel_role")
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            change_btn = st.button("✅ 변경", use_container_width=True)

        if change_btn:
            target_user = next((u for u in users if u["id"] == selected_uid), None)
            if target_user is None:
                st.error("사용자를 찾을 수 없습니다.")
            elif target_user["id"] == admin_id and new_role == "user":
                st.error("🚫 자기 자신의 관리자 권한은 강등할 수 없습니다.")
            elif target_user["role"] == new_role:
                st.info(f"이미 '{new_role}' 역할입니다.")
            else:
                db.update_user_role(selected_uid, new_role)
                st.success(
                    f"✅ **{target_user['username']}** 의 역할이 **{new_role}** 로 변경되었습니다."
                )
                st.rerun()

# ============================================================
# 탭 B : 사용자 상세 / 거래 내역
# ============================================================
with tab_detail:
    st.subheader("📋 사용자별 거래 내역 조회")

    users = db.get_all_users()
    if not users:
        st.info("가입된 사용자가 없습니다.")
        st.stop()

    # ── 사이드바: 사용자 선택 + 필터 ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 관리자 필터")

    user_map = {u["id"]: u["username"] for u in users}
    target_uid = st.sidebar.selectbox(
        "👤 사용자 선택",
        options=list(user_map.keys()),
        format_func=lambda x: f"{user_map[x]} (ID:{x})",
        key="admin_target_user",
    )

    # 기간 필터
    period = st.sidebar.selectbox(
        "📅 기간",
        ["이번 달", "지난 달", "최근 3개월", "전체", "사용자 지정"],
        key="admin_period",
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
        start_date = st.sidebar.date_input("시작일", first_of_month - timedelta(days=30), key="admin_sd")
        end_date = st.sidebar.date_input("종료일", today, key="admin_ed")
    else:  # 전체
        start_date = None
        end_date = None

    tx_type_filter = st.sidebar.radio("📌 유형", ["전체", "수입", "지출"], horizontal=True, key="admin_type")

    all_cats = db.get_categories(target_uid)
    selected_cats = st.sidebar.multiselect("🏷️ 카테고리", all_cats, default=[], key="admin_cats")

    payment_filter = st.sidebar.selectbox(
        "💳 결제수단", ["전체"] + db.DEFAULT_PAYMENT_METHODS, key="admin_pm"
    )
    keyword = st.sidebar.text_input("🔎 메모 검색", placeholder="키워드 입력", key="admin_kw")

    # ── 데이터 조회 ──
    transactions = db.admin_get_transactions(
        target_uid,
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        tx_type=tx_type_filter if tx_type_filter != "전체" else None,
        categories=selected_cats if selected_cats else None,
        payment_method=payment_filter if payment_filter != "전체" else None,
        keyword=keyword if keyword else None,
    )

    st.markdown(f"#### 📌 **{user_map[target_uid]}** 님의 거래 내역")

    if not transactions:
        show_empty_state(
            "조건에 맞는 거래가 없습니다",
            "필터 조건을 변경해보세요.",
        )
    else:
        # ── 요약 통계 ──
        df = analytics.transactions_to_dataframe(transactions)
        summary = analytics.get_summary(df)
        display_summary_cards(summary)

        st.markdown("---")

        # ── 차트 (지출 추이 + 카테고리) ──
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            expense_by_date = analytics.get_expense_by_date(df)
            fig_trend = create_expense_trend_chart(expense_by_date)
            st.plotly_chart(fig_trend, use_container_width=True)
        with chart_col2:
            expense_by_cat = analytics.get_expense_by_category(df)
            fig_pie = create_category_pie_chart(expense_by_cat)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # ── 거래 테이블 ──
        display_df = pd.DataFrame(transactions)
        type_map = {"income": "🟢 수입", "expense": "🔴 지출"}
        display_df["유형"] = display_df["type"].map(type_map)
        display_df["금액표시"] = display_df["amount"].apply(lambda x: f"{x:,.0f}원")

        show_df = display_df[
            ["id", "date", "유형", "금액표시", "category", "payment_method", "memo"]
        ].copy()
        show_df.columns = ["ID", "날짜", "유형", "금액", "카테고리", "결제수단", "메모"]
        st.dataframe(show_df, use_container_width=True, hide_index=True, height=400)

        # ── 관리자 삭제 기능 ──
        st.markdown("---")
        st.subheader("🗑️ 거래 삭제 (관리자)")

        tx_ids = [tx["id"] for tx in transactions]

        def _fmt_admin_tx(x):
            for t in transactions:
                if t["id"] == x:
                    return "ID {} | {} | {} | {} | {}".format(
                        x,
                        t["date"],
                        type_to_korean(t["type"]),
                        format_currency(t["amount"]),
                        t["category"],
                    )
            return f"ID {x}"

        del_id = st.selectbox(
            "삭제할 거래 선택", options=tx_ids, format_func=_fmt_admin_tx, key="admin_del_sel"
        )

        confirm = st.checkbox("삭제를 확인합니다", key="admin_del_confirm")
        if st.button("🗑️ 삭제 실행", type="secondary", use_container_width=True, disabled=not confirm):
            db.admin_delete_transaction(del_id)
            st.success(f"✅ ID {del_id} 거래가 삭제되었습니다.")
            st.rerun()
