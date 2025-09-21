"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    MessageCircle,
    Send,
    Bot,
    User,
    Clock,
    TrendingUp,
    TrendingDown,
    CheckCircle,
    AlertTriangle,
    DollarSign,
    Package,
    FileText,
    Phone,
    Mail,
    Calendar,
    ArrowRight,
    Zap,
    Target,
    Handshake,
    Star
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface NegotiationMessage {
    id: string;
    sender: 'ai' | 'vendor' | 'system';
    content: string;
    timestamp: Date;
    type: 'message' | 'proposal' | 'counter_offer' | 'acceptance' | 'rejection';
    data?: any;
}

interface RestockWorkflow {
    id: string;
    item: {
        id: number;
        name: string;
        current_stock: number;
        reorder_level: number;
        category: string;
    };
    status: 'analyzing' | 'vendor_selection' | 'negotiating' | 'ordering' | 'completed';
    startTime: Date;
    estimatedCompletion?: Date;
    vendors: Array<{
        id: number;
        name: string;
        price: number;
        delivery_time: number;
        rating: number;
        last_price: number;
        negotiation_status: 'pending' | 'in_progress' | 'completed' | 'failed';
    }>;
    aiRecommendation?: {
        vendor_id: number;
        reasoning: string;
        confidence: number;
        expected_savings: number;
    };
    messages: NegotiationMessage[];
}

