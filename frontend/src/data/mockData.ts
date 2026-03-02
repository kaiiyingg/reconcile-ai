export interface Transaction {
  id: string;
  timestamp: string;
  amount: number;
  category: string;
  accountId: string;
  predictedValue: number;
  anomalyScore: number;
  anomalyFlag: "high" | "medium" | "normal";
  shapValues?: { feature: string; impact: number }[];
  externalAmount?: number;
  mismatch?: boolean;
}

export interface ChartData {
  date: string;
  actual: number;
  predicted: number;
}

// Empty arrays - ready for API integration
export const mockTransactions: Transaction[] = [];
export const mockChartData: ChartData[] = [];
