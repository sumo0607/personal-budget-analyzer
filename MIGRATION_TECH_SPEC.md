# [문서 1] 기술/기능 설계 문서 — 가계부 분석기 Next.js 이관

---

## 1. AS-IS 분석

### 1.1 핵심 기능 (5개)

| # | 기능 | 현재 위치 | 설명 |
|---|------|-----------|------|
| 1 | **사용자 인증** | `auth.py`, `db.py` | bcrypt 기반 회원가입/로그인, 역할(admin/user) 분리, 세션 기반 인증 |
| 2 | **거래 CRUD** | `db.py`, `1_📝_입력.py`, `2_📋_내역.py` | 수입/지출 등록·조회·수정·삭제, 다중 필터(기간/타입/카테고리/결제수단/키워드), 정렬 |
| 3 | **소비패턴 분석** | `analytics.py`, `3_📊_분석.py` | 요약 지표, 카테고리별/요일별/월별 집계, 예산 대비 현황, 규칙 기반 인사이트(이상치·반복지출·저축률) |
| 4 | **설정 관리** | `4_⚙️_설정.py`, `db.py` | 카테고리 추가/삭제, 월별·카테고리별 예산 CRUD, CSV 내보내기, 데이터 초기화, 샘플 데이터 생성, 비밀번호 변경 |
| 5 | **관리자 패널** | `5_🔧_관리자.py`, `db.py` | 전체 사용자 목록, 역할 변경, 비밀번호 재설정, 타 사용자 거래 조회·삭제 |

### 1.2 사용자 흐름

```
[미로그인]
  └─ 로그인/회원가입 UI (탭 전환)
       ├─ 로그인 성공 → session_state["user"] 저장 → 메뉴 노출
       └─ 회원가입 성공 → 로그인 탭으로 안내

[로그인 후 - 일반 사용자]
  ├─ 🏠 대시보드 : 기간 선택 → 요약 카드 + 차트 + 인사이트 확인
  ├─ 📝 입력     : 폼 작성 → 검증 → 저장 → 요약 표시 + 최근 5건 미리보기
  ├─ 📋 내역     : 사이드바 필터 설정 → 테이블 조회 → ID 선택 → 수정/삭제
  ├─ 📊 분석     : 기간 선택 → 6종 차트(탭) + 예산 프로그레스 + 인사이트
  └─ ⚙️ 설정     : 카테고리 관리 / 예산 설정 / CSV 내보내기 / 초기화 / 샘플 생성 / 비밀번호 변경

[로그인 후 - 관리자]
  └─ 🔧 관리자   : 사용자 목록 / 역할 변경 / 비밀번호 재설정 / 타 사용자 거래 조회·삭제
```

### 1.3 상태 관리 (st.session_state 구조)

| 키 | 타입 | 용도 | 스코프 |
|----|------|------|--------|
| `user` | `dict \| None` | `{id, username, role}` — 로그인 사용자 정보 | 전역 (앱 전체) |
| `edit_mode` | `bool` | 내역 페이지 수정 모드 토글 | 내역 페이지 |
| `history_period` | `str` | 내역 페이지 기간 필터 선택값 | 내역 페이지 |
| `{prefix}_period` | `str` | 대시보드·분석 페이지별 기간 선택 | 해당 페이지 |
| `del_confirm_{id}` | `bool` | 삭제 확인 체크박스 상태 | 내역 페이지 |
| `reset_confirm` | `str` | 데이터 초기화 확인 텍스트 | 설정 페이지 |
| 폼 관련 키 (`login_username`, `reg_username`, …) | `str` | 각 폼 입력값 | 해당 폼 |

### 1.4 데이터 흐름

```
[사용자 입력 (Streamlit 위젯)]
       │
       ▼
[Python 함수 호출 (db.py)]  ← 동일 프로세스 내 직접 호출
       │
       ▼
[SQLite (budget.db)]  ← 로컬 파일 DB, WAL 모드, 파라미터 바인딩
       │
       ▼
[dict 리스트 반환]
       │
       ▼
[pandas DataFrame 변환 (analytics.py)]  ← 집계·분석
       │
       ▼
[Plotly 차트 생성 (ui_components.py)]  ← Plotly Express/Graph Objects
       │
       ▼
[Streamlit 렌더링 (st.plotly_chart, st.metric, st.dataframe)]
```

