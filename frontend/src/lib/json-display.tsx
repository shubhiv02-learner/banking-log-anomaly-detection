import type { ReactNode } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";

const RECORDS_ROW_CAP = 50;

export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

/** Coerce API payloads that may arrive as objects, arrays, or JSON strings. */
export function coerceJsonValue(input: unknown): JsonValue | undefined {
  if (input == null) return undefined;
  let value: unknown = input;
  for (let i = 0; i < 3 && typeof value === "string"; i++) {
    const text = value.trim();
    if (!text) return undefined;
    try {
      value = JSON.parse(text);
    } catch {
      return text;
    }
  }
  return value as JsonValue;
}

function formatCell(value: unknown): string {
  if (value == null) return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function humanizeKey(key: string): string {
  return key
    .replace(/_/g, " ")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function EmptyState({ label = "No data linked" }: { label?: string }) {
  return (
    <p className="text-sm text-muted-foreground py-6 text-center border border-dashed border-border rounded-lg">
      {label}
    </p>
  );
}

function KeyValueTable({ data }: { data: Record<string, JsonValue> }) {
  const entries = Object.entries(data);
  if (!entries.length) return <EmptyState />;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[40%]">Field</TableHead>
          <TableHead>Value</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entries.map(([key, value]) => (
          <TableRow key={key}>
            <TableCell className="font-medium text-muted-foreground align-top">
              {humanizeKey(key)}
            </TableCell>
            <TableCell className="font-mono text-xs break-all whitespace-pre-wrap">
              {typeof value === "object" && value !== null
                ? JSON.stringify(value, null, 2)
                : formatCell(value)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

function ObjectRowsTable({ rows }: { rows: Record<string, JsonValue>[] }) {
  if (!rows.length) return <EmptyState label="No records linked" />;

  const columns = Array.from(
    rows.reduce((set, row) => {
      Object.keys(row).forEach((k) => set.add(k));
      return set;
    }, new Set<string>()),
  );

  const visible = rows.slice(0, RECORDS_ROW_CAP);
  const truncated = rows.length > RECORDS_ROW_CAP;

  return (
    <div className="space-y-2">
      {truncated && (
        <p className="text-xs text-muted-foreground">
          Showing first {RECORDS_ROW_CAP} of {rows.length} records
        </p>
      )}
      <div className="rounded-md border border-border overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col} className="whitespace-nowrap">
                  {humanizeKey(col)}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {visible.map((row, idx) => (
              <TableRow key={idx}>
                {columns.map((col) => (
                  <TableCell key={col} className="font-mono text-xs whitespace-nowrap max-w-[220px] truncate">
                    {formatCell(row[col])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

function PrimitiveListTable({ values }: { values: JsonValue[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-14">#</TableHead>
          <TableHead>Value</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {values.map((value, idx) => (
          <TableRow key={idx}>
            <TableCell className="text-muted-foreground">{idx + 1}</TableCell>
            <TableCell className="font-mono text-xs break-all">{formatCell(value)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

/** Render nested JSON as sectioned tables for Summary tabs. */
export function JsonStructuredView({
  value,
  emptyLabel,
}: {
  value: unknown;
  emptyLabel?: string;
}) {
  const parsed = coerceJsonValue(value);
  if (parsed == null) return <EmptyState label={emptyLabel} />;

  if (Array.isArray(parsed)) {
    if (!parsed.length) return <EmptyState label={emptyLabel} />;
    const allObjects = parsed.every(
      (item) => item !== null && typeof item === "object" && !Array.isArray(item),
    );
    if (allObjects) {
      return <ObjectRowsTable rows={parsed as Record<string, JsonValue>[]} />;
    }
    return <PrimitiveListTable values={parsed} />;
  }

  if (typeof parsed === "object") {
    const entries = Object.entries(parsed as Record<string, JsonValue>);
    if (!entries.length) return <EmptyState label={emptyLabel} />;

    const scalarEntries: [string, JsonValue][] = [];
    const nestedSections: ReactNode[] = [];

    for (const [key, child] of entries) {
      if (child !== null && typeof child === "object") {
        nestedSections.push(
          <div key={key} className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {humanizeKey(key)}
            </h4>
            <JsonStructuredView value={child} emptyLabel={`No ${humanizeKey(key).toLowerCase()} data`} />
          </div>,
        );
      } else {
        scalarEntries.push([key, child]);
      }
    }

    return (
      <div className="space-y-4">
        {scalarEntries.length > 0 && (
          <KeyValueTable data={Object.fromEntries(scalarEntries)} />
        )}
        {nestedSections}
      </div>
    );
  }

  return (
    <p className="text-sm font-mono break-all border border-border rounded-lg p-3 bg-muted/40">
      {formatCell(parsed)}
    </p>
  );
}

/** Columnar table for payload_json record arrays. */
export function JsonRecordsView({ value }: { value: unknown }) {
  const parsed = coerceJsonValue(value);
  if (parsed == null) return <EmptyState label="No telemetry records linked" />;

  if (Array.isArray(parsed)) {
    if (!parsed.length) return <EmptyState label="No telemetry records linked" />;
    const allObjects = parsed.every(
      (item) => item !== null && typeof item === "object" && !Array.isArray(item),
    );
    if (allObjects) {
      return <ObjectRowsTable rows={parsed as Record<string, JsonValue>[]} />;
    }
    return <PrimitiveListTable values={parsed} />;
  }

  if (typeof parsed === "object") {
    return <KeyValueTable data={parsed as Record<string, JsonValue>} />;
  }

  return <EmptyState label="No telemetry records linked" />;
}

export function JsonRawView({ value }: { value: unknown }) {
  const parsed = coerceJsonValue(value);
  if (parsed == null) return <EmptyState label="No raw payload linked" />;

  return (
    <ScrollArea className="h-[320px] rounded-lg border border-border bg-muted/40">
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed">
        {JSON.stringify(parsed, null, 2)}
      </pre>
    </ScrollArea>
  );
}
