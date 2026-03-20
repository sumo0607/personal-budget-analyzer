import { create } from "zustand";
import type { TransactionFilter } from "@/types";
import { currentMonth } from "@/lib/utils";

interface FilterState {
  filter: TransactionFilter;
  setFilter: (partial: Partial<TransactionFilter>) => void;
  resetFilter: () => void;
  selectedMonth: string;
  setSelectedMonth: (m: string) => void;
}

const defaultFilter: TransactionFilter = {
  sort_by: "date",
  sort_order: "desc",
};

export const useFilterStore = create<FilterState>()((set) => ({
  filter: defaultFilter,
  setFilter: (partial) =>
    set((s) => ({ filter: { ...s.filter, ...partial } })),
  resetFilter: () => set({ filter: defaultFilter }),
  selectedMonth: currentMonth(),
  setSelectedMonth: (m) => set({ selectedMonth: m }),
}));
