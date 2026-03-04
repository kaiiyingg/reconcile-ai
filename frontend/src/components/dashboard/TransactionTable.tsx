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

type SortKey = "transaction_date" | "amount" | "category";

export function TransactionTable({ transactions }: { transactions: any[] }) {
  const [sortKey, setSortKey] = useState<SortKey>("transaction_date");
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
    if (sortKey === "transaction_date") {
      const dateA = new Date(a.transaction_date || a.timestamp).getTime();
      const dateB = new Date(b.transaction_date || b.timestamp).getTime();
      return mul * (dateA - dateB);
    }
    if (sortKey === "amount")
      return mul * (Number(a.amount) - Number(b.amount));
    if (sortKey === "category")
      return mul * a.category.localeCompare(b.category);
    return 0;
  });

  const SortIcon = ({ col }: { col: SortKey }) =>
    sortKey === col ? (
      sortDir === "asc" ? (
        <ChevronUp className="h-3 w-3 inline ml-1" />
      ) : (
        <ChevronDown className="h-3 w-3 inline ml-1" />
      )
    ) : null;

  const flagStyles: Record<string, string> = {
    high: "severity-high-bg severity-high border-severity-high/20",
    medium: "severity-medium-bg severity-medium border-severity-medium/20",
    normal: "bg-secondary text-secondary-foreground",
    none: "bg-secondary text-secondary-foreground",
  };

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead
                className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer"
                onClick={() => toggleSort("transaction_date")}
              >
                Date <SortIcon col="transaction_date" />
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">
                ID
              </TableHead>
              <TableHead
                className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer"
                onClick={() => toggleSort("amount")}
              >
                Amount <SortIcon col="amount" />
              </TableHead>
              <TableHead
                className="text-muted-foreground text-xs uppercase tracking-wider cursor-pointer"
                onClick={() => toggleSort("category")}
              >
                Category <SortIcon col="category" />
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">
                Status
              </TableHead>
              <TableHead className="text-muted-foreground text-xs uppercase tracking-wider">
                Source
              </TableHead>
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
                  className="border-border hover:bg-accent/50 transition-colors"
                >
                  <TableCell className="font-mono-data text-xs text-muted-foreground">
                    {new Date(
                      txn.transaction_date || txn.timestamp,
                    ).toLocaleString("en-US", {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </TableCell>
                  <TableCell className="font-mono-data text-xs">
                    {txn.id?.substring(0, 8)}...
                  </TableCell>
                  <TableCell className="font-mono-data text-sm font-medium">
                    $
                    {Number(txn.amount || 0).toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className="text-xs font-normal border-border text-muted-foreground capitalize"
                    >
                      {txn.category}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        txn.status === "completed" ? "default" : "outline"
                      }
                      className="text-xs capitalize"
                    >
                      {txn.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground capitalize">
                    {txn.source}
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
