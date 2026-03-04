import { useState } from "react";
import { transactionAPI } from "../services/transactions";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "./ui/card";
import { Upload, Download, Sparkles } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";

interface DemoDataPanelProps {
  onDataChanged?: () => void;
}

export function DemoDataPanel({ onDataChanged }: DemoDataPanelProps) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [file, setFile] = useState<File | null>(null);

  async function handleGenerateDemo() {
    setLoading(true);
    setMessage("");

    try {
      const result = await transactionAPI.generateDemo(100);
      setMessage(`✅ ${result.message}`);

      // Refresh data without reloading page
      if (onDataChanged) {
        setTimeout(() => onDataChanged(), 500);
      }
    } catch (error) {
      setMessage("❌ Failed to generate demo data");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadCSV() {
    try {
      await transactionAPI.downloadDemoCSV(100);
      setMessage("✅ CSV downloaded successfully");
    } catch (error) {
      setMessage("❌ Failed to download CSV");
    }
  }

  async function handleUploadCSV() {
    if (!file) return;

    setLoading(true);
    setMessage("");

    try {
      const result = await transactionAPI.uploadCSV(file);
      setMessage(`✅ Uploaded ${result.count || 0} transactions`);
      setFile(null);

      // Refresh data without reloading page
      if (onDataChanged) {
        setTimeout(() => onDataChanged(), 500);
      }
    } catch (error) {
      setMessage("❌ Failed to upload CSV");
    } finally {
      setLoading(false);
    }
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage("");
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction Data</CardTitle>
        <CardDescription>
          Generate demo data or upload your own CSV file
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Demo Data Section */}
        <div>
          <h3 className="text-sm font-medium mb-2">Demo Data</h3>
          <div className="flex gap-2">
            <Button onClick={handleGenerateDemo} disabled={loading}>
              <Sparkles className="h-4 w-4 mr-2" />
              {loading ? "Generating..." : "Generate Demo (100)"}
            </Button>

            <Button onClick={handleDownloadCSV} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Download CSV
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Generates 100 sample transactions (replaces existing demo data)
          </p>
        </div>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or</span>
          </div>
        </div>

        {/* Upload CSV Section */}
        <div>
          <h3 className="text-sm font-medium mb-2">Upload Your Data</h3>
          <div className="flex items-center gap-2">
            <Input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              disabled={loading}
              className="flex-1"
            />
            <Button
              onClick={handleUploadCSV}
              disabled={!file || loading}
              variant="secondary"
            >
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
          </div>
          {file && (
            <p className="text-xs text-muted-foreground mt-2">
              Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
            </p>
          )}
        </div>

        {/* Message/Status */}
        {message && (
          <Alert>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
