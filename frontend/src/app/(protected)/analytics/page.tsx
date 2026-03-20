"use client";

import { useState } from "react";
import {
  useSummary,
  useExpenseByCategory,
  useExpenseByDate,
  useIncomeExpenseByMonth,
  useExpenseByPayment,
  useExpenseByDayOfWeek,
  useInsights,
  useBudgetStatus,
} from "@/hooks/useAnalytics";
import { useFilterStore } from "@/stores/filter";
import { formatCurrency } from "@/lib/utils";
import {
  BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, LineChart, Line,
} from "recharts";

const TABS = ["지출추이", "카테고리비중", "결제수단별", "요일별", "월별비교"] as const;
type TabKey = (typeof TABS)[number];

const PIE_COLORS = ["#00475e", "#006b5f", "#1a5f7a", "#2f444d", "#70787d", "#92cfee", "#70d8c8"];

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("지출추이");
  const selectedMonth = useFilterStore((s) => s.selectedMonth);
  const startDate = `${selectedMonth}-01`;
  const endOfMonth = new Date(Number(selectedMonth.split("-")[0]), Number(selectedMonth.split("-")[1]), 0);
  const endDate = `${selectedMonth}-${String(endOfMonth.getDate()).padStart(2, "0")}`;

  const { data: summary } = useSummary(startDate, endDate);
  const { data: byCategory } = useExpenseByCategory(startDate, endDate);
  const { data: byDate } = useExpenseByDate(startDate, endDate);
  const { data: byMonth } = useIncomeExpenseByMonth();
  const { data: byPayment } = useExpenseByPayment(startDate, endDate);
  const { data: byDayOfWeek } = useExpenseByDayOfWeek(startDate, endDate);
  const { data: insights } = useInsights(startDate, endDate);
  const { data: budgetStatus } = useBudgetStatus(selectedMonth);

  const totalExpense = summary?.total_expense ?? 0;

  // 차트 데이터 처리
  const trendData = (byDate ?? []).map((d) => ({
    date: d.date?.slice(5),
    amount: d.amount,
  }));

  const categoryPieData = (byCategory ?? []).map((d) => ({
    name: d.category,
    value: d.amount,
  }));

  const paymentData = (byPayment ?? []).map((d) => ({
    name: d.payment_method,
    amount: d.amount,
  }));

  const dayOfWeekData = (byDayOfWeek ?? []).map((d) => ({
    day: d.day_korean,
    amount: d.amount,
  }));

  const monthlyCompare = (byMonth ?? []).slice(-6).map((d) => ({
    month: d.year_month?.slice(5) + "월",
    income: d.income ?? 0,
    expense: d.expense ?? d.amount,
  }));

  return (
    <div className="space-y-8 mt-4">
      {/* Hero Section */}
      <section>
        <p className="text-on-surface-variant font-label text-xs uppercase tracking-widest mb-1">소비 분석</p>
        <div className="relative overflow-hidden p-6 rounded-xl bg-gradient-to-br from-primary to-primary-container text-white shadow-xl">
          <div className="absolute -right-4 -top-4 w-32 h-32 bg-white/10 rounded-full blur-2xl" />
          <h2 className="font-headline text-3xl font-extrabold tracking-tight">
            {formatCurrency(totalExpense)}
          </h2>
          <p className="text-primary-fixed text-sm font-medium mt-1">
            이번 달 총 지출 금액
          </p>
        </div>
      </section>

      {/* Analytic Tabs */}
      <section>
        <div className="flex overflow-x-auto no-scrollbar gap-2 pb-2">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                activeTab === tab
                  ? "bg-primary text-white shadow-md"
                  : "bg-surface-container-high text-on-surface-variant"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Chart Canvas */}
        <div className="mt-4 bg-surface-container-lowest rounded-xl p-5 shadow-sm min-h-[260px]">
          {activeTab === "지출추이" && (
            <>
              <h3 className="font-bold text-on-surface mb-1">일별 지출 추이</h3>
              <p className="text-xs text-on-surface-variant mb-4">{selectedMonth}</p>
              {trendData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e1e3e4" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis hide />
                    <Tooltip formatter={(v: number) => [formatCurrency(v), "지출"]} />
                    <Line type="monotone" dataKey="amount" stroke="#00475e" strokeWidth={2} dot={{ r: 3, fill: "#00475e" }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </>
          )}

          {activeTab === "카테고리비중" && (
            <>
              <h3 className="font-bold text-on-surface mb-4">카테고리별 비중</h3>
              {categoryPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={categoryPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                      {categoryPieData.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v: number) => formatCurrency(v)} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </>
          )}

          {activeTab === "결제수단별" && (
            <>
              <h3 className="font-bold text-on-surface mb-4">결제수단별 지출</h3>
              {paymentData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={paymentData} layout="vertical" barCategoryGap="25%">
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} width={60} />
                    <Tooltip formatter={(v: number) => formatCurrency(v)} />
                    <Bar dataKey="amount" fill="#006b5f" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </>
          )}

          {activeTab === "요일별" && (
            <>
              <h3 className="font-bold text-on-surface mb-4">요일별 평균 지출</h3>
              {dayOfWeekData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={dayOfWeekData} barCategoryGap="20%">
                    <XAxis dataKey="day" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis hide />
                    <Tooltip formatter={(v: number) => [formatCurrency(v), "평균"]} />
                    <Bar dataKey="amount" fill="#1a5f7a" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </>
          )}

          {activeTab === "월별비교" && (
            <>
              <h3 className="font-bold text-on-surface mb-4">월별 수입/지출 비교</h3>
              {monthlyCompare.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={monthlyCompare} barCategoryGap="15%">
                    <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis hide />
                    <Tooltip formatter={(v: number) => formatCurrency(v)} />
                    <Bar dataKey="income" fill="#006b5f" radius={[4, 4, 0, 0]} name="수입" />
                    <Bar dataKey="expense" fill="#00475e" radius={[4, 4, 0, 0]} name="지출" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyChart />
              )}
            </>
          )}
        </div>
      </section>

      {/* AI Insights Bento Grid */}
      <section>
        <h3 className="font-headline font-bold text-lg mb-4 px-1">AI 통찰</h3>
        <div className="grid grid-cols-2 gap-4">
          {insights && insights.length > 0 && (
            <div className="col-span-2 p-4 bg-secondary-container text-on-secondary-container rounded-xl flex items-start gap-3">
              <span className="material-symbols-outlined text-secondary">lightbulb</span>
              <div>
                <p className="font-bold text-sm">{insights[0].message}</p>
              </div>
            </div>
          )}
          {/* Savings card */}
          <div className="p-4 bg-surface-container-lowest rounded-xl shadow-sm">
            <span className="material-symbols-outlined text-primary mb-2">savings</span>
            <p className="text-[10px] text-on-surface-variant uppercase font-bold tracking-tighter">순수익</p>
            <p className="text-lg font-bold">{formatCurrency(summary?.net ?? 0)}</p>
          </div>
          {/* Warning category */}
          <div className="p-4 bg-surface-container-lowest rounded-xl shadow-sm border-l-4 border-error">
            <span className="material-symbols-outlined text-error mb-2">warning</span>
            <p className="text-[10px] text-on-surface-variant uppercase font-bold tracking-tighter">TOP 카테고리</p>
            <p className="text-lg font-bold">
              {summary?.top_categories?.[0]?.category ?? "-"}
            </p>
          </div>
        </div>
      </section>

      {/* Budget Status */}
      <section className="pb-8">
        <div className="flex justify-between items-end mb-4 px-1">
          <h3 className="font-headline font-bold text-lg">예산 현황</h3>
          <a href="/settings" className="text-primary text-xs font-bold">상세보기</a>
        </div>
        <div className="space-y-6">
          {budgetStatus && budgetStatus.length > 0 ? (
            budgetStatus.map((b) => {
              const pct = Math.min(b.usage_percent, 100);
              const isOver = b.usage_percent > 100;
              const isNear = b.usage_percent > 85 && !isOver;
              const color = isOver ? "error" : isNear ? "primary" : "secondary";
              return (
                <div key={b.category} className="bg-surface-container-lowest p-4 rounded-xl shadow-sm">
                  <div className="flex justify-between mb-2">
                    <span className="font-bold text-sm">{b.category}</span>
                    <span className={`text-xs text-${color} font-bold`}>
                      {Math.round(b.usage_percent)}% 사용
                    </span>
                  </div>
                  <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
                    <div
                      className={`bg-${color} h-full rounded-full transition-all duration-500`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="flex justify-between mt-2 text-[10px] text-on-surface-variant">
                    <span>
                      {formatCurrency(b.spent)} / {formatCurrency(b.budget_amount)}
                    </span>
                    <span className={`font-medium text-${color}`}>
                      {isOver
                        ? `${formatCurrency(b.spent - b.budget_amount)} 초과`
                        : `${formatCurrency(b.remaining)} 남음`}
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-sm text-on-surface-variant text-center py-8">
              설정된 예산이 없습니다. 설정 페이지에서 예산을 추가하세요.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

function EmptyChart() {
  return (
    <div className="flex items-center justify-center h-40 text-on-surface-variant text-sm">
      데이터가 없습니다
    </div>
  );
}
