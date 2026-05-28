"use client";
import { motion } from "framer-motion";
import { TrendingDown, Users, Zap, DollarSign } from "lucide-react";

const stats = [
  { icon: TrendingDown, value: "47%", label: "Avg Token Reduction", color: "text-purple-400" },
  { icon: DollarSign, value: "$200+", label: "Monthly Savings / User", color: "text-cyan-400" },
  { icon: Zap, value: "<200ms", label: "Compression Latency", color: "text-green-400" },
  { icon: Users, value: "500+", label: "Developers on Waitlist", color: "text-violet-400" },
];

export default function Stats() {
  return (
    <section className="py-16 border-y border-purple-900/20">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <Icon className={`w-5 h-5 ${stat.color} mx-auto mb-2`} />
                <div className={`text-3xl lg:text-4xl font-bold mb-1 ${stat.color}`}>
                  {stat.value}
                </div>
                <div className="text-slate-500 text-sm">{stat.label}</div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
