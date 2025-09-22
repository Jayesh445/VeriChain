"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    Package,
    Plus,
    Edit,
    Trash2,
    Search,
    Filter,
    RefreshCw,
    AlertTriangle,
    CheckCircle,
    TrendingUp,
    TrendingDown,
    BarChart3,
    Eye
} from "lucide-react";
import VeriChainAPI, { InventoryItem } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import AISuggestions from "@/components/AISuggestions";

const CATEGORIES = [
    "WRITING_INSTRUMENTS",
    "PAPER_PRODUCTS",
    "OFFICE_SUPPLIES",
    "FILING_SUPPLIES",
    "DESK_ACCESSORIES"
];

const CATEGORY_DISPLAY = {
    "WRITING_INSTRUMENTS": "Writing Instruments",
    "PAPER_PRODUCTS": "Paper Products",
    "OFFICE_SUPPLIES": "Office Supplies",
    "FILING_SUPPLIES": "Filing Supplies",
    "DESK_ACCESSORIES": "Desk Accessories"
};

export default function InventoryManagement() {
    const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
    const [filteredItems, setFilteredItems] = useState<InventoryItem[]>([]);
    const [inventorySummary, setInventorySummary] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [showLowStockOnly, setShowLowStockOnly] = useState(false);
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
    const [newItem, setNewItem] = useState({
        name: "",
        description: "",
        category: "",
        current_stock: 0,
        reorder_level: 0,
        max_stock_level: 0,
        unit_cost: 0,
        unit: "",
        vendor_id: 1
    });
    const [stockUpdate, setStockUpdate] = useState({
        quantity: 0,
        reason: "",
        updated_by: "admin"
    });

    const [isReduceStockOpen, setIsReduceStockOpen] = useState(false);
    const [reduceStockItem, setReduceStockItem] = useState<InventoryItem | null>(null);
    const [reduceQuantity, setReduceQuantity] = useState(1);

    const { toast } = useToast();

    // Handler for auto-order from AI suggestions
    const handleAutoOrder = async (suggestion: any) => {
        try {
            // First, get all inventory items to find the suggested item
            const allItems = await VeriChainAPI.getInventoryItems();
            const foundItem = allItems.find((item: any) => item.sku === suggestion.sku || item.name === suggestion.product);

            if (!foundItem) {
                toast({
                    title: "Item Not Found",
                    description: `Could not find ${suggestion.product} in inventory`,
                    variant: "destructive"
                });
                return;
            }

            // Calculate recommended quantity (fill to max stock or default to 100)
            const recommendedQuantity = foundItem.max_stock_level ?
                Math.max(foundItem.max_stock_level - foundItem.current_stock, 50) : 100;

            await VeriChainAPI.startNegotiation({
                item_id: foundItem.id,
                quantity_needed: recommendedQuantity,
                urgency: "medium"
            });

            toast({
                title: "Auto Order Triggered",
                description: `Started AI negotiation for ${suggestion.product} (Qty: ${recommendedQuantity})`,
            });
        } catch (e: any) {
            console.error('Auto order error:', e);
            toast({
                title: "Error",
                description: `Failed to auto order ${suggestion.product}: ${e.message || 'Unknown error'}`,
                variant: "destructive"
            });
        }
    };

    const fetchInventoryData = async () => {
        try {
            setLoading(true);
            const [items, summary] = await Promise.all([
                VeriChainAPI.getInventoryItems({ limit: 100 }),
                VeriChainAPI.getInventorySummary()
            ]);
            setInventoryItems(items);
            setFilteredItems(items);
            setInventorySummary(summary);
        } catch (error) {
            console.error('Failed to fetch inventory data:', error);
            toast({
                title: "Error",
                description: "Failed to load inventory data",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchInventoryData();
    }, []);

    useEffect(() => {
        let filtered = inventoryItems;

        // Search filter
        if (searchTerm) {
            filtered = filtered.filter(item =>
                item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (item.category && item.category.toLowerCase().includes(searchTerm.toLowerCase()))
            );
        }

        // Category filter
        if (selectedCategory !== "all") {
            filtered = filtered.filter(item => item.category === selectedCategory);
        }

        // Low stock filter
        if (showLowStockOnly) {
            filtered = filtered.filter(item => item.current_stock <= item.reorder_level);
        }

        setFilteredItems(filtered);
    }, [inventoryItems, searchTerm, selectedCategory, showLowStockOnly]);

    const handleAddItem = async () => {
        try {
            await VeriChainAPI.createInventoryItem(newItem);
            toast({
                title: "Success",
                description: "Item added successfully",
            });
            setIsAddDialogOpen(false);
            setNewItem({
                name: "",
                description: "",
                category: "",
                current_stock: 0,
                reorder_level: 0,
                max_stock_level: 0,
                unit_cost: 0,
                unit: "",
                vendor_id: 1
            });
            await fetchInventoryData();
        } catch (error) {
            console.error('Failed to add item:', error);
            toast({
                title: "Error",
                description: "Failed to add item",
                variant: "destructive"
            });
        }
    };

    const handleReduceStock = async () => {
        if (!reduceStockItem) return;

        try {
            const response = await VeriChainAPI.updateStock(reduceStockItem.id, {
                quantity: -reduceQuantity, // Use negative quantity for reduction
                reason: `Manual stock reduction - reduced by ${reduceQuantity}`,
                updated_by: "admin"
            });

            let successMessage = `Stock reduced by ${reduceQuantity} units`;

            // Check if auto-negotiation was triggered
            if (response.auto_negotiation?.triggered) {
                successMessage += `. AI negotiation started automatically!`;

                toast({
                    title: "🤖 AI Agent Activated!",
                    description: (
                        <div className="space-y-2">
                            <p>{response.auto_negotiation.message}</p>
                            {response.auto_negotiation.session_id && (
                                <div className="bg-blue-50 p-2 rounded text-sm">
                                    <p className="font-medium text-blue-800">Session Details:</p>
                                    <p className="text-blue-600">
                                        ID: {response.auto_negotiation.session_id?.slice(0, 8)}...
                                    </p>
                                    <a
                                        href="/dashboard/ai-agent"
                                        className="text-blue-700 underline hover:text-blue-900"
                                        onClick={() => {
                                            // Close the current dialog and navigate
                                            setTimeout(() => window.location.href = '/dashboard/ai-agent', 100);
                                        }}
                                    >
                                        → View Live Negotiation
                                    </a>
                                </div>
                            )}
                            <p className="text-xs text-gray-500">
                                Gemini AI is now negotiating with ALL active vendors in real-time
                            </p>
                        </div>
                    ),
                    duration: 10000,
                });

                // Show additional notification for low stock scenarios
                if (reduceStockItem.current_stock - reduceQuantity <= reduceStockItem.reorder_level) {
                    setTimeout(() => {
                        toast({
                            title: "📊 Critical Stock Level Alert",
                            description: (
                                <div className="space-y-2">
                                    <p className="font-medium text-orange-800">
                                        {reduceStockItem.name} is now below reorder level!
                                    </p>
                                    <div className="bg-orange-50 p-2 rounded text-sm">
                                        <p>Current Stock: {reduceStockItem.current_stock - reduceQuantity}</p>
                                        <p>Reorder Level: {reduceStockItem.reorder_level}</p>
                                        <p className="text-orange-600 font-medium mt-1">
                                            🤖 AI Agent is automatically negotiating with vendors
                                        </p>
                                    </div>
                                    <p className="text-xs text-gray-600">
                                        You'll receive an approval request once the best vendor is selected
                                    </p>
                                </div>
                            ),
                            duration: 8000,
                        });
                    }, 3000);
                }
            } else {
                toast({
                    title: "Success",
                    description: successMessage,
                });
            }

            setIsReduceStockOpen(false);
            setReduceStockItem(null);
            setReduceQuantity(1);
            await fetchInventoryData();
        } catch (error) {
            console.error('Failed to reduce stock:', error);
            toast({
                title: "Error",
                description: "Failed to reduce stock",
                variant: "destructive"
            });
        }
    };

    const handleUpdateStock = async () => {
        if (!selectedItem) return;

        try {
            await VeriChainAPI.updateStock(selectedItem.id, stockUpdate);
            toast({
                title: "Success",
                description: "Stock updated successfully",
            });
            setIsUpdateDialogOpen(false);
            setSelectedItem(null);
            setStockUpdate({
                quantity: 0,
                reason: "",
                updated_by: "admin"
            });
            await fetchInventoryData();
        } catch (error) {
            console.error('Failed to update stock:', error);
            toast({
                title: "Error",
                description: "Failed to update stock",
                variant: "destructive"
            });
        }
    };

    const getStockStatus = (item: InventoryItem) => {
        if (item.current_stock === 0) return { status: "out", color: "bg-red-500", text: "Out of Stock" };
        if (item.current_stock <= item.reorder_level) return { status: "low", color: "bg-orange-500", text: "Low Stock" };
        if (item.current_stock >= (item.max_stock_level || 0) * 0.8) return { status: "high", color: "bg-blue-500", text: "High Stock" };
        return { status: "normal", color: "bg-green-500", text: "Normal" };
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
            <AISuggestions onAutoOrder={handleAutoOrder} />
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Inventory Management</h1>
                    <p className="text-gray-600">Manage stationery items and stock levels</p>
                </div>
                <div className="flex space-x-2">
                    <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                        <DialogTrigger asChild>
                            <Button className="bg-blue-600 hover:bg-blue-700">
                                <Plus className="h-4 w-4 mr-2" />
                                Add Item
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-md">
                            <DialogHeader>
                                <DialogTitle>Add New Inventory Item</DialogTitle>
                                <DialogDescription>
                                    Create a new stationery item in the inventory
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="name">Item Name</Label>
                                    <Input
                                        id="name"
                                        value={newItem.name}
                                        onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                                        placeholder="e.g., Blue Ballpoint Pen"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="description">Description</Label>
                                    <Input
                                        id="description"
                                        value={newItem.description}
                                        onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                                        placeholder="Item description"
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="category">Category</Label>
                                    <Select value={newItem.category} onValueChange={(value) => setNewItem({ ...newItem, category: value })}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select category" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {CATEGORIES.map(cat => (
                                                <SelectItem key={cat} value={cat}>
                                                    {CATEGORY_DISPLAY[cat as keyof typeof CATEGORY_DISPLAY]}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="current_stock">Current Stock</Label>
                                        <Input
                                            id="current_stock"
                                            type="number"
                                            value={newItem.current_stock}
                                            onChange={(e) => setNewItem({ ...newItem, current_stock: parseInt(e.target.value) || 0 })}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="reorder_level">Reorder Level</Label>
                                        <Input
                                            id="reorder_level"
                                            type="number"
                                            value={newItem.reorder_level}
                                            onChange={(e) => setNewItem({ ...newItem, reorder_level: parseInt(e.target.value) || 0 })}
                                        />
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label htmlFor="unit_cost">Unit Cost</Label>
                                        <Input
                                            id="unit_cost"
                                            type="number"
                                            step="0.01"
                                            value={newItem.unit_cost}
                                            onChange={(e) => setNewItem({ ...newItem, unit_cost: parseFloat(e.target.value) || 0 })}
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="unit">Unit</Label>
                                        <Input
                                            id="unit"
                                            value={newItem.unit}
                                            onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
                                            placeholder="e.g., piece, box, ream"
                                        />
                                    </div>
                                </div>
                                <Button onClick={handleAddItem} className="w-full">
                                    Add Item
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                    <Button onClick={fetchInventoryData} variant="outline">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Summary Cards */}
            {inventorySummary && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                            <Package className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{inventorySummary.summary?.total_items || 0}</div>
                            <p className="text-xs text-muted-foreground">Active inventory items</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                            <TrendingUp className="h-4 w-4 text-green-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-green-600">
                                ${inventorySummary.summary?.total_value?.toLocaleString() || '0'}
                            </div>
                            <p className="text-xs text-muted-foreground">Current inventory value</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                            <AlertTriangle className="h-4 w-4 text-orange-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-orange-600">
                                {inventorySummary.summary?.low_stock_count || 0}
                            </div>
                            <p className="text-xs text-muted-foreground">Items needing reorder</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Out of Stock</CardTitle>
                            <TrendingDown className="h-4 w-4 text-red-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-red-600">
                                {inventorySummary.summary?.out_of_stock_count || 0}
                            </div>
                            <p className="text-xs text-muted-foreground">Items completely depleted</p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Filters and Search */}
            <Card>
                <CardHeader>
                    <CardTitle>Filter & Search</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col md:flex-row gap-4">
                        <div className="flex-1">
                            <div className="relative">
                                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                <Input
                                    placeholder="Search items by name, SKU, or description..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="pl-10"
                                />
                            </div>
                        </div>
                        <div className="w-48">
                            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                                <SelectTrigger>
                                    <SelectValue placeholder="All Categories" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Categories</SelectItem>
                                    {CATEGORIES.map(cat => (
                                        <SelectItem key={cat} value={cat}>
                                            {CATEGORY_DISPLAY[cat as keyof typeof CATEGORY_DISPLAY]}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <Button
                            variant={showLowStockOnly ? "default" : "outline"}
                            onClick={() => setShowLowStockOnly(!showLowStockOnly)}
                        >
                            <Filter className="h-4 w-4 mr-2" />
                            Low Stock Only
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Inventory Table */}
            <Card>
                <CardHeader>
                    <CardTitle>Inventory Items ({filteredItems.length})</CardTitle>
                    <CardDescription>Manage your stationery inventory</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Item</TableHead>
                                    <TableHead>Category</TableHead>
                                    <TableHead>Stock</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Unit Price</TableHead>
                                    <TableHead>Total Value</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredItems.map((item) => {
                                    const stockStatus = getStockStatus(item);
                                    return (
                                        <TableRow key={item.id}>
                                            <TableCell>
                                                <div>
                                                    <p className="font-medium">{item.name}</p>
                                                    <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <Badge variant="outline">
                                                    {CATEGORY_DISPLAY[item.category as keyof typeof CATEGORY_DISPLAY]}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className="text-sm">
                                                    <p className="font-medium">{item.current_stock} {item.unit}</p>
                                                    <p className="text-gray-500">Reorder at: {item.reorder_level}</p>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center space-x-2">
                                                    <div className={`w-2 h-2 rounded-full ${stockStatus.color}`}></div>
                                                    <span className="text-sm">{stockStatus.text}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell>${item.unit_cost?.toFixed(2) || '0.00'}</TableCell>
                                            <TableCell>${(((item.current_stock || 0) * (item.unit_cost || 0))).toFixed(2)}</TableCell>
                                            <TableCell>
                                                <div className="flex space-x-2">
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => {
                                                            setSelectedItem(item);
                                                            setStockUpdate({
                                                                quantity: item.current_stock,
                                                                reason: "",
                                                                updated_by: "admin"
                                                            });
                                                            setIsUpdateDialogOpen(true);
                                                        }}
                                                    >
                                                        <Edit className="h-4 w-4" />
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        className="text-orange-600 border-orange-600 hover:bg-orange-50"
                                                        onClick={() => {
                                                            setReduceStockItem(item);
                                                            setReduceQuantity(Math.min(5, item.current_stock));
                                                            setIsReduceStockOpen(true);
                                                        }}
                                                        disabled={item.current_stock === 0}
                                                    >
                                                        <TrendingDown className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>

            {/* Stock Update Dialog */}
            <Dialog open={isUpdateDialogOpen} onOpenChange={setIsUpdateDialogOpen}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>Update Stock Level</DialogTitle>
                        <DialogDescription>
                            Update the stock level for {selectedItem?.name}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <div>
                            <Label htmlFor="current">Current Stock</Label>
                            <Input
                                id="current"
                                value={selectedItem?.current_stock || 0}
                                disabled
                                className="bg-gray-100"
                            />
                        </div>
                        <div>
                            <Label htmlFor="new_quantity">New Quantity</Label>
                            <Input
                                id="new_quantity"
                                type="number"
                                value={stockUpdate.quantity}
                                onChange={(e) => setStockUpdate({ ...stockUpdate, quantity: parseInt(e.target.value) || 0 })}
                            />
                        </div>
                        <div>
                            <Label htmlFor="reason">Reason for Update</Label>
                            <Input
                                id="reason"
                                value={stockUpdate.reason}
                                onChange={(e) => setStockUpdate({ ...stockUpdate, reason: e.target.value })}
                                placeholder="e.g., Stock replenishment, Inventory count correction"
                            />
                        </div>
                        <Button onClick={handleUpdateStock} className="w-full">
                            Update Stock
                        </Button>
                    </div>
                </DialogContent>
            </Dialog>

            {/* Reduce Stock Dialog */}
            <Dialog open={isReduceStockOpen} onOpenChange={setIsReduceStockOpen}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>Reduce Stock & Test AI Agent</DialogTitle>
                        <DialogDescription>
                            Reduce stock for {reduceStockItem?.name} to trigger AI negotiation workflow
                        </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                        <Alert>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                                <strong>AI Agent Testing:</strong> If stock goes below reorder level ({reduceStockItem?.reorder_level}),
                                AI agent will automatically start negotiating with vendors. You'll be notified when approval is needed.
                            </AlertDescription>
                        </Alert>
                        <div>
                            <Label htmlFor="current_stock">Current Stock</Label>
                            <Input
                                id="current_stock"
                                value={reduceStockItem?.current_stock || 0}
                                disabled
                                className="bg-gray-100"
                            />
                        </div>
                        <div>
                            <Label htmlFor="reduce_by">Reduce by (units)</Label>
                            <Input
                                id="reduce_by"
                                type="number"
                                min="1"
                                max={reduceStockItem?.current_stock || 0}
                                value={reduceQuantity}
                                onChange={(e) => setReduceQuantity(parseInt(e.target.value) || 1)}
                            />
                        </div>
                        <div>
                            <Label>New Stock Level</Label>
                            <div className="p-2 bg-gray-100 rounded text-center font-medium">
                                {Math.max(0, (reduceStockItem?.current_stock || 0) - reduceQuantity)} units
                            </div>
                        </div>
                        <div className="flex space-x-2">
                            <Button onClick={handleReduceStock} className="flex-1 bg-orange-600 hover:bg-orange-700">
                                Reduce Stock
                            </Button>
                            <Button variant="outline" onClick={() => setIsReduceStockOpen(false)} className="flex-1">
                                Cancel
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}