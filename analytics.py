"""
analytics.py - 데이터 분석 및 인사이트 생성 모듈
================================================
이 파일은 거래 데이터를 분석하여 요약 지표, 인사이트 문장, 
이상치 탐지, 반복 지출 탐지 등의 기능을 제공합니다.

[초보자 안내]
- pandas DataFrame을 사용하여 데이터를 집계합니다.
- LLM(AI)을 사용하지 않고, 규칙 기반으로 인사이트를 생성합니다.
"""

import pandas as pd
from datetime import datetime, date, timedelta
from collections import defaultdict


def transactions_to_dataframe(transactions):
    """
    거래 딕셔너리 리스트를 pandas DataFrame으로 변환합니다.
    
    Args:
        transactions (list[dict]): db.get_transactions() 결과
    
    Returns:
        pd.DataFrame: 변환된 데이터프레임
    """
    if not transactions:
        return pd.DataFrame(columns=[
            "id", "date", "type", "amount", "category",
            "payment_method", "memo", "created_at"
        ])
    
    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["day_of_week"] = df["date"].dt.dayofweek  # 0=월, 6=일
    df["day_name"] = df["date"].dt.day_name()
    return df


def get_summary(df):
    """
    기간 내 요약 지표를 계산합니다.
    
    Returns:
        dict: {
            total_income: 총 수입,
            total_expense: 총 지출,
            net: 순수익,
            daily_avg_expense: 일평균 지출,
            top_categories: 지출 상위 3개 카테고리 [(카테고리, 금액), ...],
            tx_count: 총 거래 건수,
            expense_count: 지출 건수,
            income_count: 수입 건수
        }
    """
    if df.empty:
        return {
            "total_income": 0,
            "total_expense": 0,
            "net": 0,
            "daily_avg_expense": 0,
            "top_categories": [],
            "tx_count": 0,
            "expense_count": 0,
            "income_count": 0,
        }
    
    income_df = df[df["type"] == "income"]
    expense_df = df[df["type"] == "expense"]
    
    total_income = income_df["amount"].sum() if not income_df.empty else 0
    total_expense = expense_df["amount"].sum() if not expense_df.empty else 0
    
    # 일평균 지출 계산 (기간의 날짜 수 기준)
    if not expense_df.empty:
        date_range = (df["date"].max() - df["date"].min()).days + 1
        date_range = max(date_range, 1)  # 최소 1일
        daily_avg = total_expense / date_range
    else:
        daily_avg = 0
    
    # 지출 상위 카테고리
    if not expense_df.empty:
        top_cats = (
            expense_df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )
        top_categories = [(cat, amt) for cat, amt in top_cats.items()]
    else:
        top_categories = []
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net": total_income - total_expense,
        "daily_avg_expense": daily_avg,
        "top_categories": top_categories,
        "tx_count": len(df),
        "expense_count": len(expense_df),
        "income_count": len(income_df),
    }


def get_expense_by_category(df):
    """카테고리별 지출 합계를 반환합니다."""
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty:
        return pd.DataFrame(columns=["category", "amount"])
    
    result = (
        expense_df.groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )
    return result


def get_expense_by_date(df):
    """날짜별 지출 합계를 반환합니다. (라인 차트용)"""
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty:
        return pd.DataFrame(columns=["date", "amount"])
    
    result = (
        expense_df.groupby("date")["amount"]
        .sum()
        .reset_index()
        .sort_values("date")
    )
    return result


