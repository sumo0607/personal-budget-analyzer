import Header from "@/components/Header";
import BottomNav from "@/components/BottomNav";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main className="pt-20 px-4 sm:px-6 max-w-md mx-auto pb-32">
        {children}
      </main>
      <BottomNav />
    </>
  );
}
