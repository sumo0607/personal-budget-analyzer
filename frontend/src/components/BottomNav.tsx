"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", icon: "home", label: "대시보드" },
  { href: "/transactions/new", icon: "edit_square", label: "입력" },
  { href: "/transactions", icon: "receipt_long", label: "내역" },
  { href: "/analytics", icon: "leaderboard", label: "분석" },
  { href: "/settings", icon: "settings", label: "설정" },
] as const;

export default function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-[#f8f9fa]/80 backdrop-blur-xl rounded-t-[1.5rem] border-t border-[#c0c8cd]/20 shadow-[0_-4px_24px_rgba(0,71,94,0.06)]">
      <div className="flex justify-around items-center px-4 pb-6 pt-3 w-full max-w-md mx-auto">
        {NAV_ITEMS.map((item) => {
          const isActive = 
            pathname === item.href || 
            (item.href === "/transactions" && pathname === "/transactions" ) ||
            (item.href === "/transactions/new" && pathname.startsWith("/transactions/new"));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center justify-center px-3 py-1.5 transition-all duration-300 active:scale-90",
                isActive
                  ? "bg-primary text-white rounded-xl"
                  : "text-on-surface-variant hover:text-primary",
              )}
            >
              <span
                className="material-symbols-outlined"
                style={isActive ? { fontVariationSettings: "'FILL' 1" } : undefined}
              >
                {item.icon}
              </span>
              <span className="font-label text-[10px] font-semibold uppercase tracking-wider mt-1">
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
