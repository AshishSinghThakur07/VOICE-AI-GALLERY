'use client';

import { useState } from 'react';
import { Button } from '@/components/livekit/button';
import { cn } from '@/lib/utils';

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  day: number;
  available: boolean;
}

export const AGENTS: Agent[] = [
  {
    id: 'day1',
    name: 'Basic Assistant',
    description: 'A helpful voice AI assistant for general conversations',
    icon: '🤖',
    day: 1,
    available: true,
  },
  {
    id: 'day2',
    name: 'Coffee Shop Barista',
    description: 'Order your favorite coffee with a friendly barista',
    icon: '☕',
    day: 2,
    available: true,
  },
  {
    id: 'day3',
    name: 'Wellness Companion',
    description: 'Daily health & wellness check-ins and support',
    icon: '💚',
    day: 3,
    available: true,
  },
  {
    id: 'day4',
    name: 'Active Recall Tutor',
    description: 'Learn, quiz, and teach-back with an AI tutor',
    icon: '📚',
    day: 4,
    available: true,
  },
  {
    id: 'day5',
    name: 'Sales Development Rep',
    description: 'SDR agent for answering questions and capturing leads',
    icon: '📞',
    day: 5,
    available: true,
  },
  {
    id: 'day6',
    name: 'Fraud Alert Agent',
    description: 'Bank fraud detection and verification assistant',
    icon: '🚨',
    day: 6,
    available: true,
  },
  {
    id: 'day7',
    name: 'Food Ordering',
    description: 'Order food and groceries with voice commands',
    icon: '🛒',
    day: 7,
    available: true,
  },
  {
    id: 'day8',
    name: 'Game Master',
    description: 'D&D-style interactive storytelling adventure',
    icon: '🎲',
    day: 8,
    available: true,
  },
  {
    id: 'day9',
    name: 'E-commerce Agent',
    description: 'Voice-driven shopping assistant with ACP protocol',
    icon: '🛍️',
    day: 9,
    available: true,
  },
];

interface AgentSelectorProps {
  onSelectAgent: (agentId: string) => void;
  selectedAgent?: string;
}

export function AgentSelector({ onSelectAgent, selectedAgent }: AgentSelectorProps) {
  const availableAgents = AGENTS.filter((agent) => agent.available);

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-center mb-2">🎙️ Choose Your Voice Agent</h2>
      <p className="text-muted-foreground text-center mb-8">
        Select an agent to start your conversation
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {AGENTS.map((agent) => (
          <button
            key={agent.id}
            onClick={() => agent.available && onSelectAgent(agent.id)}
            disabled={!agent.available}
            className={cn(
              'relative p-4 rounded-lg border-2 transition-all text-left',
              'hover:shadow-lg hover:scale-105',
              selectedAgent === agent.id
                ? 'border-primary bg-primary/10'
                : 'border-border bg-background',
              !agent.available && 'opacity-50 cursor-not-allowed'
            )}
          >
            <div className="flex items-start gap-3">
              <span className="text-3xl">{agent.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-semibold text-sm">{agent.name}</h3>
                  <span className="text-xs bg-muted px-2 py-0.5 rounded">Day {agent.day}</span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {agent.description}
                </p>
              </div>
            </div>
            {!agent.available && (
              <div className="absolute top-2 right-2">
                <span className="text-xs bg-muted px-2 py-1 rounded">Coming Soon</span>
              </div>
            )}
          </button>
        ))}
      </div>

      {selectedAgent && (
        <div className="text-center">
          <Button
            variant="primary"
            size="lg"
            onClick={() => onSelectAgent(selectedAgent)}
            className="w-64 font-mono"
          >
            Start Conversation
          </Button>
        </div>
      )}
    </div>
  );
}

