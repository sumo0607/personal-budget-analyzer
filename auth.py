"""
auth.py - 사용자 인증 모듈
==========================
회원가입, 로그인 기능을 제공합니다.
Streamlit session_state를 사용하여 로그인 상태를 유지합니다.
"""

import streamlit as st
import db


def check_auth():
    """
    인증 상태를 확인합니다.
    로그인되어 있으면 user_id를 반환하고,
    아니면 로그인/회원가입 UI를 표시하고 st.stop()합니다.

    Returns:
        int: 로그인된 사용자 ID
    """
    if "user" in st.session_state and st.session_state["user"] is not None:
        return st.session_state["user"]["id"]

    _show_auth_ui()
    st.stop()


def show_user_info():
    """사이드바에 로그인된 사용자 정보와 로그아웃 버튼을 표시합니다."""
    if "user" in st.session_state and st.session_state["user"] is not None:
        user = st.session_state["user"]
        st.sidebar.markdown(f"👤 **{user['username']}**님 로그인 중")
        if st.sidebar.button("🚪 로그아웃", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()
        st.sidebar.markdown("---")


def _show_auth_ui():
    """로그인/회원가입 UI를 표시합니다."""
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <h1>💰 가계부 분석기</h1>
            <p style="font-size: 1.1em; color: #888;">로그인하여 나만의 가계부를 시작하세요!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        tab_login, tab_register = st.tabs(["🔑 로그인", "📝 회원가입"])

        with tab_login:
            with st.form("login_form"):
                st.subheader("🔑 로그인")
                username = st.text_input(
                    "아이디",
                    placeholder="아이디를 입력하세요",
                    key="login_username",
                )
                password = st.text_input(
                    "비밀번호",
                    type="password",
                    placeholder="비밀번호를 입력하세요",
                    key="login_password",
                )

                if st.form_submit_button(
                    "🔑 로그인", type="primary", use_container_width=True
                ):
                    if not username or not password:
                        st.error("아이디와 비밀번호를 입력해주세요.")
                    else:
                        user = db.authenticate_user(username, password)
                        if user:
                            st.session_state["user"] = user
                            st.success(f"✅ {user['username']}님, 환영합니다!")
                            st.rerun()
                        else:
                            st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

        with tab_register:
            with st.form("register_form"):
                st.subheader("📝 회원가입")
                new_username = st.text_input(
                    "아이디",
                    placeholder="사용할 아이디를 입력하세요",
                    key="reg_username",
                )
                new_password = st.text_input(
                    "비밀번호",
                    type="password",
                    placeholder="비밀번호를 입력하세요",
                    key="reg_password",
                )
                confirm_password = st.text_input(
                    "비밀번호 확인",
                    type="password",
                    placeholder="비밀번호를 다시 입력하세요",
                    key="reg_confirm",
                )

                if st.form_submit_button(
                    "📝 회원가입", type="primary", use_container_width=True
                ):
                    if not new_username or not new_password:
                        st.error("아이디와 비밀번호를 입력해주세요.")
                    elif len(new_username) < 2:
                        st.error("아이디는 2자 이상이어야 합니다.")
                    elif len(new_password) < 4:
                        st.error("비밀번호는 4자 이상이어야 합니다.")
                    elif new_password != confirm_password:
                        st.error("비밀번호가 일치하지 않습니다.")
                    else:
                        user_id = db.register_user(new_username, new_password)
                        if user_id:
                            st.success(
                                "✅ 회원가입이 완료되었습니다! '로그인' 탭에서 로그인해주세요."
                            )
                        else:
                            st.error("❌ 이미 존재하는 아이디입니다.")
