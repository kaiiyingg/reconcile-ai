import { useState, useMemo } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { KPICards } from "@/components/dashboard/KPICards";
import { TransactionTable } from "@/components/dashboard/TransactionTable";
import { PredictionChart } from "@/components/dashboard/PredictionChart";
import { Filters } from "@/components/dashboard/Filters";
import { LedgerComparison } from "@/components/dashboard/LedgerComparison";
import { ReportsPanel } from "@/components/dashboard/ReportsPanel";
import { mockTransactions, mockChartData } from "@/data/mockData";

export function DashboardLayout({ children }: { children?: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <DashboardHeader />
          <main className="flex-1 overflow-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}

export default function DashboardPage() {
  const [category, setCategory] = useState("all");
  const [anomalyFilter, setAnomalyFilter] = useState("all");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    return mockTransactions.filter((t) => {
      if (category !== "all" && t.category !== category) return false;
      if (anomalyFilter !== "all" && t.anomalyFlag !== anomalyFilter) return false;
      if (search && !t.id.toLowerCase().includes(search.toLowerCase()) && !t.category.toLowerCase().includes(search.toLowerCase())) return false;
      return true;
    });
  }, [category, anomalyFilter, search]);

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-[1400px]">
        <KPICards transactions={filtered} />
        <Filters
          category={category}
          setCategory={setCategory}
          anomalyFilter={anomalyFilter}
          setAnomalyFilter={setAnomalyFilter}
          search={search}
          setSearch={setSearch}
        />
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2">
            <PredictionChart data={mockChartData} />
          </div>
          <div>
            <ReportsPanel transactions={filtered} />
          </div>
        </div>
        <TransactionTable transactions={filtered} />
        <LedgerComparison transactions={mockTransactions} />
      </div>
    </DashboardLayout>
  );
}
