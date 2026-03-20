"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useCreateTransaction } from "@/hooks/useTransactions";
import { useCategories } from "@/hooks/useCategories";
import { useTransactions } from "@/hooks/useTransactions";
import { PAYMENT_METHODS, CATEGORY_ICONS } from "@/types";
import { todayString, formatCurrency, formatDateKorean } from "@/lib/utils";

const schema = z.object({
  date: z.string().min(1, "날짜를 선택하세요"),
  amount: z.coerce.number().positive("금액을 입력하세요"),
  category: z.string().min(1, "카테고리를 선택하세요"),
  payment_method: z.string().min(1, "결제수단을 선택하세요"),
  memo: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

export default function NewTransactionPage() {
  const [txType, setTxType] = useState<"expense" | "income">("expense");
  const createMut = useCreateTransaction();

  const { data: categories } = useCategories(txType);
  const { data: recentTx } = useTransactions({ sort_by: "date", sort_order: "desc" });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      date: todayString(),
      amount: undefined,
      category: "",
      payment_method: PAYMENT_METHODS[0],
      memo: "",
    },
  });

  const onSubmit = (data: FormData) => {
    createMut.mutate(
      { ...data, type: txType, memo: data.memo ?? "" },
      {
        onSuccess: () => {
          toast.success("거래가 저장되었습니다");
          reset({ date: todayString(), amount: undefined, category: "", payment_method: PAYMENT_METHODS[0], memo: "" });
        },
        onError: (err) => toast.error(err.message),
      },
    );
  };

  const categoryNames = categories?.map((c) => c.name) ?? [];
  const recent5 = (recentTx ?? []).slice(0, 5);

  return (
    <div className="space-y-8 mt-4">
      {/* Section Header */}
      <header className="space-y-1">
        <p className="text-[10px] font-bold uppercase tracking-widest text-secondary font-label">Entry Module</p>
        <h2 className="text-3xl font-headline font-extrabold text-primary tracking-tight">거래 입력</h2>
      </header>

      {/* Transaction Form */}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-surface-container-lowest rounded-xl p-6 shadow-[0_-4px_24px_rgba(0,71,94,0.04)] space-y-6"
      >
        {/* Type Radio Group */}
        <div className="flex bg-surface-container-low p-1 rounded-xl">
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              className="hidden peer"
              checked={txType === "expense"}
              onChange={() => setTxType("expense")}
            />
            <div className="py-2 text-center rounded-lg text-sm font-semibold transition-all peer-checked:bg-primary peer-checked:text-white text-on-surface-variant">
              지출
            </div>
          </label>
          <label className="flex-1 cursor-pointer">
            <input
              type="radio"
              className="hidden peer"
              checked={txType === "income"}
              onChange={() => setTxType("income")}
            />
            <div className="py-2 text-center rounded-lg text-sm font-semibold transition-all peer-checked:bg-secondary peer-checked:text-white text-on-surface-variant">
              수입
            </div>
          </label>
        </div>

        <div className="space-y-4">
          {/* Date */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">날짜</label>
            <div className="relative">
              <input
                type="date"
                {...register("date")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
              />
              <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 text-outline pointer-events-none">
                calendar_today
              </span>
            </div>
            {errors.date && <p className="text-error text-xs px-1">{errors.date.message}</p>}
          </div>

          {/* Amount */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">금액</label>
            <div className="relative">
              <input
                type="number"
                placeholder="0"
                {...register("amount")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface text-2xl font-headline font-bold focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline-variant"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-on-surface-variant font-bold">₩</span>
            </div>
            {errors.amount && <p className="text-error text-xs px-1">{errors.amount.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Category */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">카테고리</label>
              <select
                {...register("category")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all appearance-none"
              >
                <option value="">선택</option>
                {categoryNames.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
              {errors.category && <p className="text-error text-xs px-1">{errors.category.message}</p>}
            </div>

            {/* Payment Method */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">결제수단</label>
              <select
                {...register("payment_method")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all appearance-none"
              >
                {PAYMENT_METHODS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Memo */}
          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">메모</label>
            <textarea
              {...register("memo")}
              rows={2}
              placeholder="거래 내용을 입력하세요"
              className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline-variant resize-none"
            />
          </div>
        </div>

        {/* Save Button */}
        <button
          type="submit"
          disabled={createMut.isPending}
          className="w-full bg-primary text-on-primary py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/20 active:scale-[0.98] transition-all duration-200 disabled:opacity-60"
        >
          {createMut.isPending ? "저장 중…" : "저장"}
        </button>
      </form>

      {/* Recent Entries */}
      <section className="space-y-4 pb-12">
        <div className="flex items-center justify-between px-1">
          <h3 className="font-headline font-bold text-primary">최근 내역</h3>
          <a href="/transactions" className="text-[10px] font-bold uppercase tracking-wider text-outline">전체보기</a>
        </div>
        <div className="space-y-3">
          {recent5.map((tx) => (
            <div
              key={tx.id}
              className="bg-surface-container-lowest p-4 rounded-xl flex items-center justify-between active:scale-95 transition-all"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    tx.type === "income"
                      ? "bg-secondary-container text-secondary"
                      : "bg-surface-container-high text-primary"
                  }`}
                >
                  <span className="material-symbols-outlined">
                    {CATEGORY_ICONS[tx.category] ?? "payments"}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-bold text-on-surface">{tx.memo || tx.category}</p>
                  <p className="text-[10px] text-outline font-medium">
                    {formatDateKorean(tx.date)} • {tx.payment_method}
                  </p>
                </div>
              </div>
              <p className={`font-headline font-bold ${tx.type === "income" ? "text-secondary" : "text-error"}`}>
                {tx.type === "income" ? "+" : "-"}
                {tx.amount.toLocaleString("ko-KR")}
              </p>
            </div>
          ))}
          {recent5.length === 0 && (
            <p className="text-sm text-on-surface-variant text-center py-8">아직 거래 내역이 없습니다</p>
          )}
        </div>
      </section>
    </div>
  );
}
