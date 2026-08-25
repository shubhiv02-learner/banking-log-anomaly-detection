import { Bell, Search, UserRound } from "lucide-react";
import { useRouterState } from "@tanstack/react-router";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { CopilotTopbarButton } from "@/components/copilot/copilot-panel";
import { useAuth } from "@/lib/auth";

const TITLES: Record<string, string> = {
  "/": "Executive Dashboard",
  "/alerts": "Alerts Center",
  "/analytics": "Service Analytics",
  "/incidents": "Incidents Center",
};

export function AppTopbar() {
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const title = TITLES[pathname] ?? "SentryyIQ";
  const { user } = useAuth();
  const activeUserName = user?.name?.trim() || null;
  const activeUserRole = user?.role?.trim() || null;

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-2 border-b bg-background/80 px-3 backdrop-blur">
      <SidebarTrigger />
      <Separator orientation="vertical" className="mx-1 h-6" />
      <h1 className="text-sm font-semibold tracking-tight">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <div className="relative hidden md:block">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search services, alerts…"
            className="h-8 w-64 pl-8 text-sm"
          />
        </div>
        <Badge variant="outline" className="hidden sm:inline-flex font-mono text-[10px]">
          PROD
        </Badge>
        {activeUserName ? (
          <div
            className="hidden items-center gap-1.5 rounded-md border border-border bg-muted/40 px-2 py-1 sm:flex"
            title={
              activeUserRole
                ? `${activeUserName} (${activeUserRole})`
                : activeUserName
            }
          >
            <UserRound className="h-3.5 w-3.5 text-muted-foreground" />
            <div className="min-w-0 leading-tight">
              <div className="max-w-[10rem] truncate text-xs font-medium">
                {activeUserName}
              </div>
              <div className="text-[10px] text-muted-foreground">Active user</div>
            </div>
          </div>
        ) : null}
        <CopilotTopbarButton />
        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>
        <ThemeToggle />
      </div>
    </header>
  );
}
