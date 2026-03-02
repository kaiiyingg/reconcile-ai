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

const categories = ["Wire Transfer", "ACH", "Card Payment", "Direct Deposit", "Fee", "Refund", "Settlement"];
const accounts = ["ACC-1001", "ACC-1002", "ACC-1003", "ACC-2001", "ACC-2002"];

function randomBetween(min: number, max: number) {
  return Math.round((Math.random() * (max - min) + min) * 100) / 100;
}

function generateShapValues(): { feature: string; impact: number }[] {
  return [
    { feature: "Transaction Amount", impact: randomBetween(-0.5, 0.8) },
    { feature: "Time of Day", impact: randomBetween(-0.3, 0.4) },
    { feature: "Category Frequency", impact: randomBetween(-0.2, 0.5) },
    { feature: "Account History", impact: randomBetween(-0.4, 0.3) },
    { feature: "Rolling Avg Deviation", impact: randomBetween(-0.6, 0.7) },
  ].sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact));
}

export function generateTransactions(count: number): Transaction[] {
  const now = Date.now();
  return Array.from({ length: count }, (_, i) => {
    const amount = randomBetween(50, 25000);
    const noise = randomBetween(-500, 500);
    const predicted = Math.max(0, amount + noise);
    const error = Math.abs(amount - predicted) / Math.max(amount, 1);
    const anomalyScore = Math.min(1, error);
    const anomalyFlag: Transaction["anomalyFlag"] =
      anomalyScore > 0.3 ? "high" : anomalyScore > 0.15 ? "medium" : "normal";
    const externalAmount = Math.random() > 0.85 ? amount + randomBetween(-200, 200) : amount;

    return {
      id: `TXN-${String(i + 1).padStart(5, "0")}`,
      timestamp: new Date(now - (count - i) * 3600000).toISOString(),
      amount,
      category: categories[Math.floor(Math.random() * categories.length)],
      accountId: accounts[Math.floor(Math.random() * accounts.length)],
      predictedValue: Math.round(predicted * 100) / 100,
      anomalyScore: Math.round(anomalyScore * 1000) / 1000,
      anomalyFlag,
      shapValues: anomalyFlag !== "normal" ? generateShapValues() : undefined,
      externalAmount: Math.round(externalAmount * 100) / 100,
      mismatch: Math.abs(externalAmount - amount) > 0.01,
    };
  });
}

export function generateChartData(days: number) {
  const now = Date.now();
  return Array.from({ length: days }, (_, i) => {
    const actual = randomBetween(8000, 35000);
    const predicted = actual + randomBetween(-3000, 3000);
    return {
      date: new Date(now - (days - i) * 86400000).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      actual: Math.round(actual),
      predicted: Math.round(predicted),
    };
  });
}

export const mockTransactions = generateTransactions(50);
export const mockChartData = generateChartData(30);
