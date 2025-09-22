"use client";

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bell, X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-react';

interface Notification {
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
    action?: {
        label: string;
        onClick: () => void;
    };
}

interface NotificationSystemProps {
    maxNotifications?: number;
    autoRemoveDelay?: number;
}

export function NotificationSystem({
    maxNotifications = 5,
    autoRemoveDelay = 5000
}: NotificationSystemProps) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [isOpen, setIsOpen] = useState(false);

    const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
        const newNotification: Notification = {
            ...notification,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date(),
            read: false
        };

        setNotifications(prev => {
            const updated = [newNotification, ...prev].slice(0, maxNotifications);
            return updated;
        });

        // Auto remove notification after delay
        if (autoRemoveDelay > 0) {
            setTimeout(() => {
                removeNotification(newNotification.id);
            }, autoRemoveDelay);
        }
    };

    const removeNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    const markAsRead = (id: string) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    };

    const clearAll = () => {
        setNotifications([]);
    };

    const unreadCount = notifications.filter(n => !n.read).length;

    const getIcon = (type: Notification['type']) => {
        switch (type) {
            case 'success':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'error':
                return <AlertCircle className="h-4 w-4 text-red-500" />;
            case 'warning':
                return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
            case 'info':
                return <Info className="h-4 w-4 text-blue-500" />;
            default:
                return <Info className="h-4 w-4 text-gray-500" />;
        }
    };

    const getBorderColor = (type: Notification['type']) => {
        switch (type) {
            case 'success':
                return 'border-l-green-500';
            case 'error':
                return 'border-l-red-500';
            case 'warning':
                return 'border-l-yellow-500';
            case 'info':
                return 'border-l-blue-500';
            default:
                return 'border-l-gray-500';
        }
    };

    // Global notification methods
    useEffect(() => {
        // Expose notification methods globally
        (window as any).addNotification = addNotification;

        return () => {
            delete (window as any).addNotification;
        };
    }, []);

    return (
        <div className="relative">
            {/* Notification Bell */}
            <Button
                variant="outline"
                size="sm"
                onClick={() => setIsOpen(!isOpen)}
                className="relative"
            >
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                    <Badge
                        variant="destructive"
                        className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
                    >
                        {unreadCount}
                    </Badge>
                )}
            </Button>

            {/* Notification Panel */}
            {isOpen && (
                <Card className="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-hidden z-50 shadow-lg">
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">Notifications</CardTitle>
                            <div className="flex items-center space-x-2">
                                {notifications.length > 0 && (
                                    <Button variant="ghost" size="sm" onClick={clearAll}>
                                        Clear All
                                    </Button>
                                )}
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => setIsOpen(false)}
                                >
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                        {notifications.length > 0 && (
                            <CardDescription>
                                {unreadCount} unread notifications
                            </CardDescription>
                        )}
                    </CardHeader>
                    <CardContent className="p-0">
                        {notifications.length === 0 ? (
                            <div className="p-4 text-center text-gray-500">
                                No notifications
                            </div>
                        ) : (
                            <div className="max-h-64 overflow-y-auto">
                                {notifications.map((notification) => (
                                    <div
                                        key={notification.id}
                                        className={`p-4 border-l-4 ${getBorderColor(notification.type)} border-b last:border-b-0 ${!notification.read ? 'bg-gray-50' : 'bg-white'
                                            }`}
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-start space-x-3 flex-1">
                                                {getIcon(notification.type)}
                                                <div className="flex-1 min-w-0">
                                                    <p className="text-sm font-medium text-gray-900">
                                                        {notification.title}
                                                    </p>
                                                    <p className="text-sm text-gray-600 mt-1">
                                                        {notification.message}
                                                    </p>
                                                    <p className="text-xs text-gray-500 mt-2">
                                                        {notification.timestamp.toLocaleTimeString()}
                                                    </p>
                                                    {notification.action && (
                                                        <Button
                                                            variant="link"
                                                            size="sm"
                                                            className="p-0 h-auto mt-2 text-blue-600"
                                                            onClick={notification.action.onClick}
                                                        >
                                                            {notification.action.label}
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex items-center space-x-1 ml-2">
                                                {!notification.read && (
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => markAsRead(notification.id)}
                                                        className="h-6 w-6 p-0"
                                                    >
                                                        <CheckCircle className="h-3 w-3" />
                                                    </Button>
                                                )}
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={() => removeNotification(notification.id)}
                                                    className="h-6 w-6 p-0"
                                                >
                                                    <X className="h-3 w-3" />
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
}

// Toast Notification Component
interface ToastNotificationProps {
    notification: Notification;
    onRemove: (id: string) => void;
}

export function ToastNotification({ notification, onRemove }: ToastNotificationProps) {
    useEffect(() => {
        const timer = setTimeout(() => {
            onRemove(notification.id);
        }, 5000);

        return () => clearTimeout(timer);
    }, [notification.id, onRemove]);

    const getBgColor = (type: Notification['type']) => {
        switch (type) {
            case 'success':
                return 'bg-green-50 border-green-200';
            case 'error':
                return 'bg-red-50 border-red-200';
            case 'warning':
                return 'bg-yellow-50 border-yellow-200';
            case 'info':
                return 'bg-blue-50 border-blue-200';
            default:
                return 'bg-gray-50 border-gray-200';
        }
    };

    return (
        <div className={`max-w-sm w-full ${getBgColor(notification.type)} border rounded-lg shadow-lg p-4 pointer-events-auto`}>
            <div className="flex items-start">
                <div className="flex-shrink-0">
                    {/* Icon based on notification type */}
                    {notification.type === 'success' && <CheckCircle className="h-5 w-5 text-green-400" />}
                    {notification.type === 'error' && <AlertCircle className="h-5 w-5 text-red-400" />}
                    {notification.type === 'warning' && <AlertTriangle className="h-5 w-5 text-yellow-400" />}
                    {notification.type === 'info' && <Info className="h-5 w-5 text-blue-400" />}
                </div>
                <div className="ml-3 w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                        {notification.message}
                    </p>
                    {notification.action && (
                        <div className="mt-3">
                            <Button
                                variant="link"
                                size="sm"
                                className="p-0 h-auto text-blue-600"
                                onClick={notification.action.onClick}
                            >
                                {notification.action.label}
                            </Button>
                        </div>
                    )}
                </div>
                <div className="ml-4 flex-shrink-0 flex">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onRemove(notification.id)}
                        className="h-6 w-6 p-0"
                    >
                        <X className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}

// Toast Container
export function ToastContainer() {
    const [toasts, setToasts] = useState<Notification[]>([]);

    const addToast = (toast: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
        const newToast: Notification = {
            ...toast,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date(),
            read: false
        };

        setToasts(prev => [...prev, newToast]);
    };

    const removeToast = (id: string) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    };

    useEffect(() => {
        // Expose toast methods globally
        (window as any).addToast = addToast;

        return () => {
            delete (window as any).addToast;
        };
    }, []);

    return (
        <div className="fixed bottom-0 right-0 z-50 p-6 space-y-4">
            {toasts.map((toast) => (
                <ToastNotification
                    key={toast.id}
                    notification={toast}
                    onRemove={removeToast}
                />
            ))}
        </div>
    );
}

// Utility functions for easy notification usage
export const showNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    if ((window as any).addNotification) {
        (window as any).addNotification(notification);
    }
};

export const showToast = (toast: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    if ((window as any).addToast) {
        (window as any).addToast(toast);
    }
};

// Convenience methods
export const showSuccess = (title: string, message: string, action?: { label: string; onClick: () => void }) => {
    showToast({ type: 'success', title, message, action });
};

export const showError = (title: string, message: string, action?: { label: string; onClick: () => void }) => {
    showToast({ type: 'error', title, message, action });
};

export const showWarning = (title: string, message: string, action?: { label: string; onClick: () => void }) => {
    showToast({ type: 'warning', title, message, action });
};

export const showInfo = (title: string, message: string, action?: { label: string; onClick: () => void }) => {
    showToast({ type: 'info', title, message, action });
};