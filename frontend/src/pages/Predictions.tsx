import { useState } from "react";
import { DashboardLayout } from "./Dashboard";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PredictionChart } from "@/components/dashboard/PredictionChart";
import { mockChartData } from "@/data/mockData";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

export default function PredictionsPage() {
  const [timeframe, setTimeframe] = useState<"7d" | "30d" | "90d">("7d");

  const predictions = [
    {
      date: "2024-03-08",
      predicted: 12500,
      actual: 12300,
      variance: -200,
      anomaly: false,
    },
    {
      date: "2024-03-09",
      predicted: 11800,
      actual: 11950,
      variance: 150,
      anomaly: false,
    },
    {
      date: "2024-03-10",
      predicted: 13200,
      actual: 15800,
      variance: 2600,
      anomaly: true,
    },
    {
      date: "2024-03-11",
      predicted: 12000,
      actual: 11800,
      variance: -200,
      anomaly: false,
    },
    {
      date: "2024-03-12",
      predicted: 14500,
      actual: 14200,
      variance: -300,
      anomaly: false,
    },
  ];

  const kpis = [
    {
      label: "Avg Prediction Accuracy",
      value: "94.2%",
      trend: "up",
      icon: TrendingUp,
    },
    {
      label: "Anomalies Detected",
      value: "12",
      trend: "neutral",
      icon: AlertTriangle,
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-[1400px]">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Predictions & Forecasts
          </h1>
          <p className="text-muted-foreground mt-2">
            AI-powered transaction predictions and anomaly detection
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {kpis.map((kpi) => (
            <Card key={kpi.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {kpi.label}
                </CardTitle>
                <kpi.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{kpi.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Transaction Forecast</CardTitle>
            <CardDescription>
              Predicted vs actual transaction amounts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs
              value={timeframe}
              onValueChange={(v) => setTimeframe(v as any)}
            >
              <TabsList>
                <TabsTrigger value="7d">7 Days</TabsTrigger>
                <TabsTrigger value="30d">30 Days</TabsTrigger>
                <TabsTrigger value="90d">90 Days</TabsTrigger>
              </TabsList>
              <TabsContent value={timeframe} className="mt-4">
                <PredictionChart data={mockChartData} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prediction Details</CardTitle>
            <CardDescription>
              Detailed breakdown of predicted vs actual values
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Predicted</TableHead>
                  <TableHead className="text-right">Actual</TableHead>
                  <TableHead className="text-right">Variance</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {predictions.map((pred) => (
                  <TableRow key={pred.date}>
                    <TableCell className="font-medium">{pred.date}</TableCell>
                    <TableCell className="text-right">
                      ${pred.predicted.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      ${pred.actual.toLocaleString()}
                    </TableCell>
                    <TableCell
                      className={`text-right ${pred.variance > 0 ? "text-green-600" : "text-red-600"}`}
                    >
                      {pred.variance > 0 ? "+" : ""}$
                      {pred.variance.toLocaleString()}
                    </TableCell>
                    <TableCell className="text-center">
                      {pred.anomaly ? (
                        <Badge variant="destructive" className="gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          Anomaly
                        </Badge>
                      ) : (
                        <Badge variant="outline">Normal</Badge>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
