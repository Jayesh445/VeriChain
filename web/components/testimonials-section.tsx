"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, ChevronLeft, ChevronRight, Quote } from "lucide-react"

const testimonials = [
  {
    name: "Sarah Chen",
    role: "Supply Chain Director",
    company: "TechFlow Industries",
    image: "/professional-woman-headshot.png",
    rating: 5,
    quote:
      "VeriChain AI reduced our inventory costs by 40% while eliminating stockouts completely. The AI predictions are incredibly accurate.",
    metrics: { cost_reduction: "40%", accuracy: "99.2%" },
  },
  {
    name: "Marcus Rodriguez",
    role: "Operations Manager",
    company: "Global Retail Corp",
    image: "/professional-man-headshot.png",
    rating: 5,
    quote:
      "The blockchain transparency gives us complete confidence in our supply chain. Our audits are now seamless and automated.",
    metrics: { time_saved: "60%", transparency: "100%" },
  },
  {
    name: "Emily Watson",
    role: "CEO",
    company: "SmartLogistics",
    image: "/professional-woman-ceo.png",
    rating: 5,
    quote:
      "Implementation was surprisingly smooth. The AI learned our patterns quickly and now manages our entire inventory autonomously.",
    metrics: { efficiency: "75%", automation: "95%" },
  },
]

export function TestimonialsSection() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
  }

  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length)
  }

  const current = testimonials[currentTestimonial]

  return (
    <section className="py-24 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <Badge variant="secondary" className="w-fit mx-auto">
            Testimonials
          </Badge>
          <h2 className="font-display text-4xl lg:text-5xl font-bold text-balance">
            Trusted by{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              industry leaders
            </span>
          </h2>
          <p className="text-xl text-muted-foreground text-pretty max-w-3xl mx-auto">
            See how companies worldwide are transforming their supply chains with our AI-powered platform.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="relative overflow-hidden">
            <CardContent className="p-8 lg:p-12">
              <div className="grid lg:grid-cols-2 gap-8 items-center">
                {/* Testimonial Content */}
                <div className="space-y-6">
                  <Quote className="w-12 h-12 text-primary/20" />

                  <blockquote className="text-xl lg:text-2xl font-medium text-pretty leading-relaxed">
                    "{current.quote}"
                  </blockquote>

                  <div className="flex items-center space-x-1">
                    {[...Array(current.rating)].map((_, i) => (
                      <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>

                  <div className="flex items-center space-x-4">
                    <img
                      src={current.image || "/placeholder.svg"}
                      alt={current.name}
                      className="w-12 h-12 rounded-full object-cover"
                    />
                    <div>
                      <div className="font-semibold">{current.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {current.role} at {current.company}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Metrics */}
                <div className="space-y-6">
                  <h4 className="font-display text-lg font-semibold">Key Results</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(current.metrics).map(([key, value]) => (
                      <div key={key} className="text-center p-4 bg-background rounded-lg border border-border">
                        <div className="font-display text-2xl font-bold text-primary">{value}</div>
                        <div className="text-sm text-muted-foreground capitalize">{key.replace("_", " ")}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex items-center justify-between mt-8 pt-8 border-t border-border">
                <div className="flex space-x-2">
                  {testimonials.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentTestimonial(index)}
                      className={`w-2 h-2 rounded-full transition-colors ${
                        index === currentTestimonial ? "bg-primary" : "bg-muted-foreground/30"
                      }`}
                    />
                  ))}
                </div>

                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={prevTestimonial}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={nextTestimonial}>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