- 모든 DB 호출은 `user_id`를 WHERE 조건으로 바인딩하여 사용자 간 데이터 격리
- 관리자 전용 함수(`admin_delete_transaction`)는 `user_id` 체크를 우회

### 1.5 외부 라이브러리 및 대체 전략

| 현재 라이브러리 | 용도 | Next.js 대체 |
|----------------|------|-------------|
| `streamlit` | UI 프레임워크 전체 | Next.js 14 App Router + React 컴포넌트 |
| `pandas` | 데이터 집계·변환 | 백엔드(FastAPI)에서 pandas 유지하거나, SQL 쿼리로 집계 직접 수행 |
| `plotly` | 차트 렌더링 | `recharts` (React 네이티브, 번들 크기 작음) 또는 `@nivo/core` |
| `bcrypt` | 비밀번호 해시 | 백엔드(FastAPI)에서 `passlib[bcrypt]` 또는 `bcrypt` 패키지 유지 |
| `sqlite3` | 데이터베이스 | 개발: SQLite(동일), 프로덕션: PostgreSQL + SQLAlchemy/Prisma |

---

## 2. TO-BE 아키텍처

### 2.1 Frontend 구조 (Next.js App Router)

```
app/
├── layout.tsx              ← 루트 레이아웃 (Sidebar + Header + AuthProvider)
├── page.tsx                ← "/" → 로그인 페이지 (미인증 시)
├── (auth)/
│   ├── login/page.tsx      ← 로그인 폼
│   └── register/page.tsx   ← 회원가입 폼
├── (protected)/
│   ├── layout.tsx          ← 인증 가드 + 네비게이션 Sidebar
│   ├── dashboard/page.tsx  ← 🏠 대시보드
│   ├── transactions/
│   │   ├── page.tsx        ← 📋 내역 (목록/필터/검색)
│   │   └── new/page.tsx    ← 📝 거래 입력
│   ├── analytics/page.tsx  ← 📊 분석
│   ├── settings/page.tsx   ← ⚙️ 설정
│   └── admin/page.tsx      ← 🔧 관리자 (admin only)
├── api/                    ← Next.js Route Handler는 사용하지 않음 (FastAPI 별도)
└── globals.css
```

### 2.2 Backend 구조 (FastAPI)

```
backend/
├── main.py                 ← FastAPI 앱 진입점, CORS 설정
├── config.py               ← 환경 변수, DB URL, JWT 시크릿
├── database.py             ← DB 엔진/세션 팩토리 (SQLAlchemy async)
├── models/
│   ├── user.py             ← User ORM 모델
│   ├── transaction.py      ← Transaction ORM 모델
│   ├── category.py         ← Category ORM 모델
│   └── budget.py           ← Budget ORM 모델
├── schemas/
│   ├── user.py             ← Pydantic request/response 스키마
│   ├── transaction.py
│   ├── category.py
│   ├── budget.py
│   └── analytics.py        ← 분석 결과 스키마
├── routers/
│   ├── auth.py             ← /api/auth/* (로그인, 회원가입, 토큰 갱신)
│   ├── transactions.py     ← /api/transactions/*
│   ├── categories.py       ← /api/categories/*
│   ├── budgets.py          ← /api/budgets/*
│   ├── analytics.py        ← /api/analytics/*
│   ├── settings.py         ← /api/settings/* (CSV, 초기화, 샘플)
│   └── admin.py            ← /api/admin/* (관리자 전용)
├── services/
│   ├── analytics_service.py ← 기존 analytics.py 로직 이관
│   └── sample_data.py       ← 샘플 데이터 생성 로직
├── middleware/
│   └── auth.py             ← JWT 인증 미들웨어, 역할 검사 Depends
└── alembic/                ← DB 마이그레이션
```

### 2.3 역할 분리 (FE vs BE)

