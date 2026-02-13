"""
4_⚙️_설정.py - 설정 페이지
===========================
카테고리 관리, 예산 설정, 데이터 관리(초기화/내보내기),
샘플 데이터 생성 기능을 제공합니다.
"""

import streamlit as st
from datetime import date
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import auth
from ui_components import format_currency

# ============================================================
# 페이지 설정
# ============================================================
# 인증 확인
user_id = auth.check_auth()

st.title("⚙️ 설정")
st.caption("카테고리, 예산, 데이터 관리를 할 수 있습니다.")

# 탭으로 설정 카테고리 구분
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏷️ 카테고리 관리", "💰 예산 설정", "📦 데이터 관리", "🎲 샘플 데이터", "🔒 비밀번호 변경"
])

# ============================================================
# 탭1: 카테고리 관리
# ============================================================
with tab1:
    st.subheader("🏷️ 카테고리 관리")
    st.caption("수입/지출 카테고리를 추가하거나 삭제할 수 있습니다.")
    
    col1, col2 = st.columns(2)
    
    # ── 지출 카테고리 ──
    with col1:
        st.markdown("#### 💸 지출 카테고리")
        expense_cats = db.get_categories(user_id, "expense")
        
        for cat in expense_cats:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"• {cat}")
            if c2.button("🗑️", key=f"del_exp_{cat}", help=f"'{cat}' 삭제"):
                db.delete_category(user_id, "expense", cat)
                st.rerun()
        
        st.markdown("---")
        with st.form("add_expense_cat"):
            new_cat = st.text_input("새 지출 카테고리명", key="new_exp_cat")
            if st.form_submit_button("➕ 추가"):
                if new_cat.strip():
                    if db.add_category(user_id, "expense", new_cat.strip()):
                        st.success(f"✅ '{new_cat}' 추가 완료!")
                        st.rerun()
                    else:
                        st.warning("⚠️ 이미 존재하는 카테고리입니다.")
                else:
                    st.warning("카테고리명을 입력해주세요.")
    
    # ── 수입 카테고리 ──
    with col2:
        st.markdown("#### 💰 수입 카테고리")
        income_cats = db.get_categories(user_id, "income")
        
        for cat in income_cats:
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"• {cat}")
            if c2.button("🗑️", key=f"del_inc_{cat}", help=f"'{cat}' 삭제"):
                db.delete_category(user_id, "income", cat)
                st.rerun()
        
        st.markdown("---")
        with st.form("add_income_cat"):
            new_cat = st.text_input("새 수입 카테고리명", key="new_inc_cat")
            if st.form_submit_button("➕ 추가"):
                if new_cat.strip():
                    if db.add_category(user_id, "income", new_cat.strip()):
                        st.success(f"✅ '{new_cat}' 추가 완료!")
                        st.rerun()
                    else:
                        st.warning("⚠️ 이미 존재하는 카테고리입니다.")
                else:
                    st.warning("카테고리명을 입력해주세요.")

# ============================================================
# 탭2: 예산 설정
# ============================================================
with tab2:
    st.subheader("💰 예산 설정")
    st.caption("월별 전체 예산 또는 카테고리별 예산을 설정할 수 있습니다.")
    
    # 예산 추가 폼
    with st.form("budget_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_month = st.text_input(
                "📅 예산 월 (YYYY-MM)",
                value=date.today().strftime("%Y-%m"),
                help="예: 2026-02"
            )
        
        with col2:
            expense_cats = db.get_categories(user_id, "expense")
            budget_cat_options = ["전체 (총 예산)"] + expense_cats
            budget_cat = st.selectbox("🏷️ 카테고리", budget_cat_options)
        
        with col3:
            budget_amount = st.number_input(
                "💵 예산 금액(원)",
                min_value=0,
                value=500000,
                step=10000
            )
        
        if st.form_submit_button("💾 예산 저장", type="primary", use_container_width=True):
            cat_value = "" if budget_cat == "전체 (총 예산)" else budget_cat
            
            if budget_amount <= 0:
                st.error("예산 금액은 0보다 커야 합니다.")
            else:
                db.set_budget(user_id, budget_month, cat_value, budget_amount)
                st.success(f"✅ {budget_month} {'전체' if not cat_value else cat_value} "
                           f"예산 {format_currency(budget_amount)} 저장 완료!")
                st.rerun()
    
    st.markdown("---")
    
    # 현재 예산 목록
    st.markdown("#### 📋 설정된 예산 목록")
    budgets = db.get_budgets(user_id)
    
    if budgets:
        import pandas as pd
        budget_df = pd.DataFrame(budgets)
        budget_df["카테고리"] = budget_df["category"].apply(lambda x: x if x else "전체")
        budget_df["예산"] = budget_df["budget_amount"].apply(lambda x: f"{x:,.0f}원")
        
        display_budget = budget_df[["id", "month", "카테고리", "예산"]].copy()
        display_budget.columns = ["ID", "월", "카테고리", "예산"]
        st.dataframe(display_budget, use_container_width=True, hide_index=True)
        
        # 예산 삭제
        del_id = st.selectbox("삭제할 예산 ID", [b["id"] for b in budgets])
        if st.button("🗑️ 선택한 예산 삭제"):
            db.delete_budget(user_id, del_id)
            st.success("✅ 예산 삭제 완료!")
            st.rerun()
    else:
        st.info("📝 아직 설정된 예산이 없습니다.")

