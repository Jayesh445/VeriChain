"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Bot,
  LayoutDashboard,
  Package,
  Users,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Shield,
  Bell,
  LogOut,
} from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

interface SidebarProps {
  userRole: "scm" | "finance"
}

export function Sidebar({ userRole }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  const scmNavItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard/scm", badge: null },
    { icon: Package, label: "Inventory", href: "/dashboard/scm/inventory", badge: "12" },
    { icon: FileText, label: "Orders", href: "/dashboard/scm/orders", badge: "3" },
    { icon: Users, label: "Vendors", href: "/dashboard/scm/vendors", badge: null },
    { icon: BarChart3, label: "Reports", href: "/dashboard/scm/reports", badge: null },
    { icon: Bell, label: "Alerts", href: "/dashboard/scm/alerts", badge: "5" },
  ]

  const financeNavItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard/finance", badge: null },
    { icon: FileText, label: "Reports", href: "/dashboard/finance/reports", badge: null },
    { icon: Shield, label: "Audit Trail", href: "/dashboard/finance/audit", badge: "2" },
    { icon: BarChart3, label: "Analytics", href: "/dashboard/finance/analytics", badge: null },
    { icon: Bell, label: "Compliance", href: "/dashboard/finance/compliance", badge: "1" },
  ]

  const navItems = userRole === "scm" ? scmNavItems : financeNavItems

  return (
    <div
      className={cn(
        "relative flex flex-col bg-card border-r border-border transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display text-lg font-bold">VeriChain</span>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={() => setIsCollapsed(!isCollapsed)} className="w-8 h-8 p-0">
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={cn(
                    "w-full justify-start",
                    isCollapsed ? "px-2" : "px-3",
                    isActive && "bg-primary/10 text-primary hover:bg-primary/20",
                  )}
                >
                  <item.icon className={cn("w-4 h-4", isCollapsed ? "mr-0" : "mr-3")} />
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 text-left">{item.label}</span>
                      {item.badge && (
                        <Badge variant="secondary" className="ml-auto text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Button>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <Link href="/dashboard/settings">
          <Button variant="ghost" className={cn("w-full justify-start", isCollapsed ? "px-2" : "px-3")}>
            <Settings className={cn("w-4 h-4", isCollapsed ? "mr-0" : "mr-3")} />
            {!isCollapsed && <span>Settings</span>}
          </Button>
        </Link>
        <Button
          variant="ghost"
          className={cn("w-full justify-start mt-2 text-muted-foreground", isCollapsed ? "px-2" : "px-3")}
          onClick={() => (window.location.href = "/auth/login")}
        >
          <LogOut className={cn("w-4 h-4", isCollapsed ? "mr-0" : "mr-3")} />
          {!isCollapsed && <span>Sign Out</span>}
        </Button>
      </div>
    </div>
  )
}
