import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      {/* Main Content */}
      <main className="flex-1 mx-auto px-4 sm:px-6 lg:px-8 py-8 max-w-7xl">
        {children}
      </main>

      <Footer />
    </div>
  );
};
