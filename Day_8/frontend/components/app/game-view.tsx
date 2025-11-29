'use client';

import React, { useState } from 'react';
import { GameStateDisplay } from './game-state';

interface Message {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  transcript?: string; // For voice transcripts
}

interface GameViewProps {
  messages: Message[];
  gameState?: any;
  isListening?: boolean;
  isLoading?: boolean;
  onSendMessage?: (message: string) => void;
}

export const GameView: React.FC<GameViewProps> = ({
  messages,
  gameState,
  isListening = false,
  isLoading = false,
  onSendMessage,
}) => {
  const [selectedTab, setSelectedTab] = useState<'character' | 'inventory' | 'quests' | 'world'>(
    'character'
  );
  const [messageInput, setMessageInput] = useState('');

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      onSendMessage?.(messageInput);
      setMessageInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-900 flex flex-col">
      {/* Top Bar - Universe & Turn Info */}
      {gameState && (
        <div className="bg-gradient-to-r from-blue-900 to-purple-900 border-b border-slate-700 px-6 py-3 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white capitalize">
              {gameState.universe?.replace('_', ' ')} Adventure
            </h2>
            <p className="text-sm text-blue-200">Turn {gameState.turn_count || 0}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-300">Location:</p>
            <p className="font-semibold text-white">{gameState.locations?.[gameState.current_location]?.name || 'Unknown'}</p>
          </div>
        </div>
      )}

      {/* Main Content - 3 Column Layout */}
      <div className="flex-1 flex gap-4 overflow-hidden p-4">
        {/* Left Panel - Character Stats */}
        <div className="w-72 overflow-hidden flex flex-col">
          <GameStateDisplay
            gameState={gameState}
            selectedTab={selectedTab}
            onTabChange={setSelectedTab}
          />
        </div>

        {/* Center Panel - Story & Messages */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Story Messages */}
          <div className="flex-1 overflow-y-auto mb-4 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-6 space-y-4">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <p className="text-3xl mb-2">🎮</p>
                  <p className="text-slate-400">Waiting for your adventure to begin...</p>
                  <p className="text-sm text-slate-500 mt-2">
                    Speak to start your voice adventure or type to interact
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className="animate-fade-in">
                  {msg.type === 'agent' && (
                    <div className="bg-gradient-to-r from-purple-900 to-purple-800 rounded-lg p-4 border border-purple-700">
                      <p className="text-xs font-semibold text-purple-300 uppercase tracking-wider mb-2">
                        Game Master
                      </p>
                      <p className="text-slate-100 leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      <p className="text-xs text-purple-400 mt-2">
                        {msg.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  )}

                  {msg.type === 'user' && (
                    <div className="bg-gradient-to-r from-blue-900 to-blue-800 rounded-lg p-4 border border-blue-700">
                      <p className="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2">
                        Your Response
                      </p>
                      <p className="text-slate-100 leading-relaxed">{msg.content}</p>
                      {msg.transcript && (
                        <p className="text-xs text-blue-300 mt-2 italic">
                          Heard: "{msg.transcript}"
                        </p>
                      )}
                      <p className="text-xs text-blue-400 mt-2">
                        {msg.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  )}

                  {msg.type === 'system' && (
                    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                      <p className="text-xs text-slate-500">
                        {msg.content}
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}

            {isLoading && (
              <div className="flex items-center justify-center gap-2 p-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-200" />
                </div>
                <span className="text-sm text-slate-400">Game Master is thinking...</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg border border-slate-700 p-4 space-y-3">
            <div className="flex gap-2">
              <textarea
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your action or say anything (voice will auto-transcribe)..."
                className="flex-1 bg-slate-900 text-white placeholder-slate-500 rounded px-3 py-2 border border-slate-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                rows={2}
              />
              <button
                onClick={handleSendMessage}
                disabled={!messageInput.trim() || isLoading}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-700 text-white font-semibold rounded transition-all duration-200"
              >
                Send
              </button>
            </div>

            {/* Voice Status */}
            {isListening && (
              <div className="flex items-center gap-2 text-green-400 text-sm">
                <span className="flex gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse delay-100" />
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse delay-200" />
                </span>
                Listening...
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Quick Actions */}
        <div className="w-64 overflow-hidden flex flex-col">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg border border-slate-700 p-4 overflow-y-auto space-y-3">
            <h3 className="font-bold text-white uppercase text-sm tracking-wider">Quick Actions</h3>

            <div className="space-y-2">
              <button className="w-full px-3 py-2 bg-gradient-to-r from-green-900 to-green-800 hover:from-green-800 hover:to-green-700 text-green-100 text-sm font-semibold rounded border border-green-700 transition-all">
                🎲 Roll Dice
              </button>
              <button className="w-full px-3 py-2 bg-gradient-to-r from-orange-900 to-orange-800 hover:from-orange-800 hover:to-orange-700 text-orange-100 text-sm font-semibold rounded border border-orange-700 transition-all">
                📦 Check Inventory
              </button>
              <button className="w-full px-3 py-2 bg-gradient-to-r from-purple-900 to-purple-800 hover:from-purple-800 hover:to-purple-700 text-purple-100 text-sm font-semibold rounded border border-purple-700 transition-all">
                💾 Save Game
              </button>
              <button className="w-full px-3 py-2 bg-gradient-to-r from-blue-900 to-blue-800 hover:from-blue-800 hover:to-blue-700 text-blue-100 text-sm font-semibold rounded border border-blue-700 transition-all">
                🗺️ Show Map
              </button>
            </div>

            {/* Quick Info */}
            <div className="border-t border-slate-700 pt-3 mt-3">
              <h4 className="font-semibold text-white text-xs uppercase tracking-wider mb-2">
                Quick Stats
              </h4>

              {gameState && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Health:</span>
                    <span className="font-bold text-green-400">
                      {gameState.player?.hp || 0}/{gameState.player?.max_hp || 100}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Status:</span>
                    <span
                      className={`font-semibold ${
                        gameState.player?.status === 'Healthy'
                          ? 'text-green-400'
                          : gameState.player?.status === 'Injured'
                            ? 'text-yellow-400'
                            : 'text-red-400'
                      }`}
                    >
                      {gameState.player?.status || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Items:</span>
                    <span className="font-bold text-amber-400">
                      {gameState.player?.inventory?.length || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Quests:</span>
                    <span className="font-bold text-blue-400">
                      {gameState.quests?.length || 0}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Recent Events */}
            {gameState?.events && gameState.events.length > 0 && (
              <div className="border-t border-slate-700 pt-3 mt-3">
                <h4 className="font-semibold text-white text-xs uppercase tracking-wider mb-2">
                  Recent Events
                </h4>
                <div className="space-y-1 text-xs text-slate-400">
                  {gameState.events.slice(-3).map((event: any, idx: number) => (
                    <p key={idx} className="text-slate-500 line-clamp-2">
                      • {event.description}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
