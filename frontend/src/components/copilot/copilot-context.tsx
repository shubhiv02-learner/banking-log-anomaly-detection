import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type CopilotContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
  openCopilot: () => void;
};

const CopilotContext = createContext<CopilotContextValue | null>(null);

export function CopilotProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const openCopilot = useCallback(() => setOpen(true), []);
  const value = useMemo(
    () => ({ open, setOpen, openCopilot }),
    [open, openCopilot],
  );

  return (
    <CopilotContext.Provider value={value}>{children}</CopilotContext.Provider>
  );
}

export function useCopilot() {
  const context = useContext(CopilotContext);
  if (!context) {
    throw new Error("useCopilot must be used within a CopilotProvider.");
  }
  return context;
}
