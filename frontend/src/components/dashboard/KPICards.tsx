import { motion } from "framer-motion";
import { Activity, AlertTriangle, TrendingUp, DollarSign } from "lucide-react";
import type { Transaction } from "@/data/mockData";

interface KPICardsProps {
  transactions: Transaction[];
}

export function KPICards({ transactions }: KPICardsProps) {
  const total = transactions.length;
  const anomalies = transactions.filter((t) => t.anomalyFlag !== "normal").length;
  const anomalyPct = total > 0 ? ((anomalies / total) * 100).toFixed(1) : "0";
  const avgError =
    total > 0
      ? (transactions.reduce((s, t) => s + Math.abs(t.amount - t.predictedValue), 0) / total).toFixed(2)
      : "0";
  const dailyCashflow = transactions.reduce((s, t) => s + t.amount, 0);

  const cards = [
    {
      label: "Total Transactions",
      value: total.toLocaleString(),
      icon: Activity,
      color: "text-primary" as const,
    },
    {
      label: "Anomaly Rate",
      value: `${anomalyPct}%`,
      icon: AlertTriangle,
      color: "text-severity-medium" as const,
    },
    {
      label: "Avg Prediction Error",
      value: `$${Number(avgError).toLocaleString()}`,
      icon: TrendingUp,
      color: "text-primary" as const,
    },
    {
      label: "Daily Cashflow",
      value: `$${Math.round(dailyCashflow).toLocaleString()}`,
      icon: DollarSign,
      color: "text-severity-low" as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, i) => (
        <motion.div
          key={card.label}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.08 }}
          className="rounded-lg border border-border bg-card p-5 glow-primary"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs uppercase tracking-wider text-muted-foreground font-medium">
              {card.label}
            </span>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </div>
          <p className="text-2xl font-bold font-mono-data">{card.value}</p>
        </motion.div>
      ))}
    </div>
  );
}