| 영역 | Frontend (Next.js) | Backend (FastAPI) |
|------|-------------------|-------------------|
| **인증** | JWT 토큰 저장(httpOnly cookie), 로그인/회원가입 폼, AuthContext | 토큰 발급/갱신/검증, bcrypt 해시, 역할 검사 |
| **거래 CRUD** | 폼 입력 + 유효성 검사(zod), 테이블 렌더링, 필터 UI | SQL 쿼리, 비즈니스 검증, 페이지네이션 |
| **분석** | 차트 렌더링(recharts), 요약 카드 표시 | 데이터 집계(SQL/pandas), 인사이트 생성 |
| **설정** | 카테고리 목록 UI, 예산 폼, 다운로드 트리거 | CRUD 처리, CSV 생성, 데이터 삭제 |
| **관리자** | 사용자 목록 테이블, 역할 변경 UI | 사용자 조회, 역할 변경, 비밀번호 재설정 |
| **유효성 검사** | 즉시 피드백(금액>0, 필수값 등) — zod | 서버 사이드 재검증(보안), 비즈니스 규칙 |

### 2.4 통신 방식

| 항목 | 결정 | 근거 |
|------|------|------|
| **기본 통신** | REST API (JSON) | CRUD 중심, 요청-응답 구조에 적합 |
| **실시간 업데이트** | 불필요 (WebSocket 미사용) | 단일 사용자 대상, 실시간 동기화 요건 없음 |
| **인증 토큰 전달** | httpOnly Cookie (access + refresh) | XSS 방어, 자동 전송 |
| **파일 다운로드** | `Content-Disposition: attachment` 헤더 | CSV 내보내기 |
| **API 베이스 URL** | `NEXT_PUBLIC_API_URL` 환경변수 | 개발/프로덕션 환경 분리 |
| **HTTP 클라이언트** | FE: `fetch` (Next.js 내장) | 별도 라이브러리 불필요 |

---

## 3. API 명세

### 3.1 인증 API

#### POST `/api/auth/register`
- **Request**: `{ username: string, password: string }`
- **Response 201**: `{ id: number, username: string, role: "user" }`
- **에러**: 400(아이디 2자 미만, 비번 4자 미만), 409(중복 아이디)

#### POST `/api/auth/login`
- **Request**: `{ username: string, password: string }`
- **Response 200**: `{ id: number, username: string, role: string }` + Set-Cookie (access_token, refresh_token)
- **에러**: 401(아이디/비밀번호 불일치)

#### POST `/api/auth/logout`
- **Request**: 없음 (쿠키 자동 전송)
- **Response 200**: `{ message: "logged out" }` + Clear-Cookie
- **에러**: 없음

#### POST `/api/auth/refresh`
- **Request**: 없음 (refresh_token 쿠키)
- **Response 200**: 새 access_token Set-Cookie
- **에러**: 401(만료/무효 토큰)

#### GET `/api/auth/me`
- **Response 200**: `{ id: number, username: string, role: string }`
- **에러**: 401(미인증)

#### PUT `/api/auth/password`
- **Request**: `{ current_password: string, new_password: string }`
- **Response 200**: `{ message: "password changed" }`
- **에러**: 400(4자 미만), 401(현재 비밀번호 불일치)

---

### 3.2 거래 API

#### GET `/api/transactions`
- **Query Params**:
  - `start_date?: string` (YYYY-MM-DD)
  - `end_date?: string` (YYYY-MM-DD)
  - `type?: "income" | "expense"`
  - `categories?: string` (쉼표 구분)
  - `payment_method?: string`
  - `keyword?: string`
  - `sort_by?: "date" | "amount"` (기본: date)
  - `sort_order?: "asc" | "desc"` (기본: desc)
  - `page?: number` (기본: 1)
  - `per_page?: number` (기본: 50)
- **Response 200**:
```
{
  data: Transaction[],
  pagination: { page, per_page, total, total_pages },
  summary: { income_sum, expense_sum, count }
}
```
- **에러**: 400(잘못된 날짜 형식)

