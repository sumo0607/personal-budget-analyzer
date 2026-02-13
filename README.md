# 💰 가계부 분석기 (Personal Budget Analyzer)

엑셀/CSV 업로드 없이 웹에서 직접 수입/지출을 입력하고, 소비패턴을 자동 분석하는 Streamlit 웹앱입니다.

## ✨ 주요 기능

| 페이지 | 기능 |
|--------|------|
| 🏠 대시보드 | 이번 달 요약, 지출 TOP 카테고리, 주요 차트, 인사이트 |
| 📝 입력 | 수입/지출 내역 폼 입력 → SQLite 저장 |
| 📋 내역 | 필터/정렬/검색 + 수정/삭제 |
| 📊 분석 | 기간별 지출 분석, 트렌드, 예산 대비, 반복지출 탐지 |
| ⚙️ 설정 | 카테고리 관리, 예산 설정, 데이터 초기화/내보내기(CSV) |

## 🛠️ 기술 스택

- **Python** 3.11+ / **Streamlit** 1.54+
- **pandas** (데이터 처리) / **plotly** (차트)
- **SQLite** (로컬 영구 저장)

## 📦 설치 및 실행

```bash
# 1. 리포지토리 클론
git clone https://github.com/sumo0607/personal-budget-analyzer.git
cd personal-budget-analyzer

# 2. 가상환경 생성 및 활성화
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📁 프로젝트 구조

```
personal-budget-analyzer/
├── app.py              # 메인 앱 (대시보드)
├── db.py               # SQLite DB 연결/CRUD
├── analytics.py        # 데이터 분석/인사이트
├── ui_components.py    # 공통 UI 컴포넌트
├── pages/
│   ├── 1_📝_입력.py    # 거래 입력
│   ├── 2_📋_내역.py    # 거래 목록/관리
│   ├── 3_📊_분석.py    # 소비패턴 분석
│   └── 4_⚙️_설정.py    # 설정
├── requirements.txt    # 패키지 목록
├── .gitignore          # Git 제외 파일
├── SPEC.md             # 기능 명세서
├── UNIMPLEMENT.md      # 미구현 기능 백로그
└── README.md           # 이 파일
```

## 📸 스크린샷

> 추후 추가 예정

## 📄 라이선스

MIT License