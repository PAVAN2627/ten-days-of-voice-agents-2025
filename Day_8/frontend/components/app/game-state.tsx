'use client';

import React from 'react';

interface GameCharacter {
  name: string;
  hp: number;
  max_hp: number;
  strength: number;
  intelligence: number;
  luck: number;
  inventory: string[];
  status: string;
}

interface GameNPC {
  name: string;
  role: string;
  attitude: string;
  alive: boolean;
  location: string;
}

interface GameLocation {
  name: string;
  description: string;
  paths: string[];
}

interface GameQuest {
  name: string;
  description: string;
  completed: boolean;
  active: boolean;
}

interface GameStateData {
  universe: string;
  player: GameCharacter;
  current_location: string;
  locations: { [key: string]: GameLocation };
  npcs: { [key: string]: GameNPC };
  quests: GameQuest[];
  events: Array<{ description: string; timestamp: string; location?: string }>;
  turn_count: number;
}

interface GameStateDisplayProps {
  gameState?: GameStateData;
  selectedTab?: 'character' | 'inventory' | 'quests' | 'world';
  onTabChange?: (tab: 'character' | 'inventory' | 'quests' | 'world') => void;
}

export const GameStateDisplay: React.FC<GameStateDisplayProps> = ({
  gameState,
  selectedTab = 'character',
  onTabChange,
}) => {
  if (!gameState) {
    return (
      <div className="rounded-lg bg-slate-900 border border-slate-700 p-6 text-center">
        <p className="text-slate-400">No active game. Start a new adventure!</p>
      </div>
    );
  }

  const universeColors: { [key: string]: string } = {
    fantasy: 'from-purple-600 to-purple-800',
    cyberpunk: 'from-pink-600 to-purple-800',
    space_opera: 'from-blue-600 to-blue-800',
    post_apocalypse: 'from-red-700 to-orange-800',
    horror: 'from-gray-900 to-black',
    romance_drama: 'from-rose-600 to-pink-800',
  };

  const gradientClass = universeColors[gameState.universe] || 'from-slate-600 to-slate-800';

  const healthPercent = (gameState.player.hp / gameState.player.max_hp) * 100;
  const healthColor =
    healthPercent > 50 ? 'bg-green-600' : healthPercent > 25 ? 'bg-yellow-600' : 'bg-red-600';

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'text-green-400';
      case 'injured':
        return 'text-yellow-400';
      case 'critical':
        return 'text-red-400';
      default:
        return 'text-slate-400';
    }
  };

  const getLocationNPCs = () => {
    return Object.values(gameState.npcs).filter(
      (npc) => npc.location === gameState.current_location && npc.alive
    );
  };

  const currentLoc = gameState.locations[gameState.current_location];

  return (
    <div className="rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className={`bg-gradient-to-r ${gradientClass} p-4 border-b border-slate-700`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-white capitalize">
              {gameState.universe.replace('_', ' ')}
            </h3>
            <p className="text-sm text-slate-200">Turn {gameState.turn_count}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-300">Currently at:</p>
            <p className="font-semibold text-white">{currentLoc?.name || 'Unknown'}</p>
          </div>
        </div>
      </div>

      {/* Character HP Bar - Always Visible */}
      <div className="bg-slate-950 border-b border-slate-700 p-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-lg font-bold text-white">{gameState.player.name}</h4>
          <span className={`text-sm font-semibold ${getStatusColor(gameState.player.status)}`}>
            {gameState.player.status}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex-1">
            <div className="bg-slate-700 rounded h-6 overflow-hidden border border-slate-600">
              <div
                className={`${healthColor} h-full transition-all duration-300 flex items-center justify-center text-xs font-bold text-white`}
                style={{ width: `${Math.max(healthPercent, 5)}%` }}
              >
                {healthPercent > 10 && `${gameState.player.hp}/${gameState.player.max_hp}`}
              </div>
            </div>
          </div>
          <span className="text-sm font-mono text-slate-300 whitespace-nowrap">
            {gameState.player.hp}/{gameState.player.max_hp} HP
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700 bg-slate-900">
        {(['character', 'inventory', 'quests', 'world'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange?.(tab)}
            className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors capitalize ${
              selectedTab === tab
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4 max-h-96 overflow-y-auto">
        {/* Character Stats */}
        {selectedTab === 'character' && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-800 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 uppercase tracking-wider">Strength</p>
                <p className="text-2xl font-bold text-orange-400">{gameState.player.strength}</p>
                <p className="text-xs text-slate-500">Physical Power</p>
              </div>
              <div className="bg-slate-800 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 uppercase tracking-wider">Intelligence</p>
                <p className="text-2xl font-bold text-blue-400">{gameState.player.intelligence}</p>
                <p className="text-xs text-slate-500">Knowledge</p>
              </div>
              <div className="bg-slate-800 rounded p-3 border border-slate-700">
                <p className="text-xs text-slate-400 uppercase tracking-wider">Luck</p>
                <p className="text-2xl font-bold text-green-400">{gameState.player.luck}</p>
                <p className="text-xs text-slate-500">Fortune</p>
              </div>
            </div>
          </div>
        )}

        {/* Inventory */}
        {selectedTab === 'inventory' && (
          <div className="space-y-2">
            <h4 className="font-semibold text-white mb-3">Inventory ({gameState.player.inventory.length} items)</h4>
            {gameState.player.inventory.length > 0 ? (
              <div className="grid grid-cols-1 gap-2">
                {gameState.player.inventory.map((item, idx) => (
                  <div key={idx} className="bg-slate-800 rounded px-3 py-2 border border-slate-700 flex items-center">
                    <span className="text-amber-400 mr-2">•</span>
                    <span className="text-slate-200 capitalize">{item}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500 italic">Empty</p>
            )}
          </div>
        )}

        {/* Quests */}
        {selectedTab === 'quests' && (
          <div className="space-y-3">
            <h4 className="font-semibold text-white mb-3">Quests ({gameState.quests.length})</h4>
            {gameState.quests.length > 0 ? (
              gameState.quests.map((quest, idx) => (
                <div
                  key={idx}
                  className={`rounded p-3 border ${
                    quest.completed
                      ? 'bg-green-900 border-green-700'
                      : quest.active
                        ? 'bg-blue-900 border-blue-700'
                        : 'bg-slate-800 border-slate-700'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className={quest.completed ? 'text-green-400' : quest.active ? 'text-blue-400' : 'text-slate-400'}>
                      {quest.completed ? '✓' : quest.active ? '◆' : '◇'}
                    </span>
                    <div className="flex-1">
                      <p className="font-semibold text-white">{quest.name}</p>
                      <p className="text-xs text-slate-300 mt-1">{quest.description}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-slate-500 italic">No quests</p>
            )}
          </div>
        )}

        {/* World Info */}
        {selectedTab === 'world' && (
          <div className="space-y-4">
            {/* Current Location */}
            <div>
              <h5 className="font-semibold text-white mb-2">Current Location</h5>
              <div className="bg-slate-800 rounded p-3 border border-slate-700">
                <p className="font-semibold text-slate-100">{currentLoc?.name}</p>
                <p className="text-sm text-slate-300 mt-2">{currentLoc?.description}</p>
                {currentLoc?.paths && currentLoc.paths.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-600">
                    <p className="text-xs text-slate-400 uppercase">Paths to:</p>
                    <p className="text-sm text-slate-300">{currentLoc.paths.join(', ')}</p>
                  </div>
                )}
              </div>
            </div>

            {/* NPCs Here */}
            {getLocationNPCs().length > 0 && (
              <div>
                <h5 className="font-semibold text-white mb-2">People Here</h5>
                <div className="space-y-2">
                  {getLocationNPCs().map((npc, idx) => (
                    <div key={idx} className="bg-slate-800 rounded p-3 border border-slate-700">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-slate-100">{npc.name}</p>
                          <p className="text-xs text-slate-400">{npc.role}</p>
                        </div>
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${
                            npc.attitude === 'friendly'
                              ? 'bg-green-900 text-green-300'
                              : npc.attitude === 'hostile'
                                ? 'bg-red-900 text-red-300'
                                : 'bg-slate-700 text-slate-300'
                          }`}
                        >
                          {npc.attitude}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
