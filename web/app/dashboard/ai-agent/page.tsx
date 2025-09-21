"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Brain,
    Search,
    MessageSquare,
    BarChart3,
    CheckCircle,
    XCircle,
    Clock,
    AlertTriangle,
    Package,
    DollarSign,
    Truck,
    RefreshCw,
    Play,
    Users
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface VendorProposal {
    vendor_id: number;
    vendor_name: string;
    unit_price: number;
    total_price: number;
    delivery_time: number;
    terms: string;
    confidence_score: number;
    profit_margin?: number;
    special_offers?: string;
}

interface ConversationMessage {
    timestamp: string;
    speaker: string;
    message: string;
    message_type: string;
}

interface NegotiationSession {
    session_id: string;
    item_id: number;
    item_name: string;
    quantity_needed: number;
    status: string;
    vendor_proposals: VendorProposal[];
    conversation: ConversationMessage[];
    best_proposal?: VendorProposal;
    ai_reasoning: string;
    created_at: string;
    updated_at: string;
    trigger_source?: string;
}

export default function AIAgentDashboard() {
    const [activeNegotiations, setActiveNegotiations] = useState<NegotiationSession[]>([]);
    const [pendingApprovals, setPendingApprovals] = useState<NegotiationSession[]>([]);
    const [selectedSession, setSelectedSession] = useState<NegotiationSession | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [startingNegotiation, setStartingNegotiation] = useState(false);
    const [inventoryItems, setInventoryItems] = useState<any[]>([]);
    const [newNegotiation, setNewNegotiation] = useState({
        item_id: '',
        quantity_needed: '',
        urgency: 'medium'
    });
    const { toast } = useToast();

    useEffect(() => {
        fetchData();
        fetchInventoryItems();
        // No automatic polling - only refresh on manual action
    }, []);

    const fetchInventoryItems = async () => {
        try {
            const items = await VeriChainAPI.getInventoryItems();
            setInventoryItems(items.filter((item: any) => item.current_stock <= item.reorder_level));
        } catch (error) {
            console.error('Failed to fetch inventory items:', error);
        }
    };

    const fetchData = async (isManualRefresh = false) => {
        try {
            if (isManualRefresh) {
                setRefreshing(true);
            }
            const [activeData, pendingData] = await Promise.all([
                VeriChainAPI.getActiveNegotiations(),
                VeriChainAPI.getPendingApprovals()
            ]);

            setActiveNegotiations(activeData.active_sessions || []);
            setPendingApprovals(pendingData.pending_approvals || []);
        } catch (error) {
            console.error('Failed to fetch AI agent data:', error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    const startNegotiation = async () => {
        try {
            setStartingNegotiation(true);
            const result = await VeriChainAPI.startNegotiation({
                item_id: parseInt(newNegotiation.item_id),
                quantity_needed: parseInt(newNegotiation.quantity_needed),
                urgency: newNegotiation.urgency
            });

            toast({
                title: "Negotiation Started",
                description: `AI agent began negotiating for item ${newNegotiation.item_id}`,
            });

            setNewNegotiation({ item_id: '', quantity_needed: '', urgency: 'medium' });
            fetchData();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to start negotiation",
                variant: "destructive"
            });
        } finally {
            setStartingNegotiation(false);
        }
    };

    const approveOrder = async (sessionId: string, approved: boolean, notes?: string) => {
        try {
            await VeriChainAPI.approveOrder({
                session_id: sessionId,
                approved,
                user_notes: notes
            });

            toast({
                title: approved ? "Order Approved" : "Order Rejected",
                description: approved ? "Stock will be updated shortly" : "Negotiation cancelled",
                variant: approved ? "default" : "destructive"
            });

            fetchData();
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to process approval",
                variant: "destructive"
            });
        }
    };

    const handleQuickAction = async (sessionId: string, action: string) => {
        try {
            // Call backend API to handle quick actions
            const response = await VeriChainAPI.sendQuickAction({
                session_id: sessionId,
                action,
                message: getQuickActionMessage(action)
            });

            toast({
                title: "Quick Action Sent",
                description: `${getQuickActionTitle(action)} request sent to AI agent`,
            });

            fetchData(); // Refresh to see updates
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to send quick action",
                variant: "destructive"
            });
        }
    };

    const getQuickActionMessage = (action: string): string => {
        switch (action) {
            case 'price_match':
                return "Please request a price match with competitors in the market.";
            case 'expedite':
                return "Request expedited delivery for this order with additional urgency.";
            case 'bulk_discount':
                return "Negotiate for bulk discount pricing on this quantity.";
            case 'accept_terms':
                return "Accept the current terms and proceed with the best available offer.";
            default:
                return "Process the request as specified.";
        }
    };

    const getQuickActionTitle = (action: string): string => {
        switch (action) {
            case 'price_match':
                return "Price Match";
            case 'expedite':
                return "Expedite Delivery";
            case 'bulk_discount':
                return "Bulk Discount";
            case 'accept_terms':
                return "Accept Terms";
            default:
                return "Quick Action";
        }
    };

    const triggerLowStockNegotiations = async () => {
        try {
            const result = await VeriChainAPI.triggerLowStockNegotiations();

            toast({
                title: "Auto-Negotiations Triggered",
                description: `Started ${result.triggered_sessions?.length || 0} AI negotiations for low stock items`,
            });

            fetchData(); // Refresh to see new negotiations
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to trigger auto-negotiations",
                variant: "destructive"
            });
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'discovering':
                return <Search className="h-4 w-4 text-blue-500" />;
            case 'negotiating':
                return <MessageSquare className="h-4 w-4 text-orange-500" />;
            case 'comparing':
                return <BarChart3 className="h-4 w-4 text-purple-500" />;
            case 'pending_approval':
                return <Clock className="h-4 w-4 text-yellow-500" />;
            case 'approved':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'rejected':
                return <XCircle className="h-4 w-4 text-red-500" />;
            default:
                return <Brain className="h-4 w-4 text-gray-500" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'discovering':
                return 'bg-blue-100 text-blue-800';
            case 'negotiating':
                return 'bg-orange-100 text-orange-800';
            case 'comparing':
                return 'bg-purple-100 text-purple-800';
            case 'pending_approval':
                return 'bg-yellow-100 text-yellow-800';
            case 'approved':
                return 'bg-green-100 text-green-800';
            case 'rejected':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">AI Agent Dashboard</h1>
                    <p className="text-gray-600">Monitor autonomous vendor negotiations and approve orders</p>
                </div>
                <div className="flex space-x-2">
                    {inventoryItems.length > 0 && (
                        <Button
                            onClick={triggerLowStockNegotiations}
                            variant="outline"
                            className="border-orange-300 text-orange-600 hover:bg-orange-50"
                        >
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            Trigger Auto-Negotiations
                        </Button>
                    )}

                    <Button
                        onClick={() => fetchData(true)}
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

                    <Dialog>
                        <DialogTrigger asChild>
                            <Button>
                                <Play className="h-4 w-4 mr-2" />
                                Start Negotiation
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-md">
                            <DialogHeader>
                                <DialogTitle>Start AI Negotiation</DialogTitle>
                                <DialogDescription>
                                    Begin AI agent negotiation for inventory replenishment
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="item_select">Select Item</Label>
                                    <select
                                        id="item_select"
                                        value={newNegotiation.item_id}
                                        onChange={(e) => {
                                            const selectedItem = inventoryItems.find(item => item.id.toString() === e.target.value);
                                            setNewNegotiation({
                                                ...newNegotiation,
                                                item_id: e.target.value,
                                                quantity_needed: selectedItem ? (selectedItem.max_stock_level - selectedItem.current_stock).toString() : ''
                                            });
                                        }}
                                        className="w-full p-2 border rounded"
                                    >
                                        <option value="">Select an item to reorder...</option>
                                        {inventoryItems.map((item) => (
                                            <option key={item.id} value={item.id}>
                                                {item.name} - Current: {item.current_stock}, Reorder: {item.reorder_level}
                                            </option>
                                        ))}
                                    </select>
                                    <p className="text-xs text-gray-500 mt-1">
                                        Showing items below reorder level
                                    </p>
                                </div>
                                <div>
                                    <Label htmlFor="quantity">Quantity Needed</Label>
                                    <Input
                                        id="quantity"
                                        type="number"
                                        value={newNegotiation.quantity_needed}
                                        onChange={(e) => setNewNegotiation({ ...newNegotiation, quantity_needed: e.target.value })}
                                        placeholder="Enter quantity"
                                    />
                                    {newNegotiation.item_id && (
                                        <p className="text-xs text-gray-500 mt-1">
                                            Recommended: {
                                                inventoryItems.find(item => item.id.toString() === newNegotiation.item_id)?.max_stock_level -
                                                inventoryItems.find(item => item.id.toString() === newNegotiation.item_id)?.current_stock || 0
                                            } units to reach max stock
                                        </p>
                                    )}
                                </div>
                                <div>
                                    <Label htmlFor="urgency">Urgency Level</Label>
                                    <select
                                        id="urgency"
                                        value={newNegotiation.urgency}
                                        onChange={(e) => setNewNegotiation({ ...newNegotiation, urgency: e.target.value })}
                                        className="w-full p-2 border rounded"
                                    >
                                        <option value="low">🟢 Low - Normal delivery</option>
                                        <option value="medium">🟡 Medium - Preferred delivery</option>
                                        <option value="high">🔴 High - Urgent delivery</option>
                                    </select>
                                </div>
                                <Button
                                    onClick={startNegotiation}
                                    disabled={startingNegotiation || !newNegotiation.item_id || !newNegotiation.quantity_needed}
                                    className="w-full"
                                >
                                    {startingNegotiation ? (
                                        <>
                                            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                            Starting AI Negotiation...
                                        </>
                                    ) : (
                                        <>
                                            <Brain className="h-4 w-4 mr-2" />
                                            Start AI Negotiation
                                        </>
                                    )}
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Low Stock Alert */}
            {inventoryItems.length > 0 && (
                <Alert className="border-yellow-300 bg-yellow-50">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <AlertDescription className="text-yellow-800">
                        <strong>{inventoryItems.length} items</strong> are below reorder level and may need restocking.
                        <span className="ml-2">
                            {inventoryItems.slice(0, 3).map(item => item.name).join(', ')}
                            {inventoryItems.length > 3 && ` and ${inventoryItems.length - 3} more`}
                        </span>
                    </AlertDescription>
                </Alert>
            )}

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Negotiations</CardTitle>
                        <Brain className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">
                            {activeNegotiations.length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            AI agents working
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
                        <Clock className="h-4 w-4 text-yellow-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-yellow-600">
                            {pendingApprovals.length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Awaiting your decision
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
                        <Users className="h-4 w-4 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-purple-600">
                            {activeNegotiations.length + pendingApprovals.length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                            All negotiations
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Main Content */}
            <Tabs defaultValue="active" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="active">Active Negotiations</TabsTrigger>
                    <TabsTrigger value="approvals">Pending Approvals</TabsTrigger>
                </TabsList>

                <TabsContent value="active" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Active AI Negotiations</CardTitle>
                            <CardDescription>Real-time view of AI agents negotiating with vendors</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {activeNegotiations.length > 0 ? (
                                <div className="space-y-4">
                                    {activeNegotiations.map((session) => (
                                        <div key={session.session_id} className="border rounded-lg p-4">
                                            <div className="flex items-start justify-between">
                                                <div className="flex items-start space-x-3">
                                                    {getStatusIcon(session.status)}
                                                    <div>
                                                        <h4 className="font-medium">{session.item_name}</h4>
                                                        <p className="text-sm text-gray-600">
                                                            Quantity: {session.quantity_needed} • Session: {session.session_id.slice(0, 8)}
                                                            {session.trigger_source === 'stock_reduction' && (
                                                                <Badge variant="outline" className="ml-2 text-xs">Auto-triggered</Badge>
                                                            )}
                                                        </p>
                                                        <p className="text-sm text-gray-800 mt-2">{session.ai_reasoning}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="flex items-center space-x-2 mb-2">
                                                        <Badge className={getStatusColor(session.status)}>
                                                            {session.status.replace('_', ' ').toUpperCase()}
                                                        </Badge>
                                                        <Dialog>
                                                            <DialogTrigger asChild>
                                                                <Button variant="outline" size="sm">
                                                                    <MessageSquare className="h-3 w-3 mr-1" />
                                                                    Chat
                                                                </Button>
                                                            </DialogTrigger>
                                                            <DialogContent className="max-w-6xl max-h-[80vh]">
                                                                <DialogHeader>
                                                                    <DialogTitle className="flex items-center gap-2">
                                                                        <MessageSquare className="h-5 w-5" />
                                                                        Vendor Negotiation: {session.item_name}
                                                                    </DialogTitle>
                                                                    <DialogDescription>
                                                                        AI-powered negotiation with {session.best_proposal?.vendor_name || 'multiple vendors'}
                                                                    </DialogDescription>
                                                                </DialogHeader>
                                                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                                                                    {/* Main Chat Area */}
                                                                    <div className="lg:col-span-2">
                                                                        <div className="h-[400px] overflow-y-auto border rounded-lg p-4 bg-gray-50">
                                                                            {session.conversation && session.conversation.length > 0 ? (
                                                                                <div className="space-y-3">
                                                                                    {session.conversation.map((message, index) => (
                                                                                        <div
                                                                                            key={index}
                                                                                            className={`flex ${message.speaker === 'AI Agent' ? 'justify-end' : 'justify-start'}`}
                                                                                        >
                                                                                            <div
                                                                                                className={`max-w-[70%] p-3 rounded-lg ${message.speaker === 'AI Agent'
                                                                                                    ? 'bg-blue-500 text-white'
                                                                                                    : 'bg-white border'
                                                                                                    }`}
                                                                                            >
                                                                                                <div className="flex items-center justify-between mb-1">
                                                                                                    <span className={`text-xs font-medium ${message.speaker === 'AI Agent' ? 'text-blue-100' : 'text-gray-600'
                                                                                                        }`}>
                                                                                                        {message.speaker}
                                                                                                    </span>
                                                                                                    <span className={`text-xs ${message.speaker === 'AI Agent' ? 'text-blue-100' : 'text-gray-400'
                                                                                                        }`}>
                                                                                                        {new Date(message.timestamp).toLocaleTimeString()}
                                                                                                    </span>
                                                                                                </div>
                                                                                                <p className="text-sm">{message.message}</p>
                                                                                                <Badge
                                                                                                    variant="outline"
                                                                                                    className={`mt-1 text-xs ${message.speaker === 'AI Agent' ? 'border-blue-200 text-blue-100' : ''
                                                                                                        }`}
                                                                                                >
                                                                                                    {message.message_type}
                                                                                                </Badge>
                                                                                            </div>
                                                                                        </div>
                                                                                    ))}
                                                                                </div>
                                                                            ) : (
                                                                                <div className="text-center py-8">
                                                                                    <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                                                                    <p className="text-gray-500">
                                                                                        {session.status === 'discovering'
                                                                                            ? 'AI agent discovering vendors...'
                                                                                            : session.status === 'negotiating'
                                                                                                ? 'Live negotiation with Gemini AI in progress...'
                                                                                                : 'Conversation will appear here as it progresses'}
                                                                                    </p>
                                                                                    <p className="text-xs text-gray-400 mt-2">
                                                                                        Session: {session.session_id} | Status: {session.status}
                                                                                    </p>
                                                                                    {session.status === 'negotiating' && (
                                                                                        <div className="mt-3">
                                                                                            <div className="animate-pulse bg-orange-300 h-2 rounded-full"></div>
                                                                                            <p className="text-xs text-orange-600 mt-1">🤖 Gemini AI negotiating with vendors...</p>
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                    </div>

                                                                    {/* Right Sidebar */}
                                                                    <div className="space-y-4">
                                                                        {/* Quick Actions */}
                                                                        <Card>
                                                                            <CardHeader className="pb-3">
                                                                                <CardTitle className="text-sm">Quick Actions</CardTitle>
                                                                            </CardHeader>
                                                                            <CardContent className="space-y-2">
                                                                                <Button
                                                                                    variant="outline"
                                                                                    size="sm"
                                                                                    className="w-full justify-start"
                                                                                    onClick={() => handleQuickAction(session.session_id, 'price_match')}
                                                                                >
                                                                                    <DollarSign className="h-4 w-4 mr-2" />
                                                                                    Request Price Match
                                                                                </Button>
                                                                                <Button
                                                                                    variant="outline"
                                                                                    size="sm"
                                                                                    className="w-full justify-start"
                                                                                    onClick={() => handleQuickAction(session.session_id, 'expedite')}
                                                                                >
                                                                                    <Clock className="h-4 w-4 mr-2" />
                                                                                    Expedite Delivery
                                                                                </Button>
                                                                                <Button
                                                                                    variant="outline"
                                                                                    size="sm"
                                                                                    className="w-full justify-start"
                                                                                    onClick={() => handleQuickAction(session.session_id, 'bulk_discount')}
                                                                                >
                                                                                    <Package className="h-4 w-4 mr-2" />
                                                                                    Bulk Discount
                                                                                </Button>
                                                                                <Button
                                                                                    variant="outline"
                                                                                    size="sm"
                                                                                    className="w-full justify-start"
                                                                                    onClick={() => handleQuickAction(session.session_id, 'accept_terms')}
                                                                                >
                                                                                    <CheckCircle className="h-4 w-4 mr-2" />
                                                                                    Accept Current Terms
                                                                                </Button>
                                                                            </CardContent>
                                                                        </Card>

                                                                        {/* Negotiation Analytics */}
                                                                        {session.best_proposal && (
                                                                            <Card>
                                                                                <CardHeader className="pb-3">
                                                                                    <CardTitle className="text-sm">Negotiation Analytics</CardTitle>
                                                                                </CardHeader>
                                                                                <CardContent className="space-y-3">
                                                                                    <div className="space-y-2">
                                                                                        <div className="flex justify-between text-sm">
                                                                                            <span className="text-gray-600">Current Price:</span>
                                                                                            <span className="font-semibold">${session.best_proposal.unit_price}</span>
                                                                                        </div>
                                                                                        <div className="flex justify-between text-sm">
                                                                                            <span className="text-gray-600">Target Price:</span>
                                                                                            <span className="font-semibold text-green-600">${(session.best_proposal.unit_price * 0.9).toFixed(2)}</span>
                                                                                        </div>
                                                                                        <div className="flex justify-between text-sm">
                                                                                            <span className="text-gray-600">Market Average:</span>
                                                                                            <span className="font-semibold">${(session.best_proposal.unit_price * 1.1).toFixed(2)}</span>
                                                                                        </div>
                                                                                        <div className="flex justify-between text-sm">
                                                                                            <span className="text-gray-600">Potential Savings:</span>
                                                                                            <span className="font-semibold text-green-600">8.5%</span>
                                                                                        </div>
                                                                                        <div className="flex justify-between text-sm">
                                                                                            <span className="text-gray-600">AI Confidence:</span>
                                                                                            <span className="font-semibold">{(session.best_proposal.confidence_score * 100).toFixed(0)}%</span>
                                                                                        </div>
                                                                                    </div>
                                                                                </CardContent>
                                                                            </Card>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </DialogContent>
                                                        </Dialog>
                                                    </div>
                                                    <Progress
                                                        value={session.status === 'discovering' ? 25 :
                                                            session.status === 'negotiating' ? 60 :
                                                                session.status === 'comparing' ? 85 : 100}
                                                        className="w-24"
                                                    />
                                                </div>
                                            </div>

                                            {session.vendor_proposals.length > 0 && (
                                                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-2">
                                                    {session.vendor_proposals.map((proposal, index) => (
                                                        <div key={index} className="text-xs p-2 bg-gray-50 rounded">
                                                            <div className="font-medium">{proposal.vendor_name}</div>
                                                            <div>${proposal.total_price} • {proposal.delivery_time}d</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                    <p className="text-gray-500">No active negotiations</p>
                                    <p className="text-sm text-gray-400">Start a new negotiation to see AI agents in action</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="approvals" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Pending Approvals</CardTitle>
                            <CardDescription>Review AI-negotiated deals and approve orders</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {pendingApprovals.length > 0 ? (
                                <div className="space-y-6">
                                    {pendingApprovals.map((session) => (
                                        <div key={session.session_id} className="border rounded-lg p-6">
                                            <div className="flex items-start justify-between mb-4">
                                                <div>
                                                    <h4 className="text-lg font-medium">{session.item_name}</h4>
                                                    <p className="text-gray-600">Quantity: {session.quantity_needed}</p>
                                                    <p className="text-sm text-gray-800 mt-2">{session.ai_reasoning}</p>
                                                </div>
                                                <Badge className="bg-yellow-100 text-yellow-800">
                                                    AWAITING APPROVAL
                                                </Badge>
                                            </div>

                                            {session.best_proposal && (
                                                <div className="bg-green-50 rounded-lg p-4 mb-4">
                                                    <h5 className="font-medium text-green-800 mb-2">
                                                        🏆 Recommended: {session.best_proposal.vendor_name}
                                                    </h5>
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                        <div>
                                                            <span className="text-gray-600">Unit Price:</span>
                                                            <div className="font-medium">${session.best_proposal.unit_price}</div>
                                                        </div>
                                                        <div>
                                                            <span className="text-gray-600">Total Cost:</span>
                                                            <div className="font-medium">${session.best_proposal.total_price}</div>
                                                        </div>
                                                        <div>
                                                            <span className="text-gray-600">Delivery:</span>
                                                            <div className="font-medium">{session.best_proposal.delivery_time} days</div>
                                                        </div>
                                                        <div>
                                                            <span className="text-gray-600">Confidence:</span>
                                                            <div className="font-medium">{(session.best_proposal.confidence_score * 100).toFixed(0)}%</div>
                                                        </div>
                                                    </div>
                                                    <p className="text-sm text-gray-600 mt-2">
                                                        Terms: {session.best_proposal.terms}
                                                    </p>
                                                </div>
                                            )}

                                            <div className="flex space-x-3">
                                                <Dialog>
                                                    <DialogTrigger asChild>
                                                        <Button
                                                            variant="outline"
                                                            className="border-blue-300 text-blue-600 hover:bg-blue-50"
                                                        >
                                                            <MessageSquare className="h-4 w-4 mr-2" />
                                                            View Conversation
                                                        </Button>
                                                    </DialogTrigger>
                                                    <DialogContent className="max-w-4xl max-h-[600px]">
                                                        <DialogHeader>
                                                            <DialogTitle>AI Agent Conversation</DialogTitle>
                                                            <DialogDescription>
                                                                View the complete negotiation conversation for {session.item_name}
                                                            </DialogDescription>
                                                        </DialogHeader>
                                                        <div className="h-[400px] overflow-y-auto border rounded-lg p-4 bg-gray-50">
                                                            {session.conversation && session.conversation.length > 0 ? (
                                                                <div className="space-y-3">
                                                                    {session.conversation.map((message, index) => (
                                                                        <div
                                                                            key={index}
                                                                            className={`flex ${message.speaker === 'AI Agent' ? 'justify-end' : 'justify-start'}`}
                                                                        >
                                                                            <div
                                                                                className={`max-w-[70%] p-3 rounded-lg ${message.speaker === 'AI Agent'
                                                                                    ? 'bg-blue-500 text-white'
                                                                                    : 'bg-white border'
                                                                                    }`}
                                                                            >
                                                                                <div className="flex items-center justify-between mb-1">
                                                                                    <span className={`text-xs font-medium ${message.speaker === 'AI Agent' ? 'text-blue-100' : 'text-gray-600'
                                                                                        }`}>
                                                                                        {message.speaker}
                                                                                    </span>
                                                                                    <span className={`text-xs ${message.speaker === 'AI Agent' ? 'text-blue-100' : 'text-gray-400'
                                                                                        }`}>
                                                                                        {new Date(message.timestamp).toLocaleTimeString()}
                                                                                    </span>
                                                                                </div>
                                                                                <p className="text-sm">{message.message}</p>
                                                                                <Badge
                                                                                    variant="outline"
                                                                                    className={`mt-1 text-xs ${message.speaker === 'AI Agent' ? 'border-blue-200 text-blue-100' : ''
                                                                                        }`}
                                                                                >
                                                                                    {message.message_type}
                                                                                </Badge>
                                                                            </div>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            ) : (
                                                                <div className="text-center py-8">
                                                                    <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                                                    <p className="text-gray-500">
                                                                        {session.status === 'discovering' || session.status === 'negotiating'
                                                                            ? 'Negotiation in progress...'
                                                                            : 'No conversation history available'}
                                                                    </p>
                                                                    <p className="text-xs text-gray-400 mt-2">
                                                                        Status: {session.status} | Session: {session.session_id}
                                                                    </p>
                                                                    {session.status === 'discovering' && (
                                                                        <div className="mt-3">
                                                                            <div className="animate-pulse bg-gray-300 h-2 rounded-full"></div>
                                                                            <p className="text-xs text-gray-500 mt-1">AI agent is discovering vendors...</p>
                                                                        </div>
                                                                    )}
                                                                    {session.status === 'negotiating' && (
                                                                        <div className="mt-3">
                                                                            <div className="animate-pulse bg-orange-300 h-2 rounded-full"></div>
                                                                            <p className="text-xs text-gray-500 mt-1">Real-time negotiation with Gemini AI in progress...</p>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            )}
                                                        </div>

                                                        {/* Vendor Proposals Summary */}
                                                        {session.vendor_proposals && session.vendor_proposals.length > 0 && (
                                                            <div className="mt-4">
                                                                <h4 className="font-medium mb-3">Vendor Proposals Comparison</h4>
                                                                <div className="grid gap-3">
                                                                    {session.vendor_proposals.map((proposal, index) => (
                                                                        <div
                                                                            key={proposal.vendor_id}
                                                                            className={`p-3 rounded border ${session.best_proposal?.vendor_id === proposal.vendor_id
                                                                                ? 'border-green-300 bg-green-50'
                                                                                : 'border-gray-200'
                                                                                }`}
                                                                        >
                                                                            <div className="flex justify-between items-start">
                                                                                <div>
                                                                                    <span className="font-medium">{proposal.vendor_name}</span>
                                                                                    {session.best_proposal?.vendor_id === proposal.vendor_id && (
                                                                                        <Badge className="ml-2 bg-green-100 text-green-800">RECOMMENDED</Badge>
                                                                                    )}
                                                                                    <div className="text-sm text-gray-600 mt-1">
                                                                                        ${proposal.unit_price}/unit • ${proposal.total_price} total • {proposal.delivery_time} days
                                                                                    </div>
                                                                                    {proposal.special_offers && (
                                                                                        <div className="text-sm text-blue-600 mt-1">
                                                                                            🎁 {proposal.special_offers}
                                                                                        </div>
                                                                                    )}
                                                                                    {proposal.profit_margin && (
                                                                                        <div className="text-xs text-gray-500 mt-1">
                                                                                            Profit Margin: {proposal.profit_margin.toFixed(1)}%
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                                <div className="text-right">
                                                                                    <div className="text-sm font-medium">
                                                                                        {(proposal.confidence_score * 100).toFixed(0)}% confidence
                                                                                    </div>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        )}
                                                    </DialogContent>
                                                </Dialog>
                                                <Button
                                                    onClick={() => approveOrder(session.session_id, true)}
                                                    className="bg-green-600 hover:bg-green-700"
                                                >
                                                    <CheckCircle className="h-4 w-4 mr-2" />
                                                    Approve Order
                                                </Button>
                                                <Button
                                                    onClick={() => approveOrder(session.session_id, false)}
                                                    variant="outline"
                                                    className="border-red-300 text-red-600 hover:bg-red-50"
                                                >
                                                    <XCircle className="h-4 w-4 mr-2" />
                                                    Reject
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <Clock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                                    <p className="text-gray-500">No pending approvals</p>
                                    <p className="text-sm text-gray-400">Completed negotiations will appear here for your review</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}