"use client";
import { motion } from "framer-motion";
import { Globe, Server, BarChart2 } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: Globe,
    title: "Install the Chrome Extension",
    description:
      "Add PromptPilot to Chrome in one click. It auto-injects into ChatGPT, Claude.ai, and Gemini — no setup needed.",
    color: "from-purple-600 to-purple-500",
    detail: "Works on Brave & Edge too",
  },
  {
    number: "02",
    icon: Server,
    title: "Type Your Prompt Normally",
    description:
      "Use AI tools exactly as before. PromptPilot silently watches your prompt and shows the live token count in real-time.",
    color: "from-cyan-600 to-cyan-500",
    detail: "< 200ms compression latency",
  },
  {
    number: "03",
    icon: BarChart2,
    title: "Hit Optimize & Track Savings",
    description:
      "Click ✨ Optimize. Your prompt gets compressed and replaced instantly. Dashboard tracks every dollar and token saved.",
    color: "from-violet-600 to-purple-500",
    detail: "30–50% savings on every prompt",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-28">
      <div
        className="orb w-[500px] h-[500px] top-0 right-0"
        style={{ background: "radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%)" }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-20">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-4xl lg:text-5xl font-bold mb-4 tracking-tight"
          >
            Up and running in{" "}
            <span className="gradient-text">3 steps</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-slate-400 text-lg max-w-xl mx-auto"
          >
            No configuration. No complex setup. Just install and start saving.
          </motion.p>
        </div>

        {/* Steps */}
        <div className="relative">
          {/* Connector line */}
          <div className="hidden lg:block absolute top-16 left-1/2 -translate-x-1/2 w-[calc(66%-80px)] h-px bg-gradient-to-r from-purple-500/30 via-cyan-500/30 to-violet-500/30" />

          <div className="grid lg:grid-cols-3 gap-8">
            {steps.map((step, i) => {
              const Icon = step.icon;
              return (
                <motion.div
                  key={step.number}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.15, duration: 0.5 }}
                  className="flex flex-col items-center text-center gap-5"
                >
                  {/* Icon circle */}
                  <div className="relative">
                    <div
                      className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center shadow-2xl`}
                    >
                      <Icon className="w-8 h-8 text-white" strokeWidth={1.5} />
                    </div>
                    <div className="absolute -top-3 -right-3 w-7 h-7 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center text-xs font-bold text-slate-400 font-mono">
                      {step.number}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="space-y-2">
                    <h3 className="text-xl font-bold text-slate-100">{step.title}</h3>
                    <p className="text-slate-400 text-sm leading-relaxed max-w-xs mx-auto">
                      {step.description}
                    </p>
                  </div>

                  {/* Detail badge */}
                  <span className="glass px-3 py-1.5 rounded-full text-xs font-semibold text-slate-400 border border-slate-700/50">
                    {step.detail}
                  </span>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Bottom comparison */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4 }}
          className="mt-20 card p-8 lg:p-10"
        >
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            {/* Before */}
            <div>
              <div className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-3">
                ❌ Without PromptPilot
              </div>
              <div className="bg-slate-900/60 border border-slate-700/40 rounded-xl p-4 text-sm text-slate-400 font-mono leading-relaxed">
                "Hello! I was wondering if you could please help me by creating a very detailed and comprehensive project report that includes user requirements, technical stack, timeline with milestones, and step-by-step explanations with examples..."
                <div className="mt-3 pt-3 border-t border-slate-700/40 flex items-center justify-between">
                  <span className="text-red-400">94 tokens</span>
                  <span className="text-slate-600">$0.0028 per call</span>
                </div>
              </div>
            </div>

            {/* After */}
            <div>
              <div className="text-xs text-slate-500 font-mono uppercase tracking-wider mb-3">
                ✅ With PromptPilot
              </div>
              <div className="bg-green-950/30 border border-green-500/20 rounded-xl p-4 text-sm text-green-200 font-mono leading-relaxed">
                "Create detailed project report with: user requirements, tech stack (with rationale), timeline with milestones, step-by-step explanations, examples per section."
                <div className="mt-3 pt-3 border-t border-green-800/30 flex items-center justify-between">
                  <span className="text-green-400 font-bold">38 tokens (−60%)</span>
                  <span className="text-green-600">$0.0011 per call</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