export default function VendorNegotiation() {
    const [workflows, setWorkflows] = useState<RestockWorkflow[]>([]);
    const [selectedWorkflow, setSelectedWorkflow] = useState<RestockWorkflow | null>(null);
    const [isNegotiationOpen, setIsNegotiationOpen] = useState(false);
    const [newMessage, setNewMessage] = useState("");
    const [loading, setLoading] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const { toast } = useToast();

    useEffect(() => {
        initializeWorkflows();
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [selectedWorkflow?.messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const initializeWorkflows = async () => {
        try {
            setLoading(true);

            // Fetch real data from inventory
            const inventoryItems = await VeriChainAPI.getInventoryItems({ low_stock_only: true });

            // Create mock workflows for demonstration
            const mockWorkflows: RestockWorkflow[] = inventoryItems.slice(0, 3).map((item, index) => ({
                id: `workflow-${item.id}`,
                item: {
                    id: item.id,
                    name: item.name,
                    current_stock: item.current_stock,
                    reorder_level: item.reorder_level,
                    category: item.category
                },
                status: index === 0 ? 'negotiating' : index === 1 ? 'vendor_selection' : 'analyzing',
                startTime: new Date(Date.now() - index * 3600000), // Stagger by hours
                estimatedCompletion: new Date(Date.now() + (24 - index * 6) * 3600000),
                vendors: [
                    {
                        id: 1,
                        name: "Office Supplies Co.",
                        price: 12.50 + (index * 2),
                        delivery_time: 3 + index,
                        rating: 4.5 - (index * 0.3),
                        last_price: 14.00 + (index * 1.5),
                        negotiation_status: index === 0 ? 'in_progress' : 'pending'
                    },
                    {
                        id: 2,
                        name: "Premium Stationery Ltd.",
                        price: 15.00 + (index * 1.5),
                        delivery_time: 2 + index,
                        rating: 4.8 - (index * 0.2),
                        last_price: 16.50 + (index * 1.2),
                        negotiation_status: 'pending'
                    },
                    {
                        id: 3,
                        name: "Budget Office Mart",
                        price: 10.00 + (index * 2.5),
                        delivery_time: 5 + index,
                        rating: 3.8 - (index * 0.1),
                        last_price: 11.50 + (index * 2),
                        negotiation_status: 'pending'
                    }
                ],
                aiRecommendation: {
                    vendor_id: 1,
                    reasoning: `Based on historical performance, delivery reliability, and price competitiveness, Office Supplies Co. offers the best value proposition for ${item.name}. Their 4.5-star rating and consistent delivery times make them reliable.`,
                    confidence: 0.87 - (index * 0.1),
                    expected_savings: 8.5 + (index * 2)
                },
                messages: generateMockMessages(item.name, index)
            }));

            setWorkflows(mockWorkflows);
        } catch (error) {
            console.error('Failed to initialize workflows:', error);
            toast({
                title: "Error",
                description: "Failed to load restock workflows",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const generateMockMessages = (itemName: string, workflowIndex: number): NegotiationMessage[] => {
        const baseMessages: NegotiationMessage[] = [
            {
                id: '1',
                sender: 'system',
                content: `🔍 **Stock Analysis Complete**\\n\\nItem: ${itemName}\\nCurrent Stock: Below reorder level\\nAction Required: Immediate restocking`,
                timestamp: new Date(Date.now() - (workflowIndex + 4) * 3600000),
                type: 'message'
            },
            {
                id: '2',
                sender: 'ai',
                content: `📊 **AI Analysis**: I've analyzed historical data and vendor performance. Based on delivery reliability, pricing trends, and quality scores, I recommend Office Supplies Co. for this order.\\n\\n**Key Factors:**\\n• 92% on-time delivery rate\\n• 15% below market average pricing\\n• Consistent quality scores`,
                timestamp: new Date(Date.now() - (workflowIndex + 3) * 3600000),
                type: 'message'
            }
        ];

        if (workflowIndex === 0) {
            // Active negotiation
            baseMessages.push(
                {
                    id: '3',
                    sender: 'ai',
                    content: `💬 **Initiating Negotiation** with Office Supplies Co.\\n\\nProposed terms:\\n• Quantity: 200 units\\n• Unit price: $12.50\\n• Delivery: 3 business days\\n• Payment terms: Net 30`,
                    timestamp: new Date(Date.now() - 2 * 3600000),
                    type: 'proposal',
                    data: { vendor: 'Office Supplies Co.', price: 12.50, quantity: 200 }
                },
                {
                    id: '4',
                    sender: 'vendor',
                    content: `Thank you for reaching out. We can fulfill this order with the following terms:\\n\\n• Quantity: 200 units\\n• Unit price: $13.75\\n• Delivery: 2 business days\\n• Payment terms: Net 15\\n\\nThis pricing reflects our premium service and faster delivery.`,
                    timestamp: new Date(Date.now() - 1.5 * 3600000),
                    type: 'counter_offer',
                    data: { price: 13.75, delivery: 2, payment: 'Net 15' }
                },
                {
                    id: '5',
                    sender: 'ai',
                    content: `🤖 **AI Negotiation Strategy**: Vendor's counter-offer is 10% higher than target. Analyzing alternatives...\\n\\n**Strategy**: Counter with volume discount request and longer payment terms to justify lower unit price.`,
                    timestamp: new Date(Date.now() - 1 * 3600000),
                    type: 'message'
                },
                {
                    id: '6',
                    sender: 'ai',
                    content: `💼 **Counter Proposal**:\\n\\nWe appreciate your quick turnaround offer. However, we'd like to propose:\\n\\n• Unit price: $12.75 (meets you halfway)\\n• Bulk order commitment: 500 units over 3 months\\n• Payment terms: Net 30\\n• Delivery: 3 business days is acceptable\\n\\nThis builds a stronger partnership while meeting our budget requirements.`,
                    timestamp: new Date(Date.now() - 0.5 * 3600000),
                    type: 'proposal',
                    data: { price: 12.75, quantity: 500, payment: 'Net 30' }
                }
            );
        }

        return baseMessages;
    };

    const sendMessage = async () => {
        if (!newMessage.trim() || !selectedWorkflow) return;

        const userMessage: NegotiationMessage = {
            id: Date.now().toString(),
            sender: 'ai',
            content: newMessage,
            timestamp: new Date(),
            type: 'message'
        };

        setSelectedWorkflow(prev => prev ? {
            ...prev,
            messages: [...prev.messages, userMessage]
        } : null);

        setNewMessage("");

        // Simulate AI response
        setTimeout(() => {
            const aiResponse: NegotiationMessage = {
                id: (Date.now() + 1).toString(),
                sender: 'vendor',
                content: `Thank you for your message. We're reviewing your proposal and will respond shortly with our analysis.`,
                timestamp: new Date(),
                type: 'message'
            };

            setSelectedWorkflow(prev => prev ? {
                ...prev,
                messages: [...prev.messages, aiResponse]
            } : null);
        }, 2000);
    };

    const getStatusIcon = (status: RestockWorkflow['status']) => {
        switch (status) {
            case 'analyzing': return <Zap className="h-4 w-4 text-blue-500" />;
            case 'vendor_selection': return <Target className="h-4 w-4 text-orange-500" />;
            case 'negotiating': return <MessageCircle className="h-4 w-4 text-purple-500" />;
            case 'ordering': return <Package className="h-4 w-4 text-green-500" />;
            case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
        }
    };

    const getStatusColor = (status: RestockWorkflow['status']) => {
        switch (status) {
            case 'analyzing': return 'bg-blue-100 text-blue-800';
            case 'vendor_selection': return 'bg-orange-100 text-orange-800';
            case 'negotiating': return 'bg-purple-100 text-purple-800';
            case 'ordering': return 'bg-green-100 text-green-800';
            case 'completed': return 'bg-green-100 text-green-800';
        }
    };

    const openNegotiation = (workflow: RestockWorkflow) => {
        setSelectedWorkflow(workflow);
        setIsNegotiationOpen(true);
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
                    <h1 className="text-3xl font-bold">Vendor Negotiations & Restock Workflows</h1>
                    <p className="text-gray-600">AI-powered vendor negotiations and supply chain automation</p>
                </div>
                <Button
                    onClick={initializeWorkflows}
                    variant="outline"
                >
                    Refresh Workflows
                </Button>
            </div>

            {/* Workflow Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
                        <Zap className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-blue-600">{workflows.length}</div>
                        <p className="text-xs text-muted-foreground">In progress</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">In Negotiation</CardTitle>
                        <MessageCircle className="h-4 w-4 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-purple-600">
                            {workflows.filter(w => w.status === 'negotiating').length}
                        </div>
                        <p className="text-xs text-muted-foreground">Active negotiations</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Avg. Savings</CardTitle>
                        <TrendingUp className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">
                            {workflows.length > 0 ? Math.round(workflows.reduce((sum, w) => sum + (w.aiRecommendation?.expected_savings || 0), 0) / workflows.length) : 0}%
                        </div>
                        <p className="text-xs text-muted-foreground">Expected savings</p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">AI Confidence</CardTitle>
                        <Bot className="h-4 w-4 text-indigo-600" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-indigo-600">
                            {workflows.length > 0 ? Math.round(workflows.reduce((sum, w) => sum + (w.aiRecommendation?.confidence || 0), 0) / workflows.length * 100) : 0}%
                        </div>
                        <p className="text-xs text-muted-foreground">Average confidence</p>
                    </CardContent>
                </Card>
            </div>

            {/* Active Workflows */}
            <Card>
                <CardHeader>
                    <CardTitle>Restock Workflows</CardTitle>
                    <CardDescription>AI-managed supply chain workflows with automated vendor negotiations</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {workflows.map((workflow) => (
                            <div key={workflow.id} className="border rounded-lg p-4 space-y-4">
                                {/* Workflow Header */}
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        {getStatusIcon(workflow.status)}
                                        <div>
                                            <h3 className="font-semibold">{workflow.item.name}</h3>
                                            <p className="text-sm text-gray-600">
                                                Stock: {workflow.item.current_stock} / Reorder: {workflow.item.reorder_level}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <Badge className={getStatusColor(workflow.status)}>
                                            {workflow.status.replace('_', ' ')}
                                        </Badge>
                                        {workflow.status === 'negotiating' && (
                                            <Button
                                                size="sm"
                                                onClick={() => openNegotiation(workflow)}
                                                className="bg-purple-600 hover:bg-purple-700"
                                            >
                                                <MessageCircle className="h-4 w-4 mr-1" />
                                                View Chat
                                            </Button>
                                        )}
                                    </div>
                                </div>

                                {/* Workflow Progress */}
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                    <div className="text-center">
                                        <div className={`p-2 rounded-full ${workflow.status === 'analyzing' || workflow.status === 'vendor_selection' || workflow.status === 'negotiating' || workflow.status === 'ordering' || workflow.status === 'completed' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'}`}>
                                            <Zap className="h-4 w-4 mx-auto" />
                                        </div>
                                        <p className="text-xs mt-1">Analysis</p>
                                    </div>
                                    <div className="text-center">
                                        <div className={`p-2 rounded-full ${workflow.status === 'vendor_selection' || workflow.status === 'negotiating' || workflow.status === 'ordering' || workflow.status === 'completed' ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-400'}`}>
                                            <Target className="h-4 w-4 mx-auto" />
                                        </div>
                                        <p className="text-xs mt-1">Selection</p>
                                    </div>
                                    <div className="text-center">
                                        <div className={`p-2 rounded-full ${workflow.status === 'negotiating' || workflow.status === 'ordering' || workflow.status === 'completed' ? 'bg-purple-100 text-purple-600' : 'bg-gray-100 text-gray-400'}`}>
                                            <MessageCircle className="h-4 w-4 mx-auto" />
                                        </div>
                                        <p className="text-xs mt-1">Negotiation</p>
                                    </div>
                                    <div className="text-center">
                                        <div className={`p-2 rounded-full ${workflow.status === 'ordering' || workflow.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'}`}>
                                            <CheckCircle className="h-4 w-4 mx-auto" />
                                        </div>
                                        <p className="text-xs mt-1">Complete</p>
                                    </div>
                                </div>

                                {/* AI Recommendation */}
                                {workflow.aiRecommendation && (
                                    <Alert className="bg-blue-50 border-blue-200">
                                        <Bot className="h-4 w-4" />
                                        <AlertDescription>
                                            <div className="font-medium mb-2">AI Recommendation: {workflow.vendors.find(v => v.id === workflow.aiRecommendation?.vendor_id)?.name}</div>
                                            <p className="text-sm">{workflow.aiRecommendation.reasoning}</p>
                                            <div className="flex items-center space-x-4 mt-2 text-sm">
                                                <span>Confidence: {Math.round(workflow.aiRecommendation.confidence * 100)}%</span>
                                                <span>Expected Savings: {workflow.aiRecommendation.expected_savings}%</span>
                                            </div>
                                        </AlertDescription>
                                    </Alert>
                                )}

                                {/* Vendor Comparison */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                    {workflow.vendors.map((vendor) => (
                                        <div key={vendor.id} className={`p-3 border rounded ${vendor.id === workflow.aiRecommendation?.vendor_id ? 'border-blue-500 bg-blue-50' : ''}`}>
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="font-medium">{vendor.name}</span>
                                                {vendor.id === workflow.aiRecommendation?.vendor_id && (
                                                    <Badge variant="outline" className="text-blue-600 border-blue-600">AI Pick</Badge>
                                                )}
                                            </div>
                                            <div className="space-y-1 text-sm">
                                                <div className="flex justify-between">
                                                    <span>Price:</span>
                                                    <span className="font-medium">${vendor.price}</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Delivery:</span>
                                                    <span>{vendor.delivery_time} days</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Rating:</span>
                                                    <span>{vendor.rating}/5</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span>Status:</span>
                                                    <Badge
                                                        variant={vendor.negotiation_status === 'in_progress' ? 'default' : 'secondary'}
                                                        className="text-xs"
                                                    >
                                                        {vendor.negotiation_status.replace('_', ' ')}
                                                    </Badge>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Negotiation Chat Dialog */}
            <Dialog open={isNegotiationOpen} onOpenChange={setIsNegotiationOpen}>
                <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
                    <DialogHeader>
                        <DialogTitle className="flex items-center space-x-2">
                            <MessageCircle className="h-5 w-5" />
                            <span>Vendor Negotiation: {selectedWorkflow?.item.name}</span>
                        </DialogTitle>
                        <DialogDescription>
                            AI-powered negotiation with {selectedWorkflow?.vendors.find(v => v.negotiation_status === 'in_progress')?.name}
                        </DialogDescription>
                    </DialogHeader>

                    <div className="flex-1 flex space-x-4">
                        {/* Chat Area */}
                        <div className="flex-1 flex flex-col">
                            <ScrollArea className="flex-1 p-4 border rounded">
                                <div className="space-y-4">
                                    {selectedWorkflow?.messages.map((message) => (
                                        <div key={message.id} className={`flex ${message.sender === 'ai' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[70%] p-3 rounded-lg ${message.sender === 'ai'
                                                    ? 'bg-blue-600 text-white'
                                                    : message.sender === 'vendor'
                                                        ? 'bg-gray-100 text-gray-900'
                                                        : 'bg-yellow-100 text-yellow-900'
                                                }`}>
                                                <div className="flex items-center space-x-2 mb-1">
                                                    {message.sender === 'ai' && <Bot className="h-4 w-4" />}
                                                    {message.sender === 'vendor' && <User className="h-4 w-4" />}
                                                    {message.sender === 'system' && <Zap className="h-4 w-4" />}
                                                    <span className="text-xs opacity-75">
                                                        {message.sender === 'ai' ? 'AI Agent' : message.sender === 'vendor' ? 'Vendor' : 'System'}
                                                    </span>
                                                    <span className="text-xs opacity-50">
                                                        {message.timestamp.toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <div className="whitespace-pre-line text-sm">
                                                    {message.content}
                                                </div>
                                                {message.type === 'proposal' && message.data && (
                                                    <div className="mt-2 p-2 bg-black bg-opacity-10 rounded text-xs">
                                                        <strong>Proposal Details:</strong><br />
                                                        Price: ${message.data.price} | Quantity: {message.data.quantity}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                    <div ref={messagesEndRef} />
                                </div>
                            </ScrollArea>

                            {/* Message Input */}
                            <div className="flex space-x-2 pt-4">
                                <Input
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    placeholder="Type AI response or negotiation message..."
                                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                                />
                                <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Sidebar */}
                        <div className="w-80 space-y-4">
                            {/* Quick Actions */}
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-sm">Quick Actions</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    <Button size="sm" variant="outline" className="w-full justify-start">
                                        <DollarSign className="h-4 w-4 mr-2" />
                                        Request Price Match
                                    </Button>
                                    <Button size="sm" variant="outline" className="w-full justify-start">
                                        <Clock className="h-4 w-4 mr-2" />
                                        Expedite Delivery
                                    </Button>
                                    <Button size="sm" variant="outline" className="w-full justify-start">
                                        <Package className="h-4 w-4 mr-2" />
                                        Bulk Discount
                                    </Button>
                                    <Button size="sm" variant="outline" className="w-full justify-start">
                                        <Handshake className="h-4 w-4 mr-2" />
                                        Accept Current Terms
                                    </Button>
                                </CardContent>
                            </Card>

                            {/* Negotiation Analytics */}
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-sm">Negotiation Analytics</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    <div className="flex justify-between text-sm">
                                        <span>Current Price:</span>
                                        <span className="font-medium">$13.75</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>Target Price:</span>
                                        <span className="font-medium text-green-600">$12.50</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>Market Average:</span>
                                        <span className="font-medium">$14.20</span>
                                    </div>
                                    <Separator />
                                    <div className="flex justify-between text-sm">
                                        <span>Potential Savings:</span>
                                        <span className="font-medium text-green-600">8.5%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span>AI Confidence:</span>
                                        <span className="font-medium">87%</span>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Vendor Info */}
                            <Card>
                                <CardHeader>
                                    <CardTitle className="text-sm">Vendor Details</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-2">
                                    <div className="flex items-center space-x-2 text-sm">
                                        <Mail className="h-4 w-4" />
                                        <span>contact@officesupplies.com</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm">
                                        <Phone className="h-4 w-4" />
                                        <span>+1-555-0101</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm">
                                        <Star className="h-4 w-4" />
                                        <span>4.5/5 Rating (125 orders)</span>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}