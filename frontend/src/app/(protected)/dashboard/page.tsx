"use client";

import Link from "next/link";
import { useSummary, useExpenseByCategory, useIncomeExpenseByMonth, useInsights, useBudgetStatus } from "@/hooks/useAnalytics";
import { useTransactions } from "@/hooks/useTransactions";
import { useFilterStore } from "@/stores/filter";
import { formatCurrency, formatCurrencyShort, formatDateKorean } from "@/lib/utils";
import { CATEGORY_ICONS } from "@/types";
import type { BudgetStatus, ChartDataPoint } from "@/types";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid,
} from "recharts";

export default function DashboardPage() {
  const selectedMonth = useFilterStore((s: { selectedMonth: string }) => s.selectedMonth);

  // 이번 달 시작일/마지막일
  const startDate = `${selectedMonth}-01`;
  const endOfMonth = new Date(Number(selectedMonth.split("-")[0]), Number(selectedMonth.split("-")[1]), 0);
  const endDate = `${selectedMonth}-${String(endOfMonth.getDate()).padStart(2, "0")}`;

  const { data: summary } = useSummary(startDate, endDate);
  const { data: categoryData } = useExpenseByCategory(startDate, endDate);
  const { data: monthlyData } = useIncomeExpenseByMonth();
  const { data: insights } = useInsights(startDate, endDate);
  const { data: budgetStatus } = useBudgetStatus(selectedMonth);
  const { data: recentTx } = useTransactions({ sort_by: "date", sort_order: "desc" });

  const totalIncome = summary?.total_income ?? 0;
  const totalExpense = summary?.total_expense ?? 0;
  const net = summary?.net ?? 0;
  const dailyAvg = summary?.daily_avg_expense ?? 0;

  // 예산 사용률 계산
  const totalBudget = budgetStatus?.reduce((s: number, b: BudgetStatus) => s + b.budget_amount, 0) ?? 0;
  const totalSpent = budgetStatus?.reduce((s: number, b: BudgetStatus) => s + b.spent, 0) ?? 0;
  const budgetPercent = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0;

  // 카테고리 비중 (상위 5개)
  const topCategories = categoryData?.slice(0, 5) ?? [];
  const totalCatExpense = topCategories.reduce((s: number, c: ChartDataPoint) => s + c.amount, 0);

  // 차트 데이터 (월별 지출 추이 — 최근 6개월)
  const chartData = (monthlyData ?? [])
    .filter((d: ChartDataPoint) => d.expense !== undefined)
    .slice(-6)
    .map((d: ChartDataPoint) => ({
      month: d.year_month?.slice(5) + "월",
      amount: d.expense ?? d.amount,
    }));

  // net 금액 분리 (hero display)
  const netAbs = Math.abs(net);
  const netMain = Math.floor(netAbs / 1000);
  const netSub = String(netAbs % 1000).padStart(3, "0");

  return (
    <div className="space-y-8 mt-4">
      {/* Hero Section: Total Balance */}
      <section>
        <p className="text-on-surface-variant font-label text-xs uppercase tracking-widest font-bold mb-1">
          이번 달 순수익
        </p>
        <div className="flex items-baseline gap-1">
          <h1 className="text-[3.5rem] font-headline font-extrabold text-primary tracking-tight leading-none">
            {net >= 0 ? "₩" : "-₩"}
            {netMain > 0 ? netMain.toLocaleString("ko-KR") : "0"}
          </h1>
          <span className="text-xl font-headline font-bold text-primary-container">
            ,{netSub}
          </span>
        </div>
      </section>

      {/* Metric Cards Bento Grid */}
      <section className="grid grid-cols-2 gap-4">
        {/* 총수입 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between h-32 shadow-[0_4px_20px_rgba(0,71,94,0.04)] border-l-4 border-secondary">
          <span className="material-symbols-outlined text-secondary text-2xl">account_balance_wallet</span>
          <div>
            <p className="text-on-surface-variant font-label text-[10px] font-bold uppercase">총수입</p>
            <p className="text-secondary font-headline font-bold text-lg leading-tight">
              {formatCurrency(totalIncome)}
            </p>
          </div>
        </div>
        {/* 총지출 */}
        <div className="bg-surface-container-lowest p-5 rounded-xl flex flex-col justify-between h-32 shadow-[0_4px_20px_rgba(0,71,94,0.04)]">
          <span className="material-symbols-outlined text-error text-2xl">receipt_long</span>
          <div>
            <p className="text-on-surface-variant font-label text-[10px] font-bold uppercase">총지출</p>
            <p className="text-error font-headline font-bold text-lg leading-tight">
              {formatCurrency(totalExpense)}
            </p>
          </div>
        </div>
        {/* 일평균지출 */}
        <div className="bg-surface-container-low p-5 rounded-xl flex flex-col justify-between h-32">
          <span className="material-symbols-outlined text-primary text-2xl">calendar_today</span>
          <div>
            <p className="text-on-surface-variant font-label text-[10px] font-bold uppercase">일평균지출</p>
            <p className="text-on-surface font-headline font-bold text-lg leading-tight">
              {formatCurrency(dailyAvg)}
            </p>
          </div>
        </div>
        {/* 예산 대비 */}
        <div className="bg-surface-container-low p-5 rounded-xl flex flex-col justify-between h-32">
          <span className="material-symbols-outlined text-primary text-2xl">bolt</span>
          <div>
            <p className="text-on-surface-variant font-label text-[10px] font-bold uppercase">예산 대비</p>
            <p className="text-on-surface font-headline font-bold text-lg leading-tight">
              {budgetPercent}% 사용
            </p>
          </div>
        </div>
      </section>

      {/* Chart Section: Trends */}
      <section className="space-y-4">
        <div className="flex justify-between items-end">
          <h2 className="text-xl font-headline font-bold text-primary tracking-tight">지출추이</h2>
          <span className="text-xs text-on-surface-variant font-label font-semibold">최근 6개월</span>
        </div>
        <div className="bg-primary-container rounded-3xl p-6 h-52 relative overflow-hidden">
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.15)" />
                <XAxis dataKey="month" tick={{ fill: "#c0e8ff", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis hide />
                <Tooltip
                  formatter={(v: number) => [formatCurrency(v), "지출"]}
                  contentStyle={{ background: "#1a5f7a", border: "none", borderRadius: 12, color: "#fff" }}
                />
                <Bar dataKey="amount" fill="#c0e8ff" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-primary-fixed-dim text-sm">
              데이터가 없습니다
            </div>
          )}
        </div>
      </section>

      {/* Category Breakdown */}
      <section className="space-y-4">
        <h2 className="text-xl font-headline font-bold text-primary tracking-tight">카테고리별 비중</h2>
        <div className="flex gap-4 overflow-x-auto no-scrollbar pb-2">
          {topCategories.length > 0 ? (
            topCategories.map((cat, i) => {
              const percent = totalCatExpense > 0 ? Math.round((cat.amount / totalCatExpense) * 100) : 0;
              const colors = ["border-primary", "border-tertiary", "border-secondary-fixed-dim", "border-secondary", "border-outline"];
              const textColors = ["text-primary", "text-tertiary", "text-secondary", "text-secondary", "text-outline"];
              return (
                <div key={cat.category} className={`min-w-[140px] bg-surface-container-lowest p-4 rounded-2xl shadow-sm border-l-4 ${colors[i % colors.length]}`}>
                  <span className={`material-symbols-outlined ${textColors[i % textColors.length]} mb-2`}>
                    {CATEGORY_ICONS[cat.category ?? ""] ?? "category"}
                  </span>
                  <p className="text-xs font-bold text-on-surface-variant">{cat.category}</p>
                  <p className="text-lg font-headline font-bold">{percent}%</p>
                </div>
              );
            })
          ) : (
            <p className="text-sm text-on-surface-variant">카테고리 데이터가 없습니다</p>
          )}
        </div>
      </section>

      {/* Recent Insights */}
      <section className="space-y-4">
        <h2 className="text-xl font-headline font-bold text-primary tracking-tight">Recent Insights</h2>
        <div className="space-y-3">
          {insights && insights.length > 0 ? (
            insights.slice(0, 4).map((insight, i) => {
              const isError = insight.type === "error" || insight.type === "warning";
              return (
                <div
                  key={i}
                  className={`flex items-start gap-4 p-4 rounded-2xl ${
                    isError ? "bg-error-container" : "bg-secondary-container"
                  }`}
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                      isError ? "bg-error" : "bg-on-secondary-container"
                    }`}
                  >
                    <span
                      className={`material-symbols-outlined text-xl ${
                        isError ? "text-error-container" : "text-secondary-container"
                      }`}
                      style={{ fontVariationSettings: "'FILL' 1" }}
                    >
                      {isError ? "warning" : insight.type === "success" ? "check_circle" : "trending_down"}
                    </span>
                  </div>
                  <div>
                    <h3 className={`font-bold text-sm ${isError ? "text-on-error-container" : "text-on-secondary-container"}`}>
                      {insight.type === "success" ? "절약 성공!" : isError ? "주의" : "인사이트"}
                    </h3>
                    <p className={`text-xs mt-0.5 ${isError ? "text-on-error-container/80" : "text-on-secondary-container/80"}`}>
                      {insight.message}
                    </p>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-sm text-on-surface-variant p-4">인사이트를 생성 중입니다…</p>
          )}
        </div>
      </section>

      {/* FAB */}
      <Link
        href="/transactions/new"
        className="fixed bottom-24 right-6 w-14 h-14 bg-primary text-white rounded-full shadow-lg flex items-center justify-center z-40 active:scale-95 transition-transform duration-200"
      >
        <span className="material-symbols-outlined text-3xl">add</span>
      </Link>
    </div>
  );
}
