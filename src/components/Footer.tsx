"use client";
import { motion } from "framer-motion";
import { Zap, Share2, GitBranch, Link2 } from "lucide-react";

const footerLinks = {
  Product: ["Features", "How it Works", "Pricing", "Changelog"],
  Developers: ["API Docs", "Chrome Extension", "VS Code Plugin", "GitHub"],
  Company: ["About", "Blog", "Privacy Policy", "Terms of Service"],
};

export default function Footer() {
  return (
    <footer className="relative border-t border-purple-900/20 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-5 gap-10 mb-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-600 to-cyan-500 flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" strokeWidth={2.5} />
              </div>
              <span className="font-bold text-lg">
                Prompt<span className="gradient-text-static">Pilot</span>
              </span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed mb-5 max-w-xs">
              The AI token optimization layer that cuts your LLM API costs by 30–50%
              without sacrificing quality.
            </p>
            <div className="flex items-center gap-3">
              {[Share2, GitBranch, Link2].map((Icon, i) => (
                <a
                  key={i}
                  href="#"
                  className="w-9 h-9 rounded-lg glass border border-slate-700/50 flex items-center justify-center text-slate-400 hover:text-white hover:border-purple-500/40 transition-all duration-200"
                >
                  <Icon className="w-4 h-4" />
                </a>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([heading, links]) => (
            <div key={heading}>
              <h4 className="font-semibold text-slate-300 mb-4 text-sm">{heading}</h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="border-t border-slate-800/50 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-slate-600 text-xs">
            © 2026 PromptPilot AI. All rights reserved.
          </p>
          <div className="flex items-center gap-4 text-xs text-slate-600">
            <span>🔒 GDPR Compliant</span>
            <span>·</span>
            <span>No prompt logging</span>
            <span>·</span>
            <span>BYOK</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
