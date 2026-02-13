"""
ui_components.py - 공통 UI 컴포넌트 모듈
========================================
여러 페이지에서 반복적으로 사용하는 UI 요소들을 모아놓았습니다.
- 사이드바 필터
- 요약 카드
- 포맷 함수 등

[초보자 안내]
이렇게 공통 함수를 분리하면, 여러 페이지에서 동일한 코드를 
중복 작성하지 않고 재사용할 수 있습니다.
"""

import streamlit as st
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ============================================================
# 날짜/금액 포맷 함수
# ============================================================

def format_currency(amount):
    """금액을 한국 원화 형식으로 변환합니다. (예: 1,234,500원)"""
    if amount >= 0:
        return f"{amount:,.0f}원"
    else:
        return f"-{abs(amount):,.0f}원"


def format_currency_color(amount):
    """금액에 따라 색상을 입힌 HTML을 반환합니다."""
    if amount > 0:
        return f'<span style="color: #2ecc71">+{amount:,.0f}원</span>'
    elif amount < 0:
        return f'<span style="color: #e74c3c">{amount:,.0f}원</span>'
    else:
        return f'<span style="color: #95a5a6">0원</span>'


def type_to_korean(tx_type):
    """영문 타입을 한글로 변환합니다."""
    return {"income": "수입", "expense": "지출"}.get(tx_type, tx_type)


def type_to_english(tx_type_kr):
    """한글 타입을 영문으로 변환합니다."""
    return {"수입": "income", "지출": "expense"}.get(tx_type_kr, tx_type_kr)


# ============================================================
# 날짜 범위 선택 (사이드바)
# ============================================================

def date_range_selector(key_prefix=""):
    """
    사이드바에 기간 선택 UI를 표시합니다.
    
    Returns:
        tuple: (start_date, end_date) - date 객체
    """
    today = date.today()
    first_of_month = today.replace(day=1)
    
    period_options = [
        "이번 달",
        "지난 달",
        "최근 3개월",
        "최근 6개월",
        "올해",
        "사용자 지정"
    ]
    
    selected = st.sidebar.selectbox(
        "📅 기간 선택",
        period_options,
        key=f"{key_prefix}_period"
    )
    
    if selected == "이번 달":
        start = first_of_month
        end = today
    elif selected == "지난 달":
        last_month_end = first_of_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = last_month_end
    elif selected == "최근 3개월":
        start = today - timedelta(days=90)
        end = today
    elif selected == "최근 6개월":
        start = today - timedelta(days=180)
        end = today
    elif selected == "올해":
        start = date(today.year, 1, 1)
        end = today
    else:  # 사용자 지정
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start = st.date_input("시작", first_of_month - timedelta(days=30),
                                  key=f"{key_prefix}_start")
        with col2:
            end = st.date_input("종료", today, key=f"{key_prefix}_end")
    
    return start, end


# ============================================================
# 요약 카드 표시
# ============================================================