# ============================================================
# 탭3: 데이터 관리
# ============================================================
with tab3:
    st.subheader("📦 데이터 관리")
    
    col1, col2 = st.columns(2)
    
    # ── CSV 내보내기 ──
    with col1:
        st.markdown("#### 📤 CSV 내보내기")
        st.caption("저장된 거래 내역을 CSV 파일로 다운로드합니다.")
        
        csv_data = db.export_transactions_csv(user_id)
        if csv_data:
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data.encode("utf-8-sig"),  # 한글 깨짐 방지
                file_name=f"가계부_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("내보낼 데이터가 없습니다.")
    
    # ── 데이터 초기화 ──
    with col2:
        st.markdown("#### 🗑️ 데이터 초기화")
        st.caption("⚠️ 이 작업은 되돌릴 수 없습니다!")
        
        st.warning("모든 거래 데이터가 영구적으로 삭제됩니다.")
        
        confirm_text = st.text_input(
            "초기화하려면 '삭제합니다'를 입력하세요",
            key="reset_confirm"
        )
        
        if st.button("🗑️ 거래 데이터만 삭제", type="secondary", use_container_width=True):
            if confirm_text == "삭제합니다":
                db.clear_all_data(user_id)
                st.success("✅ 모든 거래 데이터가 삭제되었습니다.")
                st.rerun()
            else:
                st.error("'삭제합니다'를 정확히 입력해주세요.")
        
        if st.button("💣 전체 초기화 (카테고리/예산 포함)", type="secondary", use_container_width=True):
            if confirm_text == "삭제합니다":
                db.clear_everything(user_id)
                st.success("✅ 모든 데이터가 초기화되었습니다. 기본 카테고리가 다시 생성되었습니다.")
                st.rerun()
            else:
                st.error("'삭제합니다'를 정확히 입력해주세요.")

# ============================================================
# 탭4: 샘플 데이터 생성
# ============================================================
with tab4:
    st.subheader("🎲 샘플 데이터 생성")
    st.caption("앱 테스트를 위한 데모 데이터를 자동으로 생성합니다.")
    
    st.info("""
    💡 **샘플 데이터란?**
    앱의 기능을 테스트해보기 위한 가짜 데이터입니다.
    실제 사용 시에는 직접 입력하면 됩니다.
    
    생성되는 데이터:
    - 최근 수 개월간의 수입/지출 내역
    - 다양한 카테고리와 결제수단
    - 매월 급여 수입 포함
    """)
    
    num_months = st.slider("생성할 기간 (개월)", 1, 6, 3)
    
    if st.button("🎲 샘플 데이터 생성", type="primary", use_container_width=True):
        with st.spinner("데이터를 생성하는 중..."):
            count = db.generate_sample_data(user_id, num_months=num_months)
        st.success(f"✅ {count}건의 샘플 데이터가 생성되었습니다!")
        st.balloons()
        st.info("🏠 대시보드로 이동하면 차트와 분석을 확인할 수 있습니다.")

# ============================================================
# 탭5: 비밀번호 변경
# ============================================================
with tab5:
    st.subheader("🔒 비밀번호 변경")
    st.caption("현재 비밀번호를 확인한 후 새 비밀번호로 변경합니다.")

    with st.form("change_pw_form"):
        current_pw = st.text_input("현재 비밀번호", type="password", key="cur_pw")
        new_pw = st.text_input("새 비밀번호", type="password", key="new_pw")
        confirm_pw = st.text_input("새 비밀번호 확인", type="password", key="confirm_pw")

        if st.form_submit_button("🔒 비밀번호 변경", type="primary", use_container_width=True):
            if not current_pw or not new_pw:
                st.error("모든 필드를 입력해주세요.")
            elif not db.verify_user_password(user_id, current_pw):
                st.error("❌ 현재 비밀번호가 올바르지 않습니다.")
            elif len(new_pw) < 4:
                st.error("새 비밀번호는 4자 이상이어야 합니다.")
            elif new_pw != confirm_pw:
                st.error("새 비밀번호가 일치하지 않습니다.")
            else:
                db.change_password(user_id, new_pw)
                st.success("✅ 비밀번호가 변경되었습니다!")
