"""
1_📝_입력.py - 거래 입력 페이지
================================
수입/지출 내역을 직접 입력하고 SQLite DB에 저장합니다.
엑셀 업로드 없이 웹 폼으로만 입력합니다.

[입력 필드]
- 날짜, 타입(수입/지출), 금액, 카테고리, 결제수단, 메모
"""

import streamlit as st
from datetime import date
import sys
import os

# 상위 디렉토리의 모듈을 import하기 위한 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth
from ui_components import type_to_english

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(page_title="📝 거래 입력", page_icon="📝", layout="wide")

# DB 초기화
db.init_db()

# 인증 확인
user_id = auth.check_auth()

st.title("📝 거래 입력")
auth.show_user_info()
st.caption("수입 또는 지출 내역을 입력하세요. 모든 데이터는 로컬 DB에 저장됩니다.")

st.markdown("---")

# ============================================================
# 입력 폼
# ============================================================
with st.form("transaction_form", clear_on_submit=True):
    st.subheader("💳 새 거래 등록")
    
    # 2열 레이아웃으로 입력 필드 배치
    col1, col2 = st.columns(2)
    
    with col1:
        # 날짜 입력
        tx_date = st.date_input(
            "📅 날짜 *",
            value=date.today(),
            help="거래가 발생한 날짜를 선택하세요"
        )
        
        # 타입 선택 (수입/지출)
        tx_type_kr = st.radio(
            "📌 유형 *",
            options=["지출", "수입"],
            horizontal=True,
            help="수입인지 지출인지 선택하세요"
        )
        
        # 금액 입력
        amount = st.number_input(
            "💵 금액(원) *",
            min_value=0,
            max_value=100000000,  # 1억원 한도
            value=0,
            step=1000,
            help="금액을 입력하세요 (0보다 큰 값)"
        )
    
    with col2:
        # 카테고리 선택 (수입/지출에 따라 다른 목록)
        tx_type_en = type_to_english(tx_type_kr)
        categories = db.get_categories(user_id, tx_type_en)
        
        if not categories:
            categories = ["기타"]
        
        category = st.selectbox(
            "🏷️ 카테고리 *",
            options=categories,
            help="거래 카테고리를 선택하세요"
        )
        
        # 결제수단 선택
        payment_method = st.selectbox(
            "💳 결제수단",
            options=db.DEFAULT_PAYMENT_METHODS,
            help="결제 방법을 선택하세요"
        )
        
        # 메모 입력
        memo = st.text_input(
            "📝 메모 (선택)",
            placeholder="예: 점심식사, 월급 등",
            help="간단한 메모를 남겨주세요 (선택사항)"
        )
    
    st.markdown("---")
    
    # 저장 버튼
    submitted = st.form_submit_button(
        "✅ 저장",
        use_container_width=True,
        type="primary"
    )

# ============================================================
# 저장 처리
# ============================================================
if submitted:
    # 입력 검증
    errors = []
    
    if amount <= 0:
        errors.append("💡 금액은 0보다 큰 값을 입력해주세요.")
    
    if not category:
        errors.append("💡 카테고리를 선택해주세요.")
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        # DB에 저장
        try:
            new_id = db.add_transaction(
                user_id,
                date_str=str(tx_date),
                tx_type=tx_type_en,
                amount=float(amount),
                category=category,
                payment_method=payment_method,
                memo=memo
            )
            
            # 성공 메시지
            st.success(f"✅ 거래가 저장되었습니다! (ID: {new_id})")
            
            # 저장된 내용 요약 표시
            st.markdown(f"""
            | 항목 | 내용 |
            |------|------|
            | 날짜 | {tx_date} |
            | 유형 | {tx_type_kr} |
            | 금액 | {amount:,.0f}원 |
            | 카테고리 | {category} |
            | 결제수단 | {payment_method} |
            | 메모 | {memo if memo else '-'} |
            """)
            
        except Exception as e:
            st.error(f"❌ 저장 중 오류가 발생했습니다: {str(e)}")

# ============================================================
# 최근 입력 내역 미리보기
# ============================================================
st.markdown("---")
st.subheader("🕐 최근 입력 내역")

recent = db.get_transactions(user_id, sort_by="created_at", sort_order="DESC")
if recent:
    # 최근 5건만 표시
    import pandas as pd
    recent_5 = recent[:5]
    df = pd.DataFrame(recent_5)
    
    # 컬럼 한글화
    type_map = {"income": "수입", "expense": "지출"}
    df["유형"] = df["type"].map(type_map)
    df["금액"] = df["amount"].apply(lambda x: f"{x:,.0f}원")
    
    display_df = df[["date", "유형", "금액", "category", "payment_method", "memo"]].copy()
    display_df.columns = ["날짜", "유형", "금액", "카테고리", "결제수단", "메모"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("📝 아직 입력된 거래가 없습니다. 위 폼에서 첫 거래를 입력해보세요!")