def get_income_expense_by_month(df):
    """월별 수입/지출 합계를 반환합니다."""
    if df.empty:
        return pd.DataFrame(columns=["year_month", "type", "amount"])
    
    result = (
        df.groupby(["year_month", "type"])["amount"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )
    return result


def get_expense_by_payment(df):
    """결제수단별 지출 합계를 반환합니다."""
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty:
        return pd.DataFrame(columns=["payment_method", "amount"])
    
    result = (
        expense_df.groupby("payment_method")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
    )
    return result


def get_expense_by_dayofweek(df):
    """요일별 평균 지출을 반환합니다."""
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty:
        return pd.DataFrame(columns=["day_name", "amount"])
    
    # 요일별 합계를 구하고, 주(week) 수로 나눠 평균
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_korean = {"Monday": "월", "Tuesday": "화", "Wednesday": "수",
                  "Thursday": "목", "Friday": "금", "Saturday": "토", "Sunday": "일"}
    
    result = (
        expense_df.groupby("day_name")["amount"]
        .mean()
        .reset_index()
    )
    result["day_korean"] = result["day_name"].map(day_korean)
    result["day_order"] = result["day_name"].apply(lambda x: day_order.index(x) if x in day_order else 7)
    result = result.sort_values("day_order")
    
    return result


# ============================================================
# 인사이트 생성 (규칙 기반 - LLM 없이)
# ============================================================

def generate_insights(df, budgets=None):
    """
    데이터를 분석하여 규칙 기반 인사이트를 생성합니다.
    
    Args:
        df: 거래 DataFrame
        budgets: 예산 목록 (db.get_budgets 결과)
    
    Returns:
        list[dict]: [{"type": "info/warning/success/error", "message": "..."}]
    """
    insights = []
    
    if df.empty:
        insights.append({
            "type": "info",
            "icon": "ℹ️",
            "message": "아직 거래 데이터가 없습니다. '입력' 페이지에서 거래를 추가해보세요!"
        })
        return insights
    
    summary = get_summary(df)
    
    # 1) 지출 상위 카테고리 안내
    if summary["top_categories"]:
        top_cat, top_amt = summary["top_categories"][0]
        pct = (top_amt / summary["total_expense"] * 100) if summary["total_expense"] > 0 else 0
        insights.append({
            "type": "info",
            "icon": "📊",
            "message": f"가장 큰 지출 카테고리는 **{top_cat}**이며, "
                       f"총 지출의 **{pct:.1f}%** ({top_amt:,.0f}원)를 차지합니다."
        })
    
    # 2) 전월 대비 지출 증감률
    insights.extend(_month_comparison_insight(df))
    
    # 3) 예산 대비 경고
    if budgets:
        insights.extend(_budget_warning_insights(df, budgets))
    
    # 4) 이상치 탐지
    insights.extend(_outlier_insights(df))
    
    # 5) 반복 지출 탐지
    insights.extend(_recurring_expense_insights(df))
    
    # 6) 수입/지출 비율
    if summary["total_income"] > 0 and summary["total_expense"] > 0:
        save_rate = (summary["net"] / summary["total_income"]) * 100
        if save_rate >= 30:
            insights.append({
                "type": "success",
                "icon": "🎉",
                "message": f"저축률이 **{save_rate:.1f}%**로 매우 좋습니다! 계속 유지하세요."
            })
        elif save_rate >= 10:
            insights.append({
                "type": "info",
                "icon": "💰",
                "message": f"저축률이 **{save_rate:.1f}%**입니다. "
                           f"목표 저축률(30%)까지 조금 더 절약해보세요."
            })
        elif save_rate < 0:
            insights.append({
                "type": "warning",
                "icon": "🚨",
                "message": f"이번 기간 지출이 수입보다 **{abs(summary['net']):,.0f}원** 더 많습니다. "
                           f"지출 점검이 필요합니다."
            })
    
    return insights


def _month_comparison_insight(df):
    """전월 대비 지출 증감률 인사이트"""
    insights = []
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty:
        return insights
    
    monthly = expense_df.groupby("year_month")["amount"].sum().sort_index()
    
    if len(monthly) >= 2:
        current_month = monthly.index[-1]
        prev_month = monthly.index[-2]
        current_amt = monthly[current_month]
        prev_amt = monthly[prev_month]
        
        if prev_amt > 0:
            change_pct = ((current_amt - prev_amt) / prev_amt) * 100
            if change_pct > 20:
                insights.append({
                    "type": "warning",
                    "icon": "📈",
                    "message": f"{current_month}월 지출이 전월 대비 **{change_pct:.1f}% 증가**했습니다. "
                               f"({prev_amt:,.0f}원 → {current_amt:,.0f}원)"
                })
            elif change_pct < -10:
                insights.append({
                    "type": "success",
                    "icon": "📉",
                    "message": f"{current_month}월 지출이 전월 대비 **{abs(change_pct):.1f}% 감소**했습니다. "
                               f"절약 노력이 효과적이네요!"
                })
            else:
                insights.append({
                    "type": "info",
                    "icon": "➡️",
                    "message": f"{current_month}월 지출은 전월과 비슷한 수준입니다. "
                               f"(변동률: {change_pct:+.1f}%)"
                })
    
    return insights


def _budget_warning_insights(df, budgets):
    """예산 대비 경고 인사이트"""
    insights = []
    expense_df = df[df["type"] == "expense"]
    if expense_df.empty or not budgets:
        return insights
    
    current_month = date.today().strftime("%Y-%m")
    current_expenses = expense_df[expense_df["year_month"] == current_month]
    
    if current_expenses.empty:
        return insights
    
    for budget in budgets:
        if budget["month"] != current_month:
            continue
        
        budget_amt = budget["budget_amount"]
        cat = budget["category"]
        
        if cat:  # 카테고리별 예산
            spent = current_expenses[current_expenses["category"] == cat]["amount"].sum()
            label = f"'{cat}' 카테고리"
        else:  # 전체 예산
            spent = current_expenses["amount"].sum()
            label = "전체"
        
        usage_pct = (spent / budget_amt * 100) if budget_amt > 0 else 0
        
        if usage_pct >= 100:
            insights.append({
                "type": "warning",
                "icon": "🚨",
                "message": f"{label} 예산을 **초과**했습니다! "
                           f"(예산: {budget_amt:,.0f}원, 지출: {spent:,.0f}원, {usage_pct:.0f}%)"
            })
        elif usage_pct >= 80:
            insights.append({
                "type": "warning",
                "icon": "⚠️",
                "message": f"{label} 예산의 **{usage_pct:.0f}%**를 사용했습니다. "
                           f"(잔여: {budget_amt - spent:,.0f}원)"
            })
    
    return insights


def _outlier_insights(df):
    """이상치(특이 지출) 탐지 인사이트"""
    insights = []
    expense_df = df[df["type"] == "expense"]
    if len(expense_df) < 5:
        return insights
    
    # 카테고리별 평균과 표준편차 계산
    for cat in expense_df["category"].unique():
        cat_df = expense_df[expense_df["category"] == cat]
        if len(cat_df) < 3:
            continue
        
        mean_amt = cat_df["amount"].mean()
        std_amt = cat_df["amount"].std()
        
        if std_amt == 0:
            continue
        
        # 평균 + 2*표준편차 초과 → 이상치
        threshold = mean_amt + 2 * std_amt
        outliers = cat_df[cat_df["amount"] > threshold]
        
        for _, row in outliers.iterrows():
            ratio = row["amount"] / mean_amt
            if ratio >= 2:
                insights.append({
                    "type": "info",
                    "icon": "🔍",
                    "message": f"**특이 지출 감지**: {row['date'].strftime('%m/%d')} '{cat}' "
                               f"{row['amount']:,.0f}원 (평균의 {ratio:.1f}배)"
                })
    
    # 최대 3개만 표시
    return insights[:3]


def _recurring_expense_insights(df):
    """
    반복 지출 탐지 인사이트
    같은 카테고리에서 비슷한 금액(±20%)이 28~32일 간격으로 반복되면 탐지합니다.
    """
    insights = []
    expense_df = df[df["type"] == "expense"].sort_values("date")
    
    if len(expense_df) < 4:
        return insights
    
    found_recurring = set()
    
    for cat in expense_df["category"].unique():
        cat_df = expense_df[expense_df["category"] == cat].sort_values("date")
        if len(cat_df) < 2:
            continue
        
        amounts = cat_df["amount"].values
        dates = cat_df["date"].values
        
        for i in range(len(cat_df) - 1):
            for j in range(i + 1, min(i + 5, len(cat_df))):
                amt_i = amounts[i]
                amt_j = amounts[j]
                
                # 금액 차이 20% 이내
                if amt_i > 0 and abs(amt_i - amt_j) / amt_i <= 0.2:
                    day_diff = (pd.Timestamp(dates[j]) - pd.Timestamp(dates[i])).days
                    
                    # 28~32일 간격 (월 단위 반복)
                    if 25 <= day_diff <= 35:
                        key = f"{cat}_{int(amt_i/1000)*1000}"
                        if key not in found_recurring:
                            found_recurring.add(key)
                            insights.append({
                                "type": "info",
                                "icon": "🔄",
                                "message": f"**반복 지출 감지**: '{cat}' 약 {amt_i:,.0f}원이 "
                                           f"매월 반복되고 있습니다."
                            })
    
    return insights[:3]
