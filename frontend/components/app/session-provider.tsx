'use client';

import { createContext, useContext, useMemo, useState } from 'react';
import { RoomContext } from '@livekit/components-react';
import { APP_CONFIG_DEFAULTS, type AppConfig } from '@/app-config';
import { useRoom } from '@/hooks/useRoom';

const SessionContext = createContext<{
  appConfig: AppConfig;
  isSessionActive: boolean;
  selectedAgent: string | undefined;
  startSession: (agentId?: string) => void;
  endSession: () => void;
  setSelectedAgent: (agentId: string) => void;
}>({
  appConfig: APP_CONFIG_DEFAULTS,
  isSessionActive: false,
  selectedAgent: undefined,
  startSession: () => {},
  endSession: () => {},
  setSelectedAgent: () => {},
});

interface SessionProviderProps {
  appConfig: AppConfig;
  children: React.ReactNode;
}

export const SessionProvider = ({ appConfig, children }: SessionProviderProps) => {
  const [selectedAgent, setSelectedAgent] = useState<string | undefined>(undefined);
  
  // Update appConfig with selected agent
  const configWithAgent = useMemo(
    () => ({
      ...appConfig,
      agentName: selectedAgent,
    }),
    [appConfig, selectedAgent]
  );

  const { room, isSessionActive, startSession: baseStartSession, endSession } = useRoom(configWithAgent);
  
  const startSession = (agentId?: string) => {
    if (agentId) {
      setSelectedAgent(agentId);
    }
    baseStartSession();
  };

  const contextValue = useMemo(
    () => ({
      appConfig: configWithAgent,
      isSessionActive,
      selectedAgent,
      startSession,
      endSession,
      setSelectedAgent,
    }),
    [configWithAgent, isSessionActive, selectedAgent, startSession, endSession]
  );

  return (
    <RoomContext.Provider value={room}>
      <SessionContext.Provider value={contextValue}>{children}</SessionContext.Provider>
    </RoomContext.Provider>
  );
};

export function useSession() {
  return useContext(SessionContext);
}
