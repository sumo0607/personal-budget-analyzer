// ============================================================
// 공통 타입 정의 — Python db.py / analytics.py 구조를 TypeScript로 변환
// ============================================================

export interface User {
  id: number;
  username: string;
  role: "user" | "admin";
}

export interface Transaction {
  id: number;
  user_id?: number;
  date: string;
  type: "income" | "expense";
  amount: number;
  category: string;
  payment_method: string;
  memo: string;
  created_at: string;
}

export interface TransactionCreateRequest {
  date: string;
  type: "income" | "expense";
  amount: number;
  category: string;
  payment_method: string;
  memo?: string;
}

export type TransactionUpdateRequest = TransactionCreateRequest;

export interface TransactionFilter {
  start_date?: string;
  end_date?: string;
  type?: "income" | "expense";
  categories?: string[];
  payment_method?: string;
  keyword?: string;
  sort_by?: "date" | "amount";
  sort_order?: "asc" | "desc";
}

export interface Category {
  id: number;
  type: "income" | "expense";
  name: string;
}

export interface Budget {
  id: number;
  month: string;
  category: string;
  budget_amount: number;
}

export interface BudgetStatus {
  category: string;
  budget_amount: number;
  spent: number;
  usage_percent: number;
  remaining: number;
}

export interface AnalyticsSummary {
  total_income: number;
  total_expense: number;
  net: number;
  daily_avg_expense: number;
  top_categories: { category: string; amount: number; percentage: number }[];
  tx_count: number;
  expense_count: number;
  income_count: number;
}

export interface Insight {
  type: "info" | "warning" | "success" | "error";
  icon: string;
  message: string;
}

export interface ChartDataPoint {
  date?: string;
  category?: string;
  payment_method?: string;
  day_korean?: string;
  year_month?: string;
  amount: number;
  income?: number;
  expense?: number;
}

export const PAYMENT_METHODS = ["현금", "카드", "이체", "기타"] as const;

export const DEFAULT_EXPENSE_CATEGORIES = [
  "식비", "교통", "주거/통신", "쇼핑", "문화/여가",
  "의료/건강", "교육", "경조사", "보험", "기타지출",
] as const;

export const DEFAULT_INCOME_CATEGORIES = [
  "급여", "부수입", "용돈", "투자수익", "기타수입",
] as const;

// 카테고리 → Material Symbol 아이콘 매핑
export const CATEGORY_ICONS: Record<string, string> = {
  식비: "restaurant",
  교통: "directions_car",
  "주거/통신": "home",
  쇼핑: "shopping_bag",
  "문화/여가": "sports_esports",
  "의료/건강": "local_hospital",
  교육: "school",
  경조사: "card_giftcard",
  보험: "shield",
  기타지출: "more_horiz",
  급여: "payments",
  부수입: "work",
  용돈: "wallet",
  투자수익: "trending_up",
  기타수입: "add_circle",
};
