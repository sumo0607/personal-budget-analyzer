# [문서 2] 디자인 마이그레이션 문서 — 가계부 분석기 Next.js 이관

---

## 1. 기존 UI 구조 분석 (Streamlit)

### 1.1 전체 화면 구성

```
┌──────────────────────────────────────────────────┐
│                 Streamlit 앱                      │
├──────────┬───────────────────────────────────────┤
│ Sidebar  │            Main Content               │
│ (280px)  │                                       │
│          │  ┌─ Title ──────────────────────────┐ │
│ - 앱 제목 │  │ st.title() + st.caption()       │ │
│ - 사용자  │  └─────────────────────────────────┘ │
│   정보    │                                       │
│ - 로그아웃│  ┌─ Content Area ──────────────────┐ │
│ - ──────  │  │                                 │ │
│ - 필터    │  │  st.columns() / st.tabs() /     │ │
│   컨트롤  │  │  st.form() / st.dataframe() /   │ │
│           │  │  st.plotly_chart()               │ │
│ - 네비    │  │                                 │ │
│   게이션  │  └─────────────────────────────────┘ │
│ (자동)    │                                       │
│           │  ┌─ Footer ───────────────────────┐ │
│           │  │ st.caption() v2.0              │ │
│           │  └─────────────────────────────────┘ │
└──────────┴───────────────────────────────────────┘
```

### 1.2 페이지별 UI 구조 상세

#### (1) 로그인/회원가입 (미인증 상태)

| 영역 | 구성 |
|------|------|
| 상단 | 중앙 정렬 HTML — 앱 로고 텍스트("💰 가계부 분석기") + 부제 |
| 중앙 | `st.columns([1,2,1])` 으로 중앙 폼 배치 |
| 탭 | `st.tabs(["🔑 로그인", "📝 회원가입"])` |
| 로그인 탭 | `st.form` — 아이디 text_input, 비밀번호 password_input, 로그인 버튼 |
| 회원가입 탭 | `st.form` — 아이디, 비밀번호, 비밀번호 확인, 회원가입 버튼 |

#### (2) 🏠 대시보드

| 영역 | 구성 |
|------|------|
| 사이드바 | 기간 선택 selectbox (6개 옵션), 사용자 지정 시 date_input 2개 |
| 상단 요약 | `st.columns(4)` — 4개 `st.metric` (총수입, 총지출, 순수익, 일평균지출) |
| 상위 카테고리 | `st.columns(3)` — 메달 아이콘 + `st.metric` (상위 3개 카테고리) |
| 차트 | `st.columns(2)` — 지출추이 라인차트, 카테고리 도넛차트 |
| 차트 | 전체 너비 — 월별 수입/지출 비교 바차트 |
| 인사이트 | `st.info/warning/success` 블록 리스트 |
| 빈 상태 | 데이터 없을 때 — 중앙 안내 메시지 + 빠른 시작 가이드(2열) |

#### (3) 📝 거래 입력

| 영역 | 구성 |
|------|------|
| 폼 | `st.form` + `st.columns(2)` 2열 배치 |
| 좌측 열 | date_input, radio(수입/지출), number_input(금액) |
| 우측 열 | selectbox(카테고리, 동적), selectbox(결제수단), text_input(메모) |
| 버튼 | 전체 너비 primary 저장 버튼 |
| 결과 | 성공 시 마크다운 테이블로 입력 내용 요약 |
| 최근 내역 | 밑부분에 최근 5건 `st.dataframe` |

#### (4) 📋 거래 내역

| 영역 | 구성 |
|------|------|
| 사이드바 필터 | 기간 selectbox, 유형 radio, 카테고리 multiselect, 결제수단 selectbox, 메모검색 text_input, 정렬 기준/방향 selectbox+radio |
| 상단 요약 | `st.columns(3)` — 조회건수, 수입합계, 지출합계 `st.metric` |
| 테이블 | `st.dataframe` (ID, 날짜, 유형, 금액, 카테고리, 결제수단, 메모) — height 400px |
| 수정/삭제 | `st.selectbox` (거래 ID 선택, format_func로 요약 표시) |
| 좌측 열 | 수정 `st.form` — 날짜, 유형, 금액, 카테고리, 결제수단, 메모, 수정 저장 버튼 |
| 우측 열 | 삭제 확인 — 거래 정보 표시, checkbox 확인, 삭제 실행 버튼 |

#### (5) 📊 소비패턴 분석

