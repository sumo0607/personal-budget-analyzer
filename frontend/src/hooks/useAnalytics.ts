"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function useSummary(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "summary", startDate, endDate],
    queryFn: () => analyticsApi.summary(startDate, endDate),
  });
}

export function useExpenseByCategory(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "expense-by-category", startDate, endDate],
    queryFn: () => analyticsApi.expenseByCategory(startDate, endDate),
  });
}

export function useExpenseByDate(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "expense-by-date", startDate, endDate],
    queryFn: () => analyticsApi.expenseByDate(startDate, endDate),
  });
}

export function useIncomeExpenseByMonth() {
  return useQuery({
    queryKey: ["analytics", "income-expense-by-month"],
    queryFn: () => analyticsApi.incomeExpenseByMonth(),
  });
}

export function useExpenseByPayment(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "expense-by-payment", startDate, endDate],
    queryFn: () => analyticsApi.expenseByPayment(startDate, endDate),
  });
}

export function useExpenseByDayOfWeek(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "expense-by-dayofweek", startDate, endDate],
    queryFn: () => analyticsApi.expenseByDayOfWeek(startDate, endDate),
  });
}

export function useInsights(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: ["analytics", "insights", startDate, endDate],
    queryFn: () => analyticsApi.insights(startDate, endDate),
  });
}

export function useBudgetStatus(month: string) {
  return useQuery({
    queryKey: ["analytics", "budget-status", month],
    queryFn: () => analyticsApi.budgetStatus(month),
    enabled: !!month,
  });
}
