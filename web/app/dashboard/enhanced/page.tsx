"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Bell,
    Brain,
    Activity,
    BarChart3,
    Package,
    DollarSign,
    TrendingUp,
    Users,
    AlertTriangle
} from "lucide-react";
import NotificationCenter from "@/components/NotificationCenter";
import AIAgentDashboard from "../ai-agent/page";

export default function EnhancedDashboard() {
    const [activeTab, setActiveTab] = useState("overview");
    const [notificationCount, setNotificationCount] = useState(2);

    const handleNotificationUpdate = () => {
        // This would be called when notifications are processed
        setNotificationCount(prev => Math.max(0, prev - 1));
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto p-6 space-y-6">
                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">VeriChain Dashboard</h1>
                        <p className="text-gray-600">AI-Powered Supply Chain Management</p>
                    </div>
                    <div className="flex items-center space-x-4">
                        <Button
                            variant={activeTab === "notifications" ? "default" : "outline"}
                            onClick={() => setActiveTab("notifications")}
                            className="relative"
                        >
                            <Bell className="h-4 w-4 mr-2" />
                            Notifications
                            {notificationCount > 0 && (
                                <Badge variant="destructive" className="absolute -top-2 -right-2 rounded-full px-1 min-w-[1.25rem] h-5 text-xs">
                                    {notificationCount}
                                </Badge>
                            )}
                        </Button>
                    </div>
                </div>

                {/* Main Content */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="ai-agent">AI Agent</TabsTrigger>
                        <TabsTrigger value="notifications" className="relative">
                            Notifications
                            {notificationCount > 0 && (
                                <Badge variant="destructive" className="absolute -top-1 -right-1 rounded-full px-1 min-w-[1rem] h-4 text-xs">
                                    {notificationCount}
                                </Badge>
                            )}
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="overview" className="space-y-6">
                        {/* Key Metrics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Total Inventory Value</CardTitle>
                                    <DollarSign className="h-4 w-4 text-green-600" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-green-600">$24,580</div>
                                    <p className="text-xs text-muted-foreground">
                                        +12% from last month
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Active Orders</CardTitle>
                                    <Package className="h-4 w-4 text-blue-600" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-blue-600">23</div>
                                    <p className="text-xs text-muted-foreground">
                                        5 pending approval
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">AI Negotiations</CardTitle>
                                    <Brain className="h-4 w-4 text-purple-600" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-purple-600">8</div>
                                    <p className="text-xs text-muted-foreground">
                                        3 completed today
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Cost Savings</CardTitle>
                                    <TrendingUp className="h-4 w-4 text-green-600" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold text-green-600">$3,240</div>
                                    <p className="text-xs text-muted-foreground">
                                        This quarter
                                    </p>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Recent Activity */}
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center">
                                        <Activity className="h-5 w-5 mr-2 text-blue-500" />
                                        Recent AI Decisions
                                    </CardTitle>
                                    <CardDescription>Latest autonomous actions taken by the AI agent</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="flex items-start space-x-3">
                                            <div className="p-1 bg-green-100 rounded-full">
                                                <Package className="h-3 w-3 text-green-600" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-sm font-medium">Order approved for Ballpoint Pens</p>
                                                <p className="text-xs text-gray-500">Negotiated 15% discount with Staples Inc.</p>
                                                <p className="text-xs text-gray-400">2 minutes ago</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start space-x-3">
                                            <div className="p-1 bg-blue-100 rounded-full">
                                                <Brain className="h-3 w-3 text-blue-600" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-sm font-medium">Started negotiation for Office Paper</p>
                                                <p className="text-xs text-gray-500">Contacting 5 vendors for quotes</p>
                                                <p className="text-xs text-gray-400">5 minutes ago</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start space-x-3">
                                            <div className="p-1 bg-orange-100 rounded-full">
                                                <AlertTriangle className="h-3 w-3 text-orange-600" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-sm font-medium">Low stock alert</p>
                                                <p className="text-xs text-gray-500">Printer Ink (Black) below threshold</p>
                                                <p className="text-xs text-gray-400">15 minutes ago</p>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center">
                                        <BarChart3 className="h-5 w-5 mr-2 text-purple-500" />
                                        Performance Summary
                                    </CardTitle>
                                    <CardDescription>AI agent performance metrics</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Success Rate</span>
                                            <Badge variant="outline" className="text-green-600">96.5%</Badge>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Average Savings</span>
                                            <Badge variant="outline" className="text-blue-600">18.2%</Badge>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Response Time</span>
                                            <Badge variant="outline" className="text-purple-600">1.3 min</Badge>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Active Negotiations</span>
                                            <Badge variant="outline" className="text-orange-600">8</Badge>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    <TabsContent value="ai-agent">
                        <AIAgentDashboard />
                    </TabsContent>

                    <TabsContent value="notifications">
                        <NotificationCenter onNotificationUpdate={handleNotificationUpdate} />
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}