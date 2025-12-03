'use client';

import { AGENTS } from '@/lib/agents';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-white/20">
            {/* Hero Section */}
            <div className="relative overflow-hidden">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-900/20 via-neutral-950 to-neutral-950 pointer-events-none" />

                <div className="max-w-7xl mx-auto px-6 pt-24 pb-16 relative z-10 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-white/50">
                            Voice AI Gallery
                        </h1>
                        <p className="text-xl text-neutral-400 max-w-2xl mx-auto leading-relaxed">
                            Explore a collection of 10 intelligent voice agents, each with a unique personality and purpose. Powered by <span className="text-white font-semibold">Murf Falcon</span> and <span className="text-white font-semibold">LiveKit</span>.
                        </p>
                    </motion.div>
                </div>
            </div>

            {/* Grid Section */}
            <div className="max-w-7xl mx-auto px-6 pb-24">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {AGENTS.map((agent, index) => (
                        <Link href={`/day/${agent.id}`} key={agent.id}>
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.05 }}
                                whileHover={{ y: -5, scale: 1.02 }}
                                className="group relative h-full bg-neutral-900/50 border border-neutral-800 rounded-3xl p-8 overflow-hidden hover:border-neutral-700 transition-colors"
                            >
                                {/* Gradient Background on Hover */}
                                <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500 bg-gradient-to-br ${agent.gradient}`} />

                                <div className="relative z-10 flex flex-col h-full">
                                    <div className="flex items-start justify-between mb-6">
                                        <span className="text-4xl">{agent.icon}</span>
                                        <span className="text-xs font-mono text-neutral-500 border border-neutral-800 px-2 py-1 rounded-full">
                                            DAY {agent.id}
                                        </span>
                                    </div>

                                    <h2 className="text-2xl font-bold mb-3 group-hover:text-white transition-colors">
                                        {agent.name}
                                    </h2>

                                    <p className="text-neutral-400 text-sm leading-relaxed mb-6 flex-grow">
                                        {agent.description}
                                    </p>

                                    <div className="flex items-center text-sm font-medium text-neutral-500 group-hover:text-white transition-colors">
                                        Talk to Agent <span className="ml-2 transition-transform group-hover:translate-x-1">→</span>
                                    </div>
                                </div>
                            </motion.div>
                        </Link>
                    ))}
                </div>
            </div>

            {/* Footer */}
            <footer className="border-t border-neutral-900 py-12 text-center text-neutral-600 text-sm">
                <p>Built for the Murf AI Voice Agent Challenge 2025</p>
            </footer>
        </div>
    );
}