| 영역 | 구성 |
|------|------|
| 사이드바 | 기간 선택 (date_range_selector) |
| 요약 카드 | `display_summary_cards` (4열 metric) + 상위 카테고리 텍스트 |
| 차트 탭 | `st.tabs` 6개 — 지출추이·카테고리비중·카테고리금액·결제수단·요일별·월별비교 |
| 각 탭 | plotly_chart (전체 너비) + caption (최고/최저 정보) |
| 예산 현황 | budget별 반복: `st.columns([3,1])` — 라벨 + progress 바 / 퍼센트 배지 + 잔여금 caption |
| 인사이트 | `display_insights` — info/warning/success 알림 리스트 |

#### (6) ⚙️ 설정

| 영역 | 구성 |
|------|------|
| 탭 | `st.tabs` 5개 — 카테고리·예산·데이터관리·샘플데이터·비밀번호 |
| 카테고리 탭 | 2열 — 지출/수입 카테고리 목록(•항목 + 🗑️ 버튼) + 추가 폼 |
| 예산 탭 | 3열 폼 (월, 카테고리, 금액) + 예산 목록 dataframe + 삭제 selectbox |
| 데이터관리 탭 | 2열 — CSV 다운로드 버튼 / 초기화 (확인 text_input + 2개 삭제 버튼) |
| 샘플 탭 | slider (1~6개월) + 생성 버튼 |
| 비밀번호 탭 | form — 현재비번, 새비번, 새비번확인, 변경 버튼 |

#### (7) 🔧 관리자

| 영역 | 구성 |
|------|------|
| 탭 | `st.tabs` 2개 — 가입자목록/권한관리, 사용자거래내역 |
| 가입자 탭 | dataframe(사용자목록) + 3열(사용자선택, 역할선택, 변경버튼) + 비밀번호 재설정 폼 |
| 거래내역 탭 | 사용자 selectbox + 사이드바 필터 + 요약카드 + 2열 차트 + dataframe + 삭제 기능 |

### 1.3 사용 UI 요소 전수 목록

| Streamlit 위젯 | 사용 빈도 | 사용 위치 |
|----------------|----------|-----------|
| `st.title` | 6회 | 모든 페이지 |
| `st.caption` | 10+회 | 모든 페이지 |
| `st.subheader` | 15+회 | 모든 페이지 |
| `st.metric` | 11회 | 대시보드, 내역, 분석 |
| `st.columns` | 20+회 | 모든 페이지 |
| `st.tabs` | 4회 | 인증, 분석, 설정, 관리자 |
| `st.form` + `st.form_submit_button` | 8회 | 입력, 내역(수정), 설정(카테고리/예산/비밀번호), 관리자 |
| `st.selectbox` | 15+회 | 필터, 카테고리 선택, ID 선택 |
| `st.multiselect` | 2회 | 내역 필터, 관리자 필터 |
| `st.radio` | 6회 | 유형 선택, 정렬 방향 |
| `st.date_input` | 6회 | 사용자 지정 기간, 거래 날짜 |
| `st.number_input` | 3회 | 금액 입력, 예산 금액 |
| `st.text_input` | 10+회 | 검색, 메모, 카테고리명, 비밀번호 |
| `st.checkbox` | 2회 | 삭제 확인 |
| `st.slider` | 1회 | 샘플 기간 |
| `st.button` | 10+회 | 삭제, 로그아웃, 역할변경 |
| `st.dataframe` | 5회 | 내역, 설정(예산), 관리자 |
| `st.plotly_chart` | 10회 | 대시보드(3), 분석(6), 관리자(2) |
| `st.progress` | 동적 | 분석(예산별) |
| `st.download_button` | 1회 | 설정(CSV) |
| `st.success/error/warning/info` | 30+회 | 전체 |
| `st.markdown` (HTML) | 5+회 | 로그인 화면, 빈 상태 |
| `st.spinner` | 1회 | 샘플 생성 |
| `st.balloons` | 1회 | 샘플 생성 완료 |

---

## 2. 화면 재설계 (Next.js)

### 2.1 페이지 구조

| 현재 (Streamlit) | Next.js Route | 페이지 제목 | 설명 |
|------------------|---------------|-------------|------|
| `auth._show_auth_ui` | `/login` | 로그인 | 로그인 + 회원가입 탭 |
| — | `/register` | 회원가입 | 별도 페이지로 분리 (선택사항) |
| `0_🏠_대시보드.py` | `/dashboard` | 대시보드 | 요약·차트·인사이트 |
| `1_📝_입력.py` | `/transactions/new` | 거래 입력 | 입력 폼 |
| `2_📋_내역.py` | `/transactions` | 거래 내역 | 목록·필터·수정·삭제 |
| `3_📊_분석.py` | `/analytics` | 소비 분석 | 6종 차트·예산·인사이트 |
| `4_⚙️_설정.py` | `/settings` | 설정 | 카테고리·예산·데이터·비밀번호 |
| `5_🔧_관리자.py` | `/admin` | 관리자 | 사용자 관리·거래 조회 |

