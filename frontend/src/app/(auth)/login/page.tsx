"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";

const loginSchema = z.object({
  username: z.string().min(1, "아이디를 입력하세요"),
  password: z.string().min(1, "비밀번호를 입력하세요"),
});

const registerSchema = z.object({
  username: z.string().min(2, "2자 이상 입력하세요"),
  password: z.string().min(4, "4자 이상 입력하세요"),
  confirmPassword: z.string(),
}).refine((d) => d.password === d.confirmPassword, {
  message: "비밀번호가 일치하지 않습니다",
  path: ["confirmPassword"],
});

type LoginForm = z.infer<typeof loginSchema>;
type RegisterForm = z.infer<typeof registerSchema>;

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const loginForm = useForm<LoginForm>({ resolver: zodResolver(loginSchema) });
  const registerForm = useForm<RegisterForm>({ resolver: zodResolver(registerSchema) });

  const handleLogin = async (data: LoginForm) => {
    setLoading(true);
    try {
      const res = await authApi.login(data.username, data.password);
      setAuth(res.user, res.token);
      toast.success("로그인 성공");
      router.push("/dashboard");
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "로그인 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (data: RegisterForm) => {
    setLoading(true);
    try {
      await authApi.register(data.username, data.password);
      toast.success("회원가입 성공! 로그인하세요.");
      setMode("login");
      loginForm.setValue("username", data.username);
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "회원가입 실패");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-8">
        {/* Brand */}
        <div className="text-center space-y-2">
          <div className="w-16 h-16 rounded-2xl bg-primary mx-auto flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-3xl">account_balance_wallet</span>
          </div>
          <h1 className="text-3xl font-headline font-extrabold text-primary tracking-tight">Analyzer</h1>
          <p className="text-on-surface-variant text-sm">가계부 분석기</p>
        </div>

        {/* Tab Toggle */}
        <div className="flex bg-surface-container-low p-1 rounded-xl">
          <button
            onClick={() => setMode("login")}
            className={`flex-1 py-2.5 text-center rounded-lg text-sm font-semibold transition-all ${
              mode === "login" ? "bg-primary text-white" : "text-on-surface-variant"
            }`}
          >
            로그인
          </button>
          <button
            onClick={() => setMode("register")}
            className={`flex-1 py-2.5 text-center rounded-lg text-sm font-semibold transition-all ${
              mode === "register" ? "bg-primary text-white" : "text-on-surface-variant"
            }`}
          >
            회원가입
          </button>
        </div>

        {/* Login Form */}
        {mode === "login" && (
          <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">아이디</label>
              <input
                {...loginForm.register("username")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
                placeholder="아이디를 입력하세요"
              />
              {loginForm.formState.errors.username && (
                <p className="text-error text-xs px-1">{loginForm.formState.errors.username.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">비밀번호</label>
              <input
                type="password"
                {...loginForm.register("password")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
                placeholder="비밀번호를 입력하세요"
              />
              {loginForm.formState.errors.password && (
                <p className="text-error text-xs px-1">{loginForm.formState.errors.password.message}</p>
              )}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-on-primary py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/20 active:scale-[0.98] transition-all duration-200 disabled:opacity-60"
            >
              {loading ? "로그인 중…" : "로그인"}
            </button>
          </form>
        )}

        {/* Register Form */}
        {mode === "register" && (
          <form onSubmit={registerForm.handleSubmit(handleRegister)} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">아이디</label>
              <input
                {...registerForm.register("username")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
                placeholder="2자 이상"
              />
              {registerForm.formState.errors.username && (
                <p className="text-error text-xs px-1">{registerForm.formState.errors.username.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">비밀번호</label>
              <input
                type="password"
                {...registerForm.register("password")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
                placeholder="4자 이상"
              />
              {registerForm.formState.errors.password && (
                <p className="text-error text-xs px-1">{registerForm.formState.errors.password.message}</p>
              )}
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider px-1">비밀번호 확인</label>
              <input
                type="password"
                {...registerForm.register("confirmPassword")}
                className="w-full bg-surface-container-high border-none rounded-lg px-4 py-3.5 text-on-surface font-medium focus:ring-2 focus:ring-primary/20 transition-all"
                placeholder="비밀번호를 다시 입력하세요"
              />
              {registerForm.formState.errors.confirmPassword && (
                <p className="text-error text-xs px-1">{registerForm.formState.errors.confirmPassword.message}</p>
              )}
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-on-primary py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/20 active:scale-[0.98] transition-all duration-200 disabled:opacity-60"
            >
              {loading ? "가입 중…" : "회원가입"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
