"use client"

import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Package,
  TrendingUp,
  AlertTriangle,
  Users,
  BarChart3,
  Leaf,
  Plus,
  Eye,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react"

export default function SCMDashboard() {
  const inventoryData = [
    { name: "Electronics", stock: 1247, status: "normal", change: "+12%" },
    { name: "Clothing", stock: 89, status: "low", change: "-5%" },
    { name: "Home & Garden", stock: 456, status: "normal", change: "+8%" },
    { name: "Sports", stock: 23, status: "critical", change: "-15%" },
  ]

  const aiRecommendations = [
    {
      id: 1,
      type: "reorder",
      title: "Reorder Sports Equipment",
      description: "Stock levels are critically low. Recommend ordering 500 units.",
      priority: "high",
      savings: "$2,400",
    },
    {
      id: 2,
      type: "optimize",
      title: "Optimize Electronics Inventory",
      description: "Reduce overstock by 15% to free up warehouse space.",
      priority: "medium",
      savings: "$1,200",
    },
    {
      id: 3,
      type: "vendor",
      title: "Switch Clothing Supplier",
      description: "Alternative supplier offers 12% cost reduction.",
      priority: "low",
      savings: "$800",
    },
  ]

  const vendorNegotiations = [
    {
      id: 1,
      vendor: "TechCorp Solutions",
      product: "Electronics Components",
      status: "in-progress",
      savings: "8%",
      deadline: "2 days",
    },
    {
      id: 2,
      vendor: "Global Textiles",
      product: "Clothing Materials",
      status: "pending",
      savings: "12%",
      deadline: "5 days",
    },
    {
      id: 3,
      vendor: "SportGear Inc",
      product: "Sports Equipment",
      status: "completed",
      savings: "15%",
      deadline: "Completed",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "critical":
        return "text-red-600 bg-red-100"
      case "low":
        return "text-yellow-600 bg-yellow-100"
      case "normal":
        return "text-green-600 bg-green-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "border-red-500 bg-red-50"
      case "medium":
        return "border-yellow-500 bg-yellow-50"
      case "low":
        return "border-green-500 bg-green-50"
      default:
        return "border-gray-500 bg-gray-50"
    }
  }

  return (
    <DashboardLayout userRole="scm">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold">Supply Chain Dashboard</h1>
            <p className="text-muted-foreground">Monitor and manage your inventory with AI-powered insights</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Order
            </Button>
            <Button variant="outline">
              <Eye className="w-4 h-4 mr-2" />
              View Reports
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Inventory</p>
                  <p className="text-2xl font-bold">1,815</p>
                  <p className="text-xs text-green-600">+5.2% from last month</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Package className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Orders</p>
                  <p className="text-2xl font-bold">89</p>
                  <p className="text-xs text-green-600">+12% from last week</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Low Stock Alerts</p>
                  <p className="text-2xl font-bold">5</p>
                  <p className="text-xs text-red-600">Needs attention</p>
                </div>
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Sustainability Score</p>
                  <p className="text-2xl font-bold">87%</p>
                  <p className="text-xs text-green-600">Excellent rating</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Leaf className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Inventory Status Widget */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="w-5 h-5" />
                <span>Inventory Status</span>
              </CardTitle>
              <CardDescription>Real-time stock levels with color-coded alerts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {inventoryData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      <Badge className={getStatusColor(item.status)}>{item.status}</Badge>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-muted-foreground">{item.stock} units</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p
                        className={`text-sm font-medium ${item.change.startsWith("+") ? "text-green-600" : "text-red-600"}`}
                      >
                        {item.change}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* AI Recommendations Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5" />
                <span>AI Recommendations</span>
              </CardTitle>
              <CardDescription>Actionable insights from your AI agent</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {aiRecommendations.map((rec) => (
                  <div key={rec.id} className={`p-4 rounded-lg border-l-4 ${getPriorityColor(rec.priority)}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{rec.title}</h4>
                        <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
                        <p className="text-sm font-medium text-green-600 mt-2">Potential savings: {rec.savings}</p>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        <Button size="sm" variant="outline">
                          <ThumbsUp className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <ThumbsDown className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Vendor Negotiations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="w-5 h-5" />
                <span>Vendor Negotiations</span>
              </CardTitle>
              <CardDescription>Current and upcoming contract negotiations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {vendorNegotiations.map((negotiation) => (
                  <div key={negotiation.id} className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{negotiation.vendor}</h4>
                      <Badge variant={negotiation.status === "completed" ? "default" : "secondary"}>
                        {negotiation.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{negotiation.product}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-green-600 font-medium">Savings: {negotiation.savings}</span>
                      <span className="text-muted-foreground">{negotiation.deadline}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Sales Forecast Graph */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5" />
                <span>Sales Forecast</span>
              </CardTitle>
              <CardDescription>AI-powered demand prediction for next 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-end space-x-2 p-4">
                {[65, 78, 82, 88, 92, 85, 90, 95, 88, 92, 96, 89, 94, 98].map((height, i) => (
                  <div
                    key={i}
                    className="bg-primary/60 rounded-sm flex-1 transition-all hover:bg-primary/80"
                    style={{ height: `${height}%` }}
                    title={`Day ${i + 1}: ${height}% of target`}
                  />
                ))}
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground mt-4">
                <span>Today</span>
                <span>+30 days</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sustainability Score */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Leaf className="w-5 h-5" />
              <span>Sustainability Dashboard</span>
            </CardTitle>
            <CardDescription>Environmental compliance and eco-friendly vendor metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Carbon Footprint</span>
                  <span className="text-sm text-green-600">-12%</span>
                </div>
                <Progress value={75} className="h-2" />
                <p className="text-xs text-muted-foreground">Reduced by 12% this quarter</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Eco-Certified Vendors</span>
                  <span className="text-sm text-green-600">87%</span>
                </div>
                <Progress value={87} className="h-2" />
                <p className="text-xs text-muted-foreground">23 out of 26 vendors certified</p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Waste Reduction</span>
                  <span className="text-sm text-green-600">+18%</span>
                </div>
                <Progress value={82} className="h-2" />
                <p className="text-xs text-muted-foreground">18% improvement in waste management</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
