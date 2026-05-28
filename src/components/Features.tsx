"use client";
import { motion } from "framer-motion";
import {
  Zap, Brain, BarChart3, Shield, Layers, Cpu
} from "lucide-react";

const features = [
  {
    icon: Zap,
    title: "Instant Compression",
    description:
      "Rule-based + AI compression removes filler words, redundant context, and verbose phrasing in milliseconds.",
    color: "from-purple-600 to-purple-400",
    glow: "shadow-purple-500/20",
    border: "border-purple-500/20",
    badge: "< 200ms",
  },
  {
    icon: Brain,
    title: "LLMLingua AI Engine",
    description:
      "Microsoft Research's LLMLingua — state-of-the-art semantic compression achieving 50–60% reduction with quality intact.",
    color: "from-cyan-600 to-cyan-400",
    glow: "shadow-cyan-500/20",
    border: "border-cyan-500/20",
    badge: "Research-backed",
  },
  {
    icon: BarChart3,
    title: "Token Analytics Dashboard",
    description:
      "Track every compression. See tokens saved, cost reduction, and quality scores in real-time across all sessions.",
    color: "from-violet-600 to-purple-400",
    glow: "shadow-violet-500/20",
    border: "border-violet-500/20",
    badge: "Live metrics",
  },
  {
    icon: Layers,
    title: "Multi-Model Support",
    description:
      "Works seamlessly with GPT-4o, Claude 3.5 Sonnet, and Gemini Pro. Smart routing picks the best model automatically.",
    color: "from-blue-600 to-cyan-400",
    glow: "shadow-blue-500/20",
    border: "border-blue-500/20",
    badge: "3 LLMs",
  },
  {
    icon: Cpu,
    title: "AI Memory Compression",
    description:
      "Summarizes long conversation history into compact memory. Your AI remembers context without wasting tokens.",
    color: "from-emerald-600 to-cyan-400",
    glow: "shadow-emerald-500/20",
    border: "border-emerald-500/20",
    badge: "RAG-powered",
  },
  {
    icon: Shield,
    title: "Privacy First (BYOK)",
    description:
      "Bring Your Own API Key. Your prompts never leave your control. Local rule-based compression requires zero backend.",
    color: "from-rose-600 to-orange-400",
    glow: "shadow-rose-500/20",
    border: "border-rose-500/20",
    badge: "Zero data retention",
  },
];

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } },
};

export default function Features() {
  return (
    <section id="features" className="relative py-28 overflow-hidden">
      {/* Background orb */}
      <div
        className="orb w-[700px] h-[700px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
        style={{ background: "radial-gradient(circle, rgba(124,58,237,0.06) 0%, transparent 70%)" }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass border border-purple-500/30 text-sm text-purple-300 mb-5"
          >
            <Zap className="w-3.5 h-3.5" />
            Built for AI Power Users
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl lg:text-5xl font-bold mb-4 tracking-tight"
          >
            Everything you need to{" "}
            <span className="gradient-text">ship leaner AI</span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-slate-400 text-lg max-w-2xl mx-auto"
          >
            A complete token optimization layer — from your browser extension to
            your backend API. One platform, every workflow.
          </motion.p>
        </div>

        {/* Feature grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                variants={cardVariants}
                className={`card p-6 group cursor-default shadow-lg ${feature.glow}`}
              >
                {/* Icon */}
                <div className="mb-4 flex items-start justify-between">
                  <div
                    className={`w-11 h-11 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}
                  >
                    <Icon className="w-5 h-5 text-white" strokeWidth={2} />
                  </div>
                  <span
                    className={`text-xs font-semibold px-2.5 py-1 rounded-full glass border ${feature.border} text-slate-400`}
                  >
                    {feature.badge}
                  </span>
                </div>

                {/* Content */}
                <h3 className="font-bold text-lg text-slate-100 mb-2 group-hover:text-white transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
