"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CalendarIcon, TrendingUp, TrendingDown, BarChart3, PieChart, Activity, RefreshCw } from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

// Simple chart components without external dependencies
interface ChartDataPoint {
    name: string;
    value: number;
    color?: string;
}

interface LineChartProps {
    data: ChartDataPoint[];
    height?: number;
    color?: string;
}

function SimpleLineChart({ data, height = 200, color = "#3b82f6" }: LineChartProps) {
    if (!data || data.length === 0) return <div className="text-center text-gray-500 py-8">No data available</div>;

    const maxValue = Math.max(...data.map(d => d.value));
    const minValue = Math.min(...data.map(d => d.value));
    const range = maxValue - minValue || 1;

    const points = data.map((point, index) => {
        const x = (index / (data.length - 1)) * 100;
        const y = ((maxValue - point.value) / range) * 80 + 10;
        return `${x},${y}`;
    }).join(' ');

    return (
        <div className="w-full" style={{ height }}>
            <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
                <polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="0.5"
                    points={points}
                />
                {data.map((point, index) => {
                    const x = (index / (data.length - 1)) * 100;
                    const y = ((maxValue - point.value) / range) * 80 + 10;
                    return (
                        <circle
                            key={index}
                            cx={x}
                            cy={y}
                            r="0.8"
                            fill={color}
                        />
                    );
                })}
            </svg>
            <div className="flex justify-between text-xs text-gray-500 mt-2">
                {data.map((point, index) => (
                    <span key={index}>{point.name}</span>
                ))}
            </div>
        </div>
    );
}

interface BarChartProps {
    data: ChartDataPoint[];
    height?: number;
}

