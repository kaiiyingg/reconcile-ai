import { Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Transaction } from "@/data/mockData";
import { toast } from "sonner";

interface ReportsPanelProps {
  transactions: Transaction[];
}

export function ReportsPanel({ transactions }: ReportsPanelProps) {
  const downloadCSV = () => {
    const headers = "ID,Timestamp,Amount,Category,Account,Predicted,AnomalyScore,AnomalyFlag\n";
    const rows = transactions
      .map((t) => `${t.id},${t.timestamp},${t.amount},${t.category},${t.accountId},${t.predictedValue},${t.anomalyScore},${t.anomalyFlag}`)
      .join("\n");
    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "reconcile-ai-report.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast.success("CSV report downloaded");
  };

  const exportPDF = () => {
    toast.info("PDF export would generate via server-side rendering in production");
  };

  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
        Reports & Export
      </h3>
      <div className="flex gap-3">
        <Button variant="outline" size="sm" onClick={downloadCSV} className="border-border text-sm">
          <Download className="h-4 w-4 mr-2" />
          Download CSV
        </Button>
        <Button variant="outline" size="sm" onClick={exportPDF} className="border-border text-sm">
          <FileText className="h-4 w-4 mr-2" />
          Export PDF
        </Button>
      </div>
    </div>
  );
}