### 2.2 라우팅 구조

```
app/
├── (auth)/                     ← 인증 레이아웃 그룹 (Sidebar 없음, 중앙 정렬)
│   ├── layout.tsx
│   ├── login/page.tsx
│   └── register/page.tsx
├── (protected)/                ← 인증 필수 레이아웃 그룹 (Sidebar + Header)
│   ├── layout.tsx              ← AuthGuard + Sidebar + TopBar
│   ├── dashboard/page.tsx
│   ├── transactions/
│   │   ├── page.tsx            ← 거래 목록
│   │   └── new/page.tsx        ← 거래 입력
│   ├── analytics/page.tsx
│   ├── settings/page.tsx
│   └── admin/page.tsx          ← AdminGuard 추가 적용
└── layout.tsx                  ← 루트 레이아웃 (html, body, Providers)
```

**라우팅 가드 로직**:
- Next.js `middleware.ts` 에서 쿠키 내 `access_token` 유무 확인
  - 미인증 + `(protected)` 접근 → `/login` 리다이렉트
  - 인증 + `/login` 접근 → `/dashboard` 리다이렉트
- `/admin` 접근 시 → `middleware.ts` 에서 JWT 디코딩하여 `role` 확인, admin 아니면 `/dashboard` 리다이렉트

---

## 3. 레이아웃 설계

### 3.1 전체 레이아웃

```
┌─────────────────────────────────────────────────────────────┐
│  Header (h-14, 고정 상단)                                    │
│  ┌────────┬──────────────────────────────────┬──────────┐   │
│  │ 로고    │  현재 페이지 Breadcrumb           │ 사용자   │   │
│  │ 💰     │  대시보드 > ...                   │ 아바타   │   │
│  └────────┴──────────────────────────────────┴──────────┘   │
├────────────┬────────────────────────────────────────────────┤
│  Sidebar   │  Main Content                                  │
│  (w-64,    │                                                │
│   축소:    │  ┌─ Page Header ──────────────────────────┐    │
│   w-16)    │  │ 타이틀 + 설명 + 액션 버튼             │    │
│            │  └────────────────────────────────────────┘    │
│  ─ 메뉴 ─ │                                                │
│  🏠 대시보드│  ┌─ Content ─────────────────────────────┐    │
│  📝 거래입력│  │                                       │    │
│  📋 거래내역│  │  (페이지별 고유 콘텐츠)                │    │
│  📊 소비분석│  │                                       │    │
│  ⚙️ 설정   │  │                                       │    │
│            │  └────────────────────────────────────────┘    │
│  ─ 관리 ─ │                                                │
│  🔧 관리자 │                                                │
│  (admin만) │                                                │
│            │                                                │
│  ───────   │                                                │
│  👤 사용자 │                                                │
│  🚪 로그아웃│                                                │
└────────────┴────────────────────────────────────────────────┘
```

### 3.2 인증 페이지 레이아웃 (Sidebar 없음)

```
┌──────────────────────────────────────────────┐
│              (전체 화면 중앙 정렬)              │
│                                              │
│         ┌─────────────────────────┐          │
│         │     💰 가계부 분석기      │          │
│         │   로그인하여 시작하세요    │          │
│         │                         │          │
│         │  ┌─ Card ────────────┐  │          │
│         │  │ [로그인] [회원가입] │  │          │
│         │  │                   │  │          │
│         │  │  아이디 [________] │  │          │
│         │  │  비밀번호 [______] │  │          │
│         │  │                   │  │          │
│         │  │  [  🔑 로그인  ]  │  │          │
│         │  └───────────────────┘  │          │
│         └─────────────────────────┘          │
│                                              │
└──────────────────────────────────────────────┘
```

### 3.3 반응형 기준

| Breakpoint | 너비 | Sidebar | 레이아웃 변화 |
|-----------|------|---------|-------------|
| **모바일** | < 768px | 숨김 (햄버거 메뉴로 Overlay Drawer) | 1열 배치, 차트 세로 스택, 메트릭 카드 2열 그리드 |
| **태블릿** | 768px ~ 1024px | 아이콘 전용 (w-16) 축소 모드 | 2열 그리드, 차트 2열 유지 |
| **데스크톱** | > 1024px | 펼침 (w-64) | 원본 레이아웃 유지 (4열 메트릭, 2열 차트) |

