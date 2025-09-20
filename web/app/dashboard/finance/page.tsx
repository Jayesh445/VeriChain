"use client"

import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DollarSign, TrendingUp, AlertCircle, Shield, Download, FileText, Calendar, ExternalLink } from "lucide-react"

export default function FinanceDashboard() {
  const financialSummary = {
    revenue: { value: "$2,847,392", change: "+12.5%", trend: "up" },
    expenses: { value: "$1,923,847", change: "-3.2%", trend: "down" },
    profit: { value: "$923,545", change: "+18.7%", trend: "up" },
    gstCompliance: { value: "98.5%", status: "excellent" },
  }

  const auditTrail = [
    {
      id: "0x1a2b3c4d",
      transaction: "Purchase Order #PO-2024-001",
      amount: "$45,230",
      timestamp: "2024-01-15 14:30:22",
      status: "verified",
      hash: "0x1a2b3c4d5e6f7890abcdef1234567890",
    },
    {
      id: "0x2b3c4d5e",
      transaction: "Vendor Payment - TechCorp",
      amount: "$12,500",
      timestamp: "2024-01-15 11:15:45",
      status: "verified",
      hash: "0x2b3c4d5e6f7890abcdef1234567890ab",
    },
    {
      id: "0x3c4d5e6f",
      transaction: "Inventory Adjustment",
      amount: "$8,750",
      timestamp: "2024-01-14 16:45:12",
      status: "pending",
      hash: "0x3c4d5e6f7890abcdef1234567890abcd",
    },
  ]

  const complianceAlerts = [
    {
      id: 1,
      type: "GST Filing",
      description: "Q4 GST return due in 5 days",
      priority: "high",
      dueDate: "2024-01-20",
      status: "pending",
    },
    {
      id: 2,
      type: "Audit Review",
      description: "Annual audit documentation required",
      priority: "medium",
      dueDate: "2024-02-15",
      status: "in-progress",
    },
    {
      id: 3,
      type: "Tax Compliance",
      description: "Corporate tax filing preparation",
      priority: "low",
      dueDate: "2024-03-31",
      status: "scheduled",
    },
  ]

  const reports = [
    {
      name: "Monthly P&L Statement",
      type: "Financial",
      date: "December 2024",
      status: "ready",
      size: "2.4 MB",
    },
    {
      name: "GST Compliance Report",
      type: "Tax",
      date: "Q4 2024",
      status: "ready",
      size: "1.8 MB",
    },
    {
      name: "Vendor Payment Summary",
      type: "Operational",
      date: "December 2024",
      status: "generating",
      size: "Processing...",
    },
    {
      name: "Blockchain Audit Trail",
      type: "Security",
      date: "December 2024",
      status: "ready",
      size: "5.2 MB",
    },
  ]

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "text-red-600 bg-red-100"
      case "medium":
        return "text-yellow-600 bg-yellow-100"
      case "low":
        return "text-green-600 bg-green-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "verified":
        return "text-green-600 bg-green-100"
      case "pending":
        return "text-yellow-600 bg-yellow-100"
      case "ready":
        return "text-green-600 bg-green-100"
      case "generating":
        return "text-blue-600 bg-blue-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  return (
    <DashboardLayout userRole="finance">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-3xl font-bold">Finance Dashboard</h1>
            <p className="text-muted-foreground">Monitor financial performance and ensure compliance</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button>
              <Download className="w-4 h-4 mr-2" />
              Export Reports
            </Button>
            <Button variant="outline">
              <FileText className="w-4 h-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>

        {/* Financial Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Revenue</p>
                  <p className="text-2xl font-bold">{financialSummary.revenue.value}</p>
                  <p className="text-xs text-green-600">{financialSummary.revenue.change} from last month</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Expenses</p>
                  <p className="text-2xl font-bold">{financialSummary.expenses.value}</p>
                  <p className="text-xs text-green-600">{financialSummary.expenses.change} from last month</p>
                </div>
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-red-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Net Profit</p>
                  <p className="text-2xl font-bold">{financialSummary.profit.value}</p>
                  <p className="text-xs text-green-600">{financialSummary.profit.change} from last month</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">GST Compliance</p>
                  <p className="text-2xl font-bold">{financialSummary.gstCompliance.value}</p>
                  <p className="text-xs text-green-600">Excellent rating</p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Blockchain Audit Trail */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5" />
                <span>Blockchain Audit Trail</span>
              </CardTitle>
              <CardDescription>Immutable transaction records and contract verification</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {auditTrail.map((record) => (
                  <div key={record.id} className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm">{record.transaction}</h4>
                      <Badge className={getStatusColor(record.status)}>{record.status}</Badge>
                    </div>
                    <div className="space-y-1 text-xs text-muted-foreground">
                      <p>
                        Amount: <span className="font-medium text-foreground">{record.amount}</span>
                      </p>
                      <p>Timestamp: {record.timestamp}</p>
                      <p className="flex items-center space-x-1">
                        <span>Hash:</span>
                        <code className="bg-muted px-1 rounded text-xs">{record.hash.substring(0, 20)}...</code>
                        <Button variant="ghost" size="sm" className="h-4 w-4 p-0">
                          <ExternalLink className="w-3 h-3" />
                        </Button>
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <Button variant="outline" className="w-full mt-4 bg-transparent">
                View Full Audit Trail
              </Button>
            </CardContent>
          </Card>

          {/* Compliance Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <AlertCircle className="w-5 h-5" />
                <span>Compliance Alerts</span>
              </CardTitle>
              <CardDescription>Pending submissions and compliance deadlines</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {complianceAlerts.map((alert) => (
                  <div key={alert.id} className="p-4 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{alert.type}</h4>
                      <Badge className={getPriorityColor(alert.priority)}>{alert.priority}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{alert.description}</p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>Due: {alert.dueDate}</span>
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {alert.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Reports and Analytics */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>Report Download Center</span>
            </CardTitle>
            <CardDescription>Export financial reports and compliance documents</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="financial" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="financial">Financial</TabsTrigger>
                <TabsTrigger value="tax">Tax & GST</TabsTrigger>
                <TabsTrigger value="operational">Operational</TabsTrigger>
                <TabsTrigger value="security">Security</TabsTrigger>
              </TabsList>
              <TabsContent value="financial" className="space-y-4">
                <div className="grid gap-4">
                  {reports
                    .filter((report) => report.type === "Financial")
                    .map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-8 h-8 text-muted-foreground" />
                          <div>
                            <h4 className="font-medium">{report.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {report.date} • {report.size}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(report.status)}>{report.status}</Badge>
                          {report.status === "ready" && (
                            <Button size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </TabsContent>
              <TabsContent value="tax" className="space-y-4">
                <div className="grid gap-4">
                  {reports
                    .filter((report) => report.type === "Tax")
                    .map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-8 h-8 text-muted-foreground" />
                          <div>
                            <h4 className="font-medium">{report.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {report.date} • {report.size}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(report.status)}>{report.status}</Badge>
                          {report.status === "ready" && (
                            <Button size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </TabsContent>
              <TabsContent value="operational" className="space-y-4">
                <div className="grid gap-4">
                  {reports
                    .filter((report) => report.type === "Operational")
                    .map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                        <div className="flex items-center space-x-3">
                          <FileText className="w-8 h-8 text-muted-foreground" />
                          <div>
                            <h4 className="font-medium">{report.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {report.date} • {report.size}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(report.status)}>{report.status}</Badge>
                          {report.status === "ready" && (
                            <Button size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </TabsContent>
              <TabsContent value="security" className="space-y-4">
                <div className="grid gap-4">
                  {reports
                    .filter((report) => report.type === "Security")
                    .map((report, index) => (
                      <div key={index} className="flex items-center justify-between p-4 rounded-lg border">
                        <div className="flex items-center space-x-3">
                          <Shield className="w-8 h-8 text-muted-foreground" />
                          <div>
                            <h4 className="font-medium">{report.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {report.date} • {report.size}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(report.status)}>{report.status}</Badge>
                          {report.status === "ready" && (
                            <Button size="sm">
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Financial Metrics Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>Financial Performance</span>
            </CardTitle>
            <CardDescription>Monthly revenue, expenses, and profit trends</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end space-x-2 p-4">
              {[
                { revenue: 85, expenses: 65, profit: 20 },
                { revenue: 92, expenses: 68, profit: 24 },
                { revenue: 78, expenses: 72, profit: 6 },
                { revenue: 95, expenses: 70, profit: 25 },
                { revenue: 88, expenses: 66, profit: 22 },
                { revenue: 96, expenses: 69, profit: 27 },
                { revenue: 89, expenses: 64, profit: 25 },
                { revenue: 94, expenses: 67, profit: 27 },
                { revenue: 91, expenses: 63, profit: 28 },
                { revenue: 98, expenses: 65, profit: 33 },
                { revenue: 87, expenses: 61, profit: 26 },
                { revenue: 93, expenses: 62, profit: 31 },
              ].map((data, i) => (
                <div key={i} className="flex flex-col items-center space-y-1 flex-1">
                  <div
                    className="bg-green-500 rounded-sm w-full"
                    style={{ height: `${data.revenue}%` }}
                    title={`Revenue: ${data.revenue}%`}
                  />
                  <div
                    className="bg-red-400 rounded-sm w-full"
                    style={{ height: `${data.expenses}%` }}
                    title={`Expenses: ${data.expenses}%`}
                  />
                  <div
                    className="bg-blue-500 rounded-sm w-full"
                    style={{ height: `${data.profit}%` }}
                    title={`Profit: ${data.profit}%`}
                  />
                </div>
              ))}
            </div>
            <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-sm" />
                <span>Revenue</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-red-400 rounded-sm" />
                <span>Expenses</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-sm" />
                <span>Profit</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
