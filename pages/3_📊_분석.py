"""
3_📊_분석.py - 소비패턴 분석/리포트 페이지
==========================================
기간별 지출 분석, 트렌드, 예산 대비, 반복지출 탐지 등
상세 분석 기능을 제공합니다.

[차트 목록]
- 날짜별 지출 추이 (라인)
- 카테고리별 지출 비중 (도넛/파이)
- 카테고리별 지출 금액 (바)
- 결제수단별 지출 (바)
- 요일별 평균 지출 (바)
- 월별 수입/지출 비교 (바)
"""

import streamlit as st
from datetime import date, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
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
    create_payment_bar_chart,
    create_dayofweek_chart,
    create_monthly_comparison_chart,
)

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(page_title="📊 분석", page_icon="📊", layout="wide")
db.init_db()

st.title("📊 소비패턴 분석")
st.caption("입력된 데이터를 기반으로 소비패턴을 자동 분석합니다.")

# ============================================================
# 사이드바 - 기간 선택
# ============================================================
st.sidebar.subheader("📅 분석 기간")
start_date, end_date = date_range_selector(key_prefix="analysis")

# ============================================================
# 데이터 조회
# ============================================================
transactions = db.get_transactions(
    start_date=str(start_date),
    end_date=str(end_date)
)
df = analytics.transactions_to_dataframe(transactions)

if df.empty:
    show_empty_state(
        "분석할 데이터가 없습니다",
        "선택한 기간에 거래 내역이 없습니다. '입력' 페이지에서 거래를 추가해보세요."
    )
    st.stop()

# ============================================================
# 1) 요약 카드
# ============================================================
st.subheader("📋 기간 요약")
summary = analytics.get_summary(df)
display_summary_cards(summary)

# 상위 카테고리 상세
if summary["top_categories"]:
    st.markdown("**지출 상위 카테고리:**")
    for i, (cat, amt) in enumerate(summary["top_categories"], 1):
        pct = (amt / summary["total_expense"] * 100) if summary["total_expense"] > 0 else 0
        st.markdown(f"  {i}. **{cat}** - {format_currency(amt)} ({pct:.1f}%)")

st.markdown("---")

# ============================================================
# 2) 차트 섹션
# ============================================================
st.subheader("📈 차트 분석")

# 탭으로 차트 구분
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 지출 추이", "🍩 카테고리 비중", "📊 카테고리 금액",
    "💳 결제수단별", "📅 요일별", "📊 월별 비교"
])

with tab1:
    expense_by_date = analytics.get_expense_by_date(df)
    fig = create_expense_trend_chart(expense_by_date)
    st.plotly_chart(fig, use_container_width=True)
    
    if not expense_by_date.empty:
        st.caption(f"📌 최고 지출일: {expense_by_date.loc[expense_by_date['amount'].idxmax(), 'date'].strftime('%Y-%m-%d')} "
                   f"({format_currency(expense_by_date['amount'].max())})")

with tab2:
    expense_by_cat = analytics.get_expense_by_category(df)
    fig = create_category_pie_chart(expense_by_cat)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    expense_by_cat = analytics.get_expense_by_category(df)
    fig = create_category_bar_chart(expense_by_cat)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    expense_by_payment = analytics.get_expense_by_payment(df)
    fig = create_payment_bar_chart(expense_by_payment)
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    expense_by_dow = analytics.get_expense_by_dayofweek(df)
    fig = create_dayofweek_chart(expense_by_dow)
    st.plotly_chart(fig, use_container_width=True)
    
    if not expense_by_dow.empty:
        max_day = expense_by_dow.loc[expense_by_dow["amount"].idxmax()]
        min_day = expense_by_dow.loc[expense_by_dow["amount"].idxmin()]
        st.caption(f"📌 가장 많이 쓰는 요일: {max_day['day_korean']}요일 | "
                   f"가장 적게 쓰는 요일: {min_day['day_korean']}요일")

with tab6:
    monthly_data = analytics.get_income_expense_by_month(df)
    fig = create_monthly_comparison_chart(monthly_data)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# 3) 예산 대비 현황
# ============================================================
st.subheader("💰 예산 대비 현황")

current_month = date.today().strftime("%Y-%m")
budgets = db.get_budgets(month=current_month)

if budgets:
    expense_df = df[df["type"] == "expense"]
    current_expenses = expense_df[expense_df["year_month"] == current_month] if not expense_df.empty else expense_df
    
    for budget in budgets:
        cat = budget["category"]
        budget_amt = budget["budget_amount"]
        
        if cat:
            spent = current_expenses[current_expenses["category"] == cat]["amount"].sum() if not current_expenses.empty else 0
            label = f"🏷️ {cat}"
        else:
            spent = current_expenses["amount"].sum() if not current_expenses.empty else 0
            label = "📊 전체 예산"
        
        usage_pct = (spent / budget_amt * 100) if budget_amt > 0 else 0
        remaining = budget_amt - spent
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{label}**: {format_currency(spent)} / {format_currency(budget_amt)}")
            # 프로그레스 바 (100% 초과 시 100%로 표시)
            st.progress(min(usage_pct / 100, 1.0))
        with col2:
            if usage_pct >= 100:
                st.error(f"🚨 {usage_pct:.0f}% 초과!")
            elif usage_pct >= 80:
                st.warning(f"⚠️ {usage_pct:.0f}%")
            else:
                st.success(f"✅ {usage_pct:.0f}%")
            st.caption(f"잔여: {format_currency(remaining)}")
else:
    st.info("💡 아직 설정된 예산이 없습니다. '설정' 페이지에서 예산을 설정해보세요.")

st.markdown("---")

# ============================================================
# 4) 인사이트
# ============================================================
st.subheader("💡 AI 인사이트 (규칙 기반)")
st.caption("머신러닝/AI 없이 규칙 기반으로 데이터를 분석한 결과입니다.")

insights = analytics.generate_insights(df, budgets)
display_insights(insights)
