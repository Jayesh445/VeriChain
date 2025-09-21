import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API Base Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for adding auth tokens (if needed)
apiClient.interceptors.request.use(
    (config) => {
        // Add auth token if available
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);// Types for API responses
export interface InventoryItem {
    id: number;
    sku: string;
    name: string;
    category: string;
    brand: string | null;
    unit: string | null;
    unit_cost: number;
    current_stock: number;
    reorder_level: number;
    max_stock_level: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface InventorySummary {
    total_items: number;
    total_value: number;
    low_stock_count: number;
    out_of_stock_count: number;
    categories: Record<string, number>;
}

export interface AgentInsight {
    id: number;
    type: string;
    item_id?: number;
    vendor_id?: number;
    reasoning: string;
    confidence: number;
    severity?: string;
    created_at: string;
    data: any;
}

export interface AgentDecision {
    id: number;
    decision_type: string;
    item_id?: number;
    vendor_id?: number;
    reasoning: string;
    confidence_score: number;
    is_executed: boolean;
    created_at: string;
    decision_data: any;
}

export interface Vendor {
    id: number;
    name: string;
    contact_person: string;
    email: string;
    phone: string;
    address: string;
    rating: number;
    is_active: boolean;
    created_at: string;
}

export interface SalesRecord {
    id: number;
    item_id: number;
    quantity_sold: number;
    unit_price: number;
    total_amount: number;
    customer_type: string;
    department: string;
    sale_date: string;
}

export interface Order {
    id: number;
    vendor_id: number;
    order_number: string;
    status: string;
    priority: string;
    total_amount: number;
    order_date: string;
    expected_delivery_date?: string;
    actual_delivery_date?: string;
    notes?: string;
}

export interface DashboardData {
    scm?: any;
    finance?: any;
    overview?: any;
}

// API Service Class
export class VeriChainAPI {
    // Health Check
    static async healthCheck(): Promise<any> {
        const response = await apiClient.get('/health');
        return response.data;
    }

    // Agent Operations
    static async triggerAgentAnalysis(triggerType: string = 'manual', parameters?: any): Promise<any> {
        const response = await apiClient.post('/api/agent/analyze', {
            trigger_type: triggerType,
            parameters: parameters
        });
        return response.data;
    }

    static async getAgentInsights(role: string = 'admin', limit: number = 10): Promise<any> {
        const response = await apiClient.get(`/api/agent/insights?role=${role}&limit=${limit}`);
        return response.data;
    } static async getRecentAgentDecisions(limit: number = 20): Promise<AgentDecision[]> {
        const response = await apiClient.get(`/api/agent/decisions/recent?limit=${limit}`);
        return response.data;
    } static async getAgentPerformance(): Promise<any> {
        const response = await apiClient.get('/api/agent/performance/summary');
        return response.data;
    } static async getWorkflowStatus(workflowId: string): Promise<any> {
        const response = await apiClient.get(`/api/agent/workflow/${workflowId}/status`);
        return response.data;
    }

    // Inventory Operations
    static async getInventoryItems(params?: {
        skip?: number;
        limit?: number;
        category?: string;
        low_stock_only?: boolean;
    }): Promise<InventoryItem[]> {
        const queryParams = new URLSearchParams();
        if (params?.skip) queryParams.append('skip', params.skip.toString());
        if (params?.limit) queryParams.append('limit', params.limit.toString());
        if (params?.category) queryParams.append('category', params.category);
        if (params?.low_stock_only) queryParams.append('low_stock_only', 'true');

        const response = await apiClient.get(`/api/inventory/items?${queryParams}`);
        return response.data;
    } static async getInventoryItem(itemId: number): Promise<InventoryItem> {
        const response = await apiClient.get(`/api/inventory/items/${itemId}`);
        return response.data;
    } static async getSystemHealth(): Promise<any> {
        const response = await apiClient.get('/api/monitoring/system/health');
        return response.data;
    } static async getActiveWorkflows(): Promise<any> {
        const response = await apiClient.get('/api/monitoring/workflows/active');
        return response.data;
    } static async getInventorySummary(): Promise<any> {
        const response = await apiClient.get('/api/inventory/summary');
        return response.data;
    }

    static async getInventoryAlerts(): Promise<any> {
        const response = await apiClient.get('/api/inventory/alerts');
        return response.data;
    }

    static async updateStock(itemId: number, data: {
        quantity: number;
        reason: string;
        updated_by: string;
    }): Promise<any> {
        const response = await apiClient.post(`/api/inventory/items/${itemId}/stock/update`, data);
        return response.data;
    }

    static async createInventoryItem(data: Partial<InventoryItem>): Promise<InventoryItem> {
        const response = await apiClient.post('/api/inventory/items', data);
        return response.data;
    }

    static async updateInventoryItem(itemId: number, data: Partial<InventoryItem>): Promise<InventoryItem> {
        const response = await apiClient.put(`/api/inventory/items/${itemId}`, data);
        return response.data;
    }

    static async deleteInventoryItem(itemId: number): Promise<void> {
        await apiClient.delete(`/api/inventory/items/${itemId}`);
    }

    // Dashboard Operations
    static async getSCMDashboard(): Promise<any> {
        const response = await apiClient.get('/api/dashboard/scm');
        return response.data;
    }

    static async getFinanceDashboard(): Promise<any> {
        const response = await apiClient.get('/api/dashboard/finance');
        return response.data;
    }

    static async getOverviewDashboard(): Promise<any> {
        const response = await apiClient.get('/api/dashboard/overview');
        return response.data;
    }

    static async getActiveAlerts(): Promise<any> {
        const response = await apiClient.get('/api/monitoring/alerts/active');
        return response.data;
    }

    // Sales Operations
    static async recordSale(data: Partial<SalesRecord>): Promise<SalesRecord> {
        const response = await apiClient.post('/api/sales/record', data);
        return response.data;
    }

    static async getSalesAnalytics(days: number = 30): Promise<any> {
        const response = await apiClient.get(`/api/sales/analytics?days=${days}`);
        return response.data;
    }

    // Vendor Operations
    static async getVendors(): Promise<Vendor[]> {
        const response = await apiClient.get('/api/vendors');
        return response.data;
    }

    static async createVendor(data: Partial<Vendor>): Promise<Vendor> {
        const response = await apiClient.post('/api/vendors', data);
        return response.data;
    }

    static async updateVendor(vendorId: number, data: Partial<Vendor>): Promise<Vendor> {
        const response = await apiClient.put(`/api/vendors/${vendorId}`, data);
        return response.data;
    }

    static async getVendorPerformance(vendorId: number): Promise<any> {
        const response = await apiClient.get(`/api/vendors/${vendorId}/performance`);
        return response.data;
    }

    // Order Operations
    static async getOrders(status?: string): Promise<Order[]> {
        const url = status ? `/api/orders?status=${status}` : '/api/orders';
        const response = await apiClient.get(url);
        return response.data;
    }

    static async createOrder(data: {
        vendor_id: number;
        order_items: Array<{
            item_id: number;
            quantity: number;
            unit_price: number;
        }>;
        priority: string;
        notes?: string;
    }): Promise<Order> {
        const response = await apiClient.post('/api/orders', data);
        return response.data;
    }

    static async updateOrderStatus(orderId: number, status: string): Promise<Order> {
        const response = await apiClient.patch(`/api/orders/${orderId}/status`, { status });
        return response.data;
    }
}

export default VeriChainAPI;