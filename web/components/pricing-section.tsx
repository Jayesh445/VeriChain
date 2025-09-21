import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, Zap, Crown, Building } from "lucide-react"

const plans = [
  {
    name: "Starter",
    icon: Zap,
    price: "Free",
    period: "forever",
    description: "Perfect for small businesses getting started with AI inventory management.",
    features: [
      "Up to 100 SKUs",
      "Basic AI recommendations",
      "Email support",
      "Standard integrations",
      "Monthly reports",
    ],
    cta: "Start Free",
    popular: false,
  },
  {
    name: "Professional",
    icon: Crown,
    price: "$99",
    period: "per month",
    description: "Advanced features for growing businesses with complex inventory needs.",
    features: [
      "Up to 10,000 SKUs",
      "Advanced AI predictions",
      "Priority support",
      "Custom integrations",
      "Real-time analytics",
      "Blockchain audit trails",
      "Multi-location support",
    ],
    cta: "Start Trial",
    popular: true,
  },
  {
    name: "Enterprise",
    icon: Building,
    price: "Custom",
    period: "pricing",
    description: "Tailored solutions for large enterprises with unlimited scale.",
    features: [
      "Unlimited SKUs",
      "Custom AI models",
      "Dedicated support",
      "White-label options",
      "Advanced security",
      "SLA guarantees",
      "Custom workflows",
      "On-premise deployment",
    ],
    cta: "Contact Sales",
    popular: false,
  },
]

export function PricingSection() {
  return (
    <section id="pricing" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <Badge variant="secondary" className="w-fit mx-auto">
            Pricing
          </Badge>
          <h2 className="font-display text-4xl lg:text-5xl font-bold text-balance">
            Choose your{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              perfect plan
            </span>
          </h2>
          <p className="text-xl text-muted-foreground text-pretty max-w-3xl mx-auto">
            Start free and scale as you grow. All plans include our core AI features with no hidden fees or setup costs.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <Card
              key={index}
              className={`relative group hover:shadow-xl transition-all duration-300 ${
                plan.popular ? "border-primary shadow-lg scale-105 lg:scale-110" : "hover:-translate-y-1"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground">Most Popular</Badge>
                </div>
              )}

              <CardHeader className="text-center space-y-4 pb-8">
                <div
                  className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center ${
                    plan.popular ? "bg-primary text-primary-foreground" : "bg-primary/10 text-primary"
                  }`}
                >
                  <plan.icon className="w-8 h-8" />
                </div>

                <div>
                  <CardTitle className="font-display text-2xl">{plan.name}</CardTitle>
                  <p className="text-sm text-muted-foreground mt-2 text-pretty">{plan.description}</p>
                </div>

                <div className="space-y-1">
                  <div className="flex items-baseline justify-center space-x-1">
                    <span className="font-display text-4xl font-bold">{plan.price}</span>
                    {plan.price !== "Free" && plan.price !== "Custom" && (
                      <span className="text-muted-foreground">/{plan.period.split(" ")[0]}</span>
                    )}
                  </div>
                  {plan.price !== "Custom" && <p className="text-sm text-muted-foreground">{plan.period}</p>}
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                <ul className="space-y-3">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center space-x-3">
                      <CheckCircle className="w-5 h-5 text-primary flex-shrink-0" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full ${plan.popular ? "bg-primary hover:bg-primary/90" : ""}`}
                  variant={plan.popular ? "default" : "outline"}
                >
                  {plan.cta}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Additional info */}
        <div className="text-center mt-12 space-y-4">
          <p className="text-muted-foreground">All plans include 14-day free trial • No setup fees • Cancel anytime</p>
          <div className="flex items-center justify-center space-x-8 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-primary" />
              <span>99.9% Uptime SLA</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-primary" />
              <span>24/7 Support</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-primary" />
              <span>SOC 2 Compliant</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
