import type { ReactNode } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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
            <TableCell className="font-mono text-xs break-all whitespace-pre-wrap text-foreground">
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
      <div className="rounded-md border border-border overflow-x-auto bg-card">
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
    <div className="h-[min(420px,50vh)] overflow-y-auto rounded-lg border border-border bg-card text-card-foreground [scrollbar-gutter:stable] [scrollbar-width:thin]">
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed text-foreground">
        {JSON.stringify(parsed, null, 2)}
      </pre>
    </div>
  );
}

function asStringList(value: unknown): string[] {
  const parsed = coerceJsonValue(value);
  if (!Array.isArray(parsed)) return [];
  return parsed
    .flatMap((item) => {
      if (item == null) return [];
      if (typeof item === "string" || typeof item === "number" || typeof item === "boolean") {
        return [String(item)];
      }
      if (typeof item === "object" && !Array.isArray(item)) {
        const obj = item as Record<string, JsonValue>;
        const id =
          obj.error_code ?? obj.client_id ?? obj.machine_id ?? obj.id ?? obj.name ?? obj.value;
        if (id != null && typeof id !== "object") return [String(id)];
      }
      return [];
    })
    .filter(Boolean);
}

function extractErrorCode(item: JsonValue): string | null {
  if (typeof item === "string" || typeof item === "number") return String(item);
  if (Array.isArray(item)) {
    // consumer historically nested details oddly; take first usable code
    for (const nested of item) {
      const code = extractErrorCode(nested);
      if (code) return code;
    }
    return null;
  }
  if (item && typeof item === "object") {
    const obj = item as Record<string, JsonValue>;
    const code = obj.error_code ?? obj.code;
    if (code != null && typeof code !== "object") return String(code);
  }
  return null;
}

function buildErrorNameMap(metricsDetails: unknown): Map<string, string> {
  const map = new Map<string, string>();
  const parsed = coerceJsonValue(metricsDetails);
  if (!Array.isArray(parsed)) return map;

  for (const row of parsed) {
    if (!row || typeof row !== "object" || Array.isArray(row)) continue;
    const obj = row as Record<string, JsonValue>;
    const code = obj.error_code ?? obj.code;
    const name = obj.error_name ?? obj.description;
    if (code != null && typeof code !== "object") {
      map.set(
        String(code),
        name != null && typeof name !== "object" ? String(name) : "Unknown Error",
      );
    }
  }
  return map;
}

function CommaListSection({
  title,
  values,
  count,
}: {
  title: string;
  values: string[];
  count?: number;
}) {
  const displayCount = count ?? values.length;
  const heading =
    count != null || values.length > 0 ? `${title} (${displayCount})` : title;
  return (
    <div className="space-y-2 rounded-lg border border-border bg-card p-3">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {heading}
      </h4>
      {values.length ? (
        <p className="text-sm text-foreground leading-relaxed break-words">{values.join(", ")}</p>
      ) : (
        <p className="text-sm text-muted-foreground">None</p>
      )}
    </div>
  );
}

function scalarCount(value: JsonValue | undefined, fallback: number): number {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "" && !Number.isNaN(Number(value))) {
    return Number(value);
  }
  return fallback;
}

/** Domain-aware summary for payload_summary / incident_summary. */
export function PayloadSummaryView({
  value,
  emptyLabel = "No telemetry summary linked",
}: {
  value: unknown;
  emptyLabel?: string;
}) {
  const parsed = coerceJsonValue(value);
  if (parsed == null || typeof parsed !== "object" || Array.isArray(parsed)) {
    return <EmptyState label={emptyLabel} />;
  }

  const summary = parsed as Record<string, JsonValue>;
  const regions = asStringList(summary.regions);
  const topClients = asStringList(summary.top_clients);
  const topHosts = asStringList(summary.top_hosts);
  const topEndpoints = asStringList(summary.top_endpoints);
  const nameByCode = buildErrorNameMap(summary.metrics_details);

  const topErrorsRaw = Array.isArray(summary.top_errors) ? summary.top_errors : [];
  const errorRows: { code: string; name: string }[] = [];
  const seen = new Set<string>();

  for (const item of topErrorsRaw) {
    const code = extractErrorCode(item);
    if (!code || seen.has(code)) continue;
    seen.add(code);
    let name = nameByCode.get(code);
    if (!name && item && typeof item === "object" && !Array.isArray(item)) {
      const obj = item as Record<string, JsonValue>;
      const n = obj.error_name ?? obj.description;
      if (n != null && typeof n !== "object") name = String(n);
    }
    errorRows.push({ code, name: name ?? "Unknown Error" });
  }

  if (!errorRows.length && nameByCode.size) {
    for (const [code, name] of nameByCode) {
      errorRows.push({ code, name });
    }
  }

  const reserved = new Set([
    "regions",
    "top_clients",
    "top_hosts",
    "top_endpoints",
    "top_errors",
    "metrics_details",
    "affected_clients",
    "affected_hosts",
  ]);
  const scalarEntries = Object.entries(summary).filter(
    ([key, val]) => !reserved.has(key) && (val === null || typeof val !== "object"),
  );

  const clientCount = scalarCount(summary.affected_clients, topClients.length);
  const hostCount = scalarCount(summary.affected_hosts, topHosts.length);

  return (
    <div className="space-y-4 text-foreground">
      <CommaListSection title="Regions" values={regions} />

      <div className="space-y-2">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Top Errors
        </h4>
        {errorRows.length ? (
          <div className="rounded-md border border-border overflow-x-auto bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Error Code</TableHead>
                  <TableHead>Error Name</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {errorRows.map((row) => (
                  <TableRow key={row.code}>
                    <TableCell className="font-mono text-xs">{row.code}</TableCell>
                    <TableCell className="text-sm">{row.name}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground border border-dashed border-border rounded-lg px-3 py-4">
            No top errors linked
          </p>
        )}
      </div>

      <CommaListSection title="Top Clients" values={topClients} count={clientCount} />
      <CommaListSection title="Top Hosts" values={topHosts} count={hostCount} />
      {topEndpoints.length > 0 && (
        <CommaListSection title="Top Endpoints" values={topEndpoints} />
      )}

      {scalarEntries.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Other Metrics
          </h4>
          <div className="rounded-md border border-border overflow-x-auto bg-card">
            <KeyValueTable data={Object.fromEntries(scalarEntries)} />
          </div>
        </div>
      )}
    </div>
  );
}
