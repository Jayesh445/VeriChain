"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    LayoutDashboard,
    Package,
    Users,
    Brain,
    DollarSign,
    BarChart3,
    ChevronDown,
    ExternalLink
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function QuickAccess() {
    const pathname = usePathname();

    const dashboardLinks = [
        {
            title: "SCM Dashboard",
            href: "/dashboard/scm",
            icon: LayoutDashboard,
            description: "Supply chain operations",
            color: "text-blue-600"
        },
        {
            title: "Finance Dashboard",
            href: "/dashboard/finance",
            icon: DollarSign,
            description: "Financial analysis",
            color: "text-green-600"
        },
        {
            title: "Inventory",
            href: "/dashboard/inventory",
            icon: Package,
            description: "Stock management",
            color: "text-purple-600"
        },
        {
            title: "AI Agent",
            href: "/dashboard/ai-agent",
            icon: Brain,
            description: "Autonomous decisions",
            color: "text-orange-600"
        },
        {
            title: "Vendors",
            href: "/dashboard/vendors",
            icon: Users,
            description: "Supplier management",
            color: "text-indigo-600"
        },
        {
            title: "Analytics",
            href: "/dashboard/analytics",
            icon: BarChart3,
            description: "Data insights",
            color: "text-pink-600"
        }
    ];

    const currentDashboard = dashboardLinks.find(link => pathname === link.href);

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2">
                    {currentDashboard ? (
                        <>
                            <currentDashboard.icon className={`h-4 w-4 ${currentDashboard.color}`} />
                            {currentDashboard.title}
                        </>
                    ) : (
                        <>
                            <LayoutDashboard className="h-4 w-4" />
                            Switch Dashboard
                        </>
                    )}
                    <ChevronDown className="h-4 w-4" />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-64">
                <DropdownMenuLabel>Available Dashboards</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {dashboardLinks.map((link) => (
                    <DropdownMenuItem key={link.href} asChild>
                        <Link href={link.href} className="flex items-center gap-3 p-3">
                            <link.icon className={`h-5 w-5 ${link.color}`} />
                            <div className="flex-1">
                                <div className="font-medium">{link.title}</div>
                                <div className="text-xs text-muted-foreground">{link.description}</div>
                            </div>
                            {pathname === link.href && (
                                <Badge variant="secondary" className="text-xs">Current</Badge>
                            )}
                            <ExternalLink className="h-3 w-3 opacity-50" />
                        </Link>
                    </DropdownMenuItem>
                ))}
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                    <Link href="/dashboard" className="flex items-center gap-2 p-2">
                        <LayoutDashboard className="h-4 w-4" />
                        Dashboard Home
                    </Link>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

export function DashboardBreadcrumb() {
    const pathname = usePathname();

    const getBreadcrumbInfo = () => {
        switch (pathname) {
            case "/dashboard":
                return { title: "Dashboard Home", description: "VeriChain AI Supply Chain Management" };
            case "/dashboard/scm":
                return { title: "Supply Chain Manager", description: "Operations monitoring and AI insights" };
            case "/dashboard/finance":
                return { title: "Finance Dashboard", description: "Cost analysis and budget tracking" };
            case "/dashboard/inventory":
                return { title: "Inventory Management", description: "Stock levels and item management" };
            case "/dashboard/ai-agent":
                return { title: "AI Agent Monitor", description: "Autonomous decisions and performance" };
            case "/dashboard/vendors":
                return { title: "Vendor Management", description: "Supplier performance and contacts" };
            case "/dashboard/analytics":
                return { title: "Analytics & Reports", description: "Data visualization and insights" };
            default:
                return { title: "Dashboard", description: "VeriChain Management" };
        }
    };

    const { title, description } = getBreadcrumbInfo();

    return (
        <div className="flex items-center justify-between mb-6">
            <div>
                <h1 className="text-3xl font-bold">{title}</h1>
                <p className="text-gray-600 mt-1">{description}</p>
            </div>
            <QuickAccess />
        </div>
    );
}