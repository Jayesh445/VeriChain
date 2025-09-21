"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";

import { ArrowRight, Play, Sparkles, TrendingUp, Shield } from "lucide-react";

export function HeroSection() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const router = useRouter();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background with gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-secondary/5" />

      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse delay-500" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left column - Content */}
          <div className="space-y-8">
            <div className="space-y-4">
              <Badge variant="secondary" className="w-fit">
                <Sparkles className="w-3 h-3 mr-1" />
                AI-Powered Supply Chain
              </Badge>

              <h1 className="font-display text-5xl lg:text-7xl font-bold text-balance leading-tight">
                Smart AI Agent for{" "}
                <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  Inventory
                </span>{" "}
                Management
              </h1>

              <p className="text-xl text-muted-foreground text-pretty max-w-2xl">
                Revolutionize your supply chain with autonomous AI that manages
                inventory, tracks orders, and optimizes operations in real-time.
                Powered by blockchain for ultimate trust and transparency.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                size="lg"
                className="group"
                onClick={() => router.push("/auth/signup")}
              >
                Get Started Free
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 pt-8 border-t border-border">
              <div className="text-center">
                <div className="font-display text-2xl font-bold text-primary">
                  99.9%
                </div>
                <div className="text-sm text-muted-foreground">Uptime</div>
              </div>
              <div className="text-center">
                <div className="font-display text-2xl font-bold text-primary">
                  50%
                </div>
                <div className="text-sm text-muted-foreground">
                  Cost Reduction
                </div>
              </div>
              <div className="text-center">
                <div className="font-display text-2xl font-bold text-primary">
                  24/7
                </div>
                <div className="text-sm text-muted-foreground">
                  AI Monitoring
                </div>
              </div>
            </div>
          </div>

          {/* Right column - Visual */}
          <div className="relative">
            <div className="relative mb-8">
              <img
                src="/modern-ai-dashboard-interface-with-supply-chain-an.jpg"
                alt="AI Supply Chain Dashboard"
                className="w-full h-auto rounded-2xl shadow-2xl border border-border"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/20 to-transparent rounded-2xl" />
            </div>

            <div className="relative bg-card rounded-2xl p-8 shadow-2xl border border-border">
              {/* Mock dashboard interface */}
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-lg font-semibold">
                    AI Dashboard
                  </h3>
                  <Badge variant="secondary" className="animate-pulse">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                    Live
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-primary/10 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="w-5 h-5 text-primary" />
                      <span className="text-sm font-medium">Inventory</span>
                    </div>
                    <div className="font-display text-2xl font-bold mt-2">
                      1,247
                    </div>
                    <div className="text-xs text-muted-foreground">
                      +12% this week
                    </div>
                  </div>

                  <div className="bg-secondary/10 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <Shield className="w-5 h-5 text-secondary" />
                      <span className="text-sm font-medium">Orders</span>
                    </div>
                    <div className="font-display text-2xl font-bold mt-2">
                      89
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Processing
                    </div>
                  </div>
                </div>

                {/* Animated chart placeholder */}
                <div className="bg-muted/50 rounded-lg p-4 h-32 flex items-end space-x-2">
                  {[40, 60, 45, 80, 65, 90, 75].map((height, i) => (
                    <div
                      key={i}
                      className="bg-primary/60 rounded-sm flex-1 animate-pulse"
                      style={{
                        height: `${height}%`,
                        animationDelay: `${i * 200}ms`,
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Floating elements */}
            <div className="absolute -top-4 -right-4 w-16 h-16 bg-primary rounded-full flex items-center justify-center shadow-lg animate-bounce">
              <Sparkles className="w-8 h-8 text-primary-foreground" />
            </div>

            <div className="absolute -bottom-4 -left-4 w-12 h-12 bg-secondary rounded-full flex items-center justify-center shadow-lg animate-bounce delay-1000">
              <Shield className="w-6 h-6 text-secondary-foreground" />
            </div>
          </div>
        </div>
      </div>

      {/* Video modal */}
      {isVideoPlaying && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="relative bg-background rounded-lg p-4 max-w-4xl w-full">
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-2 right-2"
              onClick={() => setIsVideoPlaying(false)}
            >
              ×
            </Button>
            <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
              <div className="text-center">
                <Play className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">
                  Demo video would play here
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
