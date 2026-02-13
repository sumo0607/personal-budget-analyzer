"""
auth.py - 사용자 인증 모듈
==========================
회원가입, 로그인, 세션 관리, 역할(role) 기반 가드 기능을 제공합니다.
비밀번호는 bcrypt로 해시하여 저장합니다.
"""

import streamlit as st
import db


# ============================================================
# 세션 헬퍼
# ============================================================

def _get_user():
    """session_state에서 현재 로그인 사용자 정보를 가져옵니다."""
    return st.session_state.get("user")


def is_logged_in():
    """로그인 여부를 반환합니다."""
    return _get_user() is not None


def get_role():
    """현재 사용자의 role을 반환합니다. 미로그인이면 None."""
    user = _get_user()
    return user["role"] if user else None


# ============================================================
# 가드 함수
# ============================================================

def require_login():
    """
    로그인을 요구합니다.
    미로그인 → 로그인/회원가입 UI 표시 후 st.stop().

    Returns:
        int: 로그인된 사용자 ID
    """
    user = _get_user()
    if user is not None:
        return user["id"]
    _show_auth_ui()
    st.stop()


# 기존 코드 호환용 별칭
check_auth = require_login


def require_admin():
    """
    관리자 권한을 요구합니다.
    미로그인이면 로그인 화면, 로그인했지만 admin이 아니면 경고 후 st.stop().

    Returns:
        int: 관리자 사용자 ID
    """
    user_id = require_login()
    user = _get_user()
    if user["role"] != "admin":
        st.error("🚫 관리자 권한이 필요합니다.")
        st.stop()
    return user_id


# ============================================================
# 사이드바 사용자 정보
# ============================================================

def show_user_info():
    """사이드바에 로그인된 사용자 정보와 로그아웃 버튼을 표시합니다."""
    user = _get_user()
    if user is None:
        return
    role_badge = "🛡️ 관리자" if user["role"] == "admin" else "👤 일반"
    st.sidebar.markdown(f"{role_badge} **{user['username']}**님")
    if st.sidebar.button("🚪 로그아웃", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()
    st.sidebar.markdown("---")


# ============================================================
# 로그인 / 회원가입 UI
# ============================================================

def _show_auth_ui():
    """로그인/회원가입 화면을 표시합니다."""
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

        # ── 로그인 탭 ──
        with tab_login:
            with st.form("login_form"):
                st.subheader("🔑 로그인")
                username = st.text_input(
                    "아이디", placeholder="아이디를 입력하세요", key="login_username"
                )
                password = st.text_input(
                    "비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_password"
                )
                if st.form_submit_button("🔑 로그인", type="primary", use_container_width=True):
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

        # ── 회원가입 탭 ──
        with tab_register:
            with st.form("register_form"):
                st.subheader("📝 회원가입")
                new_username = st.text_input(
                    "아이디", placeholder="사용할 아이디를 입력하세요", key="reg_username"
                )
                new_password = st.text_input(
                    "비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="reg_password"
                )
                confirm_password = st.text_input(
                    "비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요", key="reg_confirm"
                )
                if st.form_submit_button("📝 회원가입", type="primary", use_container_width=True):
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
                            st.success("✅ 회원가입이 완료되었습니다! '로그인' 탭에서 로그인해주세요.")
                        else:
                            st.error("❌ 이미 존재하는 아이디입니다.")
