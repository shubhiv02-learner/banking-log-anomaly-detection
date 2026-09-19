import { useRef, useState } from "react";
import { CircleHelp, Loader2, MessageSquare, UserRound } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  api,
  type CopilotAskResponse,
  type CopilotSearchResponse,
} from "@/lib/api/client";
import { useAuth } from "@/lib/auth-context";
import { CopilotAnswerMarkdown } from "@/components/copilot/copilot-answer-markdown";
import { COPILOT_ASK_EXAMPLES } from "@/components/copilot/copilot-ask-examples";
import { useCopilot } from "@/components/copilot/copilot-context";

type Mode = "ask" | "search";

/** Top-bar control that opens the shared Copilot dialog. */
export function CopilotTopbarButton() {
  const { openCopilot } = useCopilot();
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className="gap-1.5"
      aria-label="Ask SentryyIQ Copilot"
      onClick={openCopilot}
    >
      <MessageSquare className="h-4 w-4" />
      <span className="hidden sm:inline">Copilot</span>
    </Button>
  );
}

/** Hosted once in the app shell — large centered panel for long answers. */
export function CopilotPanel() {
  const { open, setOpen } = useCopilot();
  const { user } = useAuth();
  const activeUserName = user?.name?.trim() || null;
  const activeUserRole = user?.role?.trim() || null;
  const questionRef = useRef<HTMLTextAreaElement | null>(null);
  const [question, setQuestion] = useState("");
  const [mode, setMode] = useState<Mode>("ask");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [askResult, setAskResult] = useState<CopilotAskResponse | null>(null);
  const [searchResult, setSearchResult] = useState<CopilotSearchResponse | null>(
    null,
  );
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);

  function onClear() {
    setQuestion("");
    setError(null);
    setAskResult(null);
    setSearchResult(null);
    setLoading(false);
  }

  async function onCloseConversation() {
    if (loading) return;
    setError(null);
    if (conversationId) {
      setLoading(true);
      try {
        await api.copilotClose(conversationId);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Close failed");
        setLoading(false);
        return;
      } finally {
        setLoading(false);
      }
    }
    setConversationId(null);
    onClear();
  }

  function onPickExample(example: string) {
    setQuestion(example);
    setHelpOpen(false);
    window.setTimeout(() => questionRef.current?.focus(), 0);
  }

  async function onSubmit() {
    const q = question.trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    setAskResult(null);
    setSearchResult(null);

    try {
      if (mode === "ask") {
        const result = await api.copilotAsk(q, undefined, conversationId);
        setAskResult(result);
        if (result.conversation_id) {
          setConversationId(result.conversation_id);
        }
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
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent
          className={
            "flex h-[min(92vh,900px)] w-[min(100vw-1.5rem,72rem)] max-w-none " +
            "flex-col gap-4 overflow-hidden p-5 sm:p-6"
          }
        >
          <DialogHeader className="shrink-0 space-y-1.5 pr-8 text-left">
            <div className="flex items-start gap-2">
              <div className="min-w-0 flex-1 space-y-1.5">
                <DialogTitle>Ask SentryyIQ Copilot</DialogTitle>
                <DialogDescription>
                  Answer returns a grounded reply with sources. Search returns
                  matching passages only — no answer.
                </DialogDescription>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="shrink-0"
                aria-label="What can I ask?"
                onClick={() => setHelpOpen(true)}
              >
                <CircleHelp className="h-4 w-4" />
              </Button>
            </div>
          </DialogHeader>

          {activeUserName ? (
            <div className="flex shrink-0 items-center gap-2 rounded-md border border-border bg-muted/40 px-3 py-2 text-sm">
              <UserRound className="h-4 w-4 shrink-0 text-muted-foreground" />
              <p className="min-w-0 truncate">
                <span className="text-muted-foreground">Active user</span>
                <span className="mx-1.5 text-muted-foreground">·</span>
                <span className="font-medium">{activeUserName}</span>
                {activeUserRole ? (
                  <>
                    <span className="mx-1.5 text-muted-foreground">·</span>
                    <span className="text-muted-foreground">{activeUserRole}</span>
                  </>
                ) : null}
              </p>
            </div>
          ) : (
            <p className="shrink-0 text-sm text-muted-foreground">
              Sign in to attribute Copilot asks to an active user.
            </p>
          )}

          <div className="flex shrink-0 gap-2">
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
            ref={questionRef}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What does the operations guide say about…"
            className="min-h-[88px] shrink-0 resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                void onSubmit();
              }
            }}
          />

          <div className="flex shrink-0 flex-wrap items-center gap-2">
            <Button
              type="button"
              className="shrink-0"
              onClick={() => void onSubmit()}
              disabled={loading || !question.trim()}
            >
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
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onClear}
              disabled={loading}
            >
              Clear
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => void onCloseConversation()}
              disabled={loading}
            >
              Close
            </Button>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              className="gap-1.5"
              aria-label="What can I ask?"
              onClick={() => setHelpOpen(true)}
            >
              <CircleHelp className="h-4 w-4" />
              <span className="hidden sm:inline">Examples</span>
            </Button>
          </div>

          {error ? (
            <p className="shrink-0 text-sm text-destructive" role="alert">
              {error}
            </p>
          ) : null}

          <Separator className="shrink-0" />

          <ScrollArea className="min-h-0 w-full flex-1 pr-3">
            {askResult ? (
              <div className="w-full max-w-none space-y-4 pb-4">
                <section className="w-full max-w-none">
                  <h3 className="mb-2 text-sm font-semibold">Answer</h3>
                  <CopilotAnswerMarkdown content={askResult.answer || ""} />
                </section>
                {askResult.confidence ? (
                  <div className="w-full max-w-none space-y-1 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground">Confidence:</span>
                      <Badge variant="secondary">{askResult.confidence}</Badge>
                    </div>
                    {askResult.confidence_rationale ? (
                      <p className="w-full max-w-none text-muted-foreground">
                        {askResult.confidence_rationale}
                      </p>
                    ) : null}
                  </div>
                ) : null}
                {askResult.sources?.length ? (
                  <section className="w-full max-w-none">
                    <h3 className="mb-2 text-sm font-semibold">Sources</h3>
                    <ul className="w-full space-y-2">
                      {askResult.sources.map((src, i) => (
                        <li
                          key={`${src.title}-${i}`}
                          className="w-full rounded-md border border-border p-2 text-sm"
                        >
                          <div className="font-medium">{src.title}</div>
                          {src.snippet ? (
                            <p className="mt-1 w-full text-muted-foreground">
                              {src.snippet}
                            </p>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  </section>
                ) : null}
              </div>
            ) : null}

            {searchResult ? (
              <div className="w-full max-w-none space-y-3 pb-4">
                <h3 className="text-sm font-semibold">Search</h3>
                {searchResult.hits.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No matching passages.
                  </p>
                ) : (
                  <ul className="w-full space-y-2">
                    {searchResult.hits.map((hit, i) => (
                      <li
                        key={`${hit.title}-${i}`}
                        className="w-full rounded-md border border-border p-2 text-sm"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <span className="font-medium">{hit.title}</span>
                          {hit.score != null ? (
                            <Badge
                              variant="outline"
                              className="shrink-0 font-mono text-[10px]"
                            >
                              {Number(hit.score).toFixed(2)}
                            </Badge>
                          ) : null}
                        </div>
                        {hit.snippet ? (
                          <p className="mt-1 w-full text-muted-foreground">
                            {hit.snippet}
                          </p>
                        ) : null}
                        {hit.source ? (
                          <p className="mt-1 text-xs text-muted-foreground">
                            {hit.source}
                          </p>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : null}
          </ScrollArea>
        </DialogContent>
      </Dialog>

      <Sheet open={helpOpen} onOpenChange={setHelpOpen}>
        <SheetContent
          side="right"
          className="flex w-full flex-col gap-4 overflow-y-auto sm:max-w-md"
        >
          <SheetHeader>
            <SheetTitle>What can I ask?</SheetTitle>
            <SheetDescription>
              Pick an example to fill the ask box. You can edit it before sending.
            </SheetDescription>
          </SheetHeader>
          <div className="flex flex-1 flex-col gap-5 pb-6">
            {COPILOT_ASK_EXAMPLES.map((section) => (
              <section key={section.title} className="space-y-2">
                <div>
                  <h3 className="text-sm font-semibold">{section.title}</h3>
                  {section.subtitle ? (
                    <p className="text-xs text-muted-foreground">
                      {section.subtitle}
                    </p>
                  ) : null}
                </div>
                <div className="flex flex-col gap-2">
                  {section.examples.map((example) => (
                    <Button
                      key={example}
                      type="button"
                      variant="outline"
                      className="h-auto whitespace-normal px-3 py-2 text-left text-sm font-normal"
                      onClick={() => onPickExample(example)}
                    >
                      {example}
                    </Button>
                  ))}
                </div>
              </section>
            ))}
            <p className="text-sm text-muted-foreground">
              You can also ask anything in natural language.
            </p>
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}
