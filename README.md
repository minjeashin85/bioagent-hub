# BioAgent Hub — Streamlit 배포판

문헌 · 구조 · 실험 · 과제계획서를 하나로 잇는 바이오 연구 에이전트.
GitHub 에 올리고 Streamlit Community Cloud 에 연결하면 공개 URL 로 쓸 수 있음.
로그인한 사람만 들어올 수 있음.

---

## 구조

```
.
├── streamlit_app.py            로그인 게이트 + 화면 틀 (여기만 Python)
├── requirements.txt
├── app_html/
│   └── bioagent.html           앱 본체. 분석 로직 전부가 이 안에 있음
├── .streamlit/
│   ├── config.toml             정적 서빙 비활성화 (보안상 필수)
│   └── secrets.toml.example    로그인 정보 예시
├── .gitignore
└── README.md
```

**핵심 로직은 `app_html/bioagent.html` 안에 그대로 있고 `streamlit_app.py` 는 손대지 않음.**
기능을 고치려면 그 HTML 파일만 교체하면 됨.

---

## 1. GitHub 에 올리기

### 웹에서 (터미널 없이)

1. github.com → 우측 상단 **+** → **New repository**
2. 이름: `bioagent-hub` · **Private** 권장 · Create
3. 만들어진 화면에서 **uploading an existing file** 클릭
4. 이 폴더의 파일과 폴더를 통째로 끌어다 놓고 **Commit changes**

> **주의**: 앱 본체를 `static/` 폴더에 두지 말 것. Streamlit 이 그 폴더를
> `/app/static/...` 주소로 공개해 버려서 **로그인 없이 앱이 열림**.
> 반드시 `app_html/` 을 유지할 것.

> `.streamlit` 처럼 점으로 시작하는 폴더는 탐색기에서 숨김 처리될 수 있음.
> 윈도우 탐색기는 **보기 → 숨긴 항목** 을 켤 것.

### 터미널에서

```bash
cd bioagent-streamlit
git init
git add .
git commit -m "BioAgent Hub 최초 배포"
git branch -M main
git remote add origin https://github.com/<사용자명>/bioagent-hub.git
git push -u origin main
```

---

## 2. Streamlit Cloud 에 배포

1. https://share.streamlit.io 접속 → GitHub 계정으로 로그인
2. **Create app** → **Deploy a public app from GitHub**
3. 입력값
   - Repository: `<사용자명>/bioagent-hub`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. **Advanced settings → Secrets** 에 아래를 붙여넣을 것

```toml
[auth]
username = "MI"
password = "mi1234"
```

5. **Deploy** → 2~4분 뒤 `https://<앱이름>.streamlit.app` 주소가 나옴

### 로그인 정보를 바꾸려면

앱 화면 우측 하단 **Manage app → Settings → Secrets** 에서 위 값을 고치고 저장하면
재배포 없이 바로 적용됨.

> Secrets 를 설정하지 않으면 `streamlit_app.py` 의 기본값(MI / mi1234)이 쓰임.
> **저장소를 Public 으로 두면 이 기본값이 그대로 노출되므로**, 공개 저장소를 쓸 거라면
> 반드시 Secrets 로 다른 값을 지정할 것.

---

## 3. 로컬에서 먼저 확인하기

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

→ http://localhost:8501 에서 로그인 화면이 뜸.

---

## 4. 앱 내용을 수정한 뒤

`app_html/bioagent.html` 만 새 파일로 교체하고 커밋하면 됨.

```bash
git add app_html/bioagent.html
git commit -m "앱 갱신"
git push
```

Streamlit Cloud 가 push 를 감지해 자동으로 다시 배포함.

---

## 배포하면 달라지는 점

| 항목 | 로컬 HTML | Streamlit 배포판 |
|---|---|---|
| 접근 | 파일 더블클릭 | 공개 URL + 로그인 |
| 학술 DB 조회 | 정상 | 정상 |
| 문서 생성 (Word/Excel/PDF) | 정상 | 정상 |
| 3D 뷰어 · Colab 노트북 | 정상 | 정상 |
| 시약 재고 · 도구 설정 저장 | 브라우저 저장소 | 브라우저 저장소 (동일) |
| 인증 | 없음 (로컬 파일) | 로그인 필수 · 우회 경로 없음 |
| **로컬 브리지 (Vina 직접 실행)** | 정상 | **동작하지 않음** |

### 로컬 브리지가 안 되는 이유

Streamlit Cloud 는 `https` 로 서비스되는데, 브리지 서버는 사용자 PC 의 `http://127.0.0.1:8900`
에 있음. 브라우저가 https 페이지에서 http 로 요청하는 것을 **혼합 콘텐츠(mixed content)** 로
차단함. 이건 브라우저 보안 정책이라 우회할 수 없음.

**실제로 도킹을 돌려야 할 때는 아래 중 하나를 쓸 것.**

- 파트2 → 외부 도구 → **AutoDock Vina → ① Colab 노트북** (값이 채워진 상태로 받아짐)
- **CB-Dock2 / SwissDock** 웹 서비스 (설치도 좌표도 불필요)
- 브리지가 꼭 필요하면 **배포판 대신 로컬 HTML 파일**을 쓸 것 — 두 방식은 데이터를
  각자의 브라우저 저장소에 따로 보관하므로, 시약 재고는 파트3 Excel 로 옮길 것

---

## 데이터 취급

- 입력한 내용은 **서버에 저장되지 않음.** 전부 사용자 브라우저 안에서만 처리됨
- 문헌·구조·물성 조회는 브라우저가 공개 학술 API(Europe PMC, UniProt, AlphaFold DB,
  RCSB, PubChem 등)를 직접 호출함
- 시약 재고와 도구 설정은 브라우저 로컬 저장소에 남음. 브라우저 데이터를 지우면
  사라지므로 파트3 Excel 내보내기로 주기적으로 백업할 것

## 알려진 한계

- 로그인은 앱 진입을 막는 용도임. 여러 사람이 같은 계정을 공유하면 누가 무엇을 했는지
  구분되지 않음
- Streamlit Community Cloud 는 일정 시간 접속이 없으면 앱이 절전 상태로 들어감.
  다시 접속하면 30초 내외로 깨어남
- 도킹 스크립트의 grid box 좌표는 3D 뷰어에서 직접 잡아야 함
- 예산 비목 비율, 세포 시딩 밀도 프리셋, 배양용기 규격은 일반적 기준값임.
  실제 공고 기준과 사용 제품 스펙을 확인할 것