#### POST `/api/transactions`
- **Request**: `{ date: string, type: "income"|"expense", amount: number, category: string, payment_method: string, memo?: string }`
- **Response 201**: `Transaction`
- **에러**: 400(금액 ≤ 0, 필수값 누락), 404(존재하지 않는 카테고리)

#### GET `/api/transactions/:id`
- **Response 200**: `Transaction`
- **에러**: 404(존재하지 않거나 타 사용자 거래)

#### PUT `/api/transactions/:id`
- **Request**: `{ date, type, amount, category, payment_method, memo }`
- **Response 200**: `Transaction`
- **에러**: 400(유효성), 404(미존재)

#### DELETE `/api/transactions/:id`
- **Response 204**: No Content
- **에러**: 404(미존재)

---

### 3.3 카테고리 API

#### GET `/api/categories`
- **Query Params**: `type?: "income" | "expense"`
- **Response 200**: `{ income: string[], expense: string[] }` 또는 `string[]` (type 지정 시)

#### POST `/api/categories`
- **Request**: `{ type: "income"|"expense", name: string }`
- **Response 201**: `{ id, type, name }`
- **에러**: 400(빈 이름), 409(중복)

#### DELETE `/api/categories/:type/:name`
- **Response 204**: No Content
- **에러**: 404(미존재)

---

### 3.4 예산 API

#### GET `/api/budgets`
- **Query Params**: `month?: string` (YYYY-MM)
- **Response 200**: `Budget[]`

#### PUT `/api/budgets`
- **Request**: `{ month: string, category: string, budget_amount: number }`
  - `category`가 빈 문자열이면 전체 예산
- **Response 200**: `Budget` (upsert)
- **에러**: 400(금액 ≤ 0)

#### DELETE `/api/budgets/:id`
- **Response 204**: No Content
- **에러**: 404

---

### 3.5 분석 API

#### GET `/api/analytics/summary`
- **Query Params**: `start_date, end_date`
- **Response 200**:
```
{
  total_income: number,
  total_expense: number,
  net: number,
  daily_avg_expense: number,
  top_categories: [{ category: string, amount: number, percentage: number }],
  tx_count: number,
  expense_count: number,
  income_count: number
}
```

#### GET `/api/analytics/charts`
- **Query Params**: `start_date, end_date`
- **Response 200**:
```
{
  expense_by_date: [{ date: string, amount: number }],
  expense_by_category: [{ category: string, amount: number }],
  expense_by_payment: [{ payment_method: string, amount: number }],
  expense_by_dayofweek: [{ day: string, day_korean: string, amount: number }],
  income_expense_by_month: [{ year_month: string, type: string, amount: number }]
}
```

#### GET `/api/analytics/insights`
- **Query Params**: `start_date, end_date`
- **Response 200**: `[{ type: "info"|"warning"|"success"|"error", icon: string, message: string }]`

#### GET `/api/analytics/budget-status`
- **Query Params**: `month: string` (YYYY-MM)
- **Response 200**:
```
[{
  category: string,
  budget_amount: number,
  spent: number,
  usage_percent: number,
  remaining: number
}]
```

---

### 3.6 설정 API

#### GET `/api/settings/export-csv`
- **Query Params**: `start_date?, end_date?`
- **Response 200**: `text/csv` 파일 (Content-Disposition: attachment)

#### POST `/api/settings/clear-transactions`
- **Request**: `{ confirm: "삭제합니다" }`
- **Response 200**: `{ message, deleted_count }`
- **에러**: 400(확인 텍스트 불일치)

#### POST `/api/settings/clear-all`
- **Request**: `{ confirm: "삭제합니다" }`
- **Response 200**: `{ message }`
- **에러**: 400(확인 텍스트 불일치)

#### POST `/api/settings/generate-sample`
- **Request**: `{ num_months: number }` (1~6)
- **Response 201**: `{ message, count }`

---

### 3.7 관리자 API

> 모든 관리자 API는 `role: "admin"` 검증 필수

#### GET `/api/admin/users`
- **Response 200**: `[{ id, username, role, created_at, tx_count }]`

