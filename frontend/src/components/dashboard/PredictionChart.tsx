import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
} from "recharts";

interface ChartDataPoint {
  date: string;
  actual: number;
  predicted: number;
}

interface PredictionChartProps {
  data: ChartDataPoint[];
}

export function PredictionChart({ data }: PredictionChartProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
        Predicted vs Actual — 30 Day
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 20% 16%)" />
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: "hsl(215 15% 52%)" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "hsl(215 15% 52%)" }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
          <RechartsTooltip
            contentStyle={{
              backgroundColor: "hsl(222 44% 9%)",
              border: "1px solid hsl(222 20% 16%)",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "hsl(210 20% 92%)" }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line
            type="monotone"
            dataKey="actual"
            stroke="hsl(217 91% 60%)"
            strokeWidth={2}
            dot={false}
            name="Actual"
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="hsl(142 71% 45%)"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            name="Predicted"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