function SimpleBarChart({ data, height = 200 }: BarChartProps) {
    if (!data || data.length === 0) return <div className="text-center text-gray-500 py-8">No data available</div>;

    const maxValue = Math.max(...data.map(d => d.value));

    return (
        <div className="w-full" style={{ height }}>
            <div className="flex items-end justify-between h-full space-x-2">
                {data.map((item, index) => (
                    <div key={index} className="flex flex-col items-center flex-1">
                        <div
                            className="w-full bg-blue-500 rounded-t transition-all duration-300 hover:bg-blue-600"
                            style={{
                                height: `${(item.value / maxValue) * 80}%`,
                                backgroundColor: item.color || "#3b82f6"
                            }}
                            title={`${item.name}: ${item.value}`}
                        />
                        <span className="text-xs text-gray-500 mt-1 text-center">
                            {item.name}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}

interface PieChartProps {
    data: ChartDataPoint[];
    size?: number;
}

function SimplePieChart({ data, size = 150 }: PieChartProps) {
    if (!data || data.length === 0) return <div className="text-center text-gray-500 py-8">No data available</div>;

    const total = data.reduce((sum, item) => sum + item.value, 0);
    let currentAngle = 0;

    const colors = [
        "#3b82f6", "#ef4444", "#10b981", "#f59e0b",
        "#8b5cf6", "#06b6d4", "#84cc16", "#f97316"
    ];

    return (
        <div className="flex items-center space-x-4">
            <svg width={size} height={size} className="transform -rotate-90">
                {data.map((item, index) => {
                    const percentage = item.value / total;
                    const angle = percentage * 360;
                    const startAngle = currentAngle;
                    const endAngle = currentAngle + angle;

                    const x1 = Math.cos((startAngle * Math.PI) / 180) * (size / 2 - 10);
                    const y1 = Math.sin((startAngle * Math.PI) / 180) * (size / 2 - 10);
                    const x2 = Math.cos((endAngle * Math.PI) / 180) * (size / 2 - 10);
                    const y2 = Math.sin((endAngle * Math.PI) / 180) * (size / 2 - 10);

                    const largeArc = angle > 180 ? 1 : 0;
                    const pathData = [
                        `M ${size / 2} ${size / 2}`,
                        `L ${size / 2 + x1} ${size / 2 + y1}`,
                        `A ${size / 2 - 10} ${size / 2 - 10} 0 ${largeArc} 1 ${size / 2 + x2} ${size / 2 + y2}`,
                        'Z'
                    ].join(' ');

                    currentAngle += angle;

                    return (
                        <path
                            key={index}
                            d={pathData}
                            fill={item.color || colors[index % colors.length]}
                            stroke="white"
                            strokeWidth="2"
                        />
                    );
                })}
            </svg>
            <div className="space-y-2">
                {data.map((item, index) => (
                    <div key={index} className="flex items-center space-x-2">
                        <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: item.color || colors[index % colors.length] }}
                        />
                        <span className="text-sm text-gray-600">
                            {item.name}: {item.value}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function ChartsAndAnalytics() {
    const [selectedPeriod, setSelectedPeriod] = useState("30d");
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [analyticsData, setAnalyticsData] = useState<any>(null);
    const { toast } = useToast();

    const fetchAnalyticsData = async () => {
        try {
            setLoading(true);

            // Fetch real data from multiple endpoints
            const [
                inventoryItems,
                inventorySummary,
                scmDashboard,
                financeDashboard,
                salesAnalytics,
                agentDecisions,
                systemHealth
            ] = await Promise.all([
                VeriChainAPI.getInventoryItems(),
                VeriChainAPI.getInventorySummary(),
                VeriChainAPI.getSCMDashboard(),
                VeriChainAPI.getFinanceDashboard(),
                VeriChainAPI.getSalesAnalytics(30),
                VeriChainAPI.getRecentAgentDecisions(10),
                VeriChainAPI.getSystemHealth()
            ]);

            // Process data for charts
            const processedData = {
                inventory: {
                    summary: inventorySummary,
                    items: inventoryItems,
                    categoryData: processCategoryData(inventoryItems),
                    stockLevels: processStockLevels(inventoryItems)
                },
                financial: {
                    dashboard: financeDashboard,
                    salesTrends: processSalesTrends(salesAnalytics),
                    costAnalysis: processCostAnalysis(inventoryItems)
                },
                operational: {
                    scmDashboard: scmDashboard,
                    agentDecisions: agentDecisions,
                    systemHealth: systemHealth
                }
            };

            setAnalyticsData(processedData);

        } catch (error) {
            console.error('Failed to fetch analytics data:', error);

            // Set fallback data instead of leaving empty
            setAnalyticsData({
                inventory: {
                    summary: { total_items: 0, total_value: 0, low_stock_items: 0, out_of_stock_items: 0 },
                    items: [],
                    categoryData: [],
                    stockLevels: [
                        { name: "Out of Stock", value: 0, color: "#ef4444" },
                        { name: "Low Stock", value: 0, color: "#f59e0b" },
                        { name: "Normal", value: 0, color: "#3b82f6" },
                        { name: "High Stock", value: 0, color: "#10b981" }
                    ]
                },
                financial: {
                    dashboard: { total_revenue: 0, total_cost: 0, profit_margin: 0, monthly_growth: 0 },
                    salesTrends: [],
                    costAnalysis: []
                },
                operational: {
                    scmDashboard: { pending_orders: 0, overdue_orders: 0, supplier_performance: 0 },
                    agentDecisions: [],
                    systemHealth: { status: 'unknown', uptime: 0, performance: 0 }
                }
            });

            toast({
                title: "Error",
                description: "Failed to load analytics data. Using fallback data.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const refreshData = async () => {
        try {
            setRefreshing(true);
            await fetchAnalyticsData();
            toast({
                title: "Success",
                description: "Analytics data refreshed",
            });
        } catch (error) {
            console.error('Failed to refresh data:', error);
        } finally {
            setRefreshing(false);
        }
    };

    // Data processing functions with null safety
    const processCategoryData = (items: any[]) => {
        if (!items || !Array.isArray(items)) return [];

        const categoryCount = items.reduce((acc, item) => {
            const category = item?.category || 'Other';
            const stock = item?.current_stock || 0;
            acc[category] = (acc[category] || 0) + stock;
            return acc;
        }, {} as Record<string, number>);

        const colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#84cc16", "#f97316"];

        return Object.entries(categoryCount).map(([name, value], index) => ({
            name,
            value,
            color: colors[index % colors.length]
        }));
    };

    const processStockLevels = (items: any[]) => {
        if (!items || !Array.isArray(items)) return [];

        const levels = {
            'Out of Stock': items.filter(item => (item?.current_stock || 0) === 0).length,
            'Low Stock': items.filter(item => {
                const stock = item?.current_stock || 0;
                const reorder = item?.reorder_level || 0;
                return stock > 0 && stock <= reorder;
            }).length,
            'Normal': items.filter(item => {
                const stock = item?.current_stock || 0;
                const reorder = item?.reorder_level || 0;
                const max = item?.max_stock_level || 100;
                return stock > reorder && stock < max * 0.8;
            }).length,
            'High Stock': items.filter(item => {
                const stock = item?.current_stock || 0;
                const max = item?.max_stock_level || 100;
                return stock >= max * 0.8;
            }).length,
        };

        return [
            { name: "Out of Stock", value: levels['Out of Stock'], color: "#ef4444" },
            { name: "Low Stock", value: levels['Low Stock'], color: "#f59e0b" },
            { name: "Normal", value: levels['Normal'], color: "#3b82f6" },
            { name: "High Stock", value: levels['High Stock'], color: "#10b981" }
        ];
    };

    const processSalesTrends = (salesData: any) => {
        if (!salesData?.analytics?.daily_trends && !salesData?.daily_trends) return [];

        const trends = salesData?.analytics?.daily_trends || salesData?.daily_trends || [];
        return trends.slice(-7).map((day: any) => ({
            name: new Date(day?.date || Date.now()).toLocaleDateString('en', { weekday: 'short' }),
            value: day?.total_revenue || day?.revenue || 0
        }));
    };

    const processCostAnalysis = (items: any[]) => {
        if (!items || !Array.isArray(items)) return [];

        const categoryValue = items.reduce((acc, item) => {
            const category = item?.category || 'Other';
            const stock = item?.current_stock || 0;
            const cost = item?.unit_cost || 0;
            const value = stock * cost;
            acc[category] = (acc[category] || 0) + value;
            return acc;
        }, {} as Record<string, number>);

        return Object.entries(categoryValue).map(([name, value]) => ({
            name,
            value: Math.round(Number(value))
        }));
    };

    useEffect(() => {
        fetchAnalyticsData();
    }, [selectedPeriod]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!analyticsData) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <p className="text-gray-500">No analytics data available</p>
                    <Button onClick={fetchAnalyticsData} className="mt-4">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Retry
                    </Button>
                </div>
            </div>
        );
    }

    const { inventory, financial, operational } = analyticsData;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
                    <p className="text-gray-600">Real-time data insights and visualizations</p>
                </div>
                <div className="flex space-x-2">
                    <Button
                        onClick={refreshData}
                        variant="outline"
                        size="sm"
                        disabled={refreshing}
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                        <SelectTrigger className="w-32">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="7d">Last 7 days</SelectItem>
                            <SelectItem value="30d">Last 30 days</SelectItem>
                            <SelectItem value="90d">Last 90 days</SelectItem>
                            <SelectItem value="1y">Last year</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                        <BarChart3 className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">
                            {inventory.summary?.total_items || 0}
                        </div>
                        <div className="flex items-center text-xs text-gray-600">
                            Active inventory items
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                        <Activity className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">
                            ${inventory.summary?.total_value?.toLocaleString() || financial.dashboard?.total_revenue?.toLocaleString() || '0'}
                        </div>
                        <div className="flex items-center text-xs text-gray-600">
                            Current inventory value
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                        <PieChart className="h-4 w-4 text-orange-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-orange-600">
                            {operational.scmDashboard?.summary?.low_stock_items || 0}
                        </div>
                        <div className="flex items-center text-xs text-orange-600">
                            Require attention
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">AI Decisions</CardTitle>
                        <CalendarIcon className="h-4 w-4 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-purple-600">
                            {operational.agentDecisions?.length || 0}
                        </div>
                        <div className="flex items-center text-xs text-purple-600">
                            Recent automated decisions
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Charts Grid */}
            <Tabs defaultValue="trends" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="trends">Trends</TabsTrigger>
                    <TabsTrigger value="inventory">Inventory</TabsTrigger>
                    <TabsTrigger value="costs">Costs</TabsTrigger>
                </TabsList>

                <TabsContent value="trends" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Sales Trends</CardTitle>
                                <CardDescription>Daily sales revenue for the past week</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <SimpleLineChart data={financial.salesTrends || []} />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>AI Agent Activity</CardTitle>
                                <CardDescription>Recent automated decision trends</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-3">
                                    {operational.agentDecisions?.slice(0, 5).map((decision: any, index: number) => (
                                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                            <div>
                                                <p className="font-medium text-sm">{decision.decision_type}</p>
                                                <p className="text-xs text-gray-600">{decision.reasoning?.substring(0, 50)}...</p>
                                            </div>
                                            <Badge variant={decision.is_executed ? "default" : "secondary"}>
                                                {decision.is_executed ? "Executed" : "Pending"}
                                            </Badge>
                                        </div>
                                    )) || <p className="text-gray-500">No recent decisions</p>}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>System Health Overview</CardTitle>
                            <CardDescription>Current system performance metrics</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {operational.systemHealth?.status === 'healthy' ? '100%' : '85%'}
                                    </div>
                                    <div className="text-sm text-gray-600">System Health</div>
                                    <div className="mt-2 h-2 bg-gray-200 rounded">
                                        <div className="h-2 bg-blue-600 rounded" style={{
                                            width: operational.systemHealth?.status === 'healthy' ? '100%' : '85%'
                                        }}></div>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600">
                                        {Math.round(((inventory.summary?.healthy_stock_items || 0) / (inventory.summary?.total_items || 1)) * 100)}%
                                    </div>
                                    <div className="text-sm text-gray-600">Stock Health</div>
                                    <div className="mt-2 h-2 bg-gray-200 rounded">
                                        <div className="h-2 bg-green-600 rounded" style={{
                                            width: `${Math.round(((inventory.summary?.healthy_stock_items || 0) / (inventory.summary?.total_items || 1)) * 100)}%`
                                        }}></div>
                                    </div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-purple-600">
                                        {operational.agentDecisions?.filter((d: any) => d.is_executed).length || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Automated Actions</div>
                                    <div className="mt-2 h-2 bg-gray-200 rounded">
                                        <div className="h-2 bg-purple-600 rounded" style={{ width: '88%' }}></div>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="inventory" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Inventory by Category</CardTitle>
                                <CardDescription>Current stock distribution by category</CardDescription>
                            </CardHeader>
                            <CardContent className="flex justify-center">
                                <SimplePieChart data={inventory.categoryData || []} />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Stock Status</CardTitle>
                                <CardDescription>Current stock level overview</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <SimpleBarChart data={inventory.stockLevels || []} />
                            </CardContent>
                        </Card>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>Critical Inventory Items</CardTitle>
                            <CardDescription>Items requiring immediate attention</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {operational.scmDashboard?.priority_actions?.slice(0, 5).map((action: any, index: number) => (
                                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                                        <div>
                                            <p className="font-medium text-sm">{action.title}</p>
                                            <p className="text-xs text-gray-600">{action.description}</p>
                                        </div>
                                        <Badge variant={action.priority === 'urgent' ? "destructive" : "secondary"}>
                                            {action.priority}
                                        </Badge>
                                    </div>
                                )) || <p className="text-gray-500">No critical items</p>}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="costs" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cost Analysis by Category</CardTitle>
                                <CardDescription>Inventory value distribution</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <SimpleBarChart data={financial.costAnalysis || []} />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Financial Summary</CardTitle>
                                <CardDescription>Key financial metrics</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Total Inventory Value</span>
                                        <span className="font-bold">${financial.dashboard?.summary?.total_inventory_value?.toLocaleString() || '0'}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Monthly Revenue</span>
                                        <span className="font-bold">${financial.dashboard?.summary?.monthly_revenue?.toLocaleString() || '0'}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Pending Orders Value</span>
                                        <span className="font-bold">${financial.dashboard?.summary?.pending_orders_value?.toLocaleString() || '0'}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm text-gray-600">Low Stock Items</span>
                                        <span className="font-bold text-orange-600">{operational.scmDashboard?.summary?.low_stock_items || 0}</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}