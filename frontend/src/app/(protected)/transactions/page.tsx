"use client";

import { useState, useMemo } from "react";
import { useTransactions, useDeleteTransaction } from "@/hooks/useTransactions";
import { useFilterStore } from "@/stores/filter";
import { formatCurrency, formatCurrencyShort, formatDateKorean } from "@/lib/utils";
import { CATEGORY_ICONS } from "@/types";
import { toast } from "sonner";

const PAGE_SIZE = 20;

export default function TransactionHistoryPage() {
  const { filter, setFilter } = useFilterStore();
  const [keyword, setKeyword] = useState(filter.keyword ?? "");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const { data: transactions, isLoading } = useTransactions(filter);
  const deleteMut = useDeleteTransaction();

  // 키워드 필터는 로컬 debounce 대신 간단하게 처리
  const handleSearch = () => setFilter({ keyword: keyword || undefined });

  // 삭제 처리
  const handleDelete = (id: number) => {
    if (!confirm("이 거래를 삭제하시겠습니까?")) return;
    deleteMut.mutate(id, {
      onSuccess: () => toast.success("삭제되었습니다"),
      onError: (e) => toast.error(e.message),
    });
  };

  // 요약 지표 계산
  const summary = useMemo(() => {
    const txs = transactions ?? [];
    const income = txs.filter((t) => t.type === "income").reduce((s, t) => s + t.amount, 0);
    const expense = txs.filter((t) => t.type === "expense").reduce((s, t) => s + t.amount, 0);
    return { count: txs.length, income, expense };
  }, [transactions]);

  const visibleTx = (transactions ?? []).slice(0, visibleCount);
  const hasMore = visibleCount < (transactions?.length ?? 0);

  return (
    <div className="space-y-6 mt-4">
      {/* Section Header */}
      <div className="flex flex-col space-y-1">
        <h2 className="font-headline font-extrabold text-2xl tracking-tight text-primary">거래 내역</h2>
        <p className="text-on-surface-variant text-sm font-medium">Household Account Analysis</p>
      </div>

      {/* Filter Bar */}
      <section className="bg-surface-container-lowest rounded-xl p-4 shadow-sm space-y-4">
        <div className="flex items-center gap-2 bg-surface-container-low px-3 py-2 rounded-lg">
          <span className="material-symbols-outlined text-outline text-sm">search</span>
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="bg-transparent border-none focus:ring-0 text-sm w-full placeholder:text-outline-variant"
            placeholder="메모 검색"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
          {/* Date Range Chip */}
          <button
            onClick={() => {
              const start = prompt("시작일 (YYYY-MM-DD):", filter.start_date ?? "");
              const end = prompt("종료일 (YYYY-MM-DD):", filter.end_date ?? "");
              if (start !== null && end !== null) setFilter({ start_date: start || undefined, end_date: end || undefined });
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${
              filter.start_date ? "bg-primary text-white" : "bg-surface-container-high text-on-surface-variant"
            }`}
          >
            <span>날짜 범위</span>
            <span className="material-symbols-outlined text-[14px]">calendar_today</span>
          </button>

          {/* Type Chips */}
          {(["전체", "expense", "income"] as const).map((t) => {
            const label = t === "전체" ? "전체" : t === "expense" ? "지출" : "수입";
            const isActive = (t === "전체" && !filter.type) || filter.type === t;
            return (
              <button
                key={t}
                onClick={() => setFilter({ type: t === "전체" ? undefined : t })}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${
                  isActive ? "bg-primary text-white" : "bg-surface-container-high text-on-surface-variant"
                }`}
              >
                {label}
              </button>
            );
          })}

          {/* Reset */}
          {(filter.start_date || filter.type || filter.keyword) && (
            <button
              onClick={() => {
                useFilterStore.getState().resetFilter();
                setKeyword("");
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-high text-on-surface-variant text-xs font-semibold whitespace-nowrap"
            >
              <span className="material-symbols-outlined text-[14px]">filter_list_off</span>
              <span>초기화</span>
            </button>
          )}
        </div>
      </section>

      {/* Summary Metrics */}
      <section className="grid grid-cols-3 gap-3">
        <div className="bg-surface-container-lowest p-3 rounded-xl shadow-sm flex flex-col items-center justify-center text-center">
          <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant mb-1">조회건수</span>
          <span className="font-headline font-bold text-lg text-primary">{summary.count}</span>
        </div>
        <div className="bg-surface-container-lowest p-3 rounded-xl shadow-sm flex flex-col items-center justify-center text-center border-l-4 border-secondary">
          <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant mb-1">수입합계</span>
          <span className="font-headline font-bold text-sm text-secondary">+{formatCurrencyShort(summary.income)}</span>
        </div>
        <div className="bg-surface-container-lowest p-3 rounded-xl shadow-sm flex flex-col items-center justify-center text-center border-l-4 border-error">
          <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant mb-1">지출합계</span>
          <span className="font-headline font-bold text-sm text-error">-{formatCurrencyShort(summary.expense)}</span>
        </div>
      </section>

      {/* Transaction List */}
      <section className="space-y-4">
        <div className="flex items-center justify-between px-2">
          <h3 className="font-headline font-bold text-sm text-on-surface">최근 거래 현황</h3>
          <span className="text-[10px] font-bold text-outline-variant uppercase">Latest First</span>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="space-y-3">
            {visibleTx.map((tx) => (
              <div
                key={tx.id}
                className="bg-surface-container-lowest rounded-xl p-4 shadow-sm flex items-center justify-between group"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      tx.type === "income"
                        ? "bg-secondary-container text-on-secondary-container"
                        : "bg-surface-container-high text-primary"
                    }`}
                  >
                    <span className="material-symbols-outlined">
                      {CATEGORY_ICONS[tx.category] ?? "payments"}
                    </span>
                  </div>
                  <div>
                    <p className="font-bold text-sm text-on-background">{tx.memo || tx.category}</p>
                    <p className="text-[11px] text-on-surface-variant flex items-center gap-2">
                      <span className={`font-semibold ${tx.type === "income" ? "text-secondary" : "text-error"}`}>
                        {tx.type === "income" ? "수입" : "지출"}
                      </span>
                      <span className="w-1 h-1 bg-outline-variant rounded-full" />
                      <span>{formatDateKorean(tx.date)}</span>
                    </p>
                  </div>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div>
                    <p className={`font-headline font-bold text-base ${tx.type === "income" ? "text-secondary" : "text-on-surface"}`}>
                      {tx.type === "income" ? "+" : ""}₩{tx.amount.toLocaleString("ko-KR")}
                    </p>
                    <p className="text-[10px] text-outline uppercase tracking-tight">{tx.payment_method}</p>
                  </div>
                  <button
                    onClick={() => handleDelete(tx.id)}
                    className="p-1 rounded-full hover:bg-surface-container transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <span className="material-symbols-outlined text-on-surface-variant">more_vert</span>
                  </button>
                </div>
              </div>
            ))}

            {visibleTx.length === 0 && (
              <p className="text-center text-on-surface-variant py-12 text-sm">조건에 맞는 거래가 없습니다</p>
            )}
          </div>
        )}

        {/* View More */}
        {hasMore && (
          <button
            onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
            className="w-full py-4 text-xs font-bold text-primary uppercase tracking-widest bg-surface-container-low rounded-xl hover:bg-surface-container transition-colors"
          >
            더 보기 (View More)
          </button>
        )}
      </section>
    </div>
  );
}