**Streamlit 대비 변경점**: Streamlit은 반응형이지만 사이드바가 모바일에서 접기만 가능. Next.js에서는 모바일 하단 탭바 또는 햄버거 Drawer로 전환하여 모바일 경험 개선.

**필터 처리 (모바일)**:
- Streamlit: 사이드바 내 항상 노출
- Next.js (모바일): "필터" 버튼 클릭 시 바텀 시트(Sheet) 또는 Drawer로 필터 패널 표시
- Next.js (데스크톱): 콘텐츠 상단에 인라인 필터 바 또는 사이드 패널

---

## 4. 컴포넌트 설계

### 4.1 레이아웃 컴포넌트

#### `AppShell`
- **역할**: 전체 앱의 최상위 레이아웃 (Sidebar + Header + Main)
- **상태**: `isSidebarOpen: boolean` (모바일 토글)
- **재사용**: 1회 (루트 레이아웃에서만)

#### `Sidebar`
- **역할**: 좌측 네비게이션 메뉴 (페이지 링크, 사용자 정보, 로그아웃)
- **상태**: `collapsed: boolean` (태블릿에서 축소)
- **Props**: `currentPath: string`, `user: User`, `onLogout: () => void`
- **재사용**: 1회
- **하위 컴포넌트**: `SidebarNavItem`, `SidebarUserInfo`

#### `Header`
- **역할**: 상단 바 (로고, 브레드크럼, 모바일 햄버거, 사용자 드롭다운)
- **상태**: 없음 (Sidebar 토글은 AppShell에서 관리)
- **재사용**: 1회

#### `PageHeader`
- **역할**: 각 페이지 상단 제목 + 설명 + 우측 액션 버튼 영역
- **Props**: `title: string`, `description?: string`, `actions?: ReactNode`
- **재사용**: 모든 페이지

### 4.2 데이터 표시 컴포넌트

#### `MetricCard`
- **역할**: 지표 카드 (아이콘 + 라벨 + 값 + 델타)
- **Props**: `label: string`, `value: string`, `icon?: string`, `delta?: { value: string, type: "positive"|"negative"|"neutral" }`
- **상태**: 없음
- **재사용**: 대시보드(4+3), 내역(3), 분석(4)

#### `DataTable`
- **역할**: 정렬·페이지네이션이 있는 데이터 테이블 (@tanstack/react-table 기반)
- **Props**: `columns: ColumnDef[]`, `data: T[]`, `pagination?: PaginationState`, `onRowClick?: (row) => void`
- **상태**: `sorting`, `pagination` (useReactTable 내부)
- **재사용**: 내역, 관리자(사용자 목록/거래 목록), 설정(예산 목록)

#### `EmptyState`
- **역할**: 데이터 없을 때 안내 메시지 (아이콘 + 제목 + 부제 + CTA 버튼)
- **Props**: `icon?: ReactNode`, `title: string`, `description: string`, `action?: { label: string, href: string }`
- **상태**: 없음
- **재사용**: 대시보드, 내역, 분석, 관리자

#### `InsightList`
- **역할**: 인사이트 항목 리스트 (아이콘 + 타입별 색상 배경 + 메시지)
- **Props**: `insights: Insight[]`
- **상태**: 없음
- **재사용**: 대시보드, 분석

### 4.3 차트 컴포넌트

모든 차트는 `recharts` 기반으로 구현하며, 공통 Props: `data: T[]`, `height?: number`

#### `ExpenseTrendChart`
- **역할**: 날짜별 지출 추이 라인 차트
- **차트 타입**: `<LineChart>` + `<Line>` + `<Tooltip>` + `<CartesianGrid>`
- **데이터 구조**: `{ date: string, amount: number }[]`
- **재사용**: 대시보드, 관리자

#### `CategoryPieChart`
- **역할**: 카테고리별 지출 비중 도넛 차트
- **차트 타입**: `<PieChart>` + `<Pie>` (innerRadius로 도넛)
- **데이터 구조**: `{ category: string, amount: number }[]`
- **재사용**: 대시보드, 분석, 관리자

#### `CategoryBarChart`
- **역할**: 카테고리별 지출 금액 바 차트
- **차트 타입**: `<BarChart>` + `<Bar>`
- **데이터 구조**: `{ category: string, amount: number }[]`

#### `PaymentBarChart`
- **역할**: 결제수단별 지출 바 차트
- **차트 타입**: `<BarChart>` + `<Bar>`
- **데이터 구조**: `{ payment_method: string, amount: number }[]`

#### `DayOfWeekChart`
- **역할**: 요일별 평균 지출 바 차트
- **차트 타입**: `<BarChart>` + `<Bar>`
- **데이터 구조**: `{ day_korean: string, amount: number }[]`

