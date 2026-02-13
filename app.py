"""
app.py - 가계부 분석기 메인 앱 (대시보드 / Home)
=================================================
이 파일은 Streamlit 앱의 진입점(Entry Point)입니다.
실행 방법: streamlit run app.py

[화면 구성]
- 이번 달 요약 (총 수입/지출/순수익/일평균지출)
- 지출 상위 카테고리
- 주요 차트 (지출 추이, 카테고리 비중)
- 인사이트 (규칙 기반 자동 분석)

[초보자 안내]
Streamlit은 Python 스크립트를 위에서 아래로 실행하면서
자동으로 웹 UI를 생성합니다. st.xxx() 함수가 화면에 요소를 그립니다.
"""

import streamlit as st
from datetime import date, timedelta

# 로컬 모듈 임포트
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

# ============================================================
# 앱 기본 설정
# ============================================================
st.set_page_config(
    page_title="💰 가계부 분석기",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화 (테이블이 없으면 생성)
db.init_db()

# 인증 확인 (로그인하지 않으면 로그인 화면 표시 후 중단)
user_id = auth.check_auth()

# ============================================================
# 사이드바 - 공통 필터
# ============================================================
st.sidebar.title("💰 가계부 분석기")
auth.show_user_info()

# 기간 선택
start_date, end_date = date_range_selector(key_prefix="home")

st.sidebar.markdown("---")
st.sidebar.caption("📌 사이드바 메뉴에서 각 페이지로 이동하세요")

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
    
    # 빠른 시작 안내
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
    st.stop()  # 데이터가 없으면 여기서 중단

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

# 2열 레이아웃
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 날짜별 지출 추이
    expense_by_date = analytics.get_expense_by_date(df)
    fig_trend = create_expense_trend_chart(expense_by_date)
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    # 카테고리별 지출 비중 (도넛)
    expense_by_cat = analytics.get_expense_by_category(df)
    fig_pie = create_category_pie_chart(expense_by_cat)
    st.plotly_chart(fig_pie, use_container_width=True)

# 월별 수입/지출 비교 (전체 너비)
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
st.caption("💰 가계부 분석기 v1.0 | Made with Streamlit")