#### PUT `/api/admin/users/:id/role`
- **Request**: `{ role: "user" | "admin" }`
- **Response 200**: `{ id, username, role }`
- **에러**: 400(자기 자신 강등), 404

#### PUT `/api/admin/users/:id/password`
- **Request**: `{ new_password: string }`
- **Response 200**: `{ message }`
- **에러**: 400(4자 미만), 404

#### GET `/api/admin/users/:id/transactions`
- **Query Params**: 거래 API의 Query Params와 동일
- **Response 200**: 거래 API 응답 구조와 동일

#### DELETE `/api/admin/transactions/:id`
- **Response 204**: No Content
- **에러**: 404

---

## 4. 상태 관리 전략

### 4.1 전역 상태 (Zustand)

| Store | 상태 | 용도 |
|-------|------|------|
| `useAuthStore` | `{ user: User \| null, isLoading: boolean }` | 로그인 사용자 정보, 인증 상태 |
| `useFilterStore` | `{ dateRange, txType, categories, paymentMethod, keyword, sortBy, sortOrder }` | 내역/분석 페이지 필터 설정 값 공유 |

**선택 이유**: Zustand는 보일러플레이트가 적고 React 외부에서도 접근 가능하며, 이 앱 규모에 적합

### 4.2 서버 상태 (TanStack Query v5)

| Query Key | API 엔드포인트 | staleTime | 설명 |
|-----------|---------------|-----------|------|
| `["transactions", filters]` | GET /api/transactions | 30초 | 거래 목록 (필터 변경 시 자동 refetch) |
| `["transaction", id]` | GET /api/transactions/:id | 1분 | 단일 거래 (수정 폼 데이터) |
| `["categories"]` | GET /api/categories | 5분 | 카테고리 목록 (변경 빈도 낮음) |
| `["budgets", month]` | GET /api/budgets | 2분 | 예산 목록 |
| `["analytics", "summary", dateRange]` | GET /api/analytics/summary | 1분 | 요약 지표 |
| `["analytics", "charts", dateRange]` | GET /api/analytics/charts | 1분 | 차트 데이터 |
| `["analytics", "insights", dateRange]` | GET /api/analytics/insights | 1분 | 인사이트 |
| `["analytics", "budget-status", month]` | GET /api/analytics/budget-status | 1분 | 예산 현황 |
| `["admin", "users"]` | GET /api/admin/users | 30초 | 관리자: 사용자 목록 |
| `["admin", "transactions", userId, filters]` | GET /api/admin/users/:id/transactions | 30초 | 관리자: 타 사용자 거래 |

**Mutation 후 invalidation 규칙**:
- 거래 추가/수정/삭제 → `["transactions"]`, `["analytics"]` 쿼리 전부 무효화
- 카테고리 추가/삭제 → `["categories"]` 무효화
- 예산 추가/삭제 → `["budgets"]`, `["analytics", "budget-status"]` 무효화

### 4.3 로컬 상태 (React useState/useReducer)

| 컴포넌트 | 상태 | 설명 |
|----------|------|------|
| 거래 입력 폼 | `{ date, type, amount, category, paymentMethod, memo }` | 폼 필드값 (react-hook-form + zod) |
| 거래 수정 모달 | `{ isOpen, editingTransaction }` | 모달 열림/닫힘, 수정 대상 거래 |
| 삭제 확인 다이얼로그 | `{ isOpen, targetId }` | 삭제 확인 모달 |
| 분석 탭 | `activeTab: string` | 현재 활성 차트 탭 |
| 설정 탭 | `activeTab: string` | 현재 활성 설정 탭 |
| 데이터 초기화 | `{ confirmText: string }` | 확인 텍스트 입력값 |

---

## 5. 기능 매핑 (Streamlit → Next.js)

### 5.1 UI 기능 매핑

