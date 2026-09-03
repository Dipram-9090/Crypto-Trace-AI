import React, { useState, useEffect } from "react";
import { Shield, AlertTriangle, Activity, Search, RefreshCw, Cpu, Layers, GitFork } from "lucide-react";

export default function ForensicDashboard() {
  const [activeTab, setActiveTab] = useState("live");
  const [searchAddress, setSearchAddress] = useState("");
  const [liveAlerts, setLiveAlerts] = useState([
    {
      id: "ALT-8901",
      tx: "0x3f8a...9c21",
      chain: "Ethereum",
      score: 0.94,
      tier: "CRITICAL",
      reason: "OFAC Sanction Match (Tornado Cash Router)"
    },
    {
      id: "ALT-8902",
      tx: "0x7b21...41ea",
      chain: "Bitcoin",
      score: 0.88,
      tier: "CRITICAL",
      reason: "Peeling Chain Structuring (12 Hops)"
    },
    {
      id: "ALT-8903",
      tx: "0x1a9c...08fe",
      chain: "Polygon",
      score: 0.62,
      tier: "HIGH",
      reason: "Rapid Velocity Burst (>30 tx/min)"
    }
  ]);

  return (
    <div className="min-h-screen bg-[#0b0e14] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Cyber Navigation Bar */}
      <header className="border-b border-slate-800 bg-[#121824]/80 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Shield className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400">
              CRYPTO-TRACE AI
            </h1>
            <p className="text-xs text-slate-400">Enterprise AI Blockchain Forensics & Risk Engine</p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex items-center space-x-2 w-96">
          <div className="relative w-full">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search tx hash 0x..., wallet address, or ENS..."
              value={searchAddress}
              onChange={(e) => setSearchAddress(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-900/90 border border-slate-700 rounded-lg text-sm text-cyan-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition shadow-inner"
            />
          </div>
          <button className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-sm rounded-lg shadow-lg shadow-cyan-500/20 transition">
            Analyze
          </button>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>AI ENSEMBLE LIVE</span>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main className="p-6 max-w-7xl mx-auto space-y-6">
        {/* KPI Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-5 bg-[#121824] border border-slate-800 rounded-xl">
            <div className="flex justify-between items-start text-slate-400">
              <span className="text-xs uppercase tracking-wider font-semibold">Flagged Illicit Volume</span>
              <AlertTriangle className="w-4 h-4 text-red-400" />
            </div>
            <div className="text-2xl font-bold mt-2 text-red-400 font-mono">$18,420,500</div>
            <span className="text-xs text-red-400/80 font-mono">+12.4% last 24h</span>
          </div>

          <div className="p-5 bg-[#121824] border border-slate-800 rounded-xl">
            <div className="flex justify-between items-start text-slate-400">
              <span className="text-xs uppercase tracking-wider font-semibold">Trained Model F1-Score</span>
              <Cpu className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-2xl font-bold mt-2 text-cyan-400 font-mono">94.2% (XGB+GNN)</div>
            <span className="text-xs text-slate-400">Calibrated ROC-AUC 0.981</span>
          </div>

          <div className="p-5 bg-[#121824] border border-slate-800 rounded-xl">
            <div className="flex justify-between items-start text-slate-400">
              <span className="text-xs uppercase tracking-wider font-semibold">GNN Monitored Graph Nodes</span>
              <GitFork className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-2xl font-bold mt-2 text-indigo-400 font-mono">482,190 Nodes</div>
            <span className="text-xs text-slate-400">Multi-Hop Taint Depth: 5 Hops</span>
          </div>

          <div className="p-5 bg-[#121824] border border-slate-800 rounded-xl">
            <div className="flex justify-between items-start text-slate-400">
              <span className="text-xs uppercase tracking-wider font-semibold">Inference Latency</span>
              <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold mt-2 text-emerald-400 font-mono">2.4 ms/tx</div>
            <span className="text-xs text-emerald-400/80">Real-time Stream Online</span>
          </div>
        </div>

        {/* Interactive Forensic Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Live Threat Ticker */}
          <div className="lg:col-span-1 bg-[#121824] border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-red-400 animate-spin" />
                <h2 className="font-semibold text-sm tracking-wide text-slate-200">REAL-TIME THREAT STREAM</h2>
              </div>
              <span className="text-xs text-slate-500 font-mono">WS Connected</span>
            </div>

            <div className="space-y-3">
              {liveAlerts.map((alert) => (
                <div key={alert.id} className="p-3 bg-slate-900/80 border border-red-500/20 rounded-lg hover:border-red-500/50 transition cursor-pointer">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-mono text-cyan-400 font-bold">{alert.id}</span>
                    <span className="px-2 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px] font-bold font-mono">
                      RISK {alert.score * 100}%
                    </span>
                  </div>
                  <div className="text-xs text-slate-300 font-mono mt-1 truncate">{alert.tx}</div>
                  <div className="text-xs text-slate-400 mt-1">{alert.reason}</div>
                  <div className="mt-2 text-[10px] text-slate-500 font-mono flex justify-between">
                    <span>Chain: {alert.chain}</span>
                    <span className="text-cyan-400 underline hover:text-cyan-300">Trace Graph &rarr;</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Interactive Multi-Hop Graph View & Explainability */}
          <div className="lg:col-span-2 bg-[#121824] border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h2 className="font-semibold text-sm tracking-wide text-slate-200">MULTI-HOP TAINT GRAPH & SHAP REASONING</h2>
              </div>
              <div className="flex space-x-2">
                <button className="text-xs px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-mono">
                  Export SAR
                </button>
              </div>
            </div>

            {/* Simulated Cyber Graph Canvas */}
            <div className="h-64 bg-slate-950 rounded-lg border border-slate-800/80 relative overflow-hidden flex items-center justify-center">
              <div className="absolute inset-0 bg-[radial-gradient(#00f0ff_1px,transparent_1px)] [background-size:16px_16px] opacity-10"></div>
              <div className="flex flex-col items-center text-center space-y-2 z-10">
                <GitFork className="w-12 h-12 text-cyan-400/40" />
                <p className="text-sm text-slate-400 font-mono">Interactive Cytoscape.js & D3.js Network View</p>
                <p className="text-xs text-slate-600">Select any alert or enter an address to trace multi-hop peel chains</p>
              </div>
            </div>

            {/* SHAP Feature Contribution Waterfall */}
            <div className="space-y-2 pt-2">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Top SHAP Explainability Risk Drivers:
              </div>
              <div className="space-y-1.5 text-xs font-mono">
                <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded">
                  <span className="text-slate-300">1. OFAC Sanctioned Entity Link</span>
                  <span className="text-red-400 font-bold">+0.482 SHAP</span>
                </div>
                <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded">
                  <span className="text-slate-300">2. High Fan-Out Structuring Ratio</span>
                  <span className="text-orange-400 font-bold">+0.245 SHAP</span>
                </div>
                <div className="flex justify-between items-center bg-slate-900/60 p-2 rounded">
                  <span className="text-slate-300">3. Short Inter-Arrival Burst Window</span>
                  <span className="text-yellow-400 font-bold">+0.119 SHAP</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
