// API Fallback Service - Provides mock data when backend endpoints return 404
export class APIFallbackService {
    static getMockItems() {
        return [
            {
                id: 1,
                name: "A4 Paper",
                category: "paper",
                current_stock: 150,
                minimum_stock: 50,
                maximum_stock: 500,
                unit_price: 8.50,
                supplier_id: 1,
                status: "in_stock",
                last_updated: new Date().toISOString(),
                description: "High-quality A4 printing paper"
            },
            {
                id: 2,
                name: "Ballpoint Pens (Black)",
                category: "writing",
                current_stock: 25,
                minimum_stock: 30,
                maximum_stock: 200,
                unit_price: 1.25,
                supplier_id: 2,
                status: "low_stock",
                last_updated: new Date().toISOString(),
                description: "Professional black ballpoint pens"
            },
            {
                id: 3,
                name: "Sticky Notes",
                category: "office",
                current_stock: 80,
                minimum_stock: 20,
                maximum_stock: 150,
                unit_price: 3.75,
                supplier_id: 1,
                status: "in_stock",
                last_updated: new Date().toISOString(),
                description: "3x3 inch yellow sticky notes"
            }
        ];
    }

    static getMockAgentDecisions() {
        return [
            {
                id: 1,
                decision_type: "reorder",
                item_id: 2,
                reasoning: "Ballpoint pens below minimum stock threshold. Auto-reorder triggered.",
                confidence_score: 0.95,
                is_executed: true,
                created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
                execution_result: "Order placed with supplier"
            },
            {
                id: 2,
                decision_type: "alert",
                item_id: 1,
                reasoning: "High usage pattern detected for A4 Paper. Consider increasing stock levels.",
                confidence_score: 0.87,
                is_executed: false,
                created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
                execution_result: null
            },
            {
                id: 3,
                decision_type: "optimization",
                item_id: 3,
                reasoning: "Sticky notes showing seasonal demand pattern. Adjusting reorder points.",
                confidence_score: 0.92,
                is_executed: true,
                created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
                execution_result: "Reorder points updated"
            }
        ];
    }

    static getMockAgentInsights() {
        return {
            insights: {
                recommendations: [
                    {
                        id: 1,
                        type: "cost_optimization",
                        title: "Bulk Purchase Opportunity",
                        description: "Consider bulk ordering A4 paper to reduce unit costs by 15%",
                        priority: "medium",
                        potential_savings: 127.50,
                        category: "cost"
                    },
                    {
                        id: 2,
                        type: "stock_optimization",
                        title: "Reorder Point Adjustment",
                        description: "Ballpoint pens reorder point should be increased to 40 units based on usage patterns",
                        priority: "high",
                        potential_savings: null,
                        category: "efficiency"
                    },
                    {
                        id: 3,
                        type: "supplier_recommendation",
                        title: "Alternative Supplier",
                        description: "New supplier offers 10% better pricing on office supplies with same quality",
                        priority: "low",
                        potential_savings: 89.25,
                        category: "cost"
                    }
                ]
            }
        };
    }

    static getMockAgentPerformance() {
        return {
            total_decisions: 47,
            success_rate: 94.5,
            performance_score: 96,
            cost_savings: 1250.75,
            efficiency_improvements: 23.5
        };
    }

    static getMockSystemHealth() {
        return {
            agent_status: "active",
            database_status: "connected",
            ai_model_status: "operational",
            last_health_check: new Date().toISOString(),
            uptime_percentage: 99.8
        };
    }

    static getMockActiveWorkflows() {
        return [
            {
                id: "wf_001",
                type: "stock_analysis",
                status: "running",
                started_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 min ago
                current_step: 3,
                total_steps: 6,
                description: "Analyzing current stock levels and usage patterns"
            },
            {
                id: "wf_002",
                type: "supplier_evaluation",
                status: "running",
                started_at: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 min ago
                current_step: 2,
                total_steps: 4,
                description: "Evaluating supplier performance and pricing"
            }
        ];
    }

    static getMockSuppliers() {
        return [
            {
                id: 1,
                name: "Office Plus Supply Co.",
                contact_email: "orders@officeplus.com",
                contact_phone: "+1-555-0123",
                address: "123 Business Ave, Commerce City, CA 90210",
                status: "active",
                rating: 4.5,
                last_order_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
                created_at: new Date().toISOString()
            },
            {
                id: 2,
                name: "Premium Stationery Ltd.",
                contact_email: "sales@premiumstation.com",
                contact_phone: "+1-555-0456",
                address: "456 Supply Street, Trade Town, NY 10001",
                status: "active",
                rating: 4.2,
                last_order_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
                created_at: new Date().toISOString()
            }
        ];
    }

    static getMockTransactions() {
        return [
            {
                id: 1,
                type: "purchase",
                amount: 425.75,
                item_id: 1,
                supplier_id: 1,
                quantity: 50,
                date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
                status: "completed",
                description: "A4 Paper restock order"
            },
            {
                id: 2,
                type: "usage",
                amount: -156.25,
                item_id: 2,
                quantity: -125,
                date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
                status: "completed",
                description: "Office supplies distribution"
            }
        ];
    }

    static getMockAnalytics() {
        return {
            total_value: 15750.50,
            total_items: 3,
            low_stock_alerts: 1,
            pending_orders: 2,
            monthly_usage: {
                current: 1250.75,
                previous: 1180.25,
                change_percent: 5.97
            },
            top_categories: [
                { name: "paper", value: 8500.00, percentage: 54.0 },
                { name: "writing", value: 4200.50, percentage: 26.7 },
                { name: "office", value: 3050.00, percentage: 19.4 }
            ]
        };
    }

    // Main method to handle API calls with fallbacks
    static async handleAPICall<T>(
        apiCall: () => Promise<T>,
        fallbackData: T,
        endpoint: string
    ): Promise<T> {
        try {
            const result = await apiCall();
            return result;
        } catch (error: any) {
            // Check if it's a 404 error or network error
            if (error?.response?.status === 404 || error?.code === 'ECONNREFUSED' || error?.message?.includes('404')) {
                console.warn(`API endpoint ${endpoint} not available, using fallback data`);
                return fallbackData;
            }
            // Re-throw other errors
            throw error;
        }
    }
}