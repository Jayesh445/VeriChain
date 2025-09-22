"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { DashboardBreadcrumb } from "@/components/dashboard/quick-access";
import { 
  LayoutDashboard,
  Package,
  Users,
  Brain,
  DollarSign,
  BarChart3,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowRight,
  Activity,
  Target
} from "lucide-react";
import Link from "next/link";
import VeriChainAPI from "@/lib/api";

export default function DashboardHome() {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Fetch data from multiple endpoints for overview
      const [inventoryData, performanceData] = await Promise.all([
        VeriChainAPI.getInventoryItems(),
        VeriChainAPI.getAgentPerformance()
      ]);

      setDashboardData({
        inventory: inventoryData,
        performance: performanceData
      });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const dashboardCards = [
    {
      title: "Supply Chain Manager",
      description: "Monitor operations, AI insights, and performance metrics",
      icon: LayoutDashboard,
      href: "/dashboard/scm",
      color: "bg-blue-500",
      stats: { value: "96%", label: "Efficiency Rate", trend: "+5%" }
    },
    {
      title: "Finance Dashboard",
      description: "Cost analysis, budget tracking, and financial insights",
      icon: DollarSign,
      href: "/dashboard/finance",
      color: "bg-green-500",
      stats: { value: "$44.2K", label: "Monthly Spend", trend: "-8%" }
    },
    {
      title: "Inventory Management",
      description: "Stock levels, item management, and procurement",
      icon: Package,
      href: "/dashboard/inventory",
      color: "bg-purple-500",
      stats: { value: "184", label: "Items in Stock", trend: "-3%" }
    },
    {
      title: "AI Agent Monitor",
      description: "Autonomous decisions, insights, and performance",
      icon: Brain,
      href: "/dashboard/ai-agent",
      color: "bg-orange-500",
      stats: { value: "23", label: "AI Decisions", trend: "+12%" }
    },
    {
      title: "Vendor Management",
      description: "Supplier performance, contacts, and evaluation",
      icon: Users,
      href: "/dashboard/vendors",
      color: "bg-indigo-500",
      stats: { value: "4.2", label: "Avg Rating", trend: "+0.3" }
    },
    {
      title: "Analytics & Reports",
      description: "Data visualization, trends, and insights",
      icon: BarChart3,
      href: "/dashboard/analytics",
      color: "bg-pink-500",
      stats: { value: "7", label: "Active Reports", trend: "+2" }
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header with Breadcrumb */}
      <DashboardBreadcrumb />

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <Activity className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Operational</div>
            <div className="flex items-center text-xs text-green-600">
              <CheckCircle className="h-3 w-3 mr-1" />
              All systems running
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Automation</CardTitle>
            <Brain className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">Active</div>
            <div className="flex items-center text-xs text-purple-600">
              <Target className="h-3 w-3 mr-1" />
              95% confidence
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">5</div>
            <div className="flex items-center text-xs text-yellow-600">
              <Clock className="h-3 w-3 mr-1" />
              2 require attention
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">92%</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +7% this month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dashboard Navigation Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Dashboard Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dashboardCards.map((card) => (
            <Card key={card.href} className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className={`p-3 rounded-lg ${card.color} text-white`}>
                    <card.icon className="h-6 w-6" />
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {card.stats.trend}
                  </Badge>
                </div>
                <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">
                  {card.title}
                </CardTitle>
                <CardDescription className="text-sm">
                  {card.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-2xl font-bold">{card.stats.value}</div>
                    <div className="text-sm text-gray-600">{card.stats.label}</div>
                  </div>
                  <div className={`text-sm font-medium ${
                    card.stats.trend.startsWith('+') ? 'text-green-600' : 
                    card.stats.trend.startsWith('-') ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {card.stats.trend.startsWith('+') ? (
                      <TrendingUp className="h-4 w-4 inline mr-1" />
                    ) : card.stats.trend.startsWith('-') ? (
                      <TrendingDown className="h-4 w-4 inline mr-1" />
                    ) : null}
                    {card.stats.trend}
                  </div>
                </div>
                <Link href={card.href}>
                  <Button className="w-full group-hover:bg-blue-600 transition-colors">
                    Open Dashboard
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest system events and AI decisions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
              <div className="p-1 bg-blue-500 rounded-full">
                <Brain className="h-3 w-3 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">AI Agent triggered automatic reorder</p>
                <p className="text-xs text-gray-600">Ballpoint pens - Quantity: 50 units • 2 minutes ago</p>
              </div>
              <Badge variant="outline" className="text-blue-600">95% confidence</Badge>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
              <div className="p-1 bg-green-500 rounded-full">
                <CheckCircle className="h-3 w-3 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Vendor delivery completed</p>
                <p className="text-xs text-gray-600">Office Supplies Co. - Order #1234 • 1 hour ago</p>
              </div>
              <Badge variant="outline" className="text-green-600">On time</Badge>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
              <div className="p-1 bg-yellow-500 rounded-full">
                <AlertTriangle className="h-3 w-3 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Low stock alert</p>
                <p className="text-xs text-gray-600">A4 Paper - Only 5 units remaining • 3 hours ago</p>
              </div>
              <Badge variant="outline" className="text-yellow-600">Action needed</Badge>
            </div>
            
            <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
              <div className="p-1 bg-purple-500 rounded-full">
                <BarChart3 className="h-3 w-3 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Monthly report generated</p>
                <p className="text-xs text-gray-600">Supply chain performance summary • 6 hours ago</p>
              </div>
              <Badge variant="outline" className="text-purple-600">Available</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>Overall system performance metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Database Performance</span>
                <span className="font-medium">98%</span>
              </div>
              <Progress value={98} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>AI Model Accuracy</span>
                <span className="font-medium">95%</span>
              </div>
              <Progress value={95} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>API Response Time</span>
                <span className="font-medium">92%</span>
              </div>
              <Progress value={92} className="h-2" />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>System Uptime</span>
                <span className="font-medium">99.9%</span>
              </div>
              <Progress value={99.9} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Frequently used operations</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/dashboard/ai-agent">
              <Button variant="outline" className="w-full justify-start">
                <Brain className="h-4 w-4 mr-2" />
                Trigger AI Analysis
              </Button>
            </Link>
            <Link href="/dashboard/inventory">
              <Button variant="outline" className="w-full justify-start">
                <Package className="h-4 w-4 mr-2" />
                Add New Item
              </Button>
            </Link>
            <Link href="/dashboard/vendors">
              <Button variant="outline" className="w-full justify-start">
                <Users className="h-4 w-4 mr-2" />
                Manage Vendors
              </Button>
            </Link>
            <Link href="/dashboard/analytics">
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="h-4 w-4 mr-2" />
                View Reports
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}