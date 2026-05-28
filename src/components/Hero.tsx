"use client";
import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, TrendingDown, DollarSign } from "lucide-react";

const BEFORE_TEXT = `Hello! I was wondering if you could please help me by creating a very detailed and comprehensive project report. The report should include all user requirements in detail, the complete technical stack with explanations for each choice, a full project timeline with milestones, and please also include step-by-step explanations with examples for each section. I would really appreciate if you could be as thorough as possible.`;

const AFTER_TEXT = `Create detailed project report with: user requirements, tech stack (with rationale), timeline with milestones, step-by-step explanations, examples per section.`;

function useCountUp(target: number, duration: number = 1200, start: boolean = false) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime: number | null = null;
    const step = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setValue(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return value;
}

export default function Hero() {
  const [animating, setAnimating] = useState(false);
  const [showAfter, setShowAfter] = useState(false);
  const [started, setStarted] = useState(false);
  const heroRef = useRef<HTMLDivElement>(null);

  const tokensBefore = 94;
  const tokensAfter = 38;
  const savedPct = Math.round(((tokensBefore - tokensAfter) / tokensBefore) * 100);

  const displayTokens = useCountUp(showAfter ? tokensAfter : tokensBefore, 800, started);
  const displaySavings = useCountUp(showAfter ? savedPct : 0, 800, showAfter && started);

  useEffect(() => {
    // Auto-run demo once on load
    const timer = setTimeout(() => {
      setStarted(true);
      setTimeout(() => {
        setAnimating(true);
        setTimeout(() => {
          setShowAfter(true);
          setAnimating(false);
        }, 1200);
      }, 800);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const runDemo = () => {
    setShowAfter(false);
    setAnimating(false);
    setStarted(false);
    setTimeout(() => {
      setStarted(true);
      setTimeout(() => {
        setAnimating(true);
        setTimeout(() => {
          setShowAfter(true);
          setAnimating(false);
        }, 1200);
      }, 400);
    }, 200);
  };

  return (
    <section
      ref={heroRef}
      className="relative min-h-screen flex items-center justify-center pt-20 pb-16 overflow-hidden grid-bg"
    >
      {/* Background orbs */}
      <div
        className="orb w-[600px] h-[600px] top-[-200px] left-[-200px] animate-pulse-glow"
        style={{ background: "radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%)" }}
      />
      <div
        className="orb w-[500px] h-[500px] bottom-[-150px] right-[-150px] animate-pulse-glow"
        style={{
          background: "radial-gradient(circle, rgba(6,182,212,0.14) 0%, transparent 70%)",
          animationDelay: "1.5s",
        }}
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
        {/* Left — Copy */}
        <div className="flex flex-col gap-6">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 self-start px-4 py-1.5 rounded-full glass border border-purple-500/30 text-sm text-purple-300"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            AI Token Optimization · Now in Beta
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.7 }}
            className="text-5xl lg:text-6xl font-bold leading-tight tracking-tight"
          >
            Cut your AI costs{" "}
            <span className="gradient-text">by 40%.</span>
            <br />
            <span className="text-slate-300">Automatically.</span>
          </motion.h1>

          {/* Sub */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="text-lg text-slate-400 leading-relaxed max-w-xl"
          >
            PromptPilot intelligently compresses your prompts for ChatGPT, Claude, and Gemini —
            reducing token usage by <strong className="text-slate-200">30–50%</strong> without
            losing output quality. One click. Real savings.
          </motion.p>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex flex-wrap gap-6"
          >
            {[
              { icon: TrendingDown, label: "Token Reduction", value: "30–50%", color: "text-purple-400" },
              { icon: DollarSign, label: "Cost Savings", value: "~$200/mo", color: "text-cyan-400" },
              { icon: Sparkles, label: "Quality Retention", value: "94%+", color: "text-green-400" },
            ].map(({ icon: Icon, label, value, color }) => (
              <div key={label} className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${color}`} />
                <span className="text-slate-400 text-sm">{label}:</span>
                <span className={`font-bold text-sm ${color}`}>{value}</span>
              </div>
            ))}
          </motion.div>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex flex-wrap gap-4 pt-2"
          >
            <a href="#waitlist" id="hero-cta-primary" className="btn-primary flex items-center gap-2 relative z-10">
              Get Early Access
              <ArrowRight className="w-4 h-4" />
            </a>
            <button
              id="hero-demo-btn"
              onClick={runDemo}
              className="btn-secondary flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Watch Demo
            </button>
          </motion.div>

          {/* Social proof */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-xs text-slate-500"
          >
            Join <span className="text-slate-300 font-semibold">500+ developers</span> on the waitlist ·
            Works with GPT-4o, Claude 3.5, Gemini Pro
          </motion.p>
        </div>

        {/* Right — Live Demo */}
        <motion.div
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="relative"
        >
          <div className="card p-1 glow-purple">
            {/* Demo header */}
            <div className="glass rounded-t-2xl rounded-b-none px-4 py-3 flex items-center justify-between border-b border-purple-900/30">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/60" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                <div className="w-3 h-3 rounded-full bg-green-500/60" />
              </div>
              <span className="text-xs text-slate-500 font-mono">promptpilot — live demo</span>
              <div className="w-16" />
            </div>

            <div className="p-5 space-y-4">
              {/* Token meter */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500 uppercase tracking-wider font-mono">
                  Token Count
                </span>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-2xl font-bold font-mono transition-all duration-500 ${
                      showAfter ? "text-green-400" : "text-slate-200"
                    }`}
                  >
                    {displayTokens}
                  </span>
                  {showAfter && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="text-xs bg-green-500/20 text-green-400 border border-green-500/30 px-2 py-0.5 rounded-full font-semibold"
                    >
                      -{displaySavings}% saved
                    </motion.span>
                  )}
                </div>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{
                    background: showAfter
                      ? "linear-gradient(90deg, #10b981, #06b6d4)"
                      : "linear-gradient(90deg, #7c3aed, #9d6ffe)",
                  }}
                  initial={{ width: "100%" }}
                  animate={{ width: showAfter ? `${(tokensAfter / tokensBefore) * 100}%` : "100%" }}
                  transition={{ duration: 1, ease: "easeInOut" }}
                />
              </div>

              {/* Prompt area */}
              <div className="space-y-3">
                <div className="relative">
                  <div className="text-xs text-slate-500 mb-1.5 font-mono uppercase tracking-wider">
                    {showAfter ? "✨ Optimized Prompt" : "📝 Original Prompt"}
                  </div>
                  <div
                    className={`rounded-xl p-4 text-sm leading-relaxed font-mono transition-all duration-500 ${
                      showAfter
                        ? "bg-green-950/30 border border-green-500/20 text-green-200"
                        : "bg-slate-900/50 border border-slate-700/50 text-slate-300"
                    }`}
                    style={{ minHeight: "120px" }}
                  >
                    {animating ? (
                      <motion.span
                        animate={{ opacity: [1, 0, 1] }}
                        transition={{ duration: 0.4, repeat: 2 }}
                        className="text-purple-400"
                      >
                        ⚡ Compressing...
                      </motion.span>
                    ) : showAfter ? (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.5 }}
                      >
                        {AFTER_TEXT}
                      </motion.span>
                    ) : (
                      BEFORE_TEXT
                    )}
                  </div>
                </div>

                {/* Action row */}
                <div className="flex items-center gap-3">
                  {!showAfter ? (
                    <button
                      onClick={runDemo}
                      className="btn-primary text-xs px-4 py-2 flex items-center gap-1.5 relative z-10"
                    >
                      <Sparkles className="w-3 h-3" />
                      Optimize Prompt
                    </button>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-3 flex-wrap"
                    >
                      <span className="text-xs text-green-400 font-semibold">
                        ✓ 56 tokens saved · $0.0017 cheaper
                      </span>
                      <button
                        onClick={runDemo}
                        className="text-xs text-slate-500 hover:text-slate-300 transition-colors underline"
                      >
                        Run again
                      </button>
                    </motion.div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Floating badges */}
          <motion.div
            animate={{ y: [0, -6, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="absolute -top-4 -right-4 glass px-3 py-2 rounded-xl text-xs font-semibold text-cyan-300 border border-cyan-500/20"
          >
            GPT-4o · Claude · Gemini
          </motion.div>
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 3.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            className="absolute -bottom-4 -left-4 glass px-3 py-2 rounded-xl text-xs font-semibold text-purple-300 border border-purple-500/20"
          >
            🔒 Privacy first · BYOK
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