| Streamlit 기능 | 위치 | Next.js 구현 방식 |
|---------------|------|-------------------|
| `st.set_page_config()` | app.py | `app/layout.tsx` 의 `metadata` export |
| `st.navigation()` | app.py | Next.js App Router 파일 기반 라우팅 + Sidebar 네비게이션 컴포넌트 |
| `st.Page()` | app.py | `app/(protected)/*/page.tsx` 파일 각각 |
| `st.sidebar.*` | 대시보드, 내역, 분석 | `<Sidebar>` 컴포넌트 내 필터 섹션 |
| `st.tabs()` | 분석, 설정, 관리자 | Radix `Tabs` 또는 shadcn/ui `Tabs` 컴포넌트 |
| `st.form()` + `st.form_submit_button()` | 입력, 내역, 설정 | `<form>` + react-hook-form + zod 유효성 검사 |
| `st.metric()` | 대시보드, 분석 | `<MetricCard>` 커스텀 컴포넌트 |
| `st.dataframe()` | 내역, 관리자 | `@tanstack/react-table` 기반 `<DataTable>` 컴포넌트 |
| `st.plotly_chart()` | 대시보드, 분석 | `recharts` 의 `<LineChart>`, `<PieChart>`, `<BarChart>` |
| `st.progress()` | 분석(예산) | `<Progress>` 컴포넌트 (shadcn/ui) |
| `st.selectbox()` | 전체 | `<Select>` 컴포넌트 (shadcn/ui) |
| `st.multiselect()` | 내역 필터 | `<MultiSelect>` 커스텀 컴포넌트 (Combobox + Checkbox) |
| `st.radio()` | 입력, 내역 | `<RadioGroup>` 컴포넌트 |
| `st.date_input()` | 전체 | `<DatePicker>` 컴포넌트 (react-day-picker) |
| `st.number_input()` | 입력, 설정 | `<Input type="number">` + 포맷팅 |
| `st.text_input()` | 전체 | `<Input>` 컴포넌트 |
| `st.checkbox()` | 내역(삭제확인) | `<Checkbox>` 컴포넌트 |
| `st.slider()` | 설정(샘플기간) | `<Slider>` 컴포넌트 |
| `st.download_button()` | 설정 | `<a href="/api/settings/export-csv" download>` 또는 fetch + Blob + URL.createObjectURL |
| `st.success()` / `st.error()` / `st.warning()` / `st.info()` | 전체 | `sonner` toast 라이브러리 또는 shadcn/ui `Toast` |
| `st.spinner()` | 설정 | `<Skeleton>` 로딩 UI 또는 Button내 `<Loader2>` spinner |
| `st.balloons()` | 설정 | `canvas-confetti` 라이브러리 (선택) |
| `st.rerun()` | 전체 | TanStack Query `invalidateQueries()` → 자동 리렌더링 |
| `st.stop()` | 인증 가드 | Next.js middleware `redirect()` 또는 컴포넌트 내 early return |
| `st.caption()` | 전체 | `<p className="text-sm text-muted-foreground">` |
| `st.columns()` | 전체 | CSS Grid 또는 Tailwind `grid grid-cols-{n}` |

### 5.2 백엔드 기능 매핑

| Python 기능 | Next.js/FastAPI 구현 방식 |
|------------|--------------------------|
| `db.get_connection()` (SQLite 직접) | SQLAlchemy async session + 커넥션 풀 |
| `bcrypt.hashpw()` / `bcrypt.checkpw()` | FastAPI에서 `passlib[bcrypt]` 사용 (동일) |
| `st.session_state["user"]` (세션 인증) | JWT access/refresh 토큰 (httpOnly cookie) |
| `db.get_transactions()` (동적 WHERE 조건) | SQLAlchemy `select().where()` 동적 필터 체이닝 |
| `analytics.py` 전체 (pandas 집계) | `services/analytics_service.py`에서 SQL 집계 쿼리 또는 pandas 유지 |
| `db.export_transactions_csv()` | FastAPI `StreamingResponse` (text/csv) |
| `db.generate_sample_data()` | `services/sample_data.py` — bulk insert |

---

## 6. 데이터 타입 정의 (TypeScript)

### 6.1 사용자

```
User {
  id: number
  username: string
  role: "user" | "admin"
}

LoginRequest {
  username: string  // min 2자
  password: string  // min 4자
}

RegisterRequest {
  username: string  // min 2자
  password: string  // min 4자
}

ChangePasswordRequest {
  current_password: string
  new_password: string  // min 4자
}
```

