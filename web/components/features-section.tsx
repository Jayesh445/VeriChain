import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bot, BarChart3, Shield, Zap, Brain, Globe, Lock, Cpu } from "lucide-react"

const features = [
  {
    icon: Bot,
    title: "Autonomous AI Agent",
    description:
      "Self-learning AI that makes intelligent decisions about inventory management without human intervention.",
    badge: "AI-Powered",
  },
  {
    icon: BarChart3,
    title: "Real-time Analytics",
    description: "Get instant insights into your supply chain performance with advanced predictive analytics.",
    badge: "Analytics",
  },
  {
    icon: Shield,
    title: "Blockchain Security",
    description: "Immutable audit trails and smart contracts ensure complete transparency and trust.",
    badge: "Secure",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Process thousands of transactions per second with our optimized infrastructure.",
    badge: "Performance",
  },
  {
    icon: Brain,
    title: "Smart Predictions",
    description: "AI-powered demand forecasting helps prevent stockouts and overstock situations.",
    badge: "Predictive",
  },
  {
    icon: Globe,
    title: "Global Scale",
    description: "Manage supply chains across multiple regions with localized compliance and regulations.",
    badge: "Scalable",
  },
  {
    icon: Lock,
    title: "Enterprise Security",
    description: "Bank-grade encryption and security protocols protect your sensitive business data.",
    badge: "Enterprise",
  },
  {
    icon: Cpu,
    title: "API Integration",
    description: "Seamlessly integrate with existing ERP, CRM, and inventory management systems.",
    badge: "Integration",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <Badge variant="secondary" className="w-fit mx-auto">
            Features
          </Badge>
          <h2 className="font-display text-4xl lg:text-5xl font-bold text-balance">
            Everything you need for{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              smart inventory
            </span>
          </h2>
          <p className="text-xl text-muted-foreground text-pretty max-w-3xl mx-auto">
            Our AI-powered platform combines cutting-edge technology with intuitive design to revolutionize how you
            manage your supply chain operations.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-border/50 hover:border-primary/20"
            >
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {feature.badge}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <h3 className="font-display text-lg font-semibold group-hover:text-primary transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-muted-foreground text-pretty">{feature.description}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
