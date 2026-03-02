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
import { Input } from "@/components/ui/input";
import {
  Upload as UploadIcon,
  FileSpreadsheet,
  AlertCircle,
} from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // Simulate preview data
      setPreview([
        {
          id: "TXN001",
          amount: 1500.0,
          category: "Revenue",
          timestamp: "2024-03-01 10:30:00",
          status: "pending",
        },
        {
          id: "TXN002",
          amount: -450.0,
          category: "Expense",
          timestamp: "2024-03-01 11:15:00",
          status: "pending",
        },
        {
          id: "TXN003",
          amount: 2300.0,
          category: "Revenue",
          timestamp: "2024-03-01 14:20:00",
          status: "pending",
        },
      ]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);

    // Simulate upload
    setTimeout(() => {
      setUploading(false);
      setPreview([]);
      setFile(null);
      alert("Transactions uploaded successfully!");
    }, 2000);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-[1400px]">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Upload Transactions
          </h1>
          <p className="text-muted-foreground mt-2">
            Upload CSV or Excel files to import transactions
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>File Upload</CardTitle>
            <CardDescription>
              Upload a CSV or Excel file containing transaction data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
              </div>
              <Button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="min-w-[120px]"
              >
                <UploadIcon className="h-4 w-4 mr-2" />
                {uploading ? "Uploading..." : "Upload"}
              </Button>
            </div>

            {file && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileSpreadsheet className="h-4 w-4" />
                <span>{file.name}</span>
                <span className="text-xs">
                  ({(file.size / 1024).toFixed(2)} KB)
                </span>
              </div>
            )}

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                File must include columns: ID, Amount, Category, Timestamp
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {preview.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>
                Preview of uploaded transactions ({preview.length} rows)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Transaction ID</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {preview.map((txn) => (
                    <TableRow key={txn.id}>
                      <TableCell className="font-mono text-sm">
                        {txn.id}
                      </TableCell>
                      <TableCell
                        className={
                          txn.amount >= 0 ? "text-green-600" : "text-red-600"
                        }
                      >
                        ${Math.abs(txn.amount).toFixed(2)}
                      </TableCell>
                      <TableCell>{txn.category}</TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {txn.timestamp}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{txn.status}</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
