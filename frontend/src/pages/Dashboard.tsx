import { useState, useMemo, useEffect } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/dashboard/AppSidebar";
import { DashboardHeader } from "@/components/dashboard/DashboardHeader";
import { KPICards } from "@/components/dashboard/KPICards";
import { TransactionTable } from "@/components/dashboard/TransactionTable";
import { PredictionChart } from "@/components/dashboard/PredictionChart";
import { Filters } from "@/components/dashboard/Filters";
import { LedgerComparison } from "@/components/dashboard/LedgerComparison";
import { ReportsPanel } from "@/components/dashboard/ReportsPanel";
import { DemoDataPanel } from "@/components/DemoDataPanel";
import { transactionAPI } from "@/services/transactions";
import { mockChartData } from "@/data/mockData";

export function DashboardLayout({ children }: { children?: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <DashboardHeader />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}

export default function DashboardPage() {
  const [category, setCategory] = useState("all");
  const [anomalyFilter, setAnomalyFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch transactions from API
  const loadTransactions = async () => {
    setLoading(true);
    try {
      const data = await transactionAPI.getTransactions();
      // Ensure data is an array
      setTransactions(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load transactions:", error);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, []);

  const filtered = useMemo(() => {
    if (!Array.isArray(transactions)) return [];
    return transactions.filter((t) => {
      if (category !== "all" && t.category !== category) return false;
      if (anomalyFilter !== "all" && t.anomaly_flag !== anomalyFilter)
        return false;
      if (
        search &&
        !t.id.toLowerCase().includes(search.toLowerCase()) &&
        !t.category.toLowerCase().includes(search.toLowerCase())
      )
        return false;
      return true;
    });
  }, [category, anomalyFilter, search, transactions]);

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-[1400px]">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Real-time transaction monitoring and anomaly detection
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading transactions...</p>
          </div>
        ) : (
          <>
            <DemoDataPanel onDataChanged={loadTransactions} />

            {transactions.length === 0 ? (
              <div className="text-center py-12 border-2 border-dashed rounded-lg">
                <p className="text-lg font-medium mb-2">No transactions yet</p>
                <p className="text-muted-foreground mb-4">
                  Generate demo data or upload your own CSV to get started
                </p>
              </div>
            ) : (
              <>
                <KPICards transactions={filtered} />

                <Filters
                  category={category}
                  setCategory={setCategory}
                  anomalyFilter={anomalyFilter}
                  setAnomalyFilter={setAnomalyFilter}
                  search={search}
                  setSearch={setSearch}
                />

                <PredictionChart data={mockChartData} />

                <TransactionTable transactions={filtered} />

                <ReportsPanel
                  filters={{
                    category: category !== "all" ? category : undefined,
                  }}
                />

                <LedgerComparison transactions={transactions} />
              </>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
