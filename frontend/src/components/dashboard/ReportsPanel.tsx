import { Download, FileText, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { useState } from "react";

interface ReportsPanelProps {
  filters?: {
    startDate?: string;
    endDate?: string;
    category?: string;
    status?: string;
  };
}

export function ReportsPanel({ filters }: ReportsPanelProps) {
  const [loading, setLoading] = useState(false);

  const downloadCSV = async () => {
    setLoading(true);
    try {
      // Get auth token from localStorage
      const token = localStorage.getItem("token");
      if (!token) {
        toast.error("Please log in to download reports");
        setLoading(false);
        return;
      }

      // Build query params
      const params = new URLSearchParams();
      if (filters?.startDate) params.append("start_date", filters.startDate);
      if (filters?.endDate) params.append("end_date", filters.endDate);
      if (filters?.category) params.append("category", filters.category);
      if (filters?.status) params.append("status", filters.status);

      const url = `http://localhost:8000/api/reports/transactions/csv?${params.toString()}`;

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to download CSV");
      }

      const blob = await response.blob();
      const downloadUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `transactions_${new Date().toISOString().split("T")[0]}.csv`;
      a.click();
      URL.revokeObjectURL(downloadUrl);

      toast.success("CSV report downloaded");
    } catch (error) {
      console.error("Failed to download CSV:", error);
      toast.error("Failed to download CSV");
    } finally {
      setLoading(false);
    }
  };

  const getSummary = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        toast.error("Please log in to get summary");
        setLoading(false);
        return;
      }

      const response = await fetch(
        "http://localhost:8000/api/reports/summary",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Failed to get summary");
      }

      const summary = await response.json();
      console.log("Summary:", summary);
      toast.success("Summary report generated - check console");
    } catch (error) {
      console.error("Failed to get summary:", error);
      toast.error("Failed to get summary");
    } finally {
      setLoading(false);
    }
  };

  const exportPDF = () => {
    toast.info("PDF export coming soon");
  };

  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
        Reports & Export
      </h3>
      <div className="flex gap-3 flex-wrap">
        <Button
          variant="outline"
          size="sm"
          onClick={downloadCSV}
          disabled={loading}
          className="border-border text-sm"
        >
          <Download className="h-4 w-4 mr-2" />
          {loading ? "Downloading..." : "Download CSV"}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={getSummary}
          disabled={loading}
          className="border-border text-sm"
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Get Summary
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={exportPDF}
          disabled={loading}
          className="border-border text-sm"
        >
          <FileText className="h-4 w-4 mr-2" />
          Export PDF
        </Button>
      </div>
    </div>
  );
}
