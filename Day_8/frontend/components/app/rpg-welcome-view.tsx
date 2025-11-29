'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/livekit/button';
import { motion } from 'motion/react';

const universes = [
  {
    id: 'fantasy',
    name: 'Fantasy Realm',
    icon: '🐉',
    description: 'Dragons, wizards, and magical quests',
    color: 'from-purple-600 to-pink-600',
  },
  {
    id: 'space_opera',
    name: 'Space Opera',
    icon: '🚀',
    description: 'Spaceships, aliens, and galactic adventures',
    color: 'from-blue-600 to-cyan-600',
  },
  {
    id: 'cyberpunk',
    name: 'Cyberpunk City',
    icon: '🌃',
    description: 'Neon streets, hackers, and high-tech danger',
    color: 'from-pink-600 to-purple-600',
  },
  {
    id: 'horror',
    name: 'Horror Mansion',
    icon: '👻',
    description: 'Ghosts, monsters, and terrifying mysteries',
    color: 'from-gray-700 to-red-900',
  },
  {
    id: 'post_apocalypse',
    name: 'Post-Apocalypse',
    icon: '☢️',
    description: 'Wasteland survival and zombie encounters',
    color: 'from-orange-700 to-red-800',
  },
];

interface RPGWelcomeViewProps {
  onStartCall: () => void;
}

