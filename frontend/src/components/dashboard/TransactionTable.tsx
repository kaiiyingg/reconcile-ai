import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Info } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { Transaction } from "@/data/mockData";

interface TransactionTableProps {
  transactions: Transaction[];
}

type SortKey = "timestamp" | "amount" | "anomalyScore";

export function TransactionTable({ transactions }: TransactionTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const sorted = [...transactions].sort((a, b) => {
    const mul = sortDir === "asc" ? 1 : -1;
    if (sortKey === "timestamp") return mul * (new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    return mul * ((a[sortKey] as number) - (b[sortKey] as number));
  });

  const SortIcon = ({ col }: { col: SortKey }) =>
    sortKey === col ? (sortDir === "asc" ? <ChevronUp className="h-3 w-3 inline ml-1" /> : <ChevronDown className="h-3 w-3 inline ml-1" />) : null;

  const flagStyles: Record<Transaction["anomalyFlag"], string> = {
    high: "severity-high-bg severity-high border-severity-high/20",
    medium: "severity-medium-bg severity-medium border-severity-medium/20",
    normal: "bg-secondary text-secondary-foreground",
  };

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer" onClick={() => toggleSort("timestamp")}>
                Timestamp <SortIcon col="timestamp" />
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">ID</TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer" onClick={() => toggleSort("amount")}>
                Amount <SortIcon col="amount" />
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">Category</TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">Predicted</TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer" onClick={() => toggleSort("anomalyScore")}>
                Anomaly <SortIcon col="anomalyScore" />
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">XAI</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <AnimatePresence>
              {sorted.slice(0, 20).map((txn) => (
                <motion.tr
                  key={txn.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className={`border-border hover:bg-accent/50 transition-colors ${
                    txn.anomalyFlag === "high" ? "severity-high-bg" : ""
                  }`}
                >
                  <TableCell className="font-mono-data text-xs text-muted-foreground">
                    {new Date(txn.timestamp).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                  </TableCell>
                  <TableCell className="font-mono-data text-xs">{txn.id}</TableCell>
                  <TableCell className="font-mono-data text-sm font-medium">${txn.amount.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs font-normal border-border text-muted-foreground">{txn.category}</Badge>
                  </TableCell>
                  <TableCell className="font-mono-data text-sm text-muted-foreground">${txn.predictedValue.toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge className={`text-xs border ${flagStyles[txn.anomalyFlag]}`}>
                      {txn.anomalyFlag === "high" ? "HIGH" : txn.anomalyFlag === "medium" ? "MED" : "OK"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {txn.shapValues ? (
                      <Tooltip>
                        <TooltipTrigger>
                          <Info className="h-3.5 w-3.5 text-primary cursor-pointer" />
                        </TooltipTrigger>
                        <TooltipContent side="left" className="max-w-xs bg-popover border-border p-3">
                          <p className="text-xs font-medium mb-2">Feature Importance (SHAP)</p>
                          {txn.shapValues.map((sv) => (
                            <div key={sv.feature} className="flex items-center justify-between text-xs mb-1">
                              <span className="text-muted-foreground">{sv.feature}</span>
                              <span className={`font-mono-data ${sv.impact > 0 ? "severity-high" : "severity-low"}`}>
                                {sv.impact > 0 ? "+" : ""}{sv.impact.toFixed(3)}
                              </span>
                            </div>
                          ))}
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      <span className="text-muted-foreground text-xs">—</span>
                    )}
                  </TableCell>
                </motion.tr>
              ))}
            </AnimatePresence>
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
