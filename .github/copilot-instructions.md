# Project Guidelines — 가계부 분석기

## Architecture

**Monorepo structure:**
- **Root (`/`)**: Python Streamlit 원본 소스 (레거시, 참조용)
- **`/frontend`**: Next.js 14 App Router + TypeScript 마이그레이션 대상
- **`/stitch`**: HTML/Tailwind 디자인 목업 (Vault Vista 디자인 시스템)

마이그레이션 진행 중이며, 새 코드는 `/frontend` 에 작성한다.

## Tech Stack (Frontend)

- Next.js 14 (App Router), React 18, TypeScript 5.4
- Tailwind CSS 3.4 (Stitch 커스텀 토큰 사용)
- Zustand 4.5 (auth, filter 전역 상태)
- TanStack React Query 5 (서버 상태)
- Recharts 2.12 (차트)
- react-hook-form 7 + zod 3 (폼 검증)
- sonner (토스트)

## Design System — Vault Vista / Stitch

- **색상**: Material Design 3 기반 커스텀 토큰 (`tailwind.config.ts` 참조)
- **타이포**: Manrope (headline), Plus Jakarta Sans (body/label)
- **아이콘**: Material Symbols Outlined (`<span class="material-symbols-outlined">`)
- **핵심 규칙**: 1px 보더 금지 (tonal layering으로 대체), glassmorphism 네비게이션/FAB
- **디자인 레퍼런스**: `stitch/vault_vista/DESIGN.md`

## Code Conventions

- 한국어 사용자 대상 앱이므로 UI 문자열은 한국어, 코드/주석은 영어 허용
- 파일명: kebab-case (컴포넌트 파일은 PascalCase.tsx)
- 포맷 함수는 `src/lib/utils.ts`에 집중 (`formatCurrency`, `formatDateKorean` 등)
- API 호출은 `src/lib/api.ts`의 래퍼만 사용 (직접 fetch 금지)
- 서버 상태는 반드시 TanStack Query hook (`src/hooks/`) 경유
- 전역 상태는 Zustand store (`src/stores/`) 경유

## Key Documents

- 기술 설계서: `MIGRATION_TECH_SPEC.md`
- 디자인 설계서: `MIGRATION_DESIGN_SPEC.md`
- 기능 명세: `SPEC.md`
- Python 원본 로직: `db.py`, `analytics.py`
