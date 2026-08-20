import { Link, useRouterState } from "@tanstack/react-router";
import { Activity, AlertTriangle, Clock, LayoutDashboard, LogOut, ShieldCheck } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";

const navItems = [
  { title: "Executive Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Alerts Center", url: "/alerts", icon: AlertTriangle },
  { title: "Service Analytics", url: "/analytics", icon: Activity },
  { title: "Incidents Center", url: "/incidents", icon: Clock }
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const pathname = useRouterState({ select: (r) => r.location.pathname });
  const isActive = (url: string) =>
    url === "/" ? pathname === "/" : pathname.startsWith(url);
  const { user, logout } = useAuth();
  const displayName = user?.name || "Signed in";
  const displayEmail = user?.email || "";
  const initials = displayName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("") || "?";

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="border-b border-sidebar-border">
        <div className="flex items-center gap-2 px-2 py-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <ShieldCheck className="h-4 w-4" />
          </div>
          {!collapsed && (
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-semibold tracking-tight">
                SentryyIQ
              </span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                Observability
              </span>
            </div>
          )}
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Operations</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.url}>
                  <SidebarMenuButton asChild isActive={isActive(item.url)}>
                    <Link to={item.url} className="flex items-center gap-2">
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border">
        <div className="flex flex-col gap-2 px-2 py-2">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold">
              {initials}
            </div>
            {!collapsed && (
              <div className="min-w-0 flex-1">
                <div className="truncate text-xs font-medium">{displayName}</div>
                {displayEmail ? (
                  <div className="truncate text-[10px] text-muted-foreground">
                    {displayEmail}
                  </div>
                ) : null}
              </div>
            )}
            {collapsed ? (
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8 shrink-0"
                aria-label="Sign out"
                onClick={logout}
              >
                <LogOut className="h-4 w-4" />
              </Button>
            ) : null}
          </div>
          {!collapsed ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="w-full"
              onClick={logout}
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </Button>
          ) : null}
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
