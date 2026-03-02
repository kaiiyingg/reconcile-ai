import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface FiltersProps {
  category: string;
  setCategory: (v: string) => void;
  anomalyFilter: string;
  setAnomalyFilter: (v: string) => void;
  search: string;
  setSearch: (v: string) => void;
}

export function Filters({ category, setCategory, anomalyFilter, setAnomalyFilter, search, setSearch }: FiltersProps) {
  return (
    <div className="flex flex-wrap gap-3 items-center">
      <Input
        placeholder="Search transactions..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-56 bg-secondary border-border text-sm"
      />
      <Select value={category} onValueChange={setCategory}>
        <SelectTrigger className="w-44 bg-secondary border-border text-sm">
          <SelectValue placeholder="Category" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Categories</SelectItem>
          <SelectItem value="Wire Transfer">Wire Transfer</SelectItem>
          <SelectItem value="ACH">ACH</SelectItem>
          <SelectItem value="Card Payment">Card Payment</SelectItem>
          <SelectItem value="Direct Deposit">Direct Deposit</SelectItem>
          <SelectItem value="Fee">Fee</SelectItem>
          <SelectItem value="Refund">Refund</SelectItem>
          <SelectItem value="Settlement">Settlement</SelectItem>
        </SelectContent>
      </Select>
      <Select value={anomalyFilter} onValueChange={setAnomalyFilter}>
        <SelectTrigger className="w-40 bg-secondary border-border text-sm">
          <SelectValue placeholder="Anomaly" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Levels</SelectItem>
          <SelectItem value="high">High Risk</SelectItem>
          <SelectItem value="medium">Medium</SelectItem>
          <SelectItem value="normal">Normal</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