#### `MonthlyComparisonChart`
- **역할**: 월별 수입/지출 그룹 바 차트
- **차트 타입**: `<BarChart>` + `<Bar>` × 2 (수입=초록, 지출=빨강)
- **데이터 구조**: `{ year_month: string, income: number, expense: number }[]`

### 4.4 폼 컴포넌트

#### `TransactionForm`
- **역할**: 거래 입력/수정 공통 폼 (react-hook-form + zod)
- **Props**: `mode: "create"|"edit"`, `defaultValues?: TransactionCreateRequest`, `onSubmit: (data) => void`, `isLoading: boolean`
- **상태**: `loading`, 폼 필드값 (react-hook-form 내부)
- **재사용**: 거래 입력 페이지 + 수정 모달

#### `FilterPanel`
- **역할**: 거래 목록 필터 패널 (기간, 유형, 카테고리, 결제수단, 키워드, 정렬)
- **Props**: `filters: TransactionFilter`, `onChange: (filters) => void`, `categories: string[]`
- **상태**: 내부 임시 필터값 (적용 버튼 클릭 시 부모에 전달)
- **재사용**: 내역 페이지, 관리자 거래 조회

#### `BudgetForm`
- **역할**: 예산 설정 폼 (월, 카테고리, 금액)
- **Props**: `categories: string[]`, `onSubmit: (data) => void`, `isLoading: boolean`
- **재사용**: 설정 페이지

#### `CategoryManager`
- **역할**: 카테고리 목록 + 추가/삭제 UI
- **Props**: `type: "income"|"expense"`, `categories: string[]`, `onAdd: (name) => void`, `onDelete: (name) => void`
- **재사용**: 설정 페이지 (2회 — 수입/지출)

### 4.5 피드백 컴포넌트

#### `BudgetProgressBar`
- **역할**: 예산 사용 현황 프로그레스 바 (라벨 + ProgressBar + 퍼센트 배지 + 잔여액)
- **Props**: `label: string`, `spent: number`, `budget: number`
- **상태**: 없음 (usage_percent >= 100 → 빨강, >= 80 → 노랑, 그 외 → 초록)
- **재사용**: 분석 페이지 (예산별 반복)

#### `ConfirmDialog`
- **역할**: 삭제 등 위험 작업 확인 모달 (제목 + 설명 + 취소/확인 버튼)
- **Props**: `open: boolean`, `title: string`, `description: string`, `confirmLabel: string`, `onConfirm: () => void`, `onCancel: () => void`, `variant: "danger"|"warning"`
- **재사용**: 거래 삭제, 데이터 초기화, 관리자 삭제

#### `ConfirmWithTextDialog`
- **역할**: 텍스트 입력 확인 모달 (특정 텍스트 입력해야 확인 버튼 활성화)
- **Props**: `ConfirmDialog` + `confirmText: string` (예: "삭제합니다")
- **재사용**: 데이터 초기화

#### `EditTransactionModal`
- **역할**: 거래 수정 모달 (TransactionForm을 모달 내 렌더링)
- **Props**: `open: boolean`, `transaction: Transaction`, `onClose: () => void`
- **상태**: `isSubmitting: boolean`
- **재사용**: 내역 페이지

### 4.6 공통 기초 컴포넌트 (shadcn/ui 기반)

| 컴포넌트 | 사용 위치 | 비고 |
|----------|---------|------|
| `Button` | 전체 | variant: default, destructive, outline, ghost |
| `Input` | 전체 | text, password, number |
| `Select` | 전체 | 단일 선택 드롭다운 |
| `MultiSelect` | 내역 필터 | Combobox + Checkbox 조합 (커스텀 빌드) |
| `DatePicker` | 입력, 필터 | react-day-picker 기반 |
| `DateRangePicker` | 대시보드, 분석, 내역 | 시작일~종료일 범위 선택 |
| `RadioGroup` | 유형 선택, 정렬 | |
| `Checkbox` | 삭제 확인 | |
| `Slider` | 샘플 기간 | |
| `Tabs` | 분석, 설정, 관리자 | |
| `Card` | 메트릭, 폼 래핑 | |
| `Dialog / Sheet` | 모달, 모바일 필터 | |
| `Progress` | 예산 현황 | |
| `Badge` | 역할 표시, 예산 상태 | variant: default, destructive, warning, success |
| `Skeleton` | 로딩 상태 | |
| `Toast (Sonner)` | 성공/에러 알림 | |
| `Tooltip` | 차트 hover, 아이콘 설명 | |
| `DropdownMenu` | 사용자 메뉴, 행 액션 | |

---

## 5. 인터랙션 설계