### 6.2 거래

```
Transaction {
  id: number
  date: string          // "YYYY-MM-DD"
  type: "income" | "expense"
  amount: number        // > 0
  category: string
  payment_method: string
  memo: string
  created_at: string    // ISO 8601
}

TransactionCreateRequest {
  date: string
  type: "income" | "expense"
  amount: number        // > 0, max 100_000_000
  category: string
  payment_method: string  // "현금" | "카드" | "이체" | "기타"
  memo?: string
}

TransactionUpdateRequest = TransactionCreateRequest

TransactionListResponse {
  data: Transaction[]
  pagination: Pagination
  summary: { income_sum: number, expense_sum: number, count: number }
}

Pagination {
  page: number
  per_page: number
  total: number
  total_pages: number
}

TransactionFilter {
  start_date?: string
  end_date?: string
  type?: "income" | "expense"
  categories?: string[]
  payment_method?: string
  keyword?: string
  sort_by?: "date" | "amount"
  sort_order?: "asc" | "desc"
  page?: number
  per_page?: number
}
```

### 6.3 카테고리

```
Category {
  id: number
  type: "income" | "expense"
  name: string
}

CategoryMap {
  income: string[]
  expense: string[]
}

CategoryCreateRequest {
  type: "income" | "expense"
  name: string
}
```

### 6.4 예산

```
Budget {
  id: number
  month: string          // "YYYY-MM"
  category: string       // 빈 문자열이면 전체 예산
  budget_amount: number
}

BudgetUpsertRequest {
  month: string
  category: string
  budget_amount: number  // > 0
}

BudgetStatus {
  category: string
  budget_amount: number
  spent: number
  usage_percent: number
  remaining: number
}
```

### 6.5 분석

```
AnalyticsSummary {
  total_income: number
  total_expense: number
  net: number
  daily_avg_expense: number
  top_categories: TopCategory[]
  tx_count: number
  expense_count: number
  income_count: number
}

TopCategory {
  category: string
  amount: number
  percentage: number
}

ChartsData {
  expense_by_date: { date: string, amount: number }[]
  expense_by_category: { category: string, amount: number }[]
  expense_by_payment: { payment_method: string, amount: number }[]
  expense_by_dayofweek: { day: string, day_korean: string, amount: number }[]
  income_expense_by_month: { year_month: string, type: string, amount: number }[]
}

Insight {
  type: "info" | "warning" | "success" | "error"
  icon: string
  message: string
}
```

### 6.6 관리자

```
AdminUser {
  id: number
  username: string
  role: "user" | "admin"
  created_at: string
  tx_count: number
}

RoleUpdateRequest {
  role: "user" | "admin"
}

PasswordResetRequest {
  new_password: string  // min 4자
}
```

### 6.7 상수

```
PAYMENT_METHODS = ["현금", "카드", "이체", "기타"] as const

DEFAULT_EXPENSE_CATEGORIES = [
  "식비", "교통", "주거/통신", "쇼핑", "문화/여가",
  "의료/건강", "교육", "경조사", "보험", "기타지출"
] as const

DEFAULT_INCOME_CATEGORIES = [
  "급여", "부수입", "용돈", "투자수익", "기타수입"
] as const

PERIOD_OPTIONS = ["이번 달", "지난 달", "최근 3개월", "최근 6개월", "올해", "사용자 지정"] as const
```

---

## 7. 마이그레이션 단계

### Phase 1: 프로젝트 초기 설정 (백엔드 + 프론트엔드 환경)

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 1-1 | FastAPI 프로젝트 생성, SQLAlchemy 설정, Alembic 마이그레이션 초기화 | `backend/` 기본 구조 |
| 1-2 | ORM 모델 4개(User, Transaction, Category, Budget) 정의 및 마이그레이션 실행 | `models/*.py`, `alembic/versions/` |
| 1-3 | Next.js 14 프로젝트 생성 (App Router), Tailwind CSS, shadcn/ui 초기 설치 | `frontend/` 기본 구조 |
| 1-4 | ESLint, Prettier, TypeScript strict 설정 | `tsconfig.json`, `.eslintrc` |
| 1-5 | 공통 타입 정의 파일 작성 | `frontend/src/types/` |

