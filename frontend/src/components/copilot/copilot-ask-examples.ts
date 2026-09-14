/**
 * Static Copilot example asks for the Help sheet.
 */

export type CopilotExampleSection = {
  title: string;
  subtitle?: string;
  examples: string[];
};

export const COPILOT_ASK_EXAMPLES: CopilotExampleSection[] = [
  {
    title: "Operational",
    examples: [
      "Show Current critical incidents",
      "Show dashboard summary",
    ],
  },
  {
    title: "Investigation",
    subtitle: "Basic / Detailed / relationships / comparison / follow-up",
    examples: [
      "Investigate incident INC-20260805-3248",
      "Investigate INC-20260805-3248 and show raw telemetry along with analysis",
      "Do deep investigation of INC-20260805-3248",
      "Investigate INC-20260805-3248 and find if any other alerts for same service",
      "Investigate INC-20260805-3248 and find related alerts in same window",
    ],
  },
  {
    title: "Knowledge",
    examples: [
      "What does the SentryyIQ error runbook say about Ollama embedding timeout?",
      "Explain error code ERR-701",
      "How incident closure work in system",
      "Investigate INC-20260626-3098 and what does the runbook say for ERR-705?",
    ],
  },
];
