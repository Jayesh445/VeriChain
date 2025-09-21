"use client"

import type React from "react"
import { NotificationSystem, ToastContainer } from "@/components/notifications"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"

interface DashboardLayoutProps {
  children: React.ReactNode
  userRole?: "scm" | "finance" | "admin" | "inventory" | "ai-agent" | "vendor"
  userName?: string
  userEmail?: string
}

export function DashboardLayout({
  children,
  userRole = "admin",
  userName = "Demo User",
  userEmail = "demo@verichain.ai",
}: DashboardLayoutProps) {
  return (
    <>
      <div className="flex h-screen bg-background">
        <Sidebar userRole={userRole} />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Topbar userRole={userRole} userName={userName} userEmail={userEmail} />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </div>
      </div>
      <ToastContainer />
    </>
  )
}