def display_summary_cards(summary):
    """
    4개의 요약 지표를 카드 형태로 표시합니다.
    
    Args:
        summary (dict): analytics.get_summary() 결과
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 총 수입",
            value=format_currency(summary["total_income"]),
        )
    with col2:
        st.metric(
            label="💸 총 지출",
            value=format_currency(summary["total_expense"]),
        )
    with col3:
        net = summary["net"]
        st.metric(
            label="📊 순수익",
            value=format_currency(net),
            delta=f"{'흑자' if net >= 0 else '적자'}",
            delta_color="normal" if net >= 0 else "inverse"
        )
    with col4:
        st.metric(
            label="📅 일평균 지출",
            value=format_currency(summary["daily_avg_expense"]),
        )


# ============================================================
# Plotly 차트 생성 함수들
# ============================================================

def create_expense_trend_chart(df_by_date):
    """날짜별 지출 추이 라인 차트를 생성합니다."""
    if df_by_date.empty:
        return _empty_chart("지출 추이 데이터가 없습니다")
    
    fig = px.line(
        df_by_date,
        x="date",
        y="amount",
        title="📈 날짜별 지출 추이",
        labels={"date": "날짜", "amount": "금액(원)"},
        markers=True
    )
    fig.update_layout(
        hovermode="x unified",
        yaxis_tickformat=",",
        template="plotly_white",
        height=400
    )
    fig.update_traces(
        line=dict(color="#e74c3c", width=2),
        marker=dict(size=6)
    )
    return fig


def create_category_pie_chart(df_by_category):
    """카테고리별 지출 비중 도넛 차트를 생성합니다."""
    if df_by_category.empty:
        return _empty_chart("카테고리별 데이터가 없습니다")
    
    fig = px.pie(
        df_by_category,
        values="amount",
        names="category",
        title="🍩 카테고리별 지출 비중",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=400)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig


def create_category_bar_chart(df_by_category):
    """카테고리별 지출 금액 바 차트를 생성합니다."""
    if df_by_category.empty:
        return _empty_chart("카테고리별 데이터가 없습니다")
    
    fig = px.bar(
        df_by_category,
        x="category",
        y="amount",
        title="📊 카테고리별 지출 금액",
        labels={"category": "카테고리", "amount": "금액(원)"},
        color="amount",
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        yaxis_tickformat=",",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    return fig


def create_payment_bar_chart(df_by_payment):
    """결제수단별 지출 바 차트를 생성합니다."""
    if df_by_payment.empty:
        return _empty_chart("결제수단별 데이터가 없습니다")
    
    fig = px.bar(
        df_by_payment,
        x="payment_method",
        y="amount",
        title="💳 결제수단별 지출",
        labels={"payment_method": "결제수단", "amount": "금액(원)"},
        color="payment_method",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        yaxis_tickformat=",",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    return fig


def create_dayofweek_chart(df_by_dow):
    """요일별 평균 지출 차트를 생성합니다."""
    if df_by_dow.empty:
        return _empty_chart("요일별 데이터가 없습니다")
    
    fig = px.bar(
        df_by_dow,
        x="day_korean",
        y="amount",
        title="📅 요일별 평균 지출",
        labels={"day_korean": "요일", "amount": "평균 금액(원)"},
        color="amount",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        yaxis_tickformat=",",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    return fig


def create_monthly_comparison_chart(df_monthly):
    """월별 수입/지출 비교 차트를 생성합니다."""
    if df_monthly.empty:
        return _empty_chart("월별 데이터가 없습니다")
    
    type_map = {"income": "수입", "expense": "지출"}
    df_monthly = df_monthly.copy()
    df_monthly["type_kr"] = df_monthly["type"].map(type_map)
    
    color_map = {"수입": "#2ecc71", "지출": "#e74c3c"}
    
    fig = px.bar(
        df_monthly,
        x="year_month",
        y="amount",
        color="type_kr",
        barmode="group",
        title="📊 월별 수입/지출 비교",
        labels={"year_month": "월", "amount": "금액(원)", "type_kr": "유형"},
        color_discrete_map=color_map
    )
    fig.update_layout(
        yaxis_tickformat=",",
        template="plotly_white",
        height=400
    )
    return fig


def _empty_chart(message):
    """데이터가 없을 때 표시할 빈 차트를 생성합니다."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        template="plotly_white",
        height=300,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig


# ============================================================
# 인사이트 표시
# ============================================================

def display_insights(insights):
    """인사이트 목록을 Streamlit으로 표시합니다."""
    if not insights:
        st.info("분석할 데이터가 부족합니다.")
        return
    
    for insight in insights:
        icon = insight.get("icon", "ℹ️")
        msg = insight["message"]
        itype = insight.get("type", "info")
        
        if itype == "warning":
            st.warning(f"{icon} {msg}")
        elif itype == "success":
            st.success(f"{icon} {msg}")
        elif itype == "error":
            st.error(f"{icon} {msg}")
        else:
            st.info(f"{icon} {msg}")


# ============================================================
# 빈 상태 (Empty State) 표시
# ============================================================

def show_empty_state(message="아직 데이터가 없습니다", 
                     sub_message="'입력' 페이지에서 거래를 추가하거나, 설정에서 샘플 데이터를 생성해보세요!"):
    """데이터가 없을 때 친절한 안내 메시지를 표시합니다."""
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 60px 20px; color: #888;">
            <h2>📝 {message}</h2>
            <p style="font-size: 1.1em;">{sub_message}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
