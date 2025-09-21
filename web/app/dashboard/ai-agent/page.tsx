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
import { Textarea } from "@/components/ui/textarea";
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
}

interface NegotiationSession {
    session_id: string;
    item_id: number;
    item_name: string;
    quantity_needed: number;
    status: string;
    vendor_proposals: VendorProposal[];
    best_proposal?: VendorProposal;
    ai_reasoning: string;
    created_at: string;
    updated_at: string;
}

export default function AIAgentDashboard() {
    const [activeNegotiations, setActiveNegotiations] = useState<NegotiationSession[]>([]);
    const [pendingApprovals, setPendingApprovals] = useState<NegotiationSession[]>([]);
    const [selectedSession, setSelectedSession] = useState<NegotiationSession | null>(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [startingNegotiation, setStartingNegotiation] = useState(false);
    const [newNegotiation, setNewNegotiation] = useState({
        item_id: '',
        quantity_needed: '',
        urgency: 'medium'
    });
    const { toast } = useToast();

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchData = async () => {
        try {
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
                    <Button
                        onClick={fetchData}
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
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Start AI Negotiation</DialogTitle>
                                <DialogDescription>
                                    Begin AI agent negotiation for inventory replenishment
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="item_id">Item ID</Label>
                                    <Input
                                        id="item_id"
                                        value={newNegotiation.item_id}
                                        onChange={(e) => setNewNegotiation({ ...newNegotiation, item_id: e.target.value })}
                                        placeholder="Enter item ID"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="quantity">Quantity Needed</Label>
                                    <Input
                                        id="quantity"
                                        value={newNegotiation.quantity_needed}
                                        onChange={(e) => setNewNegotiation({ ...newNegotiation, quantity_needed: e.target.value })}
                                        placeholder="Enter quantity"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="urgency">Urgency</Label>
                                    <select
                                        id="urgency"
                                        value={newNegotiation.urgency}
                                        onChange={(e) => setNewNegotiation({ ...newNegotiation, urgency: e.target.value })}
                                        className="w-full p-2 border rounded"
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                    </select>
                                </div>
                                <Button
                                    onClick={startNegotiation}
                                    disabled={startingNegotiation || !newNegotiation.item_id || !newNegotiation.quantity_needed}
                                    className="w-full"
                                >
                                    {startingNegotiation ? "Starting..." : "Start Negotiation"}
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

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
                                                        </p>
                                                        <p className="text-sm text-gray-800 mt-2">{session.ai_reasoning}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <Badge className={getStatusColor(session.status)}>
                                                        {session.status.replace('_', ' ').toUpperCase()}
                                                    </Badge>
                                                    <Progress
                                                        value={session.status === 'discovering' ? 25 :
                                                            session.status === 'negotiating' ? 60 :
                                                                session.status === 'comparing' ? 85 : 100}
                                                        className="w-24 mt-2"
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