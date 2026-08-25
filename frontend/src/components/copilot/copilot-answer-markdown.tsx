import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

const markdownComponents: Components = {
  p: ({ children }) => (
    <p className="mb-2 leading-relaxed text-foreground last:mb-0">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-foreground">{children}</strong>
  ),
  em: ({ children }) => <em className="italic">{children}</em>,
  ol: ({ children }) => (
    <ol className="mb-2 list-decimal space-y-1.5 pl-5 text-foreground">{children}</ol>
  ),
  ul: ({ children }) => (
    <ul className="mb-2 list-disc space-y-1.5 pl-5 text-foreground">{children}</ul>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  h1: ({ children }) => (
    <h1 className="mb-2 mt-3 text-base font-semibold text-foreground first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-2 mt-3 text-sm font-semibold text-foreground first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-2 mt-3 text-sm font-semibold text-foreground first:mt-0">
      {children}
    </h3>
  ),
  hr: () => <hr className="my-3 border-border" />,
  code: ({ children }) => (
    <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.85em]">{children}</code>
  ),
};

type CopilotAnswerMarkdownProps = {
  content: string;
};

/** Renders Salveris Copilot answers (markdown headings, lists, emphasis). */
export function CopilotAnswerMarkdown({ content }: CopilotAnswerMarkdownProps) {
  const text = content.trim() || "No answer returned.";
  return (
    <div className="copilot-answer-markdown max-w-prose text-[0.9375rem] leading-relaxed">
      <ReactMarkdown components={markdownComponents}>{text}</ReactMarkdown>
    </div>
  );
}