### Phase 2: 인증 시스템

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 2-1 | FastAPI JWT 인증 (회원가입, 로그인, 토큰 갱신, 로그아웃) 구현 | `routers/auth.py`, `middleware/auth.py` |
| 2-2 | Next.js middleware 인증 가드 (쿠키 기반 리다이렉트) | `middleware.ts` |
| 2-3 | 로그인/회원가입 페이지 UI | `app/(auth)/login/`, `app/(auth)/register/` |
| 2-4 | AuthProvider + useAuthStore (Zustand) | `providers/auth-provider.tsx`, `stores/auth.ts` |
| 2-5 | 사이드바 사용자 정보 + 로그아웃 버튼 | `components/sidebar.tsx` |

### Phase 3: 거래 CRUD + 내역 페이지

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 3-1 | 거래 CRUD API (FastAPI) — 목록 필터/정렬/페이지네이션 포함 | `routers/transactions.py` |
| 3-2 | TanStack Query 훅: `useTransactions`, `useCreateTransaction`, `useUpdateTransaction`, `useDeleteTransaction` | `hooks/use-transactions.ts` |
| 3-3 | 거래 입력 폼 페이지 (react-hook-form + zod) | `app/(protected)/transactions/new/page.tsx` |
| 3-4 | 거래 내역 페이지: 필터 사이드바 + DataTable + 수정 모달 + 삭제 다이얼로그 | `app/(protected)/transactions/page.tsx` |

### Phase 4: 대시보드 + 분석

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 4-1 | 분석 API (summary, charts, insights, budget-status) | `routers/analytics.py`, `services/analytics_service.py` |
| 4-2 | recharts 차트 컴포넌트 6종 (LineTrend, CategoryPie, CategoryBar, PaymentBar, DayOfWeekBar, MonthlyComparison) | `components/charts/` |
| 4-3 | 대시보드 페이지 (요약 카드 + 상위 카테고리 + 주요 차트 + 인사이트) | `app/(protected)/dashboard/page.tsx` |
| 4-4 | 분석 페이지 (6탭 차트 + 예산 Progress + 인사이트) | `app/(protected)/analytics/page.tsx` |

### Phase 5: 설정 + 카테고리/예산

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 5-1 | 카테고리/예산 CRUD API | `routers/categories.py`, `routers/budgets.py` |
| 5-2 | 설정 API (CSV 내보내기, 데이터 초기화, 샘플 생성) | `routers/settings.py` |
| 5-3 | 설정 페이지 (5탭: 카테고리 / 예산 / 데이터 관리 / 샘플 / 비밀번호) | `app/(protected)/settings/page.tsx` |

### Phase 6: 관리자 패널

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 6-1 | 관리자 API (사용자 목록, 역할 변경, 비밀번호 재설정, 거래 조회/삭제) | `routers/admin.py` |
| 6-2 | 관리자 페이지 (사용자 테이블 + 역할 변경 + 비밀번호 재설정 + 거래 조회/삭제) | `app/(protected)/admin/page.tsx` |
| 6-3 | 관리자 라우트 가드 (role !== "admin" → 리다이렉트) | `middleware.ts` 확장 |

### Phase 7: 통합 테스트 + 배포

| 단계 | 작업 내용 | 산출물 |
|------|----------|--------|
| 7-1 | FastAPI 단위/통합 테스트 (pytest) | `backend/tests/` |
| 7-2 | E2E 테스트 (Playwright) — 핵심 플로우 5개 | `frontend/e2e/` |
| 7-3 | Docker Compose 구성 (frontend + backend + PostgreSQL) | `docker-compose.yml` |
| 7-4 | 기존 SQLite 데이터 → PostgreSQL 마이그레이션 스크립트 | `scripts/migrate_data.py` |
| 7-5 | CI/CD 파이프라인 (GitHub Actions) | `.github/workflows/` |
