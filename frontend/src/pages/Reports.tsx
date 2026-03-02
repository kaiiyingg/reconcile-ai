import { useState } from "react";
import { DashboardLayout } from "./Dashboard";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, FileText, FileSpreadsheet, Filter } from "lucide-react";
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

export default function ReportsPage() {
  const [reportType, setReportType] = useState("full");
  const [dateRange, setDateRange] = useState("7d");
  const [includeColumns, setIncludeColumns] = useState({
    id: true,
    amount: true,
    category: true,
    timestamp: true,
    anomalyScore: true,
    prediction: true,
    variance: false,
    status: true,
  });

  const handleExport = (format: "csv" | "pdf") => {
    alert(`Exporting ${reportType} report as ${format.toUpperCase()}...`);
  };

  const toggleColumn = (column: keyof typeof includeColumns) => {
    setIncludeColumns((prev) => ({ ...prev, [column]: !prev[column] }));
  };

  const reportStats = [
    { label: "Total Transactions", value: "1,247" },
    { label: "Anomalies Detected", value: "37" },
    { label: "Anomaly Rate", value: "2.97%" },
    { label: "Avg Transaction", value: "$8,542" },
    { label: "Total Volume", value: "$10.65M" },
    { label: "Reconciliation Rate", value: "98.3%" },
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
                <Button onClick={() => handleExport("csv")} className="flex-1">
                  <FileSpreadsheet className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
                <Button
                  onClick={() => handleExport("pdf")}
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
            <CardTitle>Recent Exports</CardTitle>
            <CardDescription>Previously generated reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                {
                  name: "Full_Report_2024-03-01.pdf",
                  date: "2024-03-01 14:30",
                  size: "2.4 MB",
                  type: "pdf",
                },
                {
                  name: "Anomalies_Report_2024-02-28.csv",
                  date: "2024-02-28 09:15",
                  size: "156 KB",
                  type: "csv",
                },
                {
                  name: "Summary_KPIs_2024-02-25.pdf",
                  date: "2024-02-25 16:45",
                  size: "890 KB",
                  type: "pdf",
                },
              ].map((file) => (
                <div
                  key={file.name}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent"
                >
                  <div className="flex items-center gap-3">
                    {file.type === "pdf" ? (
                      <FileText className="h-5 w-5 text-red-500" />
                    ) : (
                      <FileSpreadsheet className="h-5 w-5 text-green-500" />
                    )}
                    <div>
                      <p className="text-sm font-medium">{file.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {file.date} • {file.size}
                      </p>
                    </div>
                  </div>
                  <Button size="sm" variant="ghost">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
