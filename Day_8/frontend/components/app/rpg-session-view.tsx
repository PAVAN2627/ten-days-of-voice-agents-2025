'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden' as const,
  animate: 'visible' as const,
  exit: 'hidden' as const,
  transition: {
    duration: 0.3,
    delay: 0.5,
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

// Character Stats Panel Component
function CharacterStatsPanel() {
  const [stats, setStats] = useState({
    name: 'Adventurer',
    hp: 100,
    maxHp: 100,
    strength: 12,
    intelligence: 12,
    luck: 12,
    inventory: [] as string[],
    location: 'Unknown',
    universe: 'fantasy',
  });
  const [isExpanded, setIsExpanded] = useState(true);

  // Parse game state from chat messages
  const messages = useChatMessages();
  
  useEffect(() => {
    // Get stored player name, gender, and universe from sessionStorage
    const playerName = sessionStorage.getItem('playerName') || 'Adventurer';
    const playerGender = sessionStorage.getItem('playerGender') || 'neutral';
    const selectedUniverse = sessionStorage.getItem('selectedUniverse') || 'fantasy';
    
    // Initialize with default stats for horror universe
    setStats(prev => ({
      ...prev,
      name: playerName,
      universe: selectedUniverse,
      strength: selectedUniverse === 'horror' ? 10 : 12,
      intelligence: selectedUniverse === 'horror' ? 10 : 12,
      luck: selectedUniverse === 'horror' ? 10 : 12,
    }));
    
    // Store player info for easy access
    if (playerName && playerGender && selectedUniverse) {
      console.log('Player ready:', { playerName, playerGender, selectedUniverse });
    }

    // Parse latest messages for game state updates
    const lastMessages = messages.slice(-10);
    lastMessages.forEach(msg => {
      const text = msg.message || '';
      const textLower = text.toLowerCase();
      
      // Parse HP from multiple formats (case insensitive)
      // Catch-all pattern that finds any "X/Y" or "X out of Y" after health-related words
      const hpPatterns = [
        /health[:\s]+(\d+)\/(\d+)/i,                                    // "Health: 80/100"
        /health\s+(?:is\s+now|drops?\s+to|is|now)\s+(\d+)\/(\d+)/i,    // "health is now 80/100"
        /your\s+health\s+(?:is\s+now|drops?\s+to|is)\s+(\d+)\/(\d+)/i, // "your health is now 80/100"
        /health\s+(?:is\s+now|drops?\s+to|is|now)\s+(\d+)\s+out\s+of\s+(\d+)/i,  // "health is now 80 out of 100"
        /your\s+health\s+(?:is\s+now|drops?\s+to|is)\s+(\d+)\s+out\s+of\s+(\d+)/i, // "your health is now 80 out of 100"
        /(\d+)\/(\d+)/i,                                                // Fallback: any "X/Y"
      ];
      
      let hpMatch = null;
      for (const pattern of hpPatterns) {
        hpMatch = text.match(pattern);
        if (hpMatch) {
          console.log('🔍 Pattern matched:', pattern, 'in text:', text.substring(0, 150));
          break;
        }
      }
      
      if (hpMatch) {
        const newHp = parseInt(hpMatch[1]);
        const newMaxHp = parseInt(hpMatch[2]);
        
        // Calculate status based on HP percentage
        const hpPercent = (newHp / newMaxHp) * 100;
        let status = 'Healthy';
        if (hpPercent <= 0) status = 'Dead';
        else if (hpPercent <= 30) status = 'Critical';
        else if (hpPercent <= 60) status = 'Injured';
        
        console.log('✅ HP Update detected:', newHp, '/', newMaxHp, 'Status:', status);
        setStats(prev => ({
          ...prev,
          hp: newHp,
          maxHp: newMaxHp,
        }));
      } else {
        console.log('❌ No HP pattern matched in:', text.substring(0, 150));
      }
      // If no explicit HP value, don't try to calculate damage
      // The backend should always send the final HP value
      
      // Parse healing: "You heal X HP" or "✨ You heal X HP"
      const healMatch = text.match(/(?:✨\s*)?you\s+heal\s+(\d+)\s+(?:hp|health)/i);
      if (healMatch) {
        const healing = parseInt(healMatch[1]);
        console.log('Healing detected:', healing);
        setStats(prev => ({
          ...prev,
          hp: Math.min(prev.maxHp, prev.hp + healing),
        }));
      }

      // Parse location - improved patterns
      const locationPatterns = [
        /you\s+(?:enter|arrive\s+at|walk\s+into|go\s+(?:into|to)|come\s+to|step\s+into)\s+(?:the\s+)?([^.!?,]+?)(?:\.|!|\?|,|\s+where|\s+with|\s+as|\s+and)/i,
        /welcome.*?you\s+enter\s+(?:the\s+)?([^.!?,]+?)(?:\.|!|\?|,)/i,
        /welcome.*?to\s+(?:the\s+)?([^.!?,]+?)(?:\.|!|\?)/i,
        /you\s+(?:find\s+yourself|are)\s+(?:in|at|on)\s+(?:the\s+)?([^.!?,]+?)(?:\.|!|\?|,)/i,
      ];
      
      let locationFound = false;
      for (const pattern of locationPatterns) {
        const locationMatch = text.match(pattern);
        if (locationMatch) {
          const location = locationMatch[1].trim();
          // Filter out common words that aren't locations
          if (location.length > 3 && !location.match(/\b(you|the|a|an|with|where|as|now|health)\b/i)) {
            console.log('📍 Location detected:', location, 'from pattern:', pattern, 'in text:', text.substring(0, 150));
            setStats(prev => {
              console.log('📍 Updating location from', prev.location, 'to', location);
              return {
                ...prev,
                location: location,
              };
            });
            locationFound = true;
            break;
          }
        }
      }
      if (!locationFound && (text.toLowerCase().includes('welcome') || text.toLowerCase().includes('enter'))) {
        console.log('❌ Location NOT detected in message:', text.substring(0, 200));
      }

      // Parse starting inventory with multiple formats
      let startingInventoryMatch = null;
      
      // Format 1: "You have: item1, item2, item3"
      startingInventoryMatch = text.match(/you\s+have:\s*([^.!?]+)/i);
      
      // Format 2: "You have a flashlight, an old key, and a medkit"
      if (!startingInventoryMatch) {
        startingInventoryMatch = text.match(/you\s+have\s+(?:a|an|the|some)\s+([^.!?]+)/i);
      }
      
      // Format 3: "You've got a flashlight, an old key, and a medkit"
      if (!startingInventoryMatch) {
        startingInventoryMatch = text.match(/you'?ve\s+got\s+(?:a|an|the|some)?\s*([^.!?]+)/i);
      }
      
      // Format 4: "Your inventory: item1, item2, item3"
      if (!startingInventoryMatch) {
        startingInventoryMatch = text.match(/your\s+inventory:\s*([^.!?]+)/i);
      }
      
      if (startingInventoryMatch) {
        const itemsList = startingInventoryMatch[1].trim();
        // Split by comma or "and"
        const items = itemsList
          .split(/,|\s+and\s+/)
          .map(item => item.trim())
          .map(item => item.replace(/^(a|an|the|some)\s+/i, '')) // Remove articles
          .filter(item => item.length > 2 && !item.match(/\b(what|do|you|next)\b/i)); // Filter out non-items
        
        if (items.length > 0) {
          console.log('🎒 Starting inventory detected:', items, 'from:', text.substring(0, 150));
          setStats(prev => ({
            ...prev,
            inventory: [...new Set([...prev.inventory, ...items])],
          }));
        }
      }
      
      // Parse inventory additions with multiple patterns
      const itemPatterns = [
        /📦\s*you\s+acquired:\s*([^.!?]+)/i,                           // "📦 You acquired: medkit"
        /you\s+(?:acquired|found|picked\s+up|got|obtain|receive):\s*([^.!?]+)/i,     // "You acquired: medkit"
        /you\s+(?:find|spot|grab|pick\s+up|take|get)\s+(?:a|an|the|some)?\s*([a-z\s]+?)(?:\.|!|\?|,|—|\s+and)/i, // "You find a silver locket"
        /(?:a|an|the)\s+([a-z\s]+?)\s+(?:appears?|is\s+yours?|joins?\s+your\s+inventory)/i, // "A silver locket appears"
      ];
      
      for (const pattern of itemPatterns) {
        const itemMatch = text.match(pattern);
        if (itemMatch) {
          const item = itemMatch[1].trim()
            .replace(/^📦\s*/, '')
            .replace(/^(a|an|the|some)\s+/i, '')
            .replace(/\s+$/, '');
          
          // Only add if it looks like an item (not too long, not a sentence)
          if (item.length > 2 && item.length < 40 && !item.match(/\b(you|your|are|is|was|were|have|has|had)\b/i)) {
            console.log('🎒 Item acquired:', item, 'from:', text.substring(0, 100));
            setStats(prev => ({
              ...prev,
              inventory: [...new Set([...prev.inventory, item])],
            }));
            break;
          }
        }
      }

      // Parse inventory removals with multiple patterns
      const removalPatterns = [
        /(?:✅\s*)?you\s+used:\s*([^.!?]+)/i,                          // "✅ You used: medkit"
        /you\s+(?:use|consume|drink|eat|apply)\s+(?:the|your|a|an)?\s*([^.!?]+)/i, // "You use the medkit"
        /(?:the|your|a|an)\s+([^.!?]+?)\s+(?:is\s+used|was\s+consumed|disappears?)/i, // "The medkit is used"
      ];
      
      for (const pattern of removalPatterns) {
        const usedMatch = text.match(pattern);
        if (usedMatch) {
          const usedItem = usedMatch[1].trim()
            .replace(/^✅\s*/, '')
            .replace(/^(a|an|the|your)\s+/i, '')
            .replace(/\s+$/, '');
          
          console.log('🗑️ Item used/removed:', usedItem, 'from:', text.substring(0, 100));
          
          // Try to match the item in inventory (case insensitive, partial match)
          setStats(prev => {
            const matchingItem = prev.inventory.find(item => 
              item.toLowerCase().includes(usedItem.toLowerCase()) || 
              usedItem.toLowerCase().includes(item.toLowerCase())
            );
            
            if (matchingItem) {
              console.log('✅ Removing item from inventory:', matchingItem);
              return {
                ...prev,
                inventory: prev.inventory.filter(i => i !== matchingItem),
              };
            }
            
            return prev;
          });
          break;
        }
      }

      // Parse stat changes: "💪 Strength increased by 2! Now: 12"
      const statPatterns = [
        /💪\s*strength\s+(?:increased|decreased)\s+by\s+(\d+).*?now:\s*(\d+)/i,
        /🧠\s*intelligence\s+(?:increased|decreased)\s+by\s+(\d+).*?now:\s*(\d+)/i,
        /🍀\s*luck\s+(?:increased|decreased)\s+by\s+(\d+).*?now:\s*(\d+)/i,
      ];
      
      for (const pattern of statPatterns) {
        const statMatch = text.match(pattern);
        if (statMatch) {
          const newValue = parseInt(statMatch[2]);
          const statType = text.includes('💪') ? 'strength' : text.includes('🧠') ? 'intelligence' : 'luck';
          console.log(`📊 ${statType} changed to:`, newValue);
          setStats(prev => ({
            ...prev,
            [statType]: newValue,
          }));
          break;
        }
      }
    });
  }, [messages]);

  const universeColors = {
    fantasy: 'from-purple-600 to-pink-600',
    space_opera: 'from-blue-600 to-cyan-600',
    cyberpunk: 'from-pink-600 to-purple-600',
    horror: 'from-gray-700 to-red-900',
    romance_drama: 'from-rose-500 to-pink-500',
    post_apocalypse: 'from-orange-700 to-red-800',
  };

  const universeIcons = {
    fantasy: '🐉',
    space_opera: '🚀',
    cyberpunk: '🌃',
    horror: '👻',
    romance_drama: '💕',
    post_apocalypse: '☢️',
  };

  const hpPercentage = (stats.hp / stats.maxHp) * 100;
  const hpColor = hpPercentage > 60 ? 'bg-green-500' : hpPercentage > 30 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      className="fixed left-4 top-4 z-50 w-80"
    >
      <div className={`bg-gradient-to-br ${universeColors[stats.universe as keyof typeof universeColors] || universeColors.fantasy} rounded-xl shadow-2xl border-2 border-white/20 backdrop-blur-sm`}>
        {/* Header */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full p-4 flex items-center justify-between text-white hover:bg-white/10 transition-colors rounded-t-xl"
        >
          <div className="flex items-center gap-3">
            <span className="text-3xl">{universeIcons[stats.universe as keyof typeof universeIcons] || '🎲'}</span>
            <div className="text-left">
              <h3 className="font-bold text-lg">{stats.name}</h3>
              <p className="text-xs text-white/80 capitalize">{stats.universe.replace('_', ' ')}</p>
            </div>
          </div>
          <motion.span
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            ▼
          </motion.span>
        </button>

        {/* Expandable Content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="p-4 pt-0 space-y-4 text-white">
                {/* HP Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold">❤️ Health</span>
                    <motion.span
                      animate={hpPercentage < 30 ? { scale: [1, 1.1, 1] } : {}}
                      transition={{ repeat: hpPercentage < 30 ? Infinity : 0, duration: 1 }}
                      className={hpPercentage < 30 ? 'text-red-400 font-bold' : ''}
                    >
                      {stats.hp}/{stats.maxHp}
                    </motion.span>
                  </div>
                  <div className="w-full bg-black/30 rounded-full h-3 overflow-hidden border border-white/20">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ 
                        width: `${hpPercentage}%`,
                        boxShadow: hpPercentage < 30 ? '0 0 10px rgba(239, 68, 68, 0.8)' : 'none'
                      }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      className={`h-full ${hpColor} relative`}
                    >
                      {/* Shine effect */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                    </motion.div>
                  </div>
                  {/* Status Indicator */}
                  <div className="mt-2 text-center">
                    <span className={`text-xs font-bold px-3 py-1 rounded-full ${
                      hpPercentage > 60 ? 'bg-green-500/30 text-green-200' :
                      hpPercentage > 30 ? 'bg-yellow-500/30 text-yellow-200' :
                      'bg-red-500/30 text-red-200'
                    }`}>
                      {hpPercentage > 60 ? '✨ Healthy' : hpPercentage > 30 ? '🩹 Injured' : '💀 Critical'}
                    </span>
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-black/20 rounded-lg p-2 text-center">
                    <div className="text-2xl">💪</div>
                    <div className="text-xs text-white/70">Strength</div>
                    <div className="font-bold">{stats.strength}</div>
                  </div>
                  <div className="bg-black/20 rounded-lg p-2 text-center">
                    <div className="text-2xl">🧠</div>
                    <div className="text-xs text-white/70">Intelligence</div>
                    <div className="font-bold">{stats.intelligence}</div>
                  </div>
                  <div className="bg-black/20 rounded-lg p-2 text-center">
                    <div className="text-2xl">🍀</div>
                    <div className="text-xs text-white/70">Luck</div>
                    <div className="font-bold">{stats.luck}</div>
                  </div>
                </div>

                {/* Location */}
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-xs text-white/70 mb-1">📍 Current Location</div>
                  <div className="font-semibold text-sm capitalize">{stats.location}</div>
                </div>

                {/* Inventory */}
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-xs text-white/70 mb-2">🎒 Inventory ({stats.inventory.length})</div>
                  {stats.inventory.length > 0 ? (
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {stats.inventory.map((item, idx) => (
                        <div key={idx} className="text-sm bg-white/10 rounded px-2 py-1 capitalize">
                          • {item}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-sm text-white/50 italic">Empty</div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

interface RPGSessionViewProps {
  appConfig: AppConfig;
}

export const RPGSessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & RPGSessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(true); // Always show chat
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [universe, setUniverse] = useState('fantasy');
  const [backgroundLoaded, setBackgroundLoaded] = useState(false);
  const [backgroundError, setBackgroundError] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);
  const [isMusicPlaying, setIsMusicPlaying] = useState(true);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  // Load universe from sessionStorage on mount
  useEffect(() => {
    const selectedUniverse = sessionStorage.getItem('selectedUniverse') || 'fantasy';
    setUniverse(selectedUniverse);
    console.log('Universe loaded for background:', selectedUniverse);
  }, []);

  // Background music player - starts automatically when universe is loaded
  useEffect(() => {
    if (!universe) return;
    
    console.log('🎵 Setting up background music for:', universe);
    
    // Create audio element for background music
    const audio = new Audio();
    audio.loop = true; // Auto-restart when music ends
    audio.volume = 0.10; // 15% volume - very low so agent voice is clear
    audio.preload = 'auto'; // Preload the audio file
    
    // Set music based on universe
    const musicFiles = {
      fantasy: '/music/fantasy.mp3',
      space_opera: '/music/space_opera.mp3',
      cyberpunk: '/music/cyberpunk.mp3',
      horror: '/music/horror.mp3',
      post_apocalypse: '/music/post_apocalypse.mp3',
    };
    
    const musicFile = musicFiles[universe as keyof typeof musicFiles] || musicFiles.fantasy;
    audio.src = musicFile;
    
    // Add event listeners for debugging
    audio.addEventListener('loadeddata', () => {
      console.log('✅ Music loaded:', musicFile);
    });
    
    // Note: Error event might fire even if music plays (browser quirk)
    // Removed error listener to avoid false warnings
    
    audio.addEventListener('ended', () => {
      console.log('🔁 Music ended, restarting...');
      audio.play(); // Restart music (backup for loop)
    });
    
    // Try to play music immediately
    const playMusic = async () => {
      try {
        await audio.play();
        console.log('🎵 Background music playing:', musicFile);
      } catch (error) {
        console.log('⚠️ Autoplay blocked - music will start on user interaction');
        // Add click listener to start music on first user interaction
        const startMusic = () => {
          audio.play()
            .then(() => console.log('🎵 Music started after user interaction'))
            .catch(e => console.error('Music play failed:', e));
          document.removeEventListener('click', startMusic);
          document.removeEventListener('keydown', startMusic);
        };
        document.addEventListener('click', startMusic);
        document.addEventListener('keydown', startMusic);
      }
    };
    
    // Start playing music
    playMusic();
    setAudioElement(audio);
    
    // Cleanup: stop music when component unmounts or universe changes
    return () => {
      console.log('🛑 Stopping music');
      audio.pause();
      audio.src = '';
      audio.remove();
    };
  }, [universe]);

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Background images based on universe (PNG format)
  const backgroundImages = {
    fantasy: '/backgrounds/fantasy.png',
    space_opera: '/backgrounds/space.png',
    cyberpunk: '/backgrounds/cyberpunk.png',
    horror: '/backgrounds/horror.png',
    romance_drama: '/backgrounds/love.png',
    post_apocalypse: '/backgrounds/apocalypse.png',
  };

  const backgroundImage = backgroundImages[universe as keyof typeof backgroundImages] || backgroundImages.fantasy;
  
  // Fallback gradients if images not loaded
  const fallbackGradients = {
    fantasy: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    space_opera: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
    cyberpunk: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    horror: 'linear-gradient(135deg, #1a1a1a 0%, #4a0000 50%, #000000 100%)',
    romance_drama: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    post_apocalypse: 'linear-gradient(135deg, #c94b4b 0%, #4b134f 100%)',
  };
  
  const fallbackGradient = fallbackGradients[universe as keyof typeof fallbackGradients] || fallbackGradients.fantasy;

  // Preload background image
  useEffect(() => {
    console.log('Starting to load background for universe:', universe);
    console.log('Background image path:', backgroundImage);
    console.log('Fallback gradient:', fallbackGradient);
    
    let isLoaded = false;
    setBackgroundLoaded(false);
    setBackgroundError(false);
    
    const img = new Image();
    img.onload = () => {
      console.log('✅ Background image loaded successfully:', backgroundImage);
      isLoaded = true;
      setBackgroundLoaded(true);
    };
    img.onerror = (e) => {
      console.error('❌ Failed to load background image:', backgroundImage, e);
      setBackgroundError(true);
    };
    img.src = backgroundImage;
    
    // Timeout fallback - if image takes too long (10 seconds), show gradient
    const timeout = setTimeout(() => {
      if (!isLoaded) {
        console.warn('⏱️ Background loading timeout, using gradient fallback');
        setBackgroundError(true);
      }
    }, 10000);
    
    return () => clearTimeout(timeout);
  }, [backgroundImage, universe, fallbackGradient]);

  // Debug: log render state
  console.log('Rendering with:', { universe, backgroundLoaded, backgroundError, backgroundImage, fallbackGradient });

  // Keep background persistent - once loaded, keep it
  const backgroundStyle = backgroundLoaded && !backgroundError 
    ? `url("${backgroundImage}") center / cover no-repeat, ${fallbackGradient}`
    : fallbackGradient;

  // Override body background and keep it persistent
  useEffect(() => {
    if (backgroundLoaded && !backgroundError) {
      // Image loaded successfully - set and keep it
      document.body.style.background = `url("${backgroundImage}") center / cover no-repeat fixed`;
      document.body.style.backgroundColor = '#000';
      console.log('🎨 Background applied to body:', backgroundImage);
    } else {
      // Use gradient fallback
      document.body.style.background = fallbackGradient;
      document.body.style.backgroundColor = '#000';
      console.log('🎨 Gradient fallback applied');
    }
    
    return () => {
      // Only clear on unmount
      document.body.style.background = '';
      document.body.style.backgroundColor = '';
    };
  }, [backgroundLoaded, backgroundError, backgroundImage, fallbackGradient]);

  return (
    <section 
      className="fixed inset-0 w-screen h-screen overflow-hidden z-0"
      style={{
        background: backgroundStyle,
        backgroundColor: '#000',
      }}
      {...props}
    >
      {/* Loading indicator */}
      {!backgroundLoaded && !backgroundError && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-[100]">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-pulse">🎲</div>
            <p className="text-white text-xl">Loading {universe.replace('_', ' ')} world...</p>
          </div>
        </div>
      )}
      
      {/* Dark overlay for readability */}
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[1px] z-[1]" />

      {/* Character Stats Panel */}
      <div className="relative z-[30]">
        <CharacterStatsPanel />
      </div>

      {/* Control Buttons - Top Center */}
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 flex gap-3">
        {/* Music Control Button */}
        {audioElement && (
          <motion.button
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            onClick={() => {
              if (audioElement.paused) {
                audioElement.play();
                setIsMusicPlaying(true);
              } else {
                audioElement.pause();
                setIsMusicPlaying(false);
              }
            }}
            className="bg-black/60 hover:bg-black/80 backdrop-blur-md text-white px-4 py-2 rounded-full border border-white/30 transition-all hover:scale-105 shadow-lg flex items-center gap-2"
            title={isMusicPlaying ? 'Pause Music' : 'Play Music'}
          >
            <span className="text-xl">{isMusicPlaying ? '🎵' : '🔇'}</span>
            <span className="text-sm font-medium">{isMusicPlaying ? 'Music On' : 'Music Off'}</span>
          </motion.button>
        )}
        
        {/* Restart Button */}
        <motion.button
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          onClick={() => {
            if (confirm('Restart your adventure? Your current progress will be lost.')) {
              window.location.reload();
            }
          }}
          className="bg-black/60 hover:bg-black/80 backdrop-blur-md text-white px-4 py-2 rounded-full border border-white/30 transition-all hover:scale-105 shadow-lg flex items-center gap-2"
          title="Restart Adventure"
        >
          <span className="text-xl">🔄</span>
          <span className="text-sm font-medium">Restart</span>
        </motion.button>
      </div>

      {/* Chat Transcript - Always Visible */}
      <div className="fixed inset-0 grid grid-cols-1 grid-rows-1 z-[20]">
        <Fade top className="absolute inset-x-4 top-0 h-40 z-30" />
        <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px] md:pl-96">
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg, idx) => {
              const isAgent = !msg.from?.isLocal;
              return (
                <motion.div
                  key={msg.id || idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${isAgent ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      isAgent
                        ? 'bg-purple-900/80 text-white border border-purple-500/30'
                        : 'bg-blue-600/80 text-white border border-blue-400/30'
                    } backdrop-blur-md shadow-lg`}
                  >
                    <div className="text-xs opacity-70 mb-1">
                      {isAgent ? '🎭 Game Master' : '👤 You'}
                    </div>
                    <div className="text-sm leading-relaxed">{msg.message}</div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </ScrollArea>
      </div>

      {/* Bottom Control Bar */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-[40] md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="bg-slate-900/90 backdrop-blur-md relative mx-auto max-w-2xl pb-3 md:pb-12 rounded-t-2xl border-t-2 border-purple-500/30 shadow-2xl">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>
    </section>
  );
};
