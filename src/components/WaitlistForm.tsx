"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Loader2, CheckCircle2, Zap, Mail } from "lucide-react";

export default function WaitlistForm() {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes("@")) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }
    setStatus("loading");
    setErrorMsg("");

    // Simulate API call — replace with your Tally/Supabase endpoint
    await new Promise((r) => setTimeout(r, 1400));
    setStatus("success");
  };

  return (
    <section id="waitlist" className="relative py-28 overflow-hidden">
      {/* Big glow center */}
      <div
        className="orb w-[800px] h-[800px] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse-glow"
        style={{ background: "radial-gradient(circle, rgba(124,58,237,0.12) 0%, transparent 70%)" }}
      />

      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass border border-cyan-500/30 text-sm text-cyan-300 mb-6"
        >
          <Zap className="w-3.5 h-3.5" />
          Early Access · 3 Months Pro Free
        </motion.div>

        {/* Headline */}
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-4xl lg:text-5xl font-bold mb-4 tracking-tight"
        >
          Be first. Pay less.{" "}
          <span className="gradient-text">Save more.</span>
        </motion.h2>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="text-slate-400 text-lg mb-10 max-w-xl mx-auto"
        >
          Join the waitlist and get{" "}
          <strong className="text-slate-200">3 months of Pro free</strong> when we launch.
          No credit card required. Unsubscribe anytime.
        </motion.p>

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
          className="card p-8 glow-purple"
        >
          <AnimatePresence mode="wait">
            {status === "success" ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center gap-4 py-4"
              >
                <div className="w-16 h-16 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center">
                  <CheckCircle2 className="w-8 h-8 text-green-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100 mb-1">You&apos;re on the list! 🎉</h3>
                  <p className="text-slate-400 text-sm">
                    We&apos;ll email <strong className="text-slate-200">{email}</strong> when PromptPilot launches.
                    Expect 3 months of Pro — free.
                  </p>
                </div>
                <div className="flex items-center gap-6 text-sm text-slate-500">
                  <span>🧑‍💻 500+ on waitlist</span>
                  <span>🚀 Launching soon</span>
                </div>
              </motion.div>
            ) : (
              <motion.form
                key="form"
                onSubmit={handleSubmit}
                className="flex flex-col gap-4"
              >
                {/* Email input */}
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    id="waitlist-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@company.com"
                    className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl pl-11 pr-4 py-3.5 text-slate-200 placeholder-slate-500 text-sm outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/20 transition-all"
                    required
                  />
                </div>

                {/* Role select */}
                <select
                  id="waitlist-role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-900/60 border border-slate-700/50 rounded-xl px-4 py-3.5 text-sm outline-none focus:border-purple-500/60 transition-all appearance-none cursor-pointer"
                  style={{ color: role ? "#e2e8f0" : "#64748b" }}
                >
                  <option value="" disabled>
                    I am a... (optional)
                  </option>
                  <option value="developer">Developer / Engineer</option>
                  <option value="researcher">Researcher / Data Scientist</option>
                  <option value="agency">AI Agency / Freelancer</option>
                  <option value="student">Student</option>
                  <option value="founder">Founder / Product Manager</option>
                  <option value="other">Other</option>
                </select>

                {/* Error */}
                {errorMsg && (
                  <p className="text-red-400 text-sm text-left">{errorMsg}</p>
                )}

                {/* Submit */}
                <button
                  id="waitlist-submit"
                  type="submit"
                  disabled={status === "loading"}
                  className="btn-primary flex items-center justify-center gap-2 py-3.5 text-base font-semibold relative z-10 disabled:opacity-70"
                >
                  {status === "loading" ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Joining...
                    </>
                  ) : (
                    <>
                      Join Waitlist — It&apos;s Free
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>

                <p className="text-xs text-slate-500">
                  No spam. No credit card. Unsubscribe anytime. 🔒
                </p>
              </motion.form>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Trust logos placeholder */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="mt-10 flex flex-wrap justify-center gap-6 text-slate-600 text-sm"
        >
          {["Works with GPT-4o", "Works with Claude 3.5", "Works with Gemini Pro"].map((t) => (
            <span key={t} className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
              {t}
            </span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
