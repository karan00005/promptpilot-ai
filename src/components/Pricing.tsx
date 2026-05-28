"use client";
import { motion } from "framer-motion";
import { Check, Zap, Building2, ArrowRight } from "lucide-react";

const plans = [
  {
    id: "free",
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for trying out PromptPilot.",
    icon: Zap,
    iconColor: "text-slate-400",
    badge: null,
    features: [
      "50 compressions / day",
      "Rule-based compression",
      "Chrome extension",
      "Token counter",
      "Basic analytics dashboard",
      "ChatGPT + Claude support",
    ],
    missing: [
      "AI compression (LLMLingua)",
      "RAG memory",
      "Developer API",
      "Team workspace",
    ],
    cta: "Start Free",
    ctaHref: "#waitlist",
    highlight: false,
  },
  {
    id: "pro",
    name: "Pro",
    price: "$19",
    period: "per month",
    description: "For developers and power AI users.",
    icon: Zap,
    iconColor: "text-purple-400",
    badge: "Most Popular",
    features: [
      "Unlimited compressions",
      "LLMLingua AI compression (50%+)",
      "Smart context summarization",
      "RAG conversation memory",
      "All 3 models (GPT, Claude, Gemini)",
      "Developer API (1,000 calls/mo)",
      "Full analytics + cost tracker",
      "Priority support",
    ],
    missing: [],
    cta: "Get Early Access",
    ctaHref: "#waitlist",
    highlight: true,
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "Custom",
    period: "contact us",
    description: "For teams and AI-first companies.",
    icon: Building2,
    iconColor: "text-cyan-400",
    badge: null,
    features: [
      "Everything in Pro",
      "Team workspace + shared analytics",
      "Unlimited API calls",
      "SSO / SAML authentication",
      "Custom compression models",
      "99.9% SLA guarantee",
      "Dedicated success manager",
      "Enterprise billing + invoicing",
    ],
    missing: [],
    cta: "Talk to Sales",
    ctaHref: "#waitlist",
    highlight: false,
  },
];

export default function Pricing() {
  return (
    <section id="pricing" className="relative py-28">
      <div
        className="orb w-[600px] h-[600px] bottom-0 left-1/2 -translate-x-1/2"
        style={{ background: "radial-gradient(circle, rgba(124,58,237,0.07) 0%, transparent 70%)" }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl lg:text-5xl font-bold mb-4 tracking-tight"
          >
            Simple, transparent{" "}
            <span className="gradient-text">pricing</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 text-lg max-w-xl mx-auto"
          >
            Start free. Upgrade when you&apos;re ready. Cancel anytime.
            Early access users get{" "}
            <span className="text-purple-400 font-semibold">3 months Pro free</span>.
          </motion.p>
        </div>

        {/* Cards */}
        <div className="grid lg:grid-cols-3 gap-6 items-stretch">
          {plans.map((plan, i) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.12 }}
              className={`relative flex flex-col rounded-2xl p-7 ${
                plan.highlight
                  ? "bg-gradient-to-b from-purple-950/60 to-navy-card border border-purple-500/40 shadow-2xl shadow-purple-500/20"
                  : "card"
              }`}
            >
              {/* Popular badge */}
              {plan.badge && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-purple-600 to-cyan-500 text-white text-xs font-bold whitespace-nowrap shadow-lg">
                  {plan.badge}
                </div>
              )}

              {/* Header */}
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <span className={`font-bold text-lg ${plan.iconColor}`}>{plan.name}</span>
                </div>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-4xl font-bold text-slate-100">{plan.price}</span>
                  <span className="text-slate-500 text-sm">/{plan.period}</span>
                </div>
                <p className="text-slate-400 text-sm">{plan.description}</p>
              </div>

              {/* CTA */}
              <a
                id={`pricing-cta-${plan.id}`}
                href={plan.ctaHref}
                className={`flex items-center justify-center gap-2 py-2.5 px-5 rounded-xl font-semibold text-sm transition-all duration-300 mb-6 ${
                  plan.highlight
                    ? "btn-primary"
                    : "btn-secondary"
                }`}
              >
                {plan.cta}
                <ArrowRight className="w-4 h-4" />
              </a>

              {/* Features */}
              <div className="flex flex-col gap-2.5 flex-1">
                {plan.features.map((f) => (
                  <div key={f} className="flex items-start gap-2.5">
                    <Check className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-slate-300">{f}</span>
                  </div>
                ))}
                {plan.missing.map((f) => (
                  <div key={f} className="flex items-start gap-2.5 opacity-35">
                    <div className="w-4 h-4 mt-0.5 flex-shrink-0 flex items-center justify-center">
                      <div className="w-3 h-px bg-slate-600" />
                    </div>
                    <span className="text-sm text-slate-500">{f}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom note */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-slate-500 text-sm mt-8"
        >
          All plans include: BYOK (Bring Your Own API Key) · GDPR compliant · No prompt logging
        </motion.p>
      </div>
    </section>
  );
}
