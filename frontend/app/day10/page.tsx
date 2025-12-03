'use client';

import { useState, useCallback, useEffect } from 'react';
import { LiveKitRoom, RoomAudioRenderer, StartAudio, useVoiceAssistant, BarVisualizer, useConnectionState } from '@livekit/components-react';
import { AnimatePresence, motion } from 'framer-motion';
import { ConnectionState } from 'livekit-client';
import { toastAlert } from '@/components/livekit/alert-toast';

export default function Day10Page() {
    const [playerName, setPlayerName] = useState('');
    const [isJoined, setIsJoined] = useState(false);
    const [token, setToken] = useState('');
    const [url, setUrl] = useState('');
    const [isConnecting, setIsConnecting] = useState(false);

    const handleJoin = useCallback(async () => {
        if (!playerName.trim()) return;
        setIsConnecting(true);

        try {
            const response = await fetch('/api/connection-details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_config: {
                        agents: [{ agent_name: 'day10' }],
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
            toastAlert({
                title: 'Connection Error',
                description: err.message || 'Failed to connect to the game server.',
            });
        } finally {
            setIsConnecting(false);
        }
    }, [playerName]);

    if (!isJoined) {
        return (
            <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center p-4 font-sans relative overflow-hidden">
                {/* Background Effects */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-yellow-900/20 via-neutral-950 to-neutral-950 pointer-events-none" />

                <div className="max-w-md w-full space-y-8 relative z-10">
                    <div className="text-center space-y-2">
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="inline-block px-3 py-1 rounded-full bg-yellow-500/10 text-yellow-400 text-xs font-bold tracking-widest uppercase border border-yellow-500/20"
                        >
                            Day 10 Challenge
                        </motion.div>
                        <h1 className="text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-white to-neutral-500 mb-2">
                            Improv Battle
                        </h1>
                        <p className="text-neutral-400">Enter the stage and prove your wit.</p>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-neutral-900/50 backdrop-blur-xl p-8 rounded-2xl border border-neutral-800 shadow-2xl space-y-6"
                    >
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-neutral-300 mb-2">
                                Your Stage Name
                            </label>
                            <input
                                id="name"
                                type="text"
                                value={playerName}
                                onChange={(e) => setPlayerName(e.target.value)}
                                className="w-full px-4 py-3 bg-neutral-800/50 border border-neutral-700 rounded-xl focus:ring-2 focus:ring-yellow-400 focus:border-transparent outline-none transition-all text-white placeholder-neutral-600"
                                placeholder="e.g. Wayne Brady"
                                onKeyDown={(e) => e.key === 'Enter' && handleJoin()}
                                autoFocus
                            />
                        </div>

                        <button
                            onClick={handleJoin}
                            disabled={!playerName.trim() || isConnecting}
                            className="w-full py-4 px-4 bg-yellow-400 hover:bg-yellow-300 text-black font-bold rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95 shadow-[0_0_20px_rgba(250,204,21,0.3)] hover:shadow-[0_0_30px_rgba(250,204,21,0.5)]"
                        >
                            {isConnecting ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                    Connecting...
                                </span>
                            ) : (
                                'Start the Show'
                            )}
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
            onDisconnected={() => {
                setIsJoined(false);
                toastAlert({ title: 'Disconnected', description: 'The show has ended.' });
            }}
        >
            <ImprovGameUI playerName={playerName} />
            <RoomAudioRenderer />
            <StartAudio label="Click to Start Show" />
        </LiveKitRoom>
    );
}

function ImprovGameUI({ playerName }: { playerName: string }) {
    const { state, audioTrack } = useVoiceAssistant();
    const connectionState = useConnectionState();

    return (
        <div className="h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Background Ambience */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-purple-900/20 via-neutral-950 to-neutral-950 pointer-events-none" />

            {/* Header */}
            <header className="absolute top-0 left-0 right-0 p-6 flex justify-between items-center z-10">
                <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
                    <div className="text-white/80 font-bold tracking-widest text-sm uppercase">Live on Air</div>
                </div>
                <div className="text-neutral-400 text-sm">Contestant: <span className="text-white font-medium">{playerName}</span></div>
            </header>

            {/* Main Stage */}
            <main className="relative z-10 flex flex-col items-center gap-12 max-w-4xl w-full">

                {/* Host Avatar / Visualizer */}
                <div className="relative group">
                    {/* Glow Effect */}
                    <div className={`absolute inset-0 bg-yellow-400/20 blur-3xl rounded-full transition-opacity duration-500 ${state === 'speaking' ? 'opacity-100' : 'opacity-0'
                        }`} />

                    <div className={`w-64 h-64 rounded-full flex items-center justify-center transition-all duration-500 relative z-10 ${state === 'speaking' ? 'scale-105 border-yellow-400/50' : 'scale-100 border-neutral-800'
                        } border-4 bg-neutral-900/80 backdrop-blur-sm`}>

                        {state === 'speaking' || state === 'listening' ? (
                            <div className="w-40 h-20 flex items-center justify-center">
                                <BarVisualizer
                                    state={state}
                                    barCount={7}
                                    trackRef={audioTrack}
                                    className="h-full w-full"
                                    options={{ color: state === 'speaking' ? '#facc15' : '#22c55e' }}
                                />
                            </div>
                        ) : (
                            <div className="text-6xl animate-pulse">🎤</div>
                        )}

                        {/* Status Badge */}
                        <div className={`absolute -bottom-6 px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider border shadow-lg transition-colors duration-300 ${state === 'speaking'
                            ? 'bg-yellow-400 text-black border-yellow-400 shadow-yellow-400/20'
                            : state === 'listening'
                                ? 'bg-green-500 text-black border-green-500 shadow-green-500/20'
                                : 'bg-neutral-800 text-neutral-400 border-neutral-700'
                            }`}>
                            {connectionState === ConnectionState.Connecting ? 'Connecting...' :
                                state === 'speaking' ? 'Host Speaking' :
                                    state === 'listening' ? 'Your Turn' :
                                        'Thinking...'}
                        </div>
                    </div>
                </div>

                {/* Instructions / Prompts */}
                <div className="text-center space-y-4 h-24 flex flex-col justify-center">
                    <AnimatePresence mode="wait">
                        {state === 'listening' && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                className="text-3xl font-light text-green-400"
                            >
                                Go ahead, improvise!
                            </motion.div>
                        )}
                        {state === 'speaking' && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="text-xl text-yellow-400/80 italic"
                            >
                                Listen to the host...
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

            </main>

            {/* Footer Controls */}
            <footer className="absolute bottom-0 left-0 right-0 p-8 flex flex-col items-center justify-center z-10 text-neutral-500 text-xs gap-2">
                <div>Powered by Murf Falcon & LiveKit</div>
                <div className="text-xs font-bold text-neutral-500 font-mono tracking-tight max-w-lg text-center">
                    To uphold strict data integrity, all backend operations are access-controlled and sandboxed, while the live environment exposes validated frontend interface.
                </div>
            </footer>
        </div>
    );
}
