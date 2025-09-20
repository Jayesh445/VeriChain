import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Upload, Brain, Truck, BarChart3 } from "lucide-react"

const steps = [
  {
    step: "01",
    icon: Upload,
    title: "Connect Your Data",
    description: "Upload your inventory data or connect existing systems through our secure API integration.",
    color: "text-primary",
  },
  {
    step: "02",
    icon: Brain,
    title: "AI Analysis",
    description: "Our AI agent analyzes patterns, demand forecasts, and optimizes your inventory levels automatically.",
    color: "text-secondary",
  },
  {
    step: "03",
    icon: Truck,
    title: "Automated Orders",
    description: "Smart ordering system places orders automatically based on AI recommendations and business rules.",
    color: "text-accent",
  },
  {
    step: "04",
    icon: BarChart3,
    title: "Monitor & Optimize",
    description: "Real-time dashboard provides insights while AI continuously learns and improves performance.",
    color: "text-chart-4",
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <Badge variant="secondary" className="w-fit mx-auto">
            How It Works
          </Badge>
          <h2 className="font-display text-4xl lg:text-5xl font-bold text-balance">
            Get started in{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              4 simple steps
            </span>
          </h2>
          <p className="text-xl text-muted-foreground text-pretty max-w-3xl mx-auto">
            Our streamlined onboarding process gets you up and running with AI-powered inventory management in minutes,
            not months.
          </p>
        </div>

        <div className="grid lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div key={index} className="relative">
              <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="relative">
                    <div
                      className={`w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center group-hover:scale-110 transition-transform`}
                    >
                      <step.icon className={`w-8 h-8 ${step.color}`} />
                    </div>
                    <div className="absolute -top-2 -right-2 w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground text-sm font-bold">
                      {step.step}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h3 className="font-display text-xl font-semibold">{step.title}</h3>
                    <p className="text-sm text-muted-foreground text-pretty">{step.description}</p>
                  </div>
                </CardContent>
              </Card>

              {/* Connecting line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-primary/50 to-secondary/50 transform -translate-y-1/2" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
