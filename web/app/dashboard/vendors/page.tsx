"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
    Users,
    Star,
    TrendingUp,
    TrendingDown,
    Plus,
    Search,
    Filter,
    Mail,
    Phone,
    MapPin,
    Calendar,
    DollarSign,
    Clock,
    Edit,
    MoreHorizontal,
    MessageCircle
} from "lucide-react";
import VeriChainAPI from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import VendorNegotiation from "./negotiation";

interface Vendor {
    id: number;
    name: string;
    email: string;
    phone: string;
    address: string;
    category: string;
    status: 'active' | 'inactive' | 'pending';
    rating: number;
    totalOrders: number;
    totalSpend: number;
    lastOrderDate: string;
    onTimeDeliveryRate: number;
    qualityScore: number;
    responseTime: number; // hours
    contractStartDate: string;
    contractEndDate: string;
    paymentTerms: string;
    notes?: string;
}

interface VendorPerformance {
    vendorId: number;
    month: string;
    ordersCompleted: number;
    avgDeliveryTime: number;
    qualityIssues: number;
    customerSatisfaction: number;
}

export default function VendorManagement() {
    const [vendors, setVendors] = useState<Vendor[]>([]);
    const [performance, setPerformance] = useState<VendorPerformance[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");
    const [categoryFilter, setCategoryFilter] = useState("all");
    const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
    const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
    const { toast } = useToast();

    // Form state for adding/editing vendors
    const [vendorForm, setVendorForm] = useState({
        name: "",
        email: "",
        phone: "",
        address: "",
        category: "",
        paymentTerms: "",
        contractStartDate: "",
        contractEndDate: "",
        notes: ""
    });

    const fetchVendors = async () => {
        try {
            setLoading(true);
            // Since we don't have specific vendor endpoints, we'll use mock data
            const mockVendors: Vendor[] = [
                {
                    id: 1,
                    name: "Office Supplies Co.",
                    email: "contact@officesupplies.com",
                    phone: "+1-555-0101",
                    address: "123 Business Ave, City, State 12345",
                    category: "Office Supplies",
                    status: "active",
                    rating: 4.5,
                    totalOrders: 125,
                    totalSpend: 45000,
                    lastOrderDate: "2024-01-15",
                    onTimeDeliveryRate: 92,
                    qualityScore: 88,
                    responseTime: 2,
                    contractStartDate: "2023-01-01",
                    contractEndDate: "2024-12-31",
                    paymentTerms: "Net 30"
                },
                {
                    id: 2,
                    name: "Premium Stationery Ltd.",
                    email: "sales@premiumstationery.com",
                    phone: "+1-555-0102",
                    address: "456 Supply Street, City, State 12346",
                    category: "Premium Stationery",
                    status: "active",
                    rating: 4.8,
                    totalOrders: 89,
                    totalSpend: 62000,
                    lastOrderDate: "2024-01-18",
                    onTimeDeliveryRate: 96,
                    qualityScore: 94,
                    responseTime: 1,
                    contractStartDate: "2023-06-01",
                    contractEndDate: "2025-05-31",
                    paymentTerms: "Net 15"
                },
                {
                    id: 3,
                    name: "Budget Office Mart",
                    email: "orders@budgetoffice.com",
                    phone: "+1-555-0103",
                    address: "789 Economy Blvd, City, State 12347",
                    category: "Budget Supplies",
                    status: "active",
                    rating: 3.8,
                    totalOrders: 203,
                    totalSpend: 28000,
                    lastOrderDate: "2024-01-20",
                    onTimeDeliveryRate: 78,
                    qualityScore: 75,
                    responseTime: 4,
                    contractStartDate: "2023-03-01",
                    contractEndDate: "2024-02-29",
                    paymentTerms: "Net 45"
                },
                {
                    id: 4,
                    name: "Tech Supplies Pro",
                    email: "info@techsuppliespro.com",
                    phone: "+1-555-0104",
                    address: "321 Technology Way, City, State 12348",
                    category: "Technology",
                    status: "pending",
                    rating: 0,
                    totalOrders: 0,
                    totalSpend: 0,
                    lastOrderDate: "",
                    onTimeDeliveryRate: 0,
                    qualityScore: 0,
                    responseTime: 0,
                    contractStartDate: "",
                    contractEndDate: "",
                    paymentTerms: "Net 30"
                }
            ];

            setVendors(mockVendors);
        } catch (error) {
            console.error('Failed to fetch vendors:', error);
            toast({
                title: "Error",
                description: "Failed to load vendor data",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const handleAddVendor = async () => {
        try {
            // In a real app, this would call the API
            const newVendor: Vendor = {
                id: Date.now(),
                ...vendorForm,
                status: 'pending',
                rating: 0,
                totalOrders: 0,
                totalSpend: 0,
                lastOrderDate: "",
                onTimeDeliveryRate: 0,
                qualityScore: 0,
                responseTime: 0
            };

            setVendors(prev => [...prev, newVendor]);
            setIsAddDialogOpen(false);
            setVendorForm({
                name: "",
                email: "",
                phone: "",
                address: "",
                category: "",
                paymentTerms: "",
                contractStartDate: "",
                contractEndDate: "",
                notes: ""
            });

            toast({
                title: "Success",
                description: "Vendor added successfully"
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to add vendor",
                variant: "destructive"
            });
        }
    };

    const handleEditVendor = async () => {
        try {
            if (!selectedVendor) return;

            const updatedVendor = {
                ...selectedVendor,
                ...vendorForm
            };

            setVendors(prev =>
                prev.map(v => v.id === selectedVendor.id ? updatedVendor : v)
            );
            setIsEditDialogOpen(false);
            setSelectedVendor(null);

            toast({
                title: "Success",
                description: "Vendor updated successfully"
            });
        } catch (error) {
            toast({
                title: "Error",
                description: "Failed to update vendor",
                variant: "destructive"
            });
        }
    };

    const openEditDialog = (vendor: Vendor) => {
        setSelectedVendor(vendor);
        setVendorForm({
            name: vendor.name,
            email: vendor.email,
            phone: vendor.phone,
            address: vendor.address,
            category: vendor.category,
            paymentTerms: vendor.paymentTerms,
            contractStartDate: vendor.contractStartDate,
            contractEndDate: vendor.contractEndDate,
            notes: vendor.notes || ""
        });
        setIsEditDialogOpen(true);
    };

    const filteredVendors = vendors.filter(vendor => {
        const matchesSearch = vendor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            vendor.email.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === "all" || vendor.status === statusFilter;
        const matchesCategory = categoryFilter === "all" || vendor.category === categoryFilter;
        return matchesSearch && matchesStatus && matchesCategory;
    });

    const categories = Array.from(new Set(vendors.map(v => v.category)));

    useEffect(() => {
        fetchVendors();
    }, []);

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
                    <h1 className="text-3xl font-bold">Vendor Management</h1>
                    <p className="text-gray-600">Manage suppliers, track performance, and negotiate contracts</p>
                </div>
                <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                    <DialogTrigger asChild>
                        <Button className="bg-blue-600 hover:bg-blue-700">
                            <Plus className="h-4 w-4 mr-2" />
                            Add Vendor
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                        <DialogHeader>
                            <DialogTitle>Add New Vendor</DialogTitle>
                            <DialogDescription>
                                Enter vendor information to add them to your supplier network.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                            <div>
                                <Label htmlFor="name">Vendor Name</Label>
                                <Input
                                    id="name"
                                    value={vendorForm.name}
                                    onChange={(e) => setVendorForm(prev => ({ ...prev, name: e.target.value }))}
                                    placeholder="Enter vendor name"
                                />
                            </div>
                            <div>
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    value={vendorForm.email}
                                    onChange={(e) => setVendorForm(prev => ({ ...prev, email: e.target.value }))}
                                    placeholder="Enter email address"
                                />
                            </div>
                            <div>
                                <Label htmlFor="phone">Phone</Label>
                                <Input
                                    id="phone"
                                    value={vendorForm.phone}
                                    onChange={(e) => setVendorForm(prev => ({ ...prev, phone: e.target.value }))}
                                    placeholder="Enter phone number"
                                />
                            </div>
                            <div>
                                <Label htmlFor="category">Category</Label>
                                <Select value={vendorForm.category} onValueChange={(value) => setVendorForm(prev => ({ ...prev, category: value }))}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select category" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Office Supplies">Office Supplies</SelectItem>
                                        <SelectItem value="Premium Stationery">Premium Stationery</SelectItem>
                                        <SelectItem value="Budget Supplies">Budget Supplies</SelectItem>
                                        <SelectItem value="Technology">Technology</SelectItem>
                                        <SelectItem value="Other">Other</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div>
                                <Label htmlFor="address">Address</Label>
                                <Textarea
                                    id="address"
                                    value={vendorForm.address}
                                    onChange={(e) => setVendorForm(prev => ({ ...prev, address: e.target.value }))}
                                    placeholder="Enter full address"
                                />
                            </div>
                        </div>
                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleAddVendor}>Add Vendor</Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>

            {/* Main Content with Tabs */}
            <Tabs defaultValue="vendors" className="space-y-6">
                <TabsList>
                    <TabsTrigger value="vendors" className="flex items-center space-x-2">
                        <Users className="h-4 w-4" />
                        <span>Vendor Directory</span>
                    </TabsTrigger>
                    <TabsTrigger value="negotiations" className="flex items-center space-x-2">
                        <MessageCircle className="h-4 w-4" />
                        <span>AI Negotiations</span>
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="vendors" className="space-y-6">
                    {/* Performance Summary */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Vendors</CardTitle>
                                <Users className="h-4 w-4 text-blue-600" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-blue-600">{vendors.length}</div>
                                <p className="text-xs text-muted-foreground">
                                    {vendors.filter(v => v.status === 'active').length} active
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Avg Rating</CardTitle>
                                <Star className="h-4 w-4 text-yellow-600" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-yellow-600">
                                    {(vendors.filter(v => v.rating > 0).reduce((sum, v) => sum + v.rating, 0) / vendors.filter(v => v.rating > 0).length).toFixed(1)}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Supplier performance
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Spend</CardTitle>
                                <DollarSign className="h-4 w-4 text-green-600" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-green-600">
                                    ${vendors.reduce((sum, v) => sum + v.totalSpend, 0).toLocaleString()}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    This year
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">On-Time Delivery</CardTitle>
                                <Clock className="h-4 w-4 text-purple-600" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold text-purple-600">
                                    {(vendors.filter(v => v.onTimeDeliveryRate > 0).reduce((sum, v) => sum + v.onTimeDeliveryRate, 0) / vendors.filter(v => v.onTimeDeliveryRate > 0).length).toFixed(0)}%
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Average delivery rate
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Filters and Search */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Vendor Directory</CardTitle>
                            <CardDescription>Search and filter your vendor network</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                                <div className="flex-1">
                                    <div className="relative">
                                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                                        <Input
                                            placeholder="Search vendors..."
                                            value={searchTerm}
                                            onChange={(e) => setSearchTerm(e.target.value)}
                                            className="pl-10"
                                        />
                                    </div>
                                </div>
                                <Select value={statusFilter} onValueChange={setStatusFilter}>
                                    <SelectTrigger className="w-32">
                                        <SelectValue placeholder="Status" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="all">All Status</SelectItem>
                                        <SelectItem value="active">Active</SelectItem>
                                        <SelectItem value="pending">Pending</SelectItem>
                                        <SelectItem value="inactive">Inactive</SelectItem>
                                    </SelectContent>
                                </Select>
                                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                                    <SelectTrigger className="w-40">
                                        <SelectValue placeholder="Category" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="all">All Categories</SelectItem>
                                        {categories.map(category => (
                                            <SelectItem key={category} value={category}>{category}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Vendor Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {filteredVendors.map((vendor) => (
                                    <Card key={vendor.id} className="hover:shadow-lg transition-shadow">
                                        <CardHeader className="pb-3">
                                            <div className="flex justify-between items-start">
                                                <div>
                                                    <CardTitle className="text-lg">{vendor.name}</CardTitle>
                                                    <CardDescription className="mt-1">{vendor.category}</CardDescription>
                                                </div>
                                                <div className="flex items-center space-x-2">
                                                    <Badge variant={
                                                        vendor.status === 'active' ? 'default' :
                                                            vendor.status === 'pending' ? 'secondary' : 'destructive'
                                                    }>
                                                        {vendor.status}
                                                    </Badge>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => openEditDialog(vendor)}
                                                    >
                                                        <Edit className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            {/* Contact Info */}
                                            <div className="space-y-2">
                                                <div className="flex items-center text-sm text-gray-600">
                                                    <Mail className="h-4 w-4 mr-2" />
                                                    {vendor.email}
                                                </div>
                                                <div className="flex items-center text-sm text-gray-600">
                                                    <Phone className="h-4 w-4 mr-2" />
                                                    {vendor.phone}
                                                </div>
                                                <div className="flex items-center text-sm text-gray-600">
                                                    <MapPin className="h-4 w-4 mr-2" />
                                                    {vendor.address.split(',')[0]}
                                                </div>
                                            </div>

                                            {/* Performance Metrics */}
                                            {vendor.status === 'active' && (
                                                <div className="space-y-3">
                                                    <div className="flex justify-between items-center">
                                                        <span className="text-sm text-gray-600">Rating</span>
                                                        <div className="flex items-center">
                                                            <Star className="h-4 w-4 text-yellow-500 mr-1" />
                                                            <span className="text-sm font-medium">{vendor.rating}</span>
                                                        </div>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between text-sm">
                                                            <span>On-time Delivery</span>
                                                            <span>{vendor.onTimeDeliveryRate}%</span>
                                                        </div>
                                                        <Progress value={vendor.onTimeDeliveryRate} />
                                                    </div>
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between text-sm">
                                                            <span>Quality Score</span>
                                                            <span>{vendor.qualityScore}%</span>
                                                        </div>
                                                        <Progress value={vendor.qualityScore} />
                                                    </div>
                                                    <div className="flex justify-between items-center text-sm">
                                                        <span className="text-gray-600">Total Orders</span>
                                                        <span className="font-medium">{vendor.totalOrders}</span>
                                                    </div>
                                                    <div className="flex justify-between items-center text-sm">
                                                        <span className="text-gray-600">Total Spend</span>
                                                        <span className="font-medium">${vendor.totalSpend.toLocaleString()}</span>
                                                    </div>
                                                </div>
                                            )}
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Edit Vendor Dialog */}
                    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
                        <DialogContent className="max-w-md">
                            <DialogHeader>
                                <DialogTitle>Edit Vendor</DialogTitle>
                                <DialogDescription>
                                    Update vendor information and details.
                                </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                                <div>
                                    <Label htmlFor="edit-name">Vendor Name</Label>
                                    <Input
                                        id="edit-name"
                                        value={vendorForm.name}
                                        onChange={(e) => setVendorForm(prev => ({ ...prev, name: e.target.value }))}
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="edit-email">Email</Label>
                                    <Input
                                        id="edit-email"
                                        type="email"
                                        value={vendorForm.email}
                                        onChange={(e) => setVendorForm(prev => ({ ...prev, email: e.target.value }))}
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="edit-phone">Phone</Label>
                                    <Input
                                        id="edit-phone"
                                        value={vendorForm.phone}
                                        onChange={(e) => setVendorForm(prev => ({ ...prev, phone: e.target.value }))}
                                    />
                                </div>
                                <div>
                                    <Label htmlFor="edit-category">Category</Label>
                                    <Select value={vendorForm.category} onValueChange={(value) => setVendorForm(prev => ({ ...prev, category: value }))}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="Office Supplies">Office Supplies</SelectItem>
                                            <SelectItem value="Premium Stationery">Premium Stationery</SelectItem>
                                            <SelectItem value="Budget Supplies">Budget Supplies</SelectItem>
                                            <SelectItem value="Technology">Technology</SelectItem>
                                            <SelectItem value="Other">Other</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div>
                                    <Label htmlFor="edit-address">Address</Label>
                                    <Textarea
                                        id="edit-address"
                                        value={vendorForm.address}
                                        onChange={(e) => setVendorForm(prev => ({ ...prev, address: e.target.value }))}
                                    />
                                </div>
                            </div>
                            <DialogFooter>
                                <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                                    Cancel
                                </Button>
                                <Button onClick={handleEditVendor}>Save Changes</Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </TabsContent>

                <TabsContent value="negotiations">
                    <VendorNegotiation />
                </TabsContent>
            </Tabs>
        </div>
    );
}