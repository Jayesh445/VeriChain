"use client"

import { Upload, Brain, Truck } from "lucide-react";


const steps = [
  {
    number: "01",
    title: "Upload Your Inventory",
    description:
      "Connect your existing store or upload product data. Our AI instantly understands your catalog and starts learning your business patterns.",
    icon: Upload,
    image:'/assets/step-1-upload.jpg',
    color: "primary",
  },
  {
    number: "02",
    title: "AI Manages Everything",
    description:
      "Our intelligent agent monitors stock levels, predicts demand, and automatically updates inventory across all your sales channels.",
    icon: Brain,
    image: '/assets/step-2-ai-manage.jpg',
    color: "secondary",
  },
  {
    number: "03",
    title: "Orders Fulfilled Automatically",
    description:
      "When orders come in, our AI tracks fulfillment, manages shipping, and sends updates to customers. Everything happens seamlessly.",
    icon: Truck,
    image: '/assets/step-3-fulfill.jpg',
    color: "primary",
  },
];

export function HowItWorksSection2() {
  return (
    <section id="how-it-works" className="relative py-24 overflow-hidden bg-gradient-to-br from-primary/5 via-background to-secondary/5">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary/10 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative max-w-7xl mx-auto px-6">
        {/* Section heading */}
        <div className="text-center mb-20">
          <h2 className="font-display text-4xl md:text-6xl font-bold mb-6">
            How It{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Three simple steps to transform your selling process. No technical
            expertise required.
          </p>
        </div>

        {/* Steps */}
        <div className="space-y-32">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={`grid lg:grid-cols-2 gap-12 items-center ${
                index % 2 === 1 ? "lg:grid-flow-col-dense" : ""
              }`}
            >
              {/* Content */}
              <div
                className={`space-y-6 ${
                  index % 2 === 1 ? "lg:order-2" : ""
                }`}
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`
                      w-16 h-16 rounded-2xl flex items-center justify-center font-display text-2xl font-bold shadow-2xl
                      ${
                        step.color === "primary"
                          ? "bg-gradient-to-br from-primary to-primary/70 text-primary-foreground"
                          : "bg-gradient-to-br from-secondary to-secondary/70 text-secondary-foreground"
                      }
                    `}
                  >
                    {step.number}
                  </div>

                  <div
                    className={`
                      w-12 h-12 rounded-xl flex items-center justify-center shadow-lg
                      ${
                        step.color === "primary"
                          ? "bg-primary/10 text-primary"
                          : "bg-secondary/10 text-secondary"
                      }
                    `}
                  >
                    <step.icon className="w-6 h-6" />
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-display text-3xl font-bold">
                    {step.title}
                  </h3>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Image */}
              <div
                className={`relative ${
                  index % 2 === 1 ? "lg:order-1" : ""
                }`}
              >
                <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-border group">
                  <img
                    src={step.image}
                    alt={step.title}
                    className="w-full h-80 object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div
                    className={`
                      absolute inset-0 transition-opacity duration-300 group-hover:opacity-20
                      ${
                        step.color === "primary"
                          ? "bg-gradient-to-br from-primary/50 to-primary/20"
                          : "bg-gradient-to-br from-secondary/50 to-secondary/20"
                      }
                    `}
                  />
                </div>

                {/* Floating decorative elements */}
                <div
                  className={`
                    absolute -top-4 -right-4 w-20 h-20 rounded-full blur-xl opacity-60 animate-pulse
                    ${
                      step.color === "primary"
                        ? "bg-primary/30"
                        : "bg-secondary/30"
                    }
                  `}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
