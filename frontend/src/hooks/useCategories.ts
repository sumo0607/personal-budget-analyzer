"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoryApi } from "@/lib/api";

export function useCategories(type?: "income" | "expense") {
  return useQuery({
    queryKey: ["categories", type],
    queryFn: () => categoryApi.list(type),
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ type, name }: { type: "income" | "expense"; name: string }) =>
      categoryApi.create(type, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ type, name }: { type: "income" | "expense"; name: string }) =>
      categoryApi.delete(type, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}