### 5.1 사용자 입력 흐름

#### 거래 입력 (핵심 플로우)

```
1. 사용자가 /transactions/new 진입
2. 유형 RadioGroup 선택 ("지출" 기본값)
   → 선택 변경 시 카테고리 Select 옵션이 즉시 전환 (수입/지출 카테고리 다름)
3. 날짜 DatePicker 선택 (기본값: 오늘)
4. 금액 Input 입력 (step: 1000, 포커스 시 자동 전체 선택)
5. 카테고리 Select 선택
6. 결제수단 Select 선택 (기본값: "카드")
7. 메모 Input 입력 (선택)
8. "저장" Button 클릭
   → zod 프론트엔드 유효성 검사 (금액 > 0, 카테고리 필수)
   → 실패 시: 해당 필드 아래 인라인 에러 메시지 (빨간 텍스트)
   → 성공 시: API POST /api/transactions 호출
     → 로딩 중: 버튼 disabled + Loader2 스피너 표시
     → 성공: toast("거래가 저장되었습니다"), 폼 초기화, 하단 최근 내역 자동 갱신
     → 실패: toast.error("저장 중 오류가 발생했습니다")
```

#### 거래 수정 플로우

```
1. 내역 페이지에서 테이블 행 클릭 또는 행 우측 ⋮ 메뉴 → "수정" 선택
2. EditTransactionModal 열림 (기존 값 pre-fill)
3. 필드 수정 후 "저장" 클릭
   → API PUT /api/transactions/:id
   → 성공: modal 닫기 + toast("수정 완료") + 목록 자동 갱신 (invalidateQueries)
```

#### 거래 삭제 플로우

```
1. 내역 페이지에서 행 ⋮ 메뉴 → "삭제" 선택
2. ConfirmDialog 열림 ("이 거래를 삭제하시겠습니까?" + 거래 요약 정보)
3. "삭제" 버튼 클릭
   → API DELETE /api/transactions/:id
   → 성공: dialog 닫기 + toast("삭제 완료") + 목록 갱신
```

### 5.2 버튼 클릭 동작 매핑

| 버튼 | 페이지 | 동작 |
|------|--------|------|
| 로그인 | 로그인 | POST /api/auth/login → 성공시 /dashboard 리다이렉트 |
| 회원가입 | 회원가입 | POST /api/auth/register → 성공시 /login으로 이동 + toast |
| 로그아웃 | Sidebar | POST /api/auth/logout → /login 리다이렉트 |
| 저장 (거래) | 거래 입력 | POST /api/transactions → 폼 초기화 + toast |
| 수정 저장 | 수정 모달 | PUT /api/transactions/:id → modal 닫기 + 목록 갱신 |
| 삭제 실행 | 삭제 다이얼로그 | DELETE /api/transactions/:id → dialog 닫기 + 목록 갱신 |
| CSV 다운로드 | 설정 | GET /api/settings/export-csv → 파일 다운로드 트리거 |
| 데이터 삭제 | 설정 | POST /api/settings/clear-transactions → 확인 다이얼로그 → toast |
| 전체 초기화 | 설정 | POST /api/settings/clear-all → 텍스트 확인 다이얼로그 → toast |
| 샘플 생성 | 설정 | POST /api/settings/generate-sample → 로딩 스피너 → toast |
| 역할 변경 | 관리자 | PUT /api/admin/users/:id/role → toast + 목록 갱신 |
| 비밀번호 재설정 | 관리자 | PUT /api/admin/users/:id/password → toast |

### 5.3 로딩 처리 방식

| 상황 | 현재 (Streamlit) | Next.js 구현 |
|------|-----------------|-------------|
| 페이지 첫 로드 | Streamlit 자체 스피너 | `<Skeleton>` 컴포넌트 (메트릭 카드, 차트, 테이블 각각의 골격 UI) |
| 데이터 조회 | 전체 페이지 리렌더 | TanStack Query `isLoading` → 해당 영역만 Skeleton |
| 폼 제출 | `st.spinner` | Button 내 `<Loader2 className="animate-spin">` + disabled |
| 차트 로딩 | 한 번에 전부 로드 | 차트 영역별 Skeleton → 데이터 도착 시 fade-in |
| 탭 전환 | 전체 리렌더 | 탭 콘텐츠 영역만 교체, 다른 탭 데이터는 TanStack Query 캐시 |

### 5.4 에러 표시 방식

