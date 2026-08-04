"""
BioAgent Hub — Streamlit 배포 래퍼

이 파일은 로그인 게이트와 화면 틀만 담당함.
분석 로직(문헌·구조·실험·계획서·계산기)은 static/bioagent.html 안에 그대로 있고
이 스크립트가 손대지 않음. 기능을 고치려면 그 HTML 을 교체하면 됨.

인증:
  기본값 MI / 1234.
  Streamlit Cloud 의 App settings → Secrets 에 아래를 넣으면 그 값이 우선 적용됨.
      [auth]
      username = "..."
      password = "..."
  GitHub 저장소가 공개면 이 파일의 기본값도 공개되므로, 실제 운영에서는
  반드시 Secrets 로 바꿔 쓸 것.
"""
from __future__ import annotations

import hmac
from pathlib import Path

import streamlit as st

APP_TITLE = "BioAgent Hub"
# 앱 본체는 static/ 이 아니라 app_html/ 에 둠.
# static/ 에 두면 Streamlit 이 /app/static/... 으로 공개해 버려서
# 로그인하지 않고도 URL 로 직접 열 수 있게 됨. 반드시 이 경로를 유지할 것.
HTML_PATH = Path(__file__).parent / "app_html" / "bioagent.html"

DEFAULT_USER = "MI"
DEFAULT_PASS = "mi1234"

st.set_page_config(page_title=APP_TITLE, page_icon="🧬", layout="wide",
                   initial_sidebar_state="collapsed")


# ---------------------------------------------------------------------------
# 인증
# ---------------------------------------------------------------------------
def _credentials() -> tuple[str, str]:
    try:
        auth = st.secrets["auth"]
        return str(auth["username"]), str(auth["password"])
    except Exception:                                   # Secrets 미설정 시 기본값
        return DEFAULT_USER, DEFAULT_PASS


def _check(user: str, pw: str) -> bool:
    u, p = _credentials()
    # 타이밍 공격을 피하려고 상수시간 비교를 씀
    return hmac.compare_digest(user.strip(), u) and hmac.compare_digest(pw, p)


LOGIN_CSS = """
<style>
  #MainMenu, footer, header {visibility: hidden;}
  .block-container {padding-top: 3rem; max-width: 430px;}
  .bh-logo {display:flex; align-items:center; gap:10px; margin-bottom:6px;}
  .bh-logo b {font-size:22px; color:#0B3D91; letter-spacing:-.3px;}
  .bh-bars {display:flex; gap:3px;}
  .bh-bars i {width:7px; height:24px; border-radius:2px; display:block;}
  .bh-sub {color:#606672; font-size:13px; margin-bottom:22px; line-height:1.6;}
  .bh-note {color:#9AA0AC; font-size:11.5px; margin-top:18px; line-height:1.7;
            border-top:1px solid #E3E7ED; padding-top:14px;}
  div[data-testid="stForm"] {border:1px solid #E3E7ED; border-radius:12px; padding:20px 18px;
            background:#FFFFFF;}
  .stButton button {width:100%; background:#0B3D91; color:#fff; border:none;
            border-radius:8px; padding:9px 0; font-weight:600;}
  .stButton button:hover {background:#092F72; color:#fff;}
</style>
"""

LOGO = """
<div class="bh-logo">
  <span class="bh-bars">
    <i style="background:#0053D6"></i><i style="background:#65CBF3"></i>
    <i style="background:#FFDB13"></i><i style="background:#FF7D45"></i>
  </span>
  <b>BioAgent Hub</b>
</div>
<div class="bh-sub">문헌 · 구조 · 실험 · 과제계획서를 하나로 잇는 연구 에이전트<br>
계속하려면 로그인할 것.</div>
"""


def login_gate() -> bool:
    if st.session_state.get("authed"):
        return True

    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    st.markdown(LOGO, unsafe_allow_html=True)

    with st.form("login", clear_on_submit=False):
        user = st.text_input("아이디", key="u", autocomplete="username")
        pw = st.text_input("비밀번호", type="password", key="p",
                           autocomplete="current-password")
        ok = st.form_submit_button("로그인")

    if ok:
        if _check(user, pw):
            st.session_state["authed"] = True
            st.session_state["who"] = user.strip()
            st.rerun()
        else:
            st.session_state["fails"] = st.session_state.get("fails", 0) + 1
            st.error(f"아이디 또는 비밀번호가 맞지 않음 (시도 {st.session_state['fails']}회)")

    st.markdown(
        '<div class="bh-note">이 앱은 지정된 사용자만 쓰도록 되어 있음. '
        '입력한 데이터는 서버에 저장되지 않고 사용자 브라우저 안에서만 처리됨.<br>'
        '문헌·구조 조회는 공개 학술 API 를 브라우저가 직접 호출함.</div>',
        unsafe_allow_html=True)
    return False


# ---------------------------------------------------------------------------
# 본 화면
# ---------------------------------------------------------------------------
APP_CSS = """
<style>
  #MainMenu, footer {visibility: hidden;}
  header[data-testid="stHeader"] {height: 0; background: transparent;}
  .block-container {padding: 0 !important; max-width: 100% !important;}
  section[data-testid="stSidebar"] {display: none;}
  iframe[title="streamlit_app"] {border: none;}
  .bh-bar {display:flex; align-items:center; gap:10px; padding:6px 14px;
           border-bottom:1px solid #E3E7ED; background:#F4F6F9; font-size:12px;
           color:#606672;}
  .bh-bar b {color:#0B3D91;}
</style>
"""

# 앱 HTML 은 인증을 통과한 뒤에만 브라우저로 내려감.
# components.html 의 iframe 은 srcdoc 방식이라 부모와 같은 출처를 물려받으므로
# localStorage(시약 재고·도구 설정)가 그대로 동작함.


def main() -> None:
    if not login_gate():
        return

    st.markdown(APP_CSS, unsafe_allow_html=True)

    if not HTML_PATH.exists():
        st.error(f"앱 파일을 찾을 수 없음: {HTML_PATH}\n\n"
                 "저장소의 static/bioagent.html 이 있는지 확인할 것.")
        return

    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(
            f'<div class="bh-bar"><b>BioAgent Hub</b>'
            f'<span>{st.session_state.get("who", "")} 로그인됨</span>'
            f'<span style="flex:1"></span>'
            f'<span>데이터는 이 브라우저에만 저장됨</span></div>',
            unsafe_allow_html=True)
    with c2:
        if st.button("로그아웃", use_container_width=True):
            for k in ("authed", "who", "fails"):
                st.session_state.pop(k, None)
            st.rerun()

    html = HTML_PATH.read_text(encoding="utf-8")
    st.components.v1.html(html, height=1400, scrolling=False)


if __name__ == "__main__":
    main()
