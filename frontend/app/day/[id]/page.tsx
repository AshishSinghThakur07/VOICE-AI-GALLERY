'use client';

import { useState, useCallback } from 'react';
import { LiveKitRoom, RoomAudioRenderer, StartAudio, useVoiceAssistant, BarVisualizer, useConnectionState, useChat, ChatMessage } from '@livekit/components-react';
import { AnimatePresence, motion } from 'framer-motion';
import { ConnectionState } from 'livekit-client';
import { toastAlert } from '@/components/livekit/alert-toast';
import { useParams } from 'next/navigation';
import { getAgent } from '@/lib/agents';
import Link from 'next/link';

export default function DynamicAgentPage() {
    const params = useParams();
    const dayId = params?.id as string;
    const agentMetadata = getAgent(dayId);

    // Fallback if agent not found
    if (!agentMetadata) {
        return (
            <div className="min-h-screen bg-neutral-950 text-white flex items-center justify-center">
                <div className="text-center">
                    <h1 className="text-2xl font-bold mb-4">Agent Not Found</h1>
                    <Link href="/" className="text-blue-400 hover:underline">Return Home</Link>
                </div>
            </div>
        );
    }

    const agentName = `day${dayId}`;
    const [playerName, setPlayerName] = useState('');
    const [isJoined, setIsJoined] = useState(false);
    const [token, setToken] = useState('');
    const [url, setUrl] = useState('');
    const [isConnecting, setIsConnecting] = useState(false);
    const [connectionError, setConnectionError] = useState(false);

    const handleJoin = useCallback(async () => {
        if (!playerName.trim()) return;
        setIsConnecting(true);
        setConnectionError(false);

        try {
            const response = await fetch('/api/connection-details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_config: {
                        agents: [{ agent_name: agentName }],
                        metadata: JSON.stringify({ player_name: playerName })
                    }
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to get connection details');
            }

            const data = await response.json();
            setToken(data.participantToken);
            setUrl(data.serverUrl);
            setIsJoined(true);
        } catch (err: any) {
            console.error(err);
            setConnectionError(true);
            toastAlert({
                title: 'Service Unavailable',
                description: 'Could not connect to the AI agent. It might be offline.',
            });
        } finally {
            setIsConnecting(false);
        }
    }, [playerName, agentName]);

    if (connectionError) {
        return (
            <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center p-4 font-sans relative overflow-hidden">
                <div className={`absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] ${agentMetadata.gradient} opacity-20 pointer-events-none`} />

                <div className="max-w-md w-full bg-neutral-900/50 backdrop-blur-xl p-8 rounded-3xl border border-red-500/30 shadow-2xl text-center space-y-6 relative z-10">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h2 className="text-3xl font-bold text-white">Service Unavailable</h2>
                    <p className="text-neutral-400">
                        The AI Agent backend is currently offline. This is likely because this is a portfolio demo and the GPU server is not active.
                    </p>
                    <div className="p-4 bg-neutral-800/50 rounded-xl text-sm text-neutral-500">
                        <p className="font-medium text-neutral-300 mb-2">Note for Visitors:</p>
                        <p className="mb-3">This service is currently denied by the developer (Backend Offline).</p>
                        <a
                            href={agentMetadata.demoUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-bold text-lg rounded-2xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-blue-500/25 w-full sm:w-auto"
                        >
                            <span className="text-2xl">📺</span>
                            <span>Watch Demo Video on LinkedIn</span>
                            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                        </a>
                    </div>
                    <button
                        onClick={() => setConnectionError(false)}
                        className="w-full py-3 px-4 bg-neutral-800 hover:bg-neutral-700 text-white font-bold rounded-xl transition-all"
                    >
                        Try Again
                    </button>
                    <Link href="/" className="block text-blue-400 hover:text-blue-300 text-sm">
                        Return to Gallery
                    </Link>
                </div>
            </div>
        );
    }

    if (!isJoined) {
        return (
            <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center p-4 font-sans relative overflow-hidden">
                {/* Dynamic Background */}
                <div className={`absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] ${agentMetadata.gradient} opacity-20 pointer-events-none`} />

                <div className="absolute top-8 left-8 z-20">
                    <Link href="/" className="text-neutral-400 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium">
                        ← Back to Gallery
                    </Link>
                </div>

                <div className="max-w-md w-full space-y-8 relative z-10">
                    <div className="text-center space-y-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.5 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="text-6xl mb-4"
                        >
                            {agentMetadata.icon}
                        </motion.div>
                        <h1 className="text-5xl font-black tracking-tighter text-white mb-2">
                            {agentMetadata.name}
                        </h1>
                        <p className="text-neutral-400 text-lg">{agentMetadata.description}</p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="bg-neutral-900/50 backdrop-blur-xl p-8 rounded-3xl border border-neutral-800 shadow-2xl space-y-6"
                    >
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-neutral-300 mb-2">
                                Your Name
                            </label>
                            <input
                                id="name"
                                type="text"
                                value={playerName}
                                onChange={(e) => setPlayerName(e.target.value)}
                                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-xl focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all text-white placeholder-neutral-600"
                                placeholder="Enter your name..."
                                onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                                autoFocus
                            />
                        </div>

                        <button
                            onClick={handleJoin}
                            disabled={!playerName.trim() || isConnecting}
                            className={`w-full py-4 px-4 bg-gradient-to-r ${agentMetadata.gradient} text-white font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95 shadow-lg hover:shadow-xl`}
                        >
                            {isConnecting ? 'Connecting...' : 'Start Conversation'}
                        </button>
                    </motion.div>
                </div>
            </div>
        );
    }

    return (
        <LiveKitRoom
            token={token}
            serverUrl={url}
            connect={true}
            video={false}
            audio={true}
            className="min-h-screen bg-neutral-950 text-white font-sans"
            onDisconnected={() => setIsJoined(false)}
        >
            <AgentUI playerName={playerName} agentMetadata={agentMetadata} />
            <RoomAudioRenderer />
            <StartAudio label="Click to Start" />
        </LiveKitRoom>
    );
}

