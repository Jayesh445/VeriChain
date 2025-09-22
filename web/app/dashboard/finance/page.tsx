"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  RefreshCw,
  Calculator,
  PieChart,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Clock,
  ShoppingCart
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface FinanceDashboardData {
  summary: {
    inventory_value: number;
    monthly_revenue: number;
    pending_commitments: number;
    budget_alerts_count: number;
  };
  financial_metrics: any;
  budget_alerts: any[];
  cost_breakdown: any;
  cash_flow_projection: any;
  order_costs?: any[];
  vendor_spending?: any[];
  savings_opportunities?: any[];
  priority_actions?: any[];
}

export default function FinanceDashboard() {
  const [dashboardData, setDashboardData] = useState<FinanceDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { toast } = useToast();

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await VeriChainAPI.getFinanceDashboard();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to fetch finance dashboard data:', error);
      toast({
        title: "Error",
        description: "Failed to load finance dashboard data",
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
        description: "Finance dashboard refreshed",
      });
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <Alert>
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Failed to load finance dashboard data. Please try refreshing the page.
        </AlertDescription>
      </Alert>
    );
  }

  const costAnalysis = dashboardData.cost_breakdown;
  const budgetOverview = dashboardData.cash_flow_projection;
  const financialMetrics = dashboardData.financial_metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Finance Officer Dashboard</h1>
          <p className="text-gray-600">Cost analysis, budgets, and financial insights</p>
        </div>
        <div className="flex space-x-2">
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

      {/* Financial Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Inventory Value</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${dashboardData.summary?.inventory_value?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Current inventory value
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Spend</CardTitle>
            <CreditCard className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              ${dashboardData.summary?.monthly_revenue?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Monthly revenue
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Commitments</CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              ${dashboardData.summary?.pending_commitments?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Committed spending
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Budget Alerts</CardTitle>
            <TrendingDown className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {dashboardData.summary?.budget_alerts_count || '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Active alerts
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Budget and Cost Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Budget Overview</CardTitle>
            <CardDescription>Monthly budget vs actual spending</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm">Budget Progress</span>
                <span className="text-sm font-medium">
                  ${budgetOverview?.spent?.toLocaleString() || '0'} / ${budgetOverview?.total_budget?.toLocaleString() || '0'}
                </span>
              </div>
              <Progress value={budgetOverview?.utilization_percentage || 0} />
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="space-y-1">
                <p className="text-gray-600">Remaining Budget</p>
                <p className="text-lg font-semibold text-green-600">
                  ${(budgetOverview?.total_budget - budgetOverview?.spent)?.toLocaleString() || '0'}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-gray-600">Avg Daily Spend</p>
                <p className="text-lg font-semibold text-blue-600">
                  ${budgetOverview?.avg_daily_spend?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Cost Breakdown</CardTitle>
            <CardDescription>Spending by category</CardDescription>
          </CardHeader>
          <CardContent>
            {costAnalysis?.category_costs ? (
              <div className="space-y-3">
                {Object.entries(costAnalysis.category_costs).map(([category, cost]: [string, any]) => (
                  <div key={category} className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                      <span className="text-sm capitalize">{category.replace('_', ' ')}</span>
                    </div>
                    <span className="font-medium">${cost?.toLocaleString() || '0'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500">No cost breakdown available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis Tabs */}
      <Tabs defaultValue="actions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="actions">Priority Actions</TabsTrigger>
          <TabsTrigger value="orders">Order Costs</TabsTrigger>
          <TabsTrigger value="vendors">Vendor Spending</TabsTrigger>
          <TabsTrigger value="savings">Savings Opportunities</TabsTrigger>
        </TabsList>

        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Budget Alerts</CardTitle>
              <CardDescription>Financial attention needed</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.budget_alerts?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.budget_alerts.slice(0, 10).map((alert: any, index: number) => (
                    <Alert key={index} className={alert.severity === 'high' ? 'border-red-500' : 'border-orange-500'}>
                      <AlertTriangle className={`h-4 w-4 ${alert.severity === 'high' ? 'text-red-500' : 'text-orange-500'}`} />
                      <div className="flex justify-between items-start">
                        <div>
                          <AlertDescription className="font-medium">
                            {alert.message}
                          </AlertDescription>
                          <AlertDescription className="text-sm text-gray-600 mt-1">
                            {alert.impact}
                          </AlertDescription>
                        </div>
                        <Badge variant={alert.severity === 'high' ? 'destructive' : 'secondary'}>
                          {alert.severity}
                        </Badge>
                      </div>
                    </Alert>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500">No budget alerts at this time</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="orders" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown by Category</CardTitle>
              <CardDescription>Inventory value breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.cost_breakdown?.by_category ? (
                <div className="space-y-4">
                  {Object.entries(dashboardData.cost_breakdown.by_category).map(([category, data]: [string, any], index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-100 rounded-full">
                          <ShoppingCart className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{category.replace('_', ' ')}</p>
                          <p className="text-sm text-gray-600">
                            {data.items} items
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">${data.value?.toLocaleString() || '0'}</p>
                        <Badge variant="default">
                          {((data.value / dashboardData.summary.inventory_value) * 100).toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500">No cost breakdown available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vendors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reorder Estimates</CardTitle>
              <CardDescription>AI-recommended reorder cost estimates</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.cost_breakdown?.reorder_estimates?.length > 0 ? (
                <div className="space-y-4">
                  {dashboardData.cost_breakdown.reorder_estimates.slice(0, 8).map((estimate: any, index: number) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-green-100 rounded-full">
                          <Calculator className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <p className="font-medium">Item #{estimate.item_id}</p>
                          <p className="text-sm text-gray-600">
                            Confidence: {(estimate.confidence * 100).toFixed(0)}% • {new Date(estimate.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-green-600">
                          ${estimate.estimated_cost?.toLocaleString() || '0'}
                        </p>
                        <Badge variant={estimate.confidence > 0.8 ? 'default' : 'secondary'}>
                          {estimate.confidence > 0.8 ? 'High confidence' : 'Medium confidence'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500">No reorder estimates available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="savings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Financial Metrics</CardTitle>
              <CardDescription>Revenue and cost efficiency metrics</CardDescription>
            </CardHeader>
            <CardContent>
              {dashboardData.financial_metrics ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium text-green-600 mb-2">Revenue Metrics</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>30-Day Revenue:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.revenue_metrics?.revenue_30days?.toLocaleString() || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Daily Revenue:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.revenue_metrics?.avg_daily_revenue?.toFixed(2) || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Trend:</span>
                          <Badge variant="outline">{dashboardData.financial_metrics.revenue_metrics?.revenue_trend || 'stable'}</Badge>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium text-blue-600 mb-2">Cost Metrics</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Inventory Value:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.cost_metrics?.inventory_value?.toLocaleString() || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Reorder Cost:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.cost_metrics?.estimated_reorder_cost?.toLocaleString() || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Total Committed:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.cost_metrics?.total_committed_cost?.toLocaleString() || '0'}</span>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium text-purple-600 mb-2">Efficiency Metrics</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Inventory Turnover:</span>
                          <span className="font-medium">{dashboardData.financial_metrics.efficiency_metrics?.inventory_turnover?.toFixed(2) || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Cost per Transaction:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.efficiency_metrics?.cost_per_transaction?.toFixed(2) || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Order Value:</span>
                          <span className="font-medium">${dashboardData.financial_metrics.efficiency_metrics?.avg_order_value?.toFixed(2) || '0'}</span>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium text-orange-600 mb-2">Cash Flow Projection</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Expected Revenue (30d):</span>
                          <span className="font-medium text-green-600">${dashboardData.cash_flow_projection?.next_30_days?.expected_revenue?.toLocaleString() || '0'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Committed Costs:</span>
                          <span className="font-medium text-red-600">${dashboardData.cash_flow_projection?.next_30_days?.committed_costs?.toLocaleString() || '0'}</span>
                        </div>
                        <div className="flex justify-between border-t pt-2">
                          <span className="font-medium">Net Projection:</span>
                          <span className={`font-medium ${(dashboardData.cash_flow_projection?.next_30_days?.net_projection || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            ${dashboardData.cash_flow_projection?.next_30_days?.net_projection?.toLocaleString() || '0'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-gray-500">No financial metrics available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Financial Health Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Financial Health Summary</CardTitle>
          <CardDescription>Overall financial performance indicators</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 border rounded-lg">
              <CheckCircle className="h-8 w-8 mx-auto text-green-500 mb-2" />
              <p className="text-lg font-semibold text-green-600">
                {financialMetrics?.cost_efficiency_score?.toFixed(1) || '0'}%
              </p>
              <p className="text-sm text-gray-600">Cost Efficiency</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <TrendingUp className="h-8 w-8 mx-auto text-blue-500 mb-2" />
              <p className="text-lg font-semibold text-blue-600">
                {financialMetrics?.roi_percentage?.toFixed(1) || '0'}%
              </p>
              <p className="text-sm text-gray-600">ROI on Inventory</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <Clock className="h-8 w-8 mx-auto text-purple-500 mb-2" />
              <p className="text-lg font-semibold text-purple-600">
                {financialMetrics?.payment_terms_avg || '0'} days
              </p>
              <p className="text-sm text-gray-600">Avg Payment Terms</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}