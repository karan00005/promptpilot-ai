"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Zap,
  Key,
  Shield,
  Sliders,
  Code,
  Check,
  Copy,
  LogOut,
  ArrowLeft,
  Terminal,
  FileCode,
  Brain,
  Upload,
  Loader2,
  Database,
  Calendar,
  AlertCircle,
  CheckCircle2
} from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const [userEmail, setUserEmail] = useState("developer@promptpilot.ai");
  
  // API Key mock states
  const [apiKey, setApiKey] = useState("pp_live_7c3aed9d6ffe06b6d4b295");
  const [isCopied, setIsCopied] = useState(false);
  const [activeSnippetTab, setActiveSnippetTab] = useState("python");

  // Semantic Context States
  const [contextsList, setContextsList] = useState<any[]>([]);
  const [contextTitle, setContextTitle] = useState("");
  const [contextText, setContextText] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [isLoadingContexts, setIsLoadingContexts] = useState(true);
  
  useEffect(() => {
    const token = localStorage.getItem("pp_token");
    const storedEmail = localStorage.getItem("pp_user_email");
    if (!token) {
      router.push("/login");
      return;
    }
    if (storedEmail) {
      setUserEmail(storedEmail);
    }

    // Fetch dynamic context libraries
    const fetchContexts = async () => {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      try {
        const response = await fetch(`${apiBase}/api/v1/context/list`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setContextsList(data);
        }
      } catch (err) {
        console.warn("Failed to fetch contexts from backend database.", err);
      } finally {
        setIsLoadingContexts(false);
      }
    };
    
    fetchContexts();
  }, [router]);

  const handleCopyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleRegenerateKey = () => {
    const chars = "abcdef0123456789";
    let newKey = "pp_live_";
    for (let i = 0; i < 22; i++) {
      newKey += chars[Math.floor(Math.random() * chars.length)];
    }
    setApiKey(newKey);
  };

  const handleUploadContext = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!contextTitle.trim() || !contextText.trim()) return;
    
    setIsUploading(true);
    setUploadError("");
    setUploadSuccess("");
    
    const token = localStorage.getItem("pp_token");
    const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    try {
      const response = await fetch(`${apiBase}/api/v1/context/upload`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          title: contextTitle,
          text: contextText
        })
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to index context document.");
      }
      
      setUploadSuccess(`Indexed successfully! "${contextTitle}" split into ${data.chunks_count} chunks.`);
      setContextTitle("");
      setContextText("");
      
      // Refresh contexts list
      const listRes = await fetch(`${apiBase}/api/v1/context/list`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (listRes.ok) {
        const listData = await listRes.json();
        setContextsList(listData);
      }
    } catch (err: any) {
      setUploadError(err.message || "Something went wrong.");
    } finally {
      setIsUploading(false);
    }
  };

  const codeSnippets = {
    python: `from promptpilot import PromptPilot
    
pp = PromptPilot(api_key="${apiKey}")

# Standard Token Pruning
pruned = pp.compress("Please help me...")

# RAG Semantic Context Cache (95% savings)
optimized_prompt = pp.compress_with_context(
    query="How to verify Stripe Webhooks?",
    context_title="Payments API Docs",
    level=2
)
print(optimized_prompt)`,

    nodejs: `import { PromptPilot } from 'promptpilot';

const pp = new PromptPilot({ apiKey: '${apiKey}' });

// Dynamic Semantic Context Retrieval
const prompt = await pp.compressWithContext({
  query: 'How to verify Stripe Webhooks?',
  contextTitle: 'Payments API Docs',
  level: 2
});`,

    curl: `curl -X POST "http://127.0.0.1:8000/api/v1/context/compress" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer ${apiKey}" \\
     -d '{
       "prompt": "How to verify Stripe Webhooks?",
       "context_title": "Payments API Docs",
       "level": 2
     }'`
  };

  return (
    <div className="min-h-screen bg-[#070714] text-slate-100 flex flex-col font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[#070714]/85 border-b border-purple-900/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-500 flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
              <span className="font-bold text-lg">
                Prompt<span className="gradient-text-static">Pilot</span>
              </span>
            </Link>
            
            <nav className="hidden md:flex items-center gap-1">
              <Link
                href="/dashboard"
                className="px-3 py-1.5 rounded-lg text-sm font-semibold text-slate-400 hover:text-slate-200 transition-all"
              >
                Overview
              </Link>
              <span className="px-3 py-1.5 rounded-lg text-sm font-semibold bg-purple-900/20 text-purple-400">
                Settings
              </span>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end text-xs">
              <span className="font-bold text-slate-300 max-w-[180px] truncate">{userEmail}</span>
              <span className="text-cyan-400 font-semibold uppercase tracking-wider text-[10px]">Active Pro Developer</span>
            </div>
            
            <button
              onClick={() => {
                localStorage.removeItem("pp_token");
                localStorage.removeItem("pp_user_email");
                router.push("/login");
              }}
              className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-red-400 hover:border-red-900/40 transition-all duration-200"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col gap-6">
        
        {/* Back Link */}
        <Link href="/dashboard" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors mb-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Overview Dashboard
        </Link>

        {/* Title */}
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Console Settings</h1>
          <p className="text-slate-400 text-sm mt-1">
            Access credentials, default rates limits, and copyable SDK integrations.
          </p>
        </div>

        {/* Settings Grid */}
        <div className="grid lg:grid-cols-3 gap-6 items-start">
          
          {/* Main Controls (Left Column) */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            
            {/* API Keys Card */}
            <div className="card p-6 flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-purple-900/10 border border-purple-500/20 text-purple-400 mt-0.5">
                  <Key className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Developer API Credentials</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Use this token to authorize compression requests via the Chrome Extension or API.</p>
                </div>
              </div>

              {/* Input copy layout */}
              <div className="flex items-center gap-2.5">
                <input
                  type="text"
                  readOnly
                  value={apiKey}
                  className="flex-1 bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-300 font-mono text-sm outline-none"
                />
                
                <button
                  onClick={handleCopyKey}
                  className="btn-secondary py-3 px-4 flex items-center justify-center gap-2 font-semibold text-xs min-w-[90px]"
                >
                  {isCopied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-green-400" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      Copy Key
                    </>
                  )}
                </button>
              </div>

              <div className="flex gap-4 border-t border-slate-800/50 pt-4 mt-2">
                <button onClick={handleRegenerateKey} className="text-xs text-purple-400 hover:text-purple-300 font-semibold transition-colors">
                  🔄 Regenerate API Credentials Token
                </button>
              </div>
            </div>

            {/* Semantic Context Caching (RAG) Card */}
            <div className="card p-6 flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-violet-900/15 border border-violet-500/20 text-violet-400 mt-0.5">
                  <Brain className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">🧠 Semantic Context Caching (B2B RAG)</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Upload huge contexts (API guides, manual sheets, codebase) once. System queries and retrieves only relevant chunks per prompt, saving up to 95% of tokens.</p>
                </div>
              </div>

              {/* Upload Form */}
              <form onSubmit={handleUploadContext} className="flex flex-col gap-4 bg-slate-900/20 border border-slate-800/40 p-4 rounded-2xl">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Document Title</label>
                  <input
                    type="text"
                    value={contextTitle}
                    onChange={(e) => setContextTitle(e.target.value)}
                    placeholder="e.g. Payments API Docs"
                    className="w-full bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-2.5 text-slate-300 text-sm outline-none focus:border-purple-500/50 transition-colors"
                    required
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Document Content (Raw Text)</label>
                  <textarea
                    rows={4}
                    value={contextText}
                    onChange={(e) => setContextText(e.target.value)}
                    placeholder="Paste entire API manual, user guide or instructions docs here..."
                    className="w-full bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-2.5 text-slate-300 text-xs font-sans outline-none focus:border-purple-500/50 resize-none transition-colors"
                    required
                  />
                </div>

                {uploadError && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-red-400 font-semibold flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{uploadError}</span>
                  </motion.div>
                )}

                {uploadSuccess && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    <span>{uploadSuccess}</span>
                  </motion.div>
                )}

                <button
                  type="submit"
                  disabled={isUploading}
                  className="btn-primary py-2.5 px-4 flex items-center justify-center gap-2 font-bold text-xs self-end disabled:opacity-60"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Chunking & Vectoring...
                    </>
                  ) : (
                    <>
                      <Upload className="w-3.5 h-3.5" />
                      Index Context Document
                    </>
                  )}
                </button>
              </form>

              {/* Active Contexts List */}
              <div className="flex flex-col gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Libraries</span>
                {isLoadingContexts ? (
                  <div className="py-6 text-center text-xs text-slate-500 flex items-center justify-center gap-1.5">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-400" />
                    Checking indexed documents...
                  </div>
                ) : contextsList.length === 0 ? (
                  <div className="py-6 text-center border border-dashed border-slate-800 rounded-2xl text-xs text-slate-500 flex flex-col items-center justify-center gap-2">
                    <Database className="w-6 h-6 text-slate-700 animate-pulse" />
                    <span>No contexts indexed yet. Paste documents above to begin.</span>
                  </div>
                ) : (
                  <div className="overflow-hidden border border-slate-800 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="bg-slate-950/40 text-slate-500 border-b border-slate-800 font-bold uppercase text-[9px] tracking-wider">
                          <th className="py-2.5 px-3">Title</th>
                          <th className="py-2.5 px-3">Vector Chunks</th>
                          <th className="py-2.5 px-3 text-right">Created At</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/40">
                        {contextsList.map((c) => (
                          <tr key={c.id} className="hover:bg-slate-900/10 transition-colors">
                            <td className="py-2.5 px-3 font-semibold text-slate-200">{c.title}</td>
                            <td className="py-2.5 px-3 font-semibold text-purple-400">{c.chunk_count} semantic segments</td>
                            <td className="py-2.5 px-3 text-right text-slate-500 flex items-center justify-end gap-1.5">
                              <Calendar className="w-3 h-3 text-slate-600" />
                              {new Date(c.created_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Pipeline Configuration Card */}
            <div className="card p-6 flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-900/10 border border-cyan-500/20 text-cyan-400 mt-0.5">
                  <Sliders className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Optimization Engine Controls</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Configure default compression levels and strict rules limits.</p>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Default Compression Level
                  </label>
                  <select defaultValue="2" className="bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-300 text-sm outline-none">
                    <option value="1">Level 1 — Rule-based (Fast)</option>
                    <option value="2">Level 2 — Heuristic TF-IDF (Balanced)</option>
                    <option value="3">Level 3 — Local BART Summary (Deep)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Default Fallback LLM Model
                  </label>
                  <select defaultValue="gpt-4o" className="bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-300 text-sm outline-none">
                    <option value="gpt-4o">GPT-4o (OpenAI)</option>
                    <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
                    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                    <option value="gemini-pro">Gemini Pro (Google)</option>
                  </select>
                </div>
              </div>
            </div>
            
            {/* Rate Limiting Configuration Card */}
            <div className="card p-6 flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-900/10 border border-emerald-500/20 text-emerald-400 mt-0.5">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold">Rate Limits & Budget Guard</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Protect against API budget overrun and configure maximum request counts.</p>
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Daily Compression Limit
                  </label>
                  <input
                    type="text"
                    value="5,000 requests"
                    readOnly
                    className="bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-300 text-sm outline-none"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Monthly Token Savings Alert
                  </label>
                  <input
                    type="text"
                    value="Email alert on 100k saved"
                    readOnly
                    className="bg-[#0d0d26]/80 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-300 text-sm outline-none"
                  />
                </div>
              </div>
            </div>

          </div>

          {/* Quick Integration Guide (Right Column) */}
          <div className="flex flex-col gap-6">
            
            {/* SDK Code Snippets Card */}
            <div className="card p-6 flex flex-col gap-5">
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400">
                  <Code className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold">API Quickstart Guide</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Plug the prompt optimization layer directly into your backend code.</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-800">
                {["python", "nodejs", "curl"].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveSnippetTab(tab)}
                    className={`flex-1 pb-2 text-xs font-bold capitalize transition-all border-b ${
                      activeSnippetTab === tab ? "border-purple-500 text-purple-400" : "border-transparent text-slate-500 hover:text-slate-300"
                    }`}
                  >
                    {tab === "nodejs" ? "Node.js" : tab === "curl" ? "cURL" : "Python"}
                  </button>
                ))}
              </div>

              {/* Snippet Block */}
              <div className="relative">
                <pre className="bg-[#03030d] border border-slate-800/80 rounded-xl p-4 font-mono text-[10px] leading-relaxed text-purple-300 overflow-x-auto select-all max-h-[220px]">
                  {codeSnippets[activeSnippetTab as keyof typeof codeSnippets]}
                </pre>
              </div>

              <div className="flex items-center gap-2 text-xs text-slate-500">
                <Terminal className="w-3.5 h-3.5 text-purple-400" />
                <span>Base URL: <code>http://127.0.0.1:8000/api/v1</code></span>
              </div>
            </div>

            {/* Platform instructions */}
            <div className="card p-6 flex flex-col gap-4 bg-gradient-to-br from-purple-900/5 to-cyan-900/5">
              <h4 className="font-bold text-slate-300 text-sm flex items-center gap-1.5">
                <FileCode className="w-4 h-4 text-cyan-400" />
                Chrome Extension Load
              </h4>
              <p className="text-xs text-slate-500 leading-relaxed">
                To test the injected Optimize button locally:
              </p>
              <ol className="text-xs text-slate-400 list-decimal list-inside space-y-2 leading-relaxed">
                <li>Go to <code>chrome://extensions</code> in Chrome.</li>
                <li>Enable <strong>Developer Mode</strong> (top right toggle).</li>
                <li>Click <strong>Load unpacked</strong>.</li>
                <li>Select folder <code>promptpilot/apps/extension</code>.</li>
              </ol>
            </div>

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-[#070714] py-6 px-6 text-center text-xs text-slate-600">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>© 2026 PromptPilot AI. Developer Dashboard.</span>
          <div className="flex gap-4">
            <Link href="/" className="hover:text-slate-400 transition-colors">Go to Home</Link>
            <span>·</span>
            <Link href="/dashboard" className="hover:text-slate-400 transition-colors">Overview Dashboard</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