export const RPGWelcomeView = ({
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & RPGWelcomeViewProps) => {
  const [selectedUniverse, setSelectedUniverse] = useState<string | null>(null);
  const [playerName, setPlayerName] = useState('');
  const [playerGender, setPlayerGender] = useState<string>('');
  const [welcomeAudio, setWelcomeAudio] = useState<HTMLAudioElement | null>(null);
  const [isMusicPlaying, setIsMusicPlaying] = useState(true);

  // Start welcome music when component mounts
  useEffect(() => {
    console.log('🎵 Starting welcome screen music');
    
    const audio = new Audio('/music/start.mp3');
    audio.loop = true; // Loop the welcome music
    audio.volume = 0.25; // 25% volume - slightly higher for welcome screen
    audio.preload = 'auto';
    
    // Add event listeners
    audio.addEventListener('loadeddata', () => {
      console.log('✅ Welcome music loaded');
    });
    
    // Note: Error event might fire even if music plays (browser quirk)
    // Removed error listener to avoid false warnings
    
    // Try to play music
    const playMusic = async () => {
      try {
        await audio.play();
        console.log('🎵 Welcome music playing');
      } catch (error) {
        console.log('⚠️ Autoplay blocked - music will start on user interaction');
        // Start music on first interaction
        const startMusic = () => {
          audio.play()
            .then(() => console.log('🎵 Welcome music started'))
            .catch(e => console.error('Music play failed:', e));
          document.removeEventListener('click', startMusic);
          document.removeEventListener('keydown', startMusic);
        };
        document.addEventListener('click', startMusic);
        document.addEventListener('keydown', startMusic);
      }
    };
    
    playMusic();
    setWelcomeAudio(audio);
    
    // Cleanup: stop music when leaving welcome screen
    return () => {
      console.log('🛑 Stopping welcome music');
      audio.pause();
      audio.src = '';
    };
  }, []);

  const handleStart = () => {
    if (selectedUniverse && playerName && playerGender) {
      // Stop welcome music before starting game
      if (welcomeAudio) {
        welcomeAudio.pause();
        welcomeAudio.src = '';
      }
      
      // Store selection in sessionStorage (cleared when tab closes)
      sessionStorage.setItem('selectedUniverse', selectedUniverse);
      sessionStorage.setItem('playerName', playerName);
      sessionStorage.setItem('playerGender', playerGender);
      sessionStorage.setItem('autoStart', 'true');
      onStartCall();
    }
  };

  return (
    <div ref={ref} className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4" suppressHydrationWarning>
      {/* Music Control Button - Top Right */}
      {welcomeAudio && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          onClick={() => {
            if (welcomeAudio.paused) {
              welcomeAudio.play();
              setIsMusicPlaying(true);
            } else {
              welcomeAudio.pause();
              setIsMusicPlaying(false);
            }
          }}
          className="fixed right-4 top-4 z-50 bg-black/50 hover:bg-black/70 backdrop-blur-sm text-white p-3 rounded-full border border-white/20 transition-all hover:scale-110"
          title={isMusicPlaying ? 'Pause Music' : 'Play Music'}
        >
          {isMusicPlaying ? '🎵' : '🔇'}
        </motion.button>
      )}
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-6xl w-full"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-block mb-4"
          >
            <div className="text-8xl mb-4">🎲</div>
          </motion.div>
          <h1 className="text-6xl font-bold text-white mb-4 font-serif">
            Voice Game Master
          </h1>
          <p className="text-xl text-purple-200 max-w-2xl mx-auto">
            Choose your universe and embark on an epic voice-driven RPG adventure
          </p>
        </div>

        {/* Player Info Inputs */}
        <div className="mb-8 max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Name Input */}
          <div>
            <label className="block text-purple-200 mb-2 text-sm font-medium">
              Your Character Name *
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              placeholder="Enter your name"
              className="w-full px-4 py-3 bg-slate-800/50 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
              autoComplete="off"
            />
          </div>

          {/* Gender Selection */}
          <div>
            <label className="block text-purple-200 mb-2 text-sm font-medium">
              Gender *
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPlayerGender('male')}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                  playerGender === 'male'
                    ? 'bg-blue-600 border-blue-400 text-white'
                    : 'bg-slate-800/50 border-purple-500/30 text-purple-200 hover:border-purple-500/60'
                }`}
              >
                👨 Male
              </button>
              <button
                type="button"
                onClick={() => setPlayerGender('female')}
                className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                  playerGender === 'female'
                    ? 'bg-pink-600 border-pink-400 text-white'
                    : 'bg-slate-800/50 border-purple-500/30 text-purple-200 hover:border-purple-500/60'
                }`}
              >
                👩 Female
              </button>
            </div>
          </div>
        </div>

        {/* Universe Selection Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
          {universes.map((universe, index) => {
            // Background images for each universe
            const backgroundImages = {
              fantasy: '/backgrounds/fantasy.png',
              space_opera: '/backgrounds/space.png',
              cyberpunk: '/backgrounds/cyberpunk.png',
              horror: '/backgrounds/horror.png',
              post_apocalypse: '/backgrounds/apocalypse.png',
            };
            
            const bgImage = backgroundImages[universe.id as keyof typeof backgroundImages];
            
            return (
              <motion.button
                key={universe.id}
                type="button"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                onClick={() => setSelectedUniverse(universe.id)}
                className={`relative p-6 rounded-xl border-2 transition-all duration-300 overflow-hidden ${
                  selectedUniverse === universe.id
                    ? 'border-white shadow-2xl shadow-purple-500/50 scale-105'
                    : 'border-purple-500/30 hover:border-purple-500/60 hover:scale-102'
                }`}
                style={{
                  backgroundImage: `linear-gradient(to bottom, rgba(0,0,0,0.6), rgba(0,0,0,0.8)), url(${bgImage})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                }}
              >
                {selectedUniverse === universe.id && (
                  <motion.div
                    layoutId="selected"
                    className="absolute inset-0 bg-white/10 rounded-xl"
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
                <div className="relative z-10">
                  <div className="text-5xl mb-3">{universe.icon}</div>
                  <h3 className="text-xl font-bold text-white mb-2 drop-shadow-lg">{universe.name}</h3>
                  <p className="text-sm text-white drop-shadow-md">{universe.description}</p>
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Start Button */}
        <div className="text-center">
          <Button
            variant="primary"
            size="lg"
            onClick={handleStart}
            disabled={!selectedUniverse || !playerName || !playerGender}
            className={`px-12 py-6 text-xl font-bold rounded-xl transition-all duration-300 ${
              selectedUniverse && playerName && playerGender
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg shadow-purple-500/50'
                : 'bg-gray-600 cursor-not-allowed opacity-50'
            }`}
          >
            {!playerName || !playerGender
              ? '📝 Enter Name & Gender'
              : !selectedUniverse
              ? '👆 Select a Universe'
              : '🎮 Begin Adventure'}
          </Button>
        </div>

        {/* Footer Info */}
        <div className="mt-12 text-center">
          <div className="inline-block bg-slate-800/50 backdrop-blur-sm rounded-lg px-6 py-4 border border-purple-500/30">
            <p className="text-purple-200 text-sm mb-2">
              <strong>🎙️ Voice-Powered RPG Features:</strong>
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-purple-300">
              <div>✨ Character Stats</div>
              <div>🎒 Inventory System</div>
              <div>🎲 Dice Rolling</div>
              <div>💾 Save/Load Games</div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
