'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface GameCharacter {
  name: string;
  hp: number;
  max_hp: number;
  status?: string;
  strength?: number;
  intelligence?: number;
  luck?: number;
  inventory?: string[];
}

interface GameLocation {
  name: string;
  description?: string;
  paths?: string[];
}

interface GameNPC {
  name: string;
  role?: string;
  attitude?: string;
  alive?: boolean;
  location?: string;
}

interface GameQuest {
  name: string;
  description?: string;
  completed?: boolean;
  active?: boolean;
}

interface GameStateData {
  universe: string;
  player: GameCharacter;
  current_location: string;
  locations?: { [key: string]: GameLocation };
  npcs?: { [key: string]: GameNPC };
  quests?: GameQuest[];
  turn_count?: number;
}

interface GameStateDisplayProps {
  gameState?: GameStateData;
  selectedTab?: 'character' | 'inventory' | 'quests' | 'world';
  onTabChange?: (tab: 'character' | 'inventory' | 'quests' | 'world') => void;
}

const UNIVERSE_COLORS: Record<string, { from: string; to: string }> = {
  fantasy: { from: 'from-purple-600', to: 'to-purple-800' },
  cyberpunk: { from: 'from-pink-600', to: 'to-purple-800' },
  space_opera: { from: 'from-blue-600', to: 'to-blue-800' },
  post_apocalypse: { from: 'from-red-700', to: 'to-orange-800' },
  horror: { from: 'from-gray-900', to: 'to-black' },
  romance: { from: 'from-rose-600', to: 'to-pink-800' },
};

export function GameStateDisplay({
  gameState,
  selectedTab = 'character',
  onTabChange = () => {},
}: GameStateDisplayProps) {
  if (!gameState) {
    return (
      <div className="w-72 bg-gradient-to-br from-slate-800 to-slate-900 h-full flex items-center justify-center rounded-lg border border-slate-700">
        <p className="text-slate-400 text-sm">No game state</p>
      </div>
    );
  }

  const player = gameState.player;
  const healthPercent = (player.hp / player.max_hp) * 100;
  const healthColor =
    healthPercent > 60
      ? 'bg-green-500'
      : healthPercent > 30
        ? 'bg-yellow-500'
        : 'bg-red-500';

  const colors = UNIVERSE_COLORS[gameState.universe] || UNIVERSE_COLORS.fantasy;

  const renderCharacterTab = () => (
    <div className="space-y-4 p-4">
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-widest">Name</p>
        <p className="text-lg font-bold text-white mt-1">{player.name}</p>
      </div>

      {/* HP Bar */}
      <div>
        <div className="flex justify-between mb-2">
          <p className="text-xs text-slate-400 uppercase tracking-widest">Health</p>
          <p className="text-sm text-slate-300 font-mono">
            {player.hp}/{player.max_hp}
          </p>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-6 overflow-hidden border border-slate-600">
          <div
            className={`${healthColor} h-full flex items-center justify-center transition-all duration-300`}
            style={{ width: `${healthPercent}%` }}
          >
            {healthPercent > 10 && <span className="text-xs font-bold text-white">{healthPercent.toFixed(0)}%</span>}
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-1">{player.status || 'Healthy'}</p>
      </div>

      {/* Stats */}
      {(player.strength !== undefined || player.intelligence !== undefined || player.luck !== undefined) && (
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-widest mb-3">Stats</p>
          <div className="grid grid-cols-3 gap-2">
            {player.strength !== undefined && (
              <div className="bg-slate-700 rounded p-2 text-center">
                <p className="text-xs text-slate-400">STR</p>
                <p className="text-lg font-bold text-white">{player.strength}</p>
              </div>
            )}
            {player.intelligence !== undefined && (
              <div className="bg-slate-700 rounded p-2 text-center">
                <p className="text-xs text-slate-400">INT</p>
                <p className="text-lg font-bold text-white">{player.intelligence}</p>
              </div>
            )}
            {player.luck !== undefined && (
              <div className="bg-slate-700 rounded p-2 text-center">
                <p className="text-xs text-slate-400">LCK</p>
                <p className="text-lg font-bold text-white">{player.luck}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderInventoryTab = () => (
    <div className="space-y-3 p-4">
      <p className="text-xs text-slate-400 uppercase tracking-widest">Items ({player.inventory?.length || 0})</p>
      {player.inventory && player.inventory.length > 0 ? (
        <div className="space-y-2">
          {player.inventory.map((item, idx) => (
            <div key={idx} className="bg-slate-700 rounded px-3 py-2 flex items-center gap-2">
              <span className="text-sm text-white">{item}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">No items</p>
      )}
    </div>
  );

  const renderQuestsTab = () => (
    <div className="space-y-3 p-4">
      <p className="text-xs text-slate-400 uppercase tracking-widest">Quests</p>
      {gameState.quests && gameState.quests.length > 0 ? (
        <div className="space-y-2">
          {gameState.quests.map((quest, idx) => (
            <div key={idx} className="bg-slate-700 rounded px-3 py-2">
              <p className="text-sm font-semibold text-white flex items-center gap-2">
                {quest.completed ? '✓' : '○'} {quest.name}
              </p>
              {quest.description && <p className="text-xs text-slate-400 mt-1">{quest.description}</p>}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">No quests</p>
      )}
    </div>
  );

  const renderWorldTab = () => (
    <div className="space-y-3 p-4">
      <div>
        <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">Location</p>
        <p className="text-white font-semibold">{gameState.current_location}</p>
      </div>

      {gameState.locations && gameState.locations[gameState.current_location] && (
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">Description</p>
          <p className="text-sm text-slate-300">
            {gameState.locations[gameState.current_location].description}
          </p>
        </div>
      )}

      {gameState.npcs && Object.keys(gameState.npcs).length > 0 && (
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-widest mb-2">NPCs Here</p>
          {Object.values(gameState.npcs)
            .filter((npc: GameNPC) => npc.location === gameState.current_location)
            .map((npc: GameNPC, idx: number) => (
              <div key={idx} className="bg-slate-700 rounded px-3 py-2 mb-2">
                <p className="text-sm text-white font-semibold">{npc.name}</p>
                {npc.role && <p className="text-xs text-slate-400">{npc.role}</p>}
              </div>
            ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 h-full flex flex-col border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className={`bg-gradient-to-r ${colors.from} ${colors.to} px-4 py-3 text-white`}>
        <h3 className="font-bold capitalize text-lg">{gameState.universe}</h3>
        {gameState.turn_count !== undefined && <p className="text-xs text-slate-200">Turn {gameState.turn_count}</p>}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 px-4 pt-4 border-b border-slate-700">
        {(['character', 'inventory', 'quests', 'world'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => onTabChange(tab)}
            className={cn(
              'px-3 py-2 text-xs font-semibold uppercase tracking-widest transition-colors',
              selectedTab === tab
                ? `${colors.from} text-white rounded-t`
                : 'text-slate-400 hover:text-slate-300'
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {selectedTab === 'character' && renderCharacterTab()}
        {selectedTab === 'inventory' && renderInventoryTab()}
        {selectedTab === 'quests' && renderQuestsTab()}
        {selectedTab === 'world' && renderWorldTab()}
      </div>
    </div>
  );
}