| 에러 유형 | 표시 방식 | 위치 |
|-----------|---------|------|
| **폼 유효성 에러** | 필드 아래 인라인 빨간 텍스트 | 해당 Input 컴포넌트 바로 아래 |
| **API 에러 (4xx)** | `toast.error("에러 메시지")` | 화면 우상단 토스트 |
| **API 에러 (5xx)** | `toast.error("서버 오류가 발생했습니다")` | 화면 우상단 토스트 |
| **인증 만료 (401)** | 자동 토큰 갱신 시도 → 실패 시 `/login` 리다이렉트 + toast | — |
| **권한 부족 (403)** | `/dashboard` 리다이렉트 + toast | — |
| **네트워크 에러** | `toast.error("네트워크 연결을 확인해주세요")` | 화면 우상단 토스트 |
| **데이터 없음** | `<EmptyState>` 컴포넌트 | 콘텐츠 영역 중앙 |

---

## 6. 상태 기반 UI 변화

### 6.1 인증 상태

| 상태 | UI 변화 |
|------|---------|
| **미인증** | `/login` 또는 `/register` 화면만 표시. Sidebar/Header 없음. 중앙 카드 레이아웃 |
| **인증 중 (로그인 요청)** | 로그인 Button: disabled + Loader2 스피너. 입력 필드 disabled |
| **인증 완료 (user)** | Sidebar 메뉴 5개 표시. Header에 사용자명 + 역할 배지 |
| **인증 완료 (admin)** | Sidebar 메뉴 5개 + "🔧 관리자" 항목 추가 표시 |
| **세션 만료** | 자동 refresh 시도. 실패 시 → `/login` 리다이렉트 + toast("세션이 만료되었습니다") |

### 6.2 대시보드 페이지

| 상태 | UI 변화 |
|------|---------|
| **로딩** | MetricCard × 4 → Skeleton 카드. 차트 영역 → Skeleton 사각형. 인사이트 → Skeleton 줄 3개 |
| **데이터 있음** | MetricCard 값 표시. 상위 카테고리 3개 표시. 차트 2열 + 월별 차트. 인사이트 리스트 |
| **데이터 없음** | EmptyState ("아직 데이터가 없습니다") + 빠른 시작 가이드 카드 2열 (입력하기/샘플 생성) |
| **기간 변경** | 차트+메트릭 영역만 Skeleton 전환 → 새 데이터 로드 → 업데이트 |

### 6.3 거래 입력 페이지

| 상태 | UI 변화 |
|------|---------|
| **초기** | 빈 폼 (기본값: 오늘, 지출, 0원, 카드). 저장 버튼 활성 |
| **유형 변경** | 수입↔지출 전환 시 카테고리 Select 옵션 목록 즉시 교체 |
| **유효성 에러** | 해당 필드 border 빨강 + 필드 아래 에러 메시지 텍스트 |
| **저장 중** | 저장 Button: disabled + "저장 중..." 텍스트 + Loader2 스피너 |
| **저장 성공** | toast.success("거래가 저장되었습니다") + 폼 초기화 + 하단 최근 내역 갱신 |
| **저장 실패** | toast.error(에러 메시지) + 폼 값 유지 |

### 6.4 거래 내역 페이지

| 상태 | UI 변화 |
|------|---------|
| **로딩** | MetricCard 3개 Skeleton + 테이블 Skeleton (행 10개) |
| **데이터 있음** | MetricCard 3개(조회건수, 수입합계, 지출합계) + DataTable + 행 hover 시 배경색 변경 + 행 클릭 시 수정 모달 |
| **데이터 없음** | EmptyState ("조건에 맞는 거래가 없습니다") + 필터 변경 유도 텍스트 |
| **필터 변경** | 테이블 영역 로딩 표시 (overlay spinner) → 결과 업데이트 |
| **수정 모달 열림** | 배경 dim + EditTransactionModal 표시 (기존 값 pre-fill) |
| **삭제 다이얼로그** | 배경 dim + ConfirmDialog (거래 요약 정보 + 삭제/취소 버튼) |

### 6.5 분석 페이지

| 상태 | UI 변화 |
|------|---------|
| **로딩** | 요약 카드 Skeleton + 탭 내 차트 Skeleton |
| **탭 전환** | 이미 캐시된 탭 → 즉시 전환. 미캐시 → 차트 Skeleton → 로드 |
| **예산 미설정** | "예산 현황" 섹션에 info 배너 ("설정 페이지에서 예산을 설정해보세요" + 이동 링크) |
| **예산 초과** | 프로그레스 바 빨강 + "🚨 N% 초과" Badge(destructive) |
| **예산 경고** | 프로그레스 바 노랑 + "⚠️ N%" Badge(warning) |
| **예산 정상** | 프로그레스 바 초록 + "✅ N%" Badge(success) |

### 6.6 설정 페이지

