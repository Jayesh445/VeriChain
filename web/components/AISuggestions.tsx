"use client";
import { useEffect, useState } from "react";
import { TrendSuggestion } from "@/lib/api";
import VeriChainAPI from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Sparkles, ShoppingCart } from "lucide-react";

interface AISuggestionsProps {
    onAutoOrder?: (suggestion: TrendSuggestion) => void;
}

export default function AISuggestions({ onAutoOrder }: AISuggestionsProps) {
    const [suggestions, setSuggestions] = useState<TrendSuggestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSuggestions();
    }, []);

    const fetchSuggestions = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await VeriChainAPI.getAISuggestions();
            setSuggestions(data);
        } catch (e) {
            setError("Failed to load AI suggestions.");
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4 text-center">Loading AI suggestions...</div>;
    if (error) return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;
    if (!suggestions.length) return <div className="p-4 text-center text-gray-500">No AI suggestions for this season.</div>;

    return (
        <Card className="mb-6">
            <CardHeader className="flex flex-row items-center gap-2 pb-2">
                <Sparkles className="h-5 w-5 text-blue-500" />
                <CardTitle className="text-lg">AI Suggestions for You</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
                {suggestions.map((s, idx) => (
                    <div key={s.sku + idx} className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-2 last:border-b-0 last:pb-0">
                        <div>
                            <div className="font-semibold">{s.product}</div>
                            <div className="text-xs text-gray-500">{s.reason}</div>
                        </div>
                        <Button
                            className="mt-2 md:mt-0"
                            variant="outline"
                            onClick={() => onAutoOrder?.(s)}
                        >
                            <ShoppingCart className="h-4 w-4 mr-2" />
                            Auto Order
                        </Button>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
}
