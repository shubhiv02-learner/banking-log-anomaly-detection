import { useState } from "react";
import { Loader2, MessageSquare } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  api,
  type CopilotAskResponse,
  type CopilotSearchResponse,
} from "@/lib/api/client";

type Mode = "ask" | "search";

export function CopilotPanel() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<Mode>("ask");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [askResult, setAskResult] = useState<CopilotAskResponse | null>(null);
  const [searchResult, setSearchResult] = useState<CopilotSearchResponse | null>(
    null,
  );

  async function onSubmit() {
    const q = question.trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    setAskResult(null);
    setSearchResult(null);

    try {
      if (mode === "ask") {
        const result = await api.copilotAsk(q);
        setAskResult(result);
      } else {
        const result = await api.copilotSearch(q);
        setSearchResult(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="gap-1.5"
          aria-label="Ask SentryyIQ Copilot"
        >
          <MessageSquare className="h-4 w-4" />
          <span className="hidden sm:inline">Copilot</span>
        </Button>
      </SheetTrigger>
      <SheetContent
        side="right"
        className="flex w-full flex-col gap-4 sm:max-w-md lg:max-w-lg"
      >
        <SheetHeader>
          <SheetTitle>Ask SentryyIQ Copilot</SheetTitle>
          <SheetDescription>
            Answer returns a grounded reply with sources. Search returns matching
            passages only — no answer.
          </SheetDescription>
        </SheetHeader>

        <div className="flex gap-2">
          <Button
            type="button"
            size="sm"
            variant={mode === "ask" ? "default" : "outline"}
            onClick={() => setMode("ask")}
          >
            Answer
          </Button>
          <Button
            type="button"
            size="sm"
            variant={mode === "search" ? "default" : "outline"}
            onClick={() => setMode("search")}
          >
            Search
          </Button>
        </div>

        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What does the operations guide say about…"
          className="min-h-[100px] resize-none"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              void onSubmit();
            }
          }}
        />

        <Button type="button" onClick={() => void onSubmit()} disabled={loading || !question.trim()}>
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Working…
            </>
          ) : mode === "search" ? (
            "Search"
          ) : (
            "Ask"
          )}
        </Button>

        {error ? (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        ) : null}

        <Separator />

        <ScrollArea className="min-h-0 flex-1 pr-2">
          {askResult ? (
            <div className="space-y-4 pb-4">
              <section>
                <h3 className="mb-2 text-sm font-semibold">Answer</h3>
                <p className="whitespace-pre-wrap text-sm text-foreground">
                  {askResult.answer || "No answer returned."}
                </p>
              </section>
              {askResult.confidence ? (
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-muted-foreground">Confidence:</span>
                  <Badge variant="secondary">{askResult.confidence}</Badge>
                </div>
              ) : null}
              {askResult.sources?.length ? (
                <section>
                  <h3 className="mb-2 text-sm font-semibold">Sources</h3>
                  <ul className="space-y-2">
                    {askResult.sources.map((src, i) => (
                      <li
                        key={`${src.title}-${i}`}
                        className="rounded-md border border-border p-2 text-sm"
                      >
                        <div className="font-medium">{src.title}</div>
                        {src.snippet ? (
                          <p className="mt-1 text-muted-foreground">{src.snippet}</p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                </section>
              ) : null}
            </div>
          ) : null}

          {searchResult ? (
            <div className="space-y-3 pb-4">
              <h3 className="text-sm font-semibold">Search</h3>
              {searchResult.hits.length === 0 ? (
                <p className="text-sm text-muted-foreground">No matching passages.</p>
              ) : (
                <ul className="space-y-2">
                  {searchResult.hits.map((hit, i) => (
                    <li
                      key={`${hit.title}-${i}`}
                      className="rounded-md border border-border p-2 text-sm"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-medium">{hit.title}</span>
                        {hit.score != null ? (
                          <Badge variant="outline" className="shrink-0 font-mono text-[10px]">
                            {Number(hit.score).toFixed(2)}
                          </Badge>
                        ) : null}
                      </div>
                      {hit.snippet ? (
                        <p className="mt-1 text-muted-foreground">{hit.snippet}</p>
                      ) : null}
                      {hit.source ? (
                        <p className="mt-1 text-xs text-muted-foreground">{hit.source}</p>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : null}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
