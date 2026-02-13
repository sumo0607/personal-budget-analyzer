"""
0_🏠_대시보드.py - 대시보드 (홈) 페이지
=========================================
이번 달 요약, 지출 상위 카테고리, 주요 차트, 인사이트를 표시합니다.
"""

import streamlit as st
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth
import analytics
from ui_components import (
    format_currency,
    date_range_selector,
    display_summary_cards,
    display_insights,
    show_empty_state,
    create_expense_trend_chart,
    create_category_pie_chart,
    create_category_bar_chart,
    create_monthly_comparison_chart,
)

user_id = auth.check_auth()

# ============================================================
# 사이드바 - 기간 선택
# ============================================================
st.sidebar.subheader("📅 기간 선택")
start_date, end_date = date_range_selector(key_prefix="home")

# ============================================================
# 메인 콘텐츠 - 대시보드
# ============================================================
st.title("🏠 대시보드")
st.caption(f"📅 조회 기간: {start_date} ~ {end_date}")

# 데이터 조회
transactions = db.get_transactions(
    user_id,
    start_date=str(start_date),
    end_date=str(end_date)
)
df = analytics.transactions_to_dataframe(transactions)

# ── 데이터가 없는 경우 ──
if df.empty:
    show_empty_state()

    st.markdown("### 🚀 빠른 시작")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **직접 입력하기**
        1. 왼쪽 사이드바에서 **📝 입력** 페이지로 이동
        2. 거래 정보 입력 후 저장
        """)
    with col2:
        st.markdown("""
        **샘플 데이터 생성하기**
        1. 왼쪽 사이드바에서 **⚙️ 설정** 페이지로 이동
        2. '샘플 데이터 생성' 버튼 클릭
        """)
    st.stop()

# ── 요약 카드 ──
summary = analytics.get_summary(df)
display_summary_cards(summary)

st.markdown("---")

# ── 지출 상위 카테고리 ──
if summary["top_categories"]:
    st.subheader("🏆 지출 상위 카테고리")
    cols = st.columns(min(len(summary["top_categories"]), 3))
    medals = ["🥇", "🥈", "🥉"]
    for i, (cat, amt) in enumerate(summary["top_categories"]):
        with cols[i]:
            pct = (amt / summary["total_expense"] * 100) if summary["total_expense"] > 0 else 0
            st.metric(
                label=f"{medals[i]} {cat}",
                value=format_currency(amt),
                delta=f"{pct:.1f}%",
                delta_color="off"
            )

st.markdown("---")

# ── 주요 차트 ──
st.subheader("📊 주요 차트")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    expense_by_date = analytics.get_expense_by_date(df)
    fig_trend = create_expense_trend_chart(expense_by_date)
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    expense_by_cat = analytics.get_expense_by_category(df)
    fig_pie = create_category_pie_chart(expense_by_cat)
    st.plotly_chart(fig_pie, use_container_width=True)

monthly_data = analytics.get_income_expense_by_month(df)
if not monthly_data.empty:
    fig_monthly = create_monthly_comparison_chart(monthly_data)
    st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")

# ── 인사이트 ──
st.subheader("💡 인사이트")
budgets = db.get_budgets(user_id, month=date.today().strftime("%Y-%m"))
insights = analytics.generate_insights(df, budgets)
display_insights(insights)

# ── 푸터 ──
st.markdown("---")
st.caption("💰 가계부 분석기 v2.0 | Made with Streamlit")
