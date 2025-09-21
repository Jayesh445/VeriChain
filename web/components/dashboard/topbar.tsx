"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { NotificationSystem } from "@/components/notifications";
import {
  Bell,
  Search,
  Globe,
  Moon,
  Sun,
  User,
  Settings,
  LogOut,
} from "lucide-react";

interface TopbarProps {
  userRole?: "scm" | "finance" | "admin" | "inventory" | "ai-agent" | "vendor";
  userName: string;
  userEmail: string;
}

export function Topbar({ userRole, userName, userEmail }: TopbarProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  };

  const roleDisplayName =
    userRole === "scm" ? "Supply Chain Manager" :
      userRole === "finance" ? "Finance Officer" :
        userRole === "admin" ? "Administrator" : "User";

  return (
    <header className="flex items-center justify-between px-6 py-4 bg-background border-b border-border">
      {/* Search */}
      <div className="flex items-center space-x-4 flex-1 max-w-md">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search....." className="pl-10" />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-4">
        {/* Language Selector */}
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="ghost" size="sm" className="w-9 h-9 p-0">
              <Globe className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>English</DropdownMenuItem>
            <DropdownMenuItem>Spanish</DropdownMenuItem>
            <DropdownMenuItem>French</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Dark Mode Toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleDarkMode}
          className="w-9 h-9 p-0"
        >
          {isDarkMode ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </Button>

        {/* Notifications */}
        <NotificationSystem />

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 w-10 rounded-full">
              <Avatar className="h-10 w-10">
                <AvatarImage
                  src="https://github.com/shadcn.png"
                  alt={userName}
                />
                <AvatarFallback>
                  {userName
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{userName}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {userEmail}
                </p>
                <Badge variant="secondary" className="w-fit text-xs mt-1">
                  {roleDisplayName}
                </Badge>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => (window.location.href = "/auth/login")}
            >
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