function AgentUI({ playerName, agentMetadata }: { playerName: string, agentMetadata: any }) {
    const { state, audioTrack } = useVoiceAssistant();
    const connectionState = useConnectionState();
    const { chatMessages, send } = useChat();
    const [message, setMessage] = useState('');

    const handleSend = async () => {
        if (!message.trim()) return;
        await send(message);
        setMessage('');
    };

    return (
        <div className="h-screen flex flex-col lg:flex-row bg-neutral-950 relative overflow-hidden">
            <div className={`absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] ${agentMetadata.gradient} opacity-10 pointer-events-none`} />

            {/* Left Panel: Visualizer & Status */}
            <div className="flex-1 flex flex-col relative z-10 border-r border-white/5">
                <header className="p-6 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
                        <div className="text-white/80 font-bold tracking-widest text-sm uppercase">{agentMetadata.name}</div>
                    </div>
                    <div className="text-neutral-400 text-sm">User: <span className="text-white font-medium">{playerName}</span></div>
                </header>

                <main className="flex-1 flex flex-col items-center justify-center gap-12 p-4">
                    <div className="relative group">
                        <div className={`absolute inset-0 bg-gradient-to-r ${agentMetadata.gradient} blur-3xl rounded-full transition-opacity duration-500 ${state === 'speaking' ? 'opacity-40' : 'opacity-0'}`} />

                        <div className={`w-64 h-64 rounded-full flex items-center justify-center transition-all duration-500 relative z-10 ${state === 'speaking' ? 'scale-105 border-white/50' : 'scale-100 border-neutral-800'} border-4 bg-neutral-900/80 backdrop-blur-sm`}>

                            {state === 'speaking' || state === 'listening' ? (
                                <div className="w-40 h-20 flex items-center justify-center">
                                    <BarVisualizer
                                        state={state}
                                        barCount={7}
                                        trackRef={audioTrack}
                                        className="h-full w-full"
                                        style={{ color: state === 'speaking' ? '#ffffff' : '#22c55e' }}
                                    />
                                </div>
                            ) : (
                                <div className="text-6xl animate-pulse">{agentMetadata.icon}</div>
                            )}

                            <div className={`absolute -bottom-6 px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider border shadow-lg transition-colors duration-300 ${state === 'speaking'
                                ? 'bg-white text-black border-white shadow-white/20'
                                : state === 'listening'
                                    ? 'bg-green-500 text-black border-green-500 shadow-green-500/20'
                                    : 'bg-neutral-800 text-neutral-400 border-neutral-700'
                                }`}>
                                {connectionState === ConnectionState.Connecting ? 'Connecting...' :
                                    state === 'speaking' ? 'Agent Speaking' :
                                        state === 'listening' ? 'Listening' :
                                            'Thinking...'}
                            </div>
                        </div>
                    </div>

                    <div className="text-center space-y-4 h-24 flex flex-col justify-center">
                        <AnimatePresence mode="wait">
                            {state === 'listening' && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="text-xl font-light text-neutral-400"
                                >
                                    Listening...
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </main>

                <footer className="p-6 text-center space-y-4">
                    <a
                        href={agentMetadata.demoUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`group relative inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r ${agentMetadata.gradient} text-white font-bold rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-white/20`}
                    >
                        <span className="text-xl">📺</span>
                        <span>Watch Demo Video</span>
                        <div className="absolute inset-0 rounded-xl ring-2 ring-white/20 group-hover:ring-white/40 transition-all" />
                    </a>
                    <div>
                        <Link href="/" className="text-neutral-500 hover:text-white text-xs transition-colors">Exit Session</Link>
                    </div>
                    <div className="text-xs font-bold text-neutral-500 font-mono tracking-tight max-w-lg mx-auto pt-4 border-t border-white/5">
                        To uphold strict data integrity, all backend operations are access-controlled and sandboxed, while the live environment exposes validated frontend interface.
                    </div>
                </footer>
            </div>

            {/* Right Panel: Chat Interface */}
            <div className="w-full lg:w-[400px] bg-neutral-900/50 backdrop-blur-xl border-l border-white/5 flex flex-col z-20">
                <div className="p-4 border-b border-white/5 bg-neutral-900/80">
                    <h3 className="text-white font-medium text-sm flex items-center gap-2">
                        <span>💬</span> Live Transcript & Chat
                    </h3>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-neutral-700 scrollbar-track-transparent">
                    {chatMessages.length === 0 && (
                        <div className="text-center text-neutral-500 text-sm mt-10 italic">
                            Start speaking or typing to see the conversation...
                        </div>
                    )}
                    {chatMessages.map((msg: any) => {
                        const isAgent = !msg.from?.isLocal;
                        return (
                            <div key={msg.timestamp} className={`flex flex-col ${isAgent ? 'items-start' : 'items-end'}`}>
                                <div className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${isAgent
                                    ? 'bg-neutral-800 text-neutral-200 rounded-tl-none'
                                    : `bg-gradient-to-r ${agentMetadata.gradient} text-white rounded-tr-none`
                                    }`}>
                                    {msg.message}
                                </div>
                                <span className="text-[10px] text-neutral-600 mt-1 px-1">
                                    {isAgent ? agentMetadata.name : 'You'}
                                </span>
                            </div>
                        );
                    })}
                </div>

                <div className="p-4 border-t border-white/5 bg-neutral-900/80">
                    <div className="relative">
                        <input
                            type="text"
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Type a message..."
                            className="w-full bg-neutral-800/50 border border-neutral-700 rounded-xl pl-4 pr-10 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-white/10 transition-all"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!message.trim()}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-neutral-400 hover:text-white disabled:opacity-50 transition-colors"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
