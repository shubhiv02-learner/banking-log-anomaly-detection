import type { ReactNode } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { CopilotPanel } from "@/components/copilot/copilot-panel";
import { CopilotProvider } from "@/components/copilot/copilot-context";
import { AppSidebar } from "./app-sidebar";
import { AppTopbar } from "./app-topbar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <CopilotProvider>
        <div className="flex min-h-screen w-full bg-background text-foreground">
          <AppSidebar />
          <div className="flex flex-1 flex-col">
            <AppTopbar />
            <main className="flex-1 p-4 md:p-6">{children}</main>
          </div>
          <CopilotPanel />
        </div>
      </CopilotProvider>
    </SidebarProvider>
  );
}
