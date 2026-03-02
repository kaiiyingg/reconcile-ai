import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import type { Transaction } from "@/data/mockData";

interface LedgerComparisonProps {
  transactions: Transaction[];
}

export function LedgerComparison({ transactions }: LedgerComparisonProps) {
  const mismatched = transactions.filter((t) => t.mismatch).slice(0, 10);

  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider mb-4">
        Ledger Comparison — Mismatches ({mismatched.length})
      </h3>
      {mismatched.length === 0 ? (
        <p className="text-sm text-muted-foreground">No mismatches detected.</p>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-xs uppercase tracking-wider text-muted-foreground">ID</TableHead>
                <TableHead className="text-xs uppercase tracking-wider text-muted-foreground">Internal</TableHead>
                <TableHead className="text-xs uppercase tracking-wider text-muted-foreground">External</TableHead>
                <TableHead className="text-xs uppercase tracking-wider text-muted-foreground">Diff</TableHead>
                <TableHead className="text-xs uppercase tracking-wider text-muted-foreground">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mismatched.map((txn) => {
                const diff = Math.round((txn.amount - (txn.externalAmount ?? txn.amount)) * 100) / 100;
                return (
                  <TableRow key={txn.id} className="border-border hover:bg-accent/50">
                    <TableCell className="font-mono-data text-xs">{txn.id}</TableCell>
                    <TableCell className="font-mono-data text-sm">${txn.amount.toLocaleString()}</TableCell>
                    <TableCell className="font-mono-data text-sm">${(txn.externalAmount ?? txn.amount).toLocaleString()}</TableCell>
                    <TableCell className={`font-mono-data text-sm ${diff !== 0 ? "severity-high" : ""}`}>
                      {diff > 0 ? "+" : ""}{diff}
                    </TableCell>
                    <TableCell>
                      <Badge className="severity-high-bg severity-high border border-severity-high/20 text-xs">Mismatch</Badge>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
