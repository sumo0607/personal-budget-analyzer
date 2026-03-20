"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { budgetApi } from "@/lib/api";

export function useBudgets(month?: string) {
  return useQuery({
    queryKey: ["budgets", month],
    queryFn: () => budgetApi.list(month),
  });
}

export function useSetBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ month, category, amount }: { month: string; category: string; amount: number }) =>
      budgetApi.set(month, category, amount),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["analytics", "budget-status"] });
    },
  });
}

export function useDeleteBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => budgetApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["analytics", "budget-status"] });
    },
  });
}
