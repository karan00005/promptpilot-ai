"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Zap, Mail, Lock, ArrowRight, Loader2, AlertCircle, CheckCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Clear errors when toggling modes
  useEffect(() => {
    setError("");
    setSuccess("");
  }, [isSignUp]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    const endpoint = isSignUp ? "/api/v1/auth/signup" : "/api/v1/auth/login";
    
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    
    try {
      const response = await fetch(`${apiBase}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed. Please verify credentials.");
      }

      if (isSignUp) {
        setSuccess("Account created successfully! Redirecting you...");
        // Auto login on signup success
        localStorage.setItem("pp_token", data.token);
        localStorage.setItem("pp_user_email", data.user.email);
        setTimeout(() => {
          router.push("/dashboard");
        }, 1500);
      } else {
        setSuccess("Access authorized! Redirecting to developer console...");
        localStorage.setItem("pp_token", data.token);
        localStorage.setItem("pp_user_email", data.user.email);
        setTimeout(() => {
          router.push("/dashboard");
        }, 1200);
      }
    } catch (err: any) {
      setError(err.message || "Unable to reach the PromptPilot API. Verify the server is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen relative flex items-center justify-center bg-[#070714] overflow-hidden px-6">
      {/* Background orbs */}
      <div
        className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full blur-[150px] opacity-20 pointer-events-none"
        style={{ background: "radial-gradient(circle, #7c3aed 0%, transparent 70%)" }}
      />
      <div
        className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full blur-[150px] opacity-20 pointer-events-none"
        style={{ background: "radial-gradient(circle, #06b6d4 0%, transparent 70%)" }}
      />

      <div className="relative z-10 w-full max-w-md">
        {/* Brand Link */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-500 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl text-slate-100">
              Prompt<span className="gradient-text-static">Pilot</span>
            </span>
          </Link>
          <p className="text-slate-400 text-sm">
            {isSignUp ? "Create your developer account" : "Log in to your developer console"}
          </p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-8 glow-purple"
        >
          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            
            {/* Dynamic Glassmorphic Alerts */}
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 text-xs font-semibold flex items-start gap-2.5"
              >
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            {success && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-xs font-semibold flex items-start gap-2.5"
              >
                <CheckCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{success}</span>
              </motion.div>
            )}

            {/* Email Field */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl pl-11 pr-4 py-3.5 text-slate-200 placeholder-slate-500 text-sm outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/20 transition-all"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-2">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Password
                </label>
                {!isSignUp && (
                  <a href="#" className="text-xs text-purple-400 hover:underline">
                    Forgot password?
                  </a>
                )}
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl pl-11 pr-4 py-3.5 text-slate-200 placeholder-slate-500 text-sm outline-none focus:border-purple-500/60 focus:ring-1 focus:ring-purple-500/20 transition-all"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3.5 mt-2 font-semibold disabled:opacity-70"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {isSignUp ? "Signing Up..." : "Authenticating..."}
                </>
              ) : (
                <>
                  {isSignUp ? "Create Account" : "Access Console"}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Sign Up / Login */}
          <div className="mt-6 text-center text-sm text-slate-500">
            {isSignUp ? (
              <>
                Already have an account?{" "}
                <button
                  onClick={() => setIsSignUp(false)}
                  className="text-purple-400 font-semibold hover:underline"
                >
                  Log in
                </button>
              </>
            ) : (
              <>
                New to PromptPilot?{" "}
                <button
                  onClick={() => setIsSignUp(true)}
                  className="text-purple-400 font-semibold hover:underline"
                >
                  Sign up free
                </button>
              </>
            )}
          </div>
        </motion.div>

        {/* Local dev notice */}
        <p className="mt-8 text-center text-xs text-slate-600">
          🔒 Secure Auth powered by local SQLite database. Create an account, and log in securely.
        </p>
      </div>
    </main>
  );
}
