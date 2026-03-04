import { useState, useEffect } from "react";
import { DashboardLayout } from "./Dashboard";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Download,
  FileText,
  FileSpreadsheet,
  Filter,
  BarChart3,
} from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

export default function ReportsPage() {
  const [reportType, setReportType] = useState("full");
  const [dateRange, setDateRange] = useState("7d");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<any>(null);
  const [includeColumns, setIncludeColumns] = useState({
    id: true,
    amount: true,
    category: true,
    transaction_date: true,
    source: true,
    status: true,
    description: true,
  });

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;

      const response = await fetch(
        "http://localhost:8000/api/reports/summary",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error("Failed to load summary:", error);
    }
  };

  const handleExport = async (format: "csv" | "pdf") => {
    if (format === "pdf") {
      toast.info("PDF export coming soon");
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        toast.error("Please log in to export reports");
        return;
      }

      const response = await fetch(
        "http://localhost:8000/api/reports/transactions/csv",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Failed to download CSV");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `transactions_${new Date().toISOString().split("T")[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);

      toast.success("CSV report downloaded");
    } catch (error) {
      console.error("Failed to export:", error);
      toast.error("Failed to export report");
    } finally {
      setLoading(false);
    }
  };

  const toggleColumn = (column: keyof typeof includeColumns) => {
    setIncludeColumns((prev) => ({ ...prev, [column]: !prev[column] }));
  };

  const reportStats = summary
    ? [
        {
          label: "Total Transactions",
          value: summary.summary?.total_transactions?.toLocaleString() || "0",
        },
        {
          label: "Total Revenue",
          value: summary.summary?.total_revenue
            ? `$${summary.summary.total_revenue.toLocaleString()}`
            : "$0",
        },
        {
          label: "Total Expenses",
          value: summary.summary?.total_expenses
            ? `$${Math.abs(summary.summary.total_expenses).toLocaleString()}`
            : "$0",
        },
        {
          label: "Net Amount",
          value: summary.summary?.net_amount
            ? `$${summary.summary.net_amount.toLocaleString()}`
            : "$0",
        },
        {
          label: "Avg Transaction",
          value: summary.summary?.avg_amount
            ? `$${summary.summary.avg_amount.toFixed(2)}`
            : "$0",
        },
        {
          label: "Categories",
          value: summary.by_category?.length?.toString() || "0",
        },
      ]
    : [
        { label: "Total Transactions", value: "-" },
        { label: "Total Revenue", value: "-" },
        { label: "Total Expenses", value: "-" },
        { label: "Net Amount", value: "-" },
        { label: "Avg Transaction", value: "-" },
        { label: "Categories", value: "-" },
      ];

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-[1400px]">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Reports & Export
          </h1>
          <p className="text-muted-foreground mt-2">
            Generate and download comprehensive reconciliation reports
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {reportStats.map((stat) => (
            <Card key={stat.label}>
              <CardHeader className="pb-2">
                <CardDescription className="text-xs">
                  {stat.label}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Export Options</CardTitle>
              <CardDescription>Configure and download reports</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Report Type</Label>
                  <Select value={reportType} onValueChange={setReportType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="full">Full Report</SelectItem>
                      <SelectItem value="anomalies">Anomalies Only</SelectItem>
                      <SelectItem value="predictions">
                        Predictions Only
                      </SelectItem>
                      <SelectItem value="summary">Summary KPIs</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Date Range</Label>
                  <Select value={dateRange} onValueChange={setDateRange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="7d">Last 7 Days</SelectItem>
                      <SelectItem value="30d">Last 30 Days</SelectItem>
                      <SelectItem value="90d">Last 90 Days</SelectItem>
                      <SelectItem value="custom">Custom Range</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              <div className="flex gap-4">
                <Button
                  onClick={() => handleExport("csv")}
                  disabled={loading}
                  className="flex-1"
                >
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  {loading ? "Exporting..." : "Export CSV"}
                </Button>
                <Button
                  onClick={() => handleExport("pdf")}
                  disabled={loading}
                  variant="outline"
                  className="flex-1"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                Column Selection
              </CardTitle>
              <CardDescription>Choose columns to include</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(includeColumns).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <Checkbox
                    id={key}
                    checked={value}
                    onCheckedChange={() => toggleColumn(key as any)}
                  />
                  <Label
                    htmlFor={key}
                    className="text-sm font-normal cursor-pointer capitalize"
                  >
                    {key.replace(/([A-Z])/g, " $1").trim()}
                  </Label>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Quick Export</CardTitle>
            <CardDescription>Download your transaction data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button
                onClick={() => handleExport("csv")}
                disabled={loading}
                className="w-full justify-start"
                variant="outline"
              >
                <FileSpreadsheet className="h-5 w-5 text-green-500 mr-3" />
                <div className="text-left flex-1">
                  <p className="text-sm font-medium">
                    Download All Transactions (CSV)
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Export complete transaction history
                  </p>
                </div>
                <Download className="h-4 w-4" />
              </Button>

              <Button
                onClick={() => handleExport("pdf")}
                disabled={loading}
                className="w-full justify-start"
                variant="outline"
              >
                <FileText className="h-5 w-5 text-red-500 mr-3" />
                <div className="text-left flex-1">
                  <p className="text-sm font-medium">Summary Report (PDF)</p>
                  <p className="text-xs text-muted-foreground">
                    Coming soon - Full summary with charts
                  </p>
                </div>
                <Download className="h-4 w-4" />
              </Button>

              <Button
                onClick={loadSummary}
                disabled={loading}
                className="w-full justify-start"
                variant="outline"
              >
                <BarChart3 className="h-5 w-5 text-blue-500 mr-3" />
                <div className="text-left flex-1">
                  <p className="text-sm font-medium">Refresh Statistics</p>
                  <p className="text-xs text-muted-foreground">
                    Update summary data above
                  </p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
