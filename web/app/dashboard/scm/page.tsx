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
  success: boolean;
  dashboard_type: string;
  summary: {
    total_items: number;
    critical_items: number;
    low_stock_items: number;
    pending_orders: number;
    priority_actions_count: number;
  };
  priority_actions: any[];
  performance_metrics: {
    stock_health: any;
    order_fulfillment: any;
    ai_recommendations: any;
  };
  recent_trends: {
    sales_trend_7days: any[];
    avg_daily_sales: number;
  };
  operational_alerts: any[];
  generated_at: string;
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
            <div className="text-2xl font-bold">{dashboardData.summary?.total_items || 0}</div>
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
              {dashboardData.summary?.low_stock_items || 0}
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
            <div className="text-2xl font-bold">{dashboardData.summary?.pending_orders || 0}</div>
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
              {dashboardData.operational_alerts?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.operational_alerts.slice(0, 8).map((decision: any, index: number) => (
                    <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <div className={`p-2 rounded-full ${decision.type === 'REORDER' ? 'bg-blue-100 text-blue-600' :
                        decision.type === 'ALERT' ? 'bg-orange-100 text-orange-600' :
                          'bg-gray-100 text-gray-600'
                        }`}>
                        {decision.type === 'REORDER' ? <Package2 className="h-4 w-4" /> :
                          decision.type === 'ALERT' ? <AlertTriangle className="h-4 w-4" /> :
                            <Brain className="h-4 w-4" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium capitalize">{decision.type} Decision</p>
                            <p className="text-sm text-gray-600 mt-1">{decision.message}</p>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline">
                              {(decision.confidence * 100).toFixed(0)}% confidence
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
              {dashboardData.recent_trends ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <TrendingUp className="h-8 w-8 mx-auto text-green-500 mb-2" />
                      <p className="text-2xl font-bold">{dashboardData.recent_trends.avg_daily_sales?.toFixed(0) || 0}</p>
                      <p className="text-sm text-gray-600">Avg Daily Sales</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <ArrowUp className="h-8 w-8 mx-auto text-blue-500 mb-2" />
                      <p className="text-2xl font-bold">{dashboardData.recent_trends.sales_trend_7days?.length || 0}</p>
                      <p className="text-sm text-gray-600">Active Days (7 days)</p>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <Package className="h-8 w-8 mx-auto text-purple-500 mb-2" />
                      <p className="text-2xl font-bold">
                        {dashboardData.recent_trends.sales_trend_7days?.reduce((sum: number, day: any) => sum + (day.total_quantity || 0), 0) || 0}
                      </p>
                      <p className="text-sm text-gray-600">Units Sold (7 days)</p>
                    </div>
                  </div>
                  {dashboardData.recent_trends.sales_trend_7days?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-medium">Daily Sales Breakdown</h4>
                      <div className="space-y-2">
                        {dashboardData.recent_trends.sales_trend_7days.map((day: any, index: number) => (
                          <div key={index} className="flex justify-between items-center p-2 border rounded">
                            <span className="text-sm">{new Date(day.date).toLocaleDateString()}</span>
                            <div className="flex space-x-4 text-sm">
                              <span>{day.total_quantity} units</span>
                              <span className="font-medium">${day.total_amount?.toFixed(2) || '0.00'}</span>
                              <span className="text-gray-500">{day.transaction_count} orders</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
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