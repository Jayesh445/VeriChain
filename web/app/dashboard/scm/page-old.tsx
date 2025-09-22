"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  AlertTriangle, 
  Package, 
  TrendingUp, 
  Users, 
  RefreshCw,
  Brain,
  Clock,
  CheckCircle,
  XCircle,
  ArrowUp,
  ArrowDown,
  Package2,
  ShoppingCart
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface DashboardData {
  inventory_summary: any;
  priority_actions: any[];
  performance_metrics: any;
  recent_decisions: any[];
  sales_trends: any;
  pending_orders: any[];
}

export default function SCMDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [agentAnalyzing, setAgentAnalyzing] = useState(false);
  const { toast } = useToast();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await VeriChainAPI.getSCMDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast({
        title: "Error",
        description: "Failed to load dashboard data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshDashboard = async () => {
    try {
      setRefreshing(true);
      await fetchDashboardData();
      toast({
        title: "Success",
        description: "Dashboard data refreshed",
      });
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const triggerAIAnalysis = async () => {
    try {
      setAgentAnalyzing(true);
      const result = await VeriChainAPI.triggerAgentAnalysis('manual');
      toast({
        title: "AI Analysis Started",
        description: `Workflow ${result.workflow_id} initiated successfully`,
      });
      // Refresh dashboard after a delay to show updated insights
      setTimeout(() => {
        fetchDashboardData();
      }, 3000);
    } catch (error) {
      console.error('Failed to trigger AI analysis:', error);
      toast({
        title: "Error",
        description: "Failed to start AI analysis",
        variant: "destructive"
      });
    } finally {
      setAgentAnalyzing(false);
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

  if (!dashboardData) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load dashboard data. Please try refreshing the page.
        </AlertDescription>
      </Alert>
    );
  }

  const stockHealth = dashboardData.performance_metrics?.stock_health;
  const orderFulfillment = dashboardData.performance_metrics?.order_fulfillment;
  const aiRecommendations = dashboardData.performance_metrics?.ai_recommendations;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Supply Chain Manager Dashboard</h1>
          <p className="text-gray-600">Real-time insights and operational control</p>
        </div>
        <div className="flex space-x-2">
          <Button 
            onClick={triggerAIAnalysis} 
            disabled={agentAnalyzing}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {agentAnalyzing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Brain className="h-4 w-4 mr-2" />
            )}
            Run AI Analysis
          </Button>
          <Button 
            onClick={refreshDashboard} 
            disabled={refreshing}
            variant="outline"
          >
            {refreshing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.inventory_summary?.total_items || 0}</div>
            <p className="text-xs text-muted-foreground">
              Active inventory items
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {dashboardData.inventory_summary?.low_stock_items || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Items needing attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Orders</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.pending_orders?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              Orders in progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Recommendations</CardTitle>
            <Brain className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {aiRecommendations?.reorder_recommendations || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Active suggestions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Stock Health</CardTitle>
            <CardDescription>Overall inventory status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Health Score</span>
                <span className="text-sm font-medium">
                  {stockHealth?.health_percentage?.toFixed(1) || 0}%
                </span>
              </div>
              <Progress value={stockHealth?.health_percentage || 0} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>Healthy: {stockHealth?.healthy_items || 0}</span>
              </div>
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                <span>Attention: {stockHealth?.attention_needed || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Order Fulfillment</CardTitle>
            <CardDescription>Delivery performance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">On-Time Rate</span>
                <span className="text-sm font-medium">
                  {orderFulfillment?.on_time_rate?.toFixed(1) || 0}%
                </span>
              </div>
              <Progress value={orderFulfillment?.on_time_rate || 0} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-blue-500" />
                <span>Pending: {orderFulfillment?.pending_orders || 0}</span>
              </div>
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-red-500" />
                <span>Overdue: {orderFulfillment?.overdue_orders || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">AI Activity</CardTitle>
            <CardDescription>Autonomous decision making</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-3 text-sm">
              <div className="flex justify-between items-center">
                <span>Total Decisions</span>
                <Badge variant="secondary">{aiRecommendations?.total_decisions || 0}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>Reorder Recommendations</span>
                <Badge variant="outline">{aiRecommendations?.reorder_recommendations || 0}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span>Active Alerts</span>
                <Badge variant="destructive">{aiRecommendations?.active_alerts || 0}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Priority Actions and Recent Activity */}
      <Tabs defaultValue="actions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="actions">Priority Actions</TabsTrigger>
          <TabsTrigger value="decisions">AI Decisions</TabsTrigger>
          <TabsTrigger value="trends">Sales Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Priority Actions Required</CardTitle>
              <CardDescription>Immediate attention needed</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.priority_actions?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.priority_actions.slice(0, 10).map((action: any, index: number) => (
                    <Alert key={index} className={action.priority === 'urgent' ? 'border-red-500' : 'border-orange-500'}>
                      <AlertTriangle className={`h-4 w-4 ${action.priority === 'urgent' ? 'text-red-500' : 'text-orange-500'}`} />
                      <div className="flex justify-between items-start">
                        <div>
                          <AlertDescription className="font-medium">
                            {action.title}
                          </AlertDescription>
                          <AlertDescription className="text-sm text-gray-600 mt-1">
                            {action.description}
                          </AlertDescription>
                        </div>
                        <Badge variant={action.priority === 'urgent' ? 'destructive' : 'secondary'}>
                          {action.priority}
                        </Badge>
                      </div>
                    </Alert>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500">No priority actions at this time</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="decisions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent AI Decisions</CardTitle>
              <CardDescription>Latest autonomous recommendations</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.recent_decisions?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.recent_decisions.slice(0, 8).map((decision: any, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <div className={`p-2 rounded-full ${
                        decision.decision_type === 'reorder' ? 'bg-blue-100 text-blue-600' :
                        decision.decision_type === 'alert' ? 'bg-orange-100 text-orange-600' :
                        'bg-gray-100 text-gray-600'
                      }`}>
                        {decision.decision_type === 'reorder' ? <Package2 className="h-4 w-4" /> :
                         decision.decision_type === 'alert' ? <AlertTriangle className="h-4 w-4" /> :
                         <Brain className="h-4 w-4" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium capitalize">{decision.decision_type} Decision</p>
                            <p className="text-sm text-gray-600 mt-1">{decision.reasoning}</p>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline">
                              {(decision.confidence_score * 100).toFixed(0)}% confidence
                            </Badge>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(decision.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500">No recent AI decisions</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sales Trends</CardTitle>
              <CardDescription>Recent sales performance</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.sales_trends ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <TrendingUp className="h-8 w-8 mx-auto text-green-500 mb-2" />
                      <p className="text-2xl font-bold">{dashboardData.sales_trends.total_sales || 0}</p>
                      <p className="text-sm text-gray-600">Total Sales (7 days)</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <ArrowUp className="h-8 w-8 mx-auto text-blue-500 mb-2" />
                      <p className="text-2xl font-bold">{dashboardData.sales_trends.avg_daily_sales || 0}</p>
                      <p className="text-sm text-gray-600">Avg Daily Sales</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <Package className="h-8 w-8 mx-auto text-purple-500 mb-2" />
                      <p className="text-2xl font-bold">{dashboardData.sales_trends.top_selling_items || 0}</p>
                      <p className="text-sm text-gray-600">Top Selling Items</p>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-gray-500">No sales trend data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
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
