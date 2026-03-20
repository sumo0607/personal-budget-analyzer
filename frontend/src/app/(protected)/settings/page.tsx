"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuthStore } from "@/stores/auth";
import { useFilterStore } from "@/stores/filter";
import { useCategories, useCreateCategory, useDeleteCategory } from "@/hooks/useCategories";
import { useBudgets, useSetBudget, useDeleteBudget } from "@/hooks/useBudgets";
import { authApi } from "@/lib/api";
import { currentMonth, formatCurrency } from "@/lib/utils";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const selectedMonth = useFilterStore((s) => s.selectedMonth);
  const setSelectedMonth = useFilterStore((s) => s.setSelectedMonth);
  const router = useRouter();

  const [activeSection, setActiveSection] = useState<"budget" | "category" | "account">("budget");

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore
    }
    clearAuth();
    router.push("/login");
    toast.success("로그아웃되었습니다");
  };

  return (
    <div className="space-y-6 mt-4">
      {/* Header */}
      <div className="space-y-1">
        <p className="text-[10px] font-bold uppercase tracking-widest text-secondary font-label">Settings</p>
        <h2 className="text-3xl font-headline font-extrabold text-primary tracking-tight">설정</h2>
      </div>

      {/* User Info Card */}
      <div className="bg-surface-container-lowest rounded-xl p-5 shadow-sm flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-lg">
          {user?.username?.charAt(0).toUpperCase() ?? "U"}
        </div>
        <div className="flex-1">
          <p className="font-bold text-on-surface">{user?.username ?? "사용자"}</p>
          <p className="text-xs text-on-surface-variant">{user?.role === "admin" ? "관리자" : "일반 사용자"}</p>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 rounded-lg bg-surface-container-high text-on-surface-variant text-sm font-semibold hover:bg-surface-container transition-colors"
        >
          로그아웃
        </button>
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2">
        {(["budget", "category", "account"] as const).map((s) => {
          const labels = { budget: "예산 관리", category: "카테고리", account: "계정" };
          return (
            <button
              key={s}
              onClick={() => setActiveSection(s)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-all ${
                activeSection === s
                  ? "bg-primary text-white shadow-md"
                  : "bg-surface-container-high text-on-surface-variant"
              }`}
            >
              {labels[s]}
            </button>
          );
        })}
      </div>

      {activeSection === "budget" && <BudgetSection month={selectedMonth} onMonthChange={setSelectedMonth} />}
      {activeSection === "category" && <CategorySection />}
      {activeSection === "account" && (
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm space-y-4">
          <h3 className="font-headline font-bold text-primary">계정 관리</h3>
          <p className="text-sm text-on-surface-variant">
            아이디: <span className="font-bold text-on-surface">{user?.username}</span>
          </p>
          <p className="text-sm text-on-surface-variant">
            권한: <span className="font-bold text-on-surface">{user?.role}</span>
          </p>
        </div>
      )}
    </div>
  );
}

// ── Budget Management Section ──
function BudgetSection({ month, onMonthChange }: { month: string; onMonthChange: (m: string) => void }) {
  const { data: budgets } = useBudgets(month);
  const setBudget = useSetBudget();
  const deleteBudget = useDeleteBudget();
  const [newCat, setNewCat] = useState("");
  const [newAmt, setNewAmt] = useState("");

  const handleAdd = () => {
    if (!newCat || !newAmt) return;
    setBudget.mutate(
      { month, category: newCat, amount: Number(newAmt) },
      {
        onSuccess: () => {
          toast.success("예산이 설정되었습니다");
          setNewCat("");
          setNewAmt("");
        },
      },
    );
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="font-headline font-bold text-primary">예산 관리</h3>
        <input
          type="month"
          value={month}
          onChange={(e) => onMonthChange(e.target.value)}
          className="bg-surface-container-high border-none rounded-lg px-3 py-2 text-sm font-medium"
        />
      </div>

      {/* Add Budget */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newCat}
          onChange={(e) => setNewCat(e.target.value)}
          placeholder="카테고리"
          className="flex-1 bg-surface-container-high border-none rounded-lg px-3 py-2.5 text-sm"
        />
        <input
          type="number"
          value={newAmt}
          onChange={(e) => setNewAmt(e.target.value)}
          placeholder="금액"
          className="w-28 bg-surface-container-high border-none rounded-lg px-3 py-2.5 text-sm"
        />
        <button
          onClick={handleAdd}
          disabled={setBudget.isPending}
          className="px-4 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold active:scale-95 transition-all disabled:opacity-60"
        >
          추가
        </button>
      </div>

      {/* Budget List */}
      <div className="space-y-3">
        {budgets?.map((b) => (
          <div key={b.id} className="flex items-center justify-between py-3 px-1">
            <div>
              <p className="font-bold text-sm">{b.category || "전체"}</p>
              <p className="text-xs text-on-surface-variant">{month}</p>
            </div>
            <div className="flex items-center gap-3">
              <p className="font-headline font-bold text-primary">{formatCurrency(b.budget_amount)}</p>
              <button
                onClick={() => deleteBudget.mutate(b.id, { onSuccess: () => toast.success("삭제됨") })}
                className="p-1 rounded-full hover:bg-error-container transition-colors"
              >
                <span className="material-symbols-outlined text-error text-lg">delete</span>
              </button>
            </div>
          </div>
        ))}
        {(!budgets || budgets.length === 0) && (
          <p className="text-sm text-on-surface-variant text-center py-4">설정된 예산이 없습니다</p>
        )}
      </div>
    </div>
  );
}

// ── Category Management Section ──
function CategorySection() {
  const [catType, setCatType] = useState<"expense" | "income">("expense");
  const { data: categories } = useCategories(catType);
  const createCat = useCreateCategory();
  const deleteCat = useDeleteCategory();
  const [newName, setNewName] = useState("");

  const handleAdd = () => {
    if (!newName.trim()) return;
    createCat.mutate(
      { type: catType, name: newName.trim() },
      {
        onSuccess: () => {
          toast.success("카테고리가 추가되었습니다");
          setNewName("");
        },
        onError: (e) => toast.error(e.message),
      },
    );
  };

  return (
    <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm space-y-6">
      <h3 className="font-headline font-bold text-primary">카테고리 관리</h3>

      {/* Type Toggle */}
      <div className="flex bg-surface-container-low p-1 rounded-xl">
        <button
          onClick={() => setCatType("expense")}
          className={`flex-1 py-2 text-center rounded-lg text-sm font-semibold transition-all ${
            catType === "expense" ? "bg-primary text-white" : "text-on-surface-variant"
          }`}
        >
          지출
        </button>
        <button
          onClick={() => setCatType("income")}
          className={`flex-1 py-2 text-center rounded-lg text-sm font-semibold transition-all ${
            catType === "income" ? "bg-secondary text-white" : "text-on-surface-variant"
          }`}
        >
          수입
        </button>
      </div>

      {/* Add */}
      <div className="flex gap-2">
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder="새 카테고리 이름"
          className="flex-1 bg-surface-container-high border-none rounded-lg px-3 py-2.5 text-sm"
        />
        <button
          onClick={handleAdd}
          disabled={createCat.isPending}
          className="px-4 py-2.5 bg-primary text-white rounded-lg text-sm font-semibold active:scale-95 transition-all disabled:opacity-60"
        >
          추가
        </button>
      </div>

      {/* List */}
      <div className="space-y-2">
        {categories?.map((c) => (
          <div key={c.id} className="flex items-center justify-between py-2 px-1">
            <span className="text-sm font-medium">{c.name}</span>
            <button
              onClick={() =>
                deleteCat.mutate(
                  { type: catType, name: c.name },
                  { onSuccess: () => toast.success("삭제됨") },
                )
              }
              className="p-1 rounded-full hover:bg-error-container transition-colors"
            >
              <span className="material-symbols-outlined text-error text-lg">close</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