| 상태 | UI 변화 |
|------|---------|
| **카테고리 삭제 중** | 해당 항목 opacity 50% + 삭제 아이콘 스피너 |
| **예산 저장 중** | 저장 Button 로딩 상태 |
| **CSV 다운로드** | 다운로드 버튼 클릭 → 브라우저 파일 다운로드 트리거. 데이터 없으면 버튼 disabled |
| **초기화 확인** | "삭제합니다" 미입력 → 삭제 버튼 disabled(회색). 입력 → 활성(빨강) |
| **샘플 생성 중** | 버튼 로딩 + 프로그레스 불확정 표시 |
| **샘플 생성 완료** | toast.success + confetti 효과 (선택) |

---

## 7. UX 개선 포인트

### 7.1 Streamlit 대비 개선 사항

| 항목 | Streamlit (현재 문제) | Next.js (개선) |
|------|---------------------|---------------|
| **페이지 전환 속도** | 매 인터랙션마다 전체 Python 스크립트 재실행 (1~3초 지연) | SPA 클라이언트 네비게이션 (즉시 전환), TanStack Query 캐시로 재방문 시 데이터 즉시 표시 |
| **부분 업데이트** | `st.rerun()`으로 전체 페이지 재렌더링 | React 가상 DOM — 변경된 컴포넌트만 리렌더링 |
| **거래 수정 UX** | 하단 selectbox에서 ID 선택 → 별도 폼에서 수정 (스크롤 이동 필요) | 테이블 행 클릭 → 인라인 모달에서 바로 수정 (컨텍스트 유지) |
| **거래 삭제 UX** | checkbox 확인 + 버튼 클릭 (2단계, 같은 페이지) | 모달 다이얼로그 1회 확인 (더 명확한 의도 확인) |
| **알림/피드백** | `st.success()` → 페이지 내 고정 배너 (스크롤 위치에 따라 안 보일 수 있음) | Toast 알림 (화면 우상단 고정, 3초 후 자동 사라짐) — 어디서든 보임 |
| **필터 적용** | 사이드바 위젯 변경 즉시 전체 재실행 (타이핑 중에도) | 필터 변경 → "적용" 버튼 또는 디바운스(300ms) 후 API 호출 (불필요한 요청 방지) |
| **모바일 대응** | Streamlit 기본 반응형 (제한적) | 모바일 퍼스트 반응형 — 하단 네비, 시트 필터, 터치 최적화 |
| **로딩 경험** | 빈 화면 → 한 번에 전체 표시 | Skeleton UI → 점진적 표시 (레이아웃 시프트 없음) |
| **URL 공유** | Streamlit URL에 상태 미반영 (항상 같은 URL) | 필터/기간이 URL 쿼리 파라미터에 반영 (`/transactions?type=expense&start=2026-01-01`) → 북마크/공유 가능 |
| **키보드 접근성** | Streamlit 위젯 기본 수준 | Tab 네비게이션, Enter 제출, Escape 모달 닫기, 포커스 트랩 |
| **테이블 기능** | `st.dataframe` (정렬만 가능) | 열 정렬, 행 선택, 페이지네이션, 행 클릭 액션, 열 너비 조절 |
| **차트 인터랙션** | Plotly 기본 호버 | Recharts 커스텀 툴팁 + 클릭 이벤트 + 범례 토글 + 반응형 리사이징 |

### 7.2 추가 사용성 개선 방향

| 개선 항목 | 구체 내용 |
|-----------|---------|
| **빠른 입력** | 대시보드 또는 내역 페이지 우하단에 FAB(Floating Action Button) "+" → 거래 입력 모달 바로 열림 |
| **최근 입력 반복** | 거래 입력 시 "지난 거래 복사" 버튼 → 최근 거래 목록에서 선택하면 값 자동 채움 |
| **기간 프리셋** | DateRangePicker에 프리셋 버튼 내장 ("이번 달", "지난 달", "최근 3개월" 등 원클릭) |
| **다크 모드** | next-themes 기반 시스템/라이트/다크 모드 토글 (Sidebar 하단 또는 Header 우측) |
| **검색 강화** | 거래 내역 상단에 통합 검색 바 — 메모뿐 아니라 카테고리, 금액 범위도 한 곳에서 검색 |
| **데이터 시각화 강화** | 히트맵(캘린더 뷰) — 날짜별 지출 강도를 색상으로 표시 (GitHub 잔디 스타일) |
| **오프라인 지원** | PWA + Service Worker로 오프라인 조회 가능 (선택적 추가 개선) |
| **국제화 준비** | next-intl 적용 가능한 구조로 설계 (현재는 한국어 단일) |
