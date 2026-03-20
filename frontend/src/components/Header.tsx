"use client";

import { useAuthStore } from "@/stores/auth";

export default function Header() {
  const user = useAuthStore((s) => s.user);

  return (
    <header className="fixed top-0 w-full z-50 bg-[#f8f9fa]/80 backdrop-blur-md bg-gradient-to-b from-[#f8f9fa] to-transparent shadow-none">
      <div className="flex justify-between items-center px-6 h-16 w-full max-w-md mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-fixed overflow-hidden flex items-center justify-center text-primary font-bold text-sm">
            {user?.username?.charAt(0).toUpperCase() ?? "A"}
          </div>
          <span className="text-primary font-extrabold tracking-tighter font-headline text-lg">
            Analyzer
          </span>
        </div>
        <button className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container-low/50 transition-colors active:scale-95 duration-200">
          <span className="material-symbols-outlined text-primary">notifications</span>
        </button>
      </div>
    </header>
  );
}
