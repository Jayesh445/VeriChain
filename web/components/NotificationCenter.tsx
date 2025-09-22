"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
    Bell,
    CheckCircle,
    XCircle,
    AlertTriangle,
    Info,
    Clock,
    Package,
    MessageSquare,
    Truck,
    DollarSign,
    X
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface Notification {
    id: string;
    type: 'approval_request' | 'order_update' | 'negotiation_complete' | 'system_alert' | 'info';
    title: string;
    message: string;
    metadata?: any;
    created_at: string;
    read: boolean;
    requires_action: boolean;
}

interface NotificationCenterProps {
    onNotificationUpdate?: () => void;
}

export default function NotificationCenter({ onNotificationUpdate }: NotificationCenterProps) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
    const [approvalNotes, setApprovalNotes] = useState('');
    const [processingApproval, setProcessingApproval] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        fetchNotifications();
        // No automatic polling - only refresh manually or when needed
    }, []);

    const fetchNotifications = async () => {
        try {
            setLoading(true);
            const response = await VeriChainAPI.getNotifications();

            if (response.success) {
                setNotifications(response.notifications || []);
            } else {
                setNotifications([]);
            }
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
            // Fallback to empty array if backend fails
            setNotifications([]);
        } finally {
            setLoading(false);
        }
    };

    const handleApproval = async (notificationId: string, sessionId: string, approved: boolean) => {
        try {
            setProcessingApproval(true);

            await VeriChainAPI.approveOrder({
                session_id: sessionId,
                approved,
                user_notes: approvalNotes
            });

            // Mark notification as read and remove from list
            setNotifications(prev => prev.filter(n => n.id !== notificationId));

            toast({
                title: approved ? "Order Approved" : "Order Rejected",
                description: approved ? "The order will be processed shortly" : "The negotiation has been cancelled",
                variant: approved ? "default" : "destructive"
            });

            setSelectedNotification(null);
            setApprovalNotes('');

            if (onNotificationUpdate) {
                onNotificationUpdate();
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to process approval",
                variant: "destructive"
            });
        } finally {
            setProcessingApproval(false);
        }
    };

    const markAsRead = (notificationId: string) => {
        setNotifications(prev =>
            prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
        );
    };

    const dismissNotification = (notificationId: string) => {
        setNotifications(prev => prev.filter(n => n.id !== notificationId));
    };

    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'approval_request':
                return <Clock className="h-5 w-5 text-orange-500" />;
            case 'negotiation_complete':
                return <MessageSquare className="h-5 w-5 text-blue-500" />;
            case 'order_update':
                return <Package className="h-5 w-5 text-green-500" />;
            case 'system_alert':
                return <AlertTriangle className="h-5 w-5 text-red-500" />;
            default:
                return <Info className="h-5 w-5 text-gray-500" />;
        }
    };

    const getNotificationColor = (type: string, read: boolean) => {
        const opacity = read ? 'bg-opacity-50' : '';
        switch (type) {
            case 'approval_request':
                return `bg-orange-50 border-orange-200 ${opacity}`;
            case 'negotiation_complete':
                return `bg-blue-50 border-blue-200 ${opacity}`;
            case 'order_update':
                return `bg-green-50 border-green-200 ${opacity}`;
            case 'system_alert':
                return `bg-red-50 border-red-200 ${opacity}`;
            default:
                return `bg-gray-50 border-gray-200 ${opacity}`;
        }
    };

    const unreadCount = notifications.filter(n => !n.read).length;
    const actionRequiredCount = notifications.filter(n => n.requires_action && !n.read).length;

    if (loading) {
        return (
            <div className="animate-pulse space-y-4">
                <div className="h-8 bg-gray-200 rounded w-1/4"></div>
                <div className="space-y-3">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-20 bg-gray-200 rounded"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-3">
                    <Bell className="h-6 w-6 text-blue-600" />
                    <h2 className="text-2xl font-bold">Notifications</h2>
                    {unreadCount > 0 && (
                        <Badge variant="destructive" className="rounded-full">
                            {unreadCount}
                        </Badge>
                    )}
                </div>
                {actionRequiredCount > 0 && (
                    <Alert className="w-auto border-orange-200 bg-orange-50">
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                        <AlertDescription className="text-orange-800">
                            {actionRequiredCount} notification{actionRequiredCount > 1 ? 's' : ''} require{actionRequiredCount === 1 ? 's' : ''} your action
                        </AlertDescription>
                    </Alert>
                )}
            </div>

            {/* Notifications List */}
            <div className="space-y-4">
                {notifications.length > 0 ? (
                    notifications.map((notification) => (
                        <Card key={notification.id} className={`cursor-pointer transition-all hover:shadow-md ${getNotificationColor(notification.type, notification.read)}`}>
                            <CardContent className="p-4">
                                <div className="flex items-start justify-between">
                                    <div
                                        className="flex items-start space-x-3 flex-1"
                                        onClick={() => {
                                            markAsRead(notification.id);
                                            if (notification.requires_action) {
                                                setSelectedNotification(notification);
                                            }
                                        }}
                                    >
                                        {getNotificationIcon(notification.type)}
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-2">
                                                <h4 className={`font-medium ${!notification.read ? 'text-gray-900' : 'text-gray-600'}`}>
                                                    {notification.title}
                                                </h4>
                                                {!notification.read && (
                                                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                                )}
                                                {notification.requires_action && (
                                                    <Badge variant="outline" className="text-xs">
                                                        Action Required
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className={`text-sm mt-1 ${!notification.read ? 'text-gray-700' : 'text-gray-500'}`}>
                                                {notification.message}
                                            </p>
                                            <p className="text-xs text-gray-400 mt-2">
                                                {new Date(notification.created_at).toLocaleString()}
                                            </p>

                                            {/* Metadata Display */}
                                            {notification.metadata && (
                                                <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                                                    {notification.metadata.vendor_name && (
                                                        <div className="flex items-center space-x-1">
                                                            <Truck className="h-3 w-3" />
                                                            <span>{notification.metadata.vendor_name}</span>
                                                        </div>
                                                    )}
                                                    {notification.metadata.total_cost && (
                                                        <div className="flex items-center space-x-1">
                                                            <DollarSign className="h-3 w-3" />
                                                            <span>${notification.metadata.total_cost.toFixed(2)}</span>
                                                        </div>
                                                    )}
                                                    {notification.metadata.delivery_time && (
                                                        <div className="flex items-center space-x-1">
                                                            <Clock className="h-3 w-3" />
                                                            <span>{notification.metadata.delivery_time} days</span>
                                                        </div>
                                                    )}
                                                    {notification.metadata.item_name && (
                                                        <div className="flex items-center space-x-1">
                                                            <Package className="h-3 w-3" />
                                                            <span>{notification.metadata.item_name}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            dismissNotification(notification.id);
                                        }}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        <X className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))
                ) : (
                    <Card>
                        <CardContent className="p-8 text-center">
                            <Bell className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                            <p className="text-gray-500">No notifications</p>
                            <p className="text-sm text-gray-400">You're all caught up!</p>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Approval Dialog */}
            <Dialog open={selectedNotification !== null} onOpenChange={() => setSelectedNotification(null)}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>Order Approval Required</DialogTitle>
                        <DialogDescription>
                            Review the AI-negotiated deal and decide whether to proceed with the order.
                        </DialogDescription>
                    </DialogHeader>

                    {selectedNotification && selectedNotification.metadata && (
                        <div className="space-y-4">
                            <div className="bg-blue-50 rounded-lg p-4">
                                <h4 className="font-medium text-blue-900 mb-2">Deal Summary</h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span>Item:</span>
                                        <span className="font-medium">{selectedNotification.metadata.item_name}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Vendor:</span>
                                        <span className="font-medium">{selectedNotification.metadata.vendor_name}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Total Cost:</span>
                                        <span className="font-medium">
                                            ${selectedNotification.metadata.total_cost?.toFixed(2) || 'N/A'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Delivery:</span>
                                        <span className="font-medium">
                                            {selectedNotification.metadata.delivery_time || 'N/A'} days
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div>
                                <Label htmlFor="approval-notes">Notes (Optional)</Label>
                                <Textarea
                                    id="approval-notes"
                                    value={approvalNotes}
                                    onChange={(e) => setApprovalNotes(e.target.value)}
                                    placeholder="Add any notes about this approval..."
                                    className="mt-1"
                                />
                            </div>

                            <div className="flex space-x-3">
                                <Button
                                    onClick={() => handleApproval(
                                        selectedNotification.id,
                                        selectedNotification.metadata.session_id,
                                        true
                                    )}
                                    disabled={processingApproval}
                                    className="bg-green-600 hover:bg-green-700 flex-1"
                                >
                                    <CheckCircle className="h-4 w-4 mr-2" />
                                    {processingApproval ? "Processing..." : "Approve Order"}
                                </Button>
                                <Button
                                    onClick={() => handleApproval(
                                        selectedNotification.id,
                                        selectedNotification.metadata.session_id,
                                        false
                                    )}
                                    disabled={processingApproval}
                                    variant="outline"
                                    className="border-red-300 text-red-600 hover:bg-red-50 flex-1"
                                >
                                    <XCircle className="h-4 w-4 mr-2" />
                                    Reject
                                </Button>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
}