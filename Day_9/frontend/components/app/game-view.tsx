'use client';

import React, { useState } from 'react';
import type { Message } from '@livekit/components-react';
import { cn } from '@/lib/utils';
import { GameStateDisplay } from './game-state';

interface GameMessage {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  transcript?: string;
}

interface GameViewProps {
  messages?: GameMessage[];
  gameState?: any;
  isListening?: boolean;
  isLoading?: boolean;
  onSendMessage?: (message: string) => void;
  className?: string;
}

export function GameView({
  messages = [],
  gameState,
  isListening = false,
  isLoading = false,
  onSendMessage,
  className,
}: GameViewProps) {
  const [selectedTab, setSelectedTab] = useState<'character' | 'inventory' | 'quests' | 'world'>('character');
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      onSendMessage?.(inputValue);
      setInputValue('');
    }
  };

  const recentEvents = messages
    .filter((m) => m.type === 'system')
    .slice(-3)
    .reverse();

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'agent':
        return 'bg-purple-900 border-purple-700 text-purple-50';
      case 'user':
        return 'bg-blue-900 border-blue-700 text-blue-50';
      case 'system':
        return 'bg-slate-800 border-slate-700 text-slate-200';
      default:
        return 'bg-slate-800 border-slate-700 text-slate-200';
    }
  };

  return (
    <div className={cn('h-full w-full bg-slate-950', className)}>
      {/* Main 3-Column Layout */}
      <div className="flex h-full gap-4 p-4">
        {/* Left Panel - Character Stats */}
        <div className="w-72 flex-shrink-0">
          <GameStateDisplay gameState={gameState} selectedTab={selectedTab} onTabChange={setSelectedTab} />
        </div>

        {/* Center Panel - Story Messages */}
        <div className="flex-1 flex flex-col gap-4">
          {/* Story Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-lg px-4 py-3 border border-purple-500">
            <h2 className="text-white font-bold text-lg">
              {gameState?.universe ? `${gameState.universe.toUpperCase()}` : 'Game Story'} -{' '}
              <span className="text-purple-200">{gameState?.current_location || 'Unknown'}</span>
            </h2>
            {gameState?.turn_count && (
              <p className="text-purple-100 text-sm">Turn {gameState.turn_count}</p>
            )}
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto scrollbar-hide space-y-3 rounded-lg bg-slate-900 p-4 border border-slate-700">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <p className="text-slate-400 text-center">
                  Welcome to your adventure!
                  <br />
                  <span className="text-sm">Start by sending a message...</span>
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={msg.id || idx}
                  className={cn(
                    'rounded-lg px-4 py-3 border animate-fade-in',
                    getMessageColor(msg.type),
                    idx > messages.length - 3 ? 'delay-100' : ''
                  )}
                >
                  <div className="flex justify-between items-start gap-2 mb-1">
                    <p className="text-xs font-semibold uppercase tracking-widest opacity-75">
                      {msg.type === 'agent' ? '⚔️ Narrator' : msg.type === 'user' ? '🗣️ You' : '📢 System'}
                    </p>
                    <p className="text-xs opacity-50 font-mono">{msg.timestamp?.toLocaleTimeString() || ''}</p>
                  </div>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                  {msg.transcript && (
                    <p className="text-xs opacity-60 italic mt-2">Heard: "{msg.transcript}"</p>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-400">
                <p className="text-sm flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
                  Narrator is thinking...
                </p>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={isListening ? 'Listening...' : 'Type your action...'}
              disabled={isLoading}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 disabled:opacity-50"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors"
            >
              {isLoading ? 'Wait...' : 'Send'}
            </button>
          </div>
        </div>

        {/* Right Panel - Quick Actions & Events */}
        <div className="w-64 flex flex-col gap-4">
          {/* Quick Stats */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-3">Quick Stats</p>
            {gameState?.player ? (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">HP</span>
                  <span className="text-white font-mono">
                    {gameState.player.hp}/{gameState.player.max_hp}
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded h-4">
                  <div
                    className={`h-full rounded transition-all ${
                      gameState.player.hp / gameState.player.max_hp > 0.6
                        ? 'bg-green-500'
                        : gameState.player.hp / gameState.player.max_hp > 0.3
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                    }`}
                    style={{ width: `${(gameState.player.hp / gameState.player.max_hp) * 100}%` }}
                  />
                </div>
                {gameState.player.strength !== undefined && (
                  <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-700">
                    <div className="text-center">
                      <p className="text-xs text-slate-400">STR</p>
                      <p className="text-lg font-bold text-white">{gameState.player.strength}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">INT</p>
                      <p className="text-lg font-bold text-white">{gameState.player.intelligence}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-400">LCK</p>
                      <p className="text-lg font-bold text-white">{gameState.player.luck}</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No game state</p>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-4 border border-slate-700">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-3">Quick Actions</p>
            <div className="space-y-2">
              {['Look Around', 'Talk to NPC', 'Take Item', 'Check Quest'].map((action) => (
                <button
                  key={action}
                  onClick={() => setInputValue(action)}
                  className="w-full bg-slate-700 hover:bg-slate-600 text-white text-sm px-3 py-2 rounded transition-colors text-left"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>

          {/* Recent Events */}
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-4 border border-slate-700 flex-1 overflow-y-auto">
            <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-3">Recent Events</p>
            {recentEvents.length > 0 ? (
              <div className="space-y-2">
                {recentEvents.map((event, idx) => (
                  <p key={idx} className="text-xs text-slate-300 line-clamp-2">
                    {event.content}
                  </p>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500">No events yet</p>
            )}
          </div>

          {/* Voice Indicator */}
          {isListening && (
            <div className="bg-green-900 border border-green-700 rounded-lg p-3 flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-xs text-green-100 font-semibold">Listening...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
