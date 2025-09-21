"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
    Brain,
    TrendingUp,
    Calendar,
    Package,
    ShoppingCart,
    Sparkles,
    Clock,
    Target,
    AlertTriangle,
    CheckCircle,
    Star,
    Zap
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface TrendRecommendation {
    product_id: number;
    product_name: string;
    category: string;
    trend_name: string;
    reason: string;
    recommended_quantity: number;
    urgency: string;
    confidence: number;
    priority: number;
    estimated_demand_increase: string;
}

interface AISuggestionsProps {
    onOrderTriggered?: () => void;
}

export default function AISuggestionsPanel({ onOrderTriggered }: AISuggestionsProps) {
    const [recommendations, setRecommendations] = useState<TrendRecommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [orderingStates, setOrderingStates] = useState<Record<number, boolean>>({});
    const { toast } = useToast();

    useEffect(() => {
        fetchRecommendations();
        // Refresh suggestions every 30 minutes
        const interval = setInterval(fetchRecommendations, 30 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const fetchRecommendations = async () => {
        try {
            setLoading(true);
            const response = await VeriChainAPI.getTrendRecommendations();
            
            if (response.success) {
                setRecommendations(response.recommendations || []);
            } else {
                setRecommendations([]);
            }
        } catch (error) {
            console.error('Failed to fetch trend recommendations:', error);
            setRecommendations([]);
        } finally {
            setLoading(false);
        }
    };

    const handleAutoOrder = async (recommendation: TrendRecommendation) => {
        try {
            setOrderingStates(prev => ({ ...prev, [recommendation.product_id]: true }));
            
            const response = await VeriChainAPI.autoOrderSuggestion({
                product_id: recommendation.product_id,
                quantity: recommendation.recommended_quantity,
                trend_category: recommendation.category,
                trend_reason: recommendation.reason
            });

            if (response.success) {
                toast({
                    title: "🤖 AI Order Started",
                    description: `AI agent started negotiating for ${recommendation.product_name} (${recommendation.recommended_quantity} units)`,
                });

                onOrderTriggered?.();
            }
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to start AI negotiation for suggested product",
                variant: "destructive"
            });
        } finally {
            setOrderingStates(prev => ({ ...prev, [recommendation.product_id]: false }));
        }
    };

    const getCategoryIcon = (category: string) => {
        switch (category) {
            case 'festival':
                return <Sparkles className="h-4 w-4 text-purple-500" />;
            case 'school_season':
                return <Calendar className="h-4 w-4 text-blue-500" />;
            case 'exam_period':
                return <Target className="h-4 w-4 text-red-500" />;
            case 'weather_seasonal':
                return <TrendingUp className="h-4 w-4 text-green-500" />;
            case 'business_quarterly':
                return <Package className="h-4 w-4 text-orange-500" />;
            default:
                return <Brain className="h-4 w-4 text-gray-500" />;
        }
    };

    const getUrgencyColor = (urgency: string) => {
        switch (urgency) {
            case 'critical':
                return 'bg-red-100 text-red-800 border-red-300';
            case 'high':
                return 'bg-orange-100 text-orange-800 border-orange-300';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800 border-yellow-300';
            case 'low':
                return 'bg-green-100 text-green-800 border-green-300';
            default:
                return 'bg-gray-100 text-gray-800 border-gray-300';
        }
    };

    const getCategoryLabel = (category: string) => {
        const labels = {
            'festival': 'Festival Season',
            'school_season': 'School Period',
            'exam_period': 'Exam Season',
            'weather_seasonal': 'Seasonal Trend',
            'business_quarterly': 'Business Cycle'
        };
        return labels[category as keyof typeof labels] || category;
    };

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5 text-blue-600" />
                        AI Smart Suggestions
                    </CardTitle>
                    <CardDescription>Analyzing trends and patterns...</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-blue-600" />
                    AI Smart Suggestions
                    <Badge variant="outline" className="ml-auto">
                        {recommendations.length} suggestions
                    </Badge>
                </CardTitle>
                <CardDescription>
                    AI-powered recommendations based on festivals, school seasons, exams, and trends
                </CardDescription>
            </CardHeader>
            <CardContent>
                {recommendations.length > 0 ? (
                    <div className="space-y-4">
                        {recommendations.slice(0, 6).map((recommendation) => (
                            <div
                                key={recommendation.product_id}
                                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        {/* Header */}
                                        <div className="flex items-center gap-2 mb-2">
                                            {getCategoryIcon(recommendation.category)}
                                            <h4 className="font-semibold text-lg">{recommendation.product_name}</h4>
                                            <Badge variant="outline" className="text-xs">
                                                {getCategoryLabel(recommendation.category)}
                                            </Badge>
                                        </div>

                                        {/* Trend Information */}
                                        <div className="mb-3">
                                            <div className="flex items-center gap-2 mb-1">
                                                <TrendingUp className="h-4 w-4 text-blue-500" />
                                                <span className="font-medium text-blue-700">{recommendation.trend_name}</span>
                                            </div>
                                            <p className="text-sm text-gray-600 leading-relaxed">
                                                {recommendation.reason}
                                            </p>
                                        </div>

                                        {/* Metrics */}
                                        <div className="grid grid-cols-3 gap-4 mb-3">
                                            <div className="text-center">
                                                <div className="text-lg font-bold text-blue-600">
                                                    {recommendation.recommended_quantity}
                                                </div>
                                                <div className="text-xs text-gray-500">Recommended Qty</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-lg font-bold text-green-600">
                                                    {(recommendation.confidence * 100).toFixed(0)}%
                                                </div>
                                                <div className="text-xs text-gray-500">AI Confidence</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-lg font-bold text-purple-600">
                                                    {recommendation.estimated_demand_increase}
                                                </div>
                                                <div className="text-xs text-gray-500">Demand Increase</div>
                                            </div>
                                        </div>

                                        {/* Priority and Urgency */}
                                        <div className="flex items-center gap-2 mb-3">
                                            <Badge className={getUrgencyColor(recommendation.urgency)}>
                                                {recommendation.urgency.toUpperCase()} PRIORITY
                                            </Badge>
                                            <div className="flex items-center gap-1">
                                                <Star className="h-3 w-3 text-yellow-500" />
                                                <span className="text-xs text-gray-600">
                                                    Priority: {recommendation.priority}/10
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Action Button */}
                                    <div className="ml-4">
                                        <Button
                                            onClick={() => handleAutoOrder(recommendation)}
                                            disabled={orderingStates[recommendation.product_id]}
                                            className="flex items-center gap-2"
                                            size="sm"
                                        >
                                            {orderingStates[recommendation.product_id] ? (
                                                <>
                                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                                    Starting...
                                                </>
                                            ) : (
                                                <>
                                                    <Zap className="h-4 w-4" />
                                                    Auto Order
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {recommendations.length > 6 && (
                            <Alert>
                                <AlertTriangle className="h-4 w-4" />
                                <AlertDescription>
                                    <strong>{recommendations.length - 6} more suggestions available.</strong>
                                    {" "}Showing top 6 high-priority recommendations.
                                </AlertDescription>
                            </Alert>
                        )}
                    </div>
                ) : (
                    <div className="text-center py-8">
                        <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-4" />
                        <p className="text-gray-500 mb-2">No urgent trend suggestions at the moment</p>
                        <p className="text-sm text-gray-400">
                            AI is monitoring seasonal patterns, festivals, and school cycles for recommendations
                        </p>
                    </div>
                )}

                {/* Refresh Info */}
                <div className="mt-4 pt-4 border-t">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Last updated: {new Date().toLocaleTimeString()}
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={fetchRecommendations}
                            disabled={loading}
                        >
                            Refresh Suggestions
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}