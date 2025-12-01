'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  LiveKitRoom,
  VideoConference,
  useConnectionState,
} from '@livekit/components-react';
import { ConnectionState } from 'livekit-client';
import { Mic, MicOff, RotateCcw, Volume2, VolumeX } from 'lucide-react';
import { MessageLogger } from './message-logger';
import { DebugPanel } from './debug-panel';
import { ChatOverlay } from './chat-overlay';

interface GameState {
  player_name: string | null;
  current_round: number;
  max_rounds: number;
  phase: 'intro' | 'awaiting_improv' | 'reacting' | 'done';
  rounds: any[];
}

export default function ImprovisationBattle() {
  const [isHydrated, setIsHydrated] = useState(false);
  const [playerName, setPlayerName] = useState('');
  const [gameStarted, setGameStarted] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [gameState, setGameState] = useState<GameState>({
    player_name: null,
    current_round: 0,
    max_rounds: 3,
    phase: 'intro',
    rounds: [],
  });

  // Update game state based on transcript messages
  useEffect(() => {
    if (!transcript || transcript.length === 0) return;

    const lastFewMessages = transcript.slice(-5).join(' ').toLowerCase();
    const allMessages = transcript.join(' ').toLowerCase();
    let newPhase: GameState['phase'] = gameState.phase;

    // Check if game is complete
    if (lastFewMessages.includes('wrap') || 
        lastFewMessages.includes('thanks for') || 
        lastFewMessages.includes('closing thoughts') ||
        lastFewMessages.includes('that\'s our last round')) {
      newPhase = 'done';
    } else if (lastFewMessages.includes('scenario') || lastFewMessages.includes('improvise')) {
      newPhase = 'awaiting_improv';
    }

    // Count COMPLETED rounds ONLY by looking for explicit "Round X complete!" markers
    let roundCount = 0;
    
    // ONLY count explicit completion markers from the backend
    const roundCompleteMatches = allMessages.match(/round (\d+) complete/gi);
    if (roundCompleteMatches) {
      // Count the number of unique "round X complete" messages
      roundCount = roundCompleteMatches.length;
    }
    
    // Cap at max rounds
    roundCount = Math.min(roundCount, 3);

    setGameState(prev => ({
      ...prev,
      current_round: roundCount,
      phase: newPhase,
    }));
  }, [transcript, gameState.phase]);
  const [isMicOn, setIsMicOn] = useState(true);
  const [isMusicOn, setIsMusicOn] = useState(true);
  const [token, setToken] = useState('');
  const [url, setUrl] = useState('');
  const [backgroundMusic, setBackgroundMusic] = useState<HTMLAudioElement | null>(null);
  const transcriptContainerRef = React.useRef<HTMLDivElement>(null);
  const processedMessagesRef = React.useRef<Set<string>>(new Set());

  // Ensure hydration is complete before rendering
  useEffect(() => {
    console.log('Setting isHydrated to true');
    setIsHydrated(true);
  }, []);

  // Auto-scroll transcript to bottom
  useEffect(() => {
    if (transcriptContainerRef.current) {
      transcriptContainerRef.current.scrollTop = transcriptContainerRef.current.scrollHeight;
    }
  }, [transcript]);

  // Initialize welcome music (plays on welcome screen)
  useEffect(() => {
    if (!isHydrated) return;
    
    const welcomeAudio = new Audio('/music/start.mp3');
    welcomeAudio.loop = true;
    welcomeAudio.volume = 0.1;
    welcomeAudio.preload = 'auto';
    
    // Try to autoplay welcome music
    if (!gameStarted) {
      welcomeAudio.play().catch(() => {
        console.log('Welcome music autoplay prevented - user interaction needed');
      });
    }
    
    setBackgroundMusic(welcomeAudio);

    return () => {
      welcomeAudio.pause();
      welcomeAudio.src = '';
    };
  }, [isHydrated, gameStarted]);

  // Switch to game music when game starts
  useEffect(() => {
    if (!isHydrated) return;
    
    if (gameStarted) {
      // Stop welcome music
      if (backgroundMusic) {
        backgroundMusic.pause();
      }
      
      // Start game music
      const gameAudio = new Audio('/music/backgroundmusic.mp3');
      gameAudio.loop = true;
      gameAudio.volume = 0.05; // Very low volume for game (5%)
      gameAudio.preload = 'auto';
      
      if (isMusicOn) {
        gameAudio.play().catch(() => {
          console.log('Game music autoplay prevented');
        });
      }
      
      setBackgroundMusic(gameAudio);
      
      return () => {
        gameAudio.pause();
        gameAudio.src = '';
      };
    }
  }, [gameStarted, isHydrated]);

  // Control music playback
  useEffect(() => {
    if (backgroundMusic) {
      if (isMusicOn) {
        backgroundMusic.play().catch(() => {
          console.log('Music autoplay prevented');
        });
      } else {
        backgroundMusic.pause();
      }
    }
  }, [isMusicOn, backgroundMusic]);

  // Get LiveKit credentials
  useEffect(() => {
    const getToken = async () => {
      try {
        const response = await fetch('/api/get-participant-token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: playerName || 'user' }),
        });
        const data = await response.json();
        if (data.token && data.url) {
          setToken(data.token);
          setUrl(data.url);
          
          // Add connection message to transcript with delay
          setTimeout(() => {
            console.log('Adding connection messages to transcript');
            setTranscript(prev => {
              const connectionMessages = [
                '📡 Voice connection established! Ready to start improvising...',
                '🎬 Say something to begin your improv battle!',
                '💡 Speak clearly and the host will respond to you.',
                `🎮 Debug: Connected at ${new Date().toLocaleTimeString()}`,
              ];
              console.log('Connection messages added:', connectionMessages);
              return [...prev, ...connectionMessages];
            });
          }, 1000);
        } else {
          console.error('Failed to get token:', data.error);
          setTranscript(prev => [...prev, '❌ Failed to connect to voice']);
        }
      } catch (error) {
        console.error('Error getting token:', error);
        setTranscript(prev => [...prev, '❌ Connection error']);
      }
    };

    if (gameStarted && playerName) {
      getToken();
    }
  }, [gameStarted, playerName]);

  const handleStartGame = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('handleStartGame called with playerName:', playerName);
    if (playerName.trim()) {
      setGameStarted(true);
      setGameState((prev) => ({
        ...prev,
        player_name: playerName,
      }));
      const initialMessages = [
        `🎤 Welcome to Improv Battle, ${playerName}!`,
        "🎭 I'm your host and I'm so excited you're here.",
        "📋 Here's how this works: I'll give you improv scenarios, you act them out in character.",
        "⭐ I'll react with feedback - sometimes supportive, sometimes critical.",
        "🎬 We're doing 3 rounds total. Let's see what you've got!",
      ];
      console.log('Setting initial transcript:', initialMessages);
      setTranscript(initialMessages);
      console.log('Game started, transcript should be set');
    } else {
      console.log('Player name is empty');
    }
  };

  const handleRestart = () => {
    setGameStarted(false);
    setPlayerName('');
    setTranscript([]);
    setGameState({
      player_name: null,
      current_round: 0,
      max_rounds: 3,
      phase: 'intro',
      rounds: [],
    });
  };

  const handleSaveGame = async () => {
    if (!gameStarted || transcript.length === 0) {
      alert('No game to save!');
      return;
    }

    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `${playerName || 'player'}_improv_${timestamp}.txt`;
      
      // Format the transcript for saving
      const saveContent = [
        '='.repeat(60),
        'IMPROV BATTLE - GAME TRANSCRIPT',
        '='.repeat(60),
        `Player: ${playerName}`,
        `Date: ${new Date().toLocaleString()}`,
        `Rounds Completed: ${gameState.current_round}/${gameState.max_rounds}`,
        `Status: ${gameState.phase}`,
        '='.repeat(60),
        '',
        ...transcript,
        '',
        '='.repeat(60),
        'END OF TRANSCRIPT',
        '='.repeat(60),
      ].join('\n');

      // Send to backend to save
      const response = await fetch('/api/save-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename,
          content: saveContent,
          playerName,
          gameState,
        }),
      });

      if (response.ok) {
        alert(`Game saved as: ${filename}`);
      } else {
        throw new Error('Failed to save');
      }
    } catch (error) {
      console.error('Error saving game:', error);
      alert('Failed to save game. Check console for details.');
    }
  };

  const handleAddMessage = (message: string, isUser: boolean) => {
    console.log('handleAddMessage called:', { message, isUser, timestamp: new Date().toISOString() });
    
    setTranscript(prev => {
      const messagePrefix = isUser ? '🎤 You:' : '🤖 Host:';
      const lastMessage = prev[prev.length - 1];
      
      // Check if the last message is from the same sender
      if (lastMessage && lastMessage.includes(messagePrefix)) {
        // Extract the text without timestamp and prefix
        const lastText = lastMessage.replace(/^\[.*?\]\s*/, '').replace(messagePrefix, '').trim();
        const newText = message.replace(messagePrefix, '').trim();
        
        // If new text is longer, it's an update - replace the last message
        if (newText.length > lastText.length && newText.startsWith(lastText.slice(0, 20))) {
          console.log('📝 Updating last message (streaming)');
          const timestampedMessage = `[${new Date().toLocaleTimeString()}] ${message}`;
          return [...prev.slice(0, -1), timestampedMessage];
        }
      }
      
      // Otherwise, add as new message
      console.log('✅ Adding new message to transcript');
      const timestampedMessage = `[${new Date().toLocaleTimeString()}] ${message}`;
      return [...prev, timestampedMessage];
    });
    
    // Clean up old processed messages to prevent memory leaks
    if (processedMessagesRef.current.size > 100) {
      processedMessagesRef.current.clear();
    }
  };

  // Prevent hydration mismatch
  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-950 via-black to-purple-900 flex items-center justify-center">
        <div className="text-purple-300">Loading...</div>
      </div>
    );
  }

  if (!gameStarted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-950 via-black to-purple-900 flex items-center justify-center p-4 relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-72 h-72 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
          <div className="absolute top-40 right-20 w-72 h-72 bg-pink-600 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-2000"></div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-lg w-full relative z-10"
        >
          <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl p-10 border border-purple-500/30 shadow-2xl">
            {/* Header */}
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="text-center mb-8"
            >
              <div className="text-6xl mb-4">🎭</div>
              <h1 className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 mb-2">
                Improv Battle
              </h1>
              <p className="text-purple-300 text-lg font-medium">
                Voice-First Game Show
              </p>
              <div className="mt-4 flex justify-center gap-2">
                <span className="text-2xl">🎤</span>
                <span className="text-2xl">⭐</span>
                <span className="text-2xl">🎬</span>
              </div>
            </motion.div>

            {/* Music Toggle on Welcome Screen */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="absolute top-4 right-4"
            >
              <button
                onClick={() => setIsMusicOn(!isMusicOn)}
                className={`p-3 rounded-lg transition-all ${
                  isMusicOn
                    ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
                    : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                }`}
                title={isMusicOn ? 'Music On' : 'Music Off'}
              >
                {isMusicOn ? <Volume2 size={24} /> : <VolumeX size={24} />}
              </button>
            </motion.div>

            {/* Form */}
            <form onSubmit={handleStartGame} className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <label className="block text-purple-200 text-sm font-semibold mb-3">
                  Enter Your Name (Contestant)
                </label>
                <input
                  type="text"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  placeholder="Your stage name..."
                  className="w-full px-4 py-3 rounded-lg bg-white/10 border border-purple-500/50 text-white placeholder-purple-400/50 focus:outline-none focus:border-pink-500/70 focus:ring-2 focus:ring-pink-500/30 transition-all"
                  required
                  autoFocus
                />
              </motion.div>

              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-lg transition-all duration-200 shadow-lg hover:shadow-pink-500/50"
              >
                🎬 Start Improv Battle
              </motion.button>
            </form>

            {/* How It Works */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-8 pt-6 border-t border-purple-500/20"
            >
              <h3 className="text-purple-200 font-bold mb-4 text-center">
                How It Works:
              </h3>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { icon: '🎭', text: 'Get Scenarios' },
                  { icon: '🎤', text: 'Improvise' },
                  { icon: '⭐', text: 'Get Reactions' },
                  { icon: '🏆', text: 'Get Feedback' },
                ].map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 + idx * 0.1 }}
                    className="flex items-center gap-2 text-purple-300 text-sm"
                  >
                    <span className="text-xl">{item.icon}</span>
                    <span>{item.text}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Bottom tagline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center text-purple-400 text-sm mt-6"
          >
            Be creative, be bold, be funny!
          </motion.p>
        </motion.div>
      </div>
    );
  }

  // Game Screen
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-950 via-black to-purple-900 relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 opacity-20 pointer-events-none">
        <div className="absolute top-0 left-1/3 w-96 h-96 bg-purple-600 rounded-full mix-blend-multiply filter blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-pink-600 rounded-full mix-blend-multiply filter blur-3xl animate-pulse delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen p-4 flex flex-col lg:flex-row gap-4 overflow-hidden h-screen">
        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex-1 flex flex-col min-h-0 h-1/2 lg:h-auto lg:min-h-[calc(100vh-2rem)]"
        >
          {/* Header with Controls */}
          <div className="flex justify-between items-center mb-4 bg-white/5 backdrop-blur-md rounded-lg p-4 border border-purple-500/20">
            <h1 className="text-2xl font-bold text-white">
              🎭 Improv Battle
            </h1>
            <div className="flex gap-2">
              <button
                onClick={() => setIsMicOn(!isMicOn)}
                className={`p-2 rounded-lg transition-all ${
                  isMicOn
                    ? 'bg-green-500/20 text-green-400'
                    : 'bg-red-500/20 text-red-400'
                }`}
                title={isMicOn ? 'Mic On' : 'Mic Off'}
              >
                {isMicOn ? <Mic size={20} /> : <MicOff size={20} />}
              </button>
              <button
                onClick={() => setIsMusicOn(!isMusicOn)}
                className={`p-2 rounded-lg transition-all ${
                  isMusicOn
                    ? 'bg-blue-500/20 text-blue-400'
                    : 'bg-gray-500/20 text-gray-400'
                }`}
                title={isMusicOn ? 'Music On' : 'Music Off'}
              >
                {isMusicOn ? <Volume2 size={20} /> : <VolumeX size={20} />}
              </button>
              <button
                onClick={() => {
                  console.log('Test message button clicked');
                  handleAddMessage('Test message from user', true);
                  setTimeout(() => {
                    handleAddMessage('Test response from host', false);
                  }, 1000);
                }}
                className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/40 transition-all"
                title="Test Messages"
              >
                💬
              </button>
              <button
                onClick={handleRestart}
                className="p-2 rounded-lg bg-purple-500/20 text-purple-400 hover:bg-purple-500/40 transition-all"
                title="Restart Game"
              >
                <RotateCcw size={20} />
              </button>
              <button
                onClick={handleSaveGame}
                className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/40 transition-all"
                title="Save Game"
              >
                💾
              </button>
            </div>
          </div>

          {/* Video Conference / Loading */}
          <div className="flex-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md rounded-xl border border-purple-500/20 overflow-hidden flex items-center justify-center">
            {token && url ? (
              <LiveKitRoom
                video={false}
                audio={true}
                token={token}
                serverUrl={url}
                className="w-full h-full relative"
              >
                <MessageLogger onMessage={handleAddMessage} />
                <VideoConference />
                {/* Show chat overlay with better styling */}
                <div className="absolute inset-0 pointer-events-none flex items-end justify-center pb-24">
                  <div className="w-full max-w-2xl mx-4 pointer-events-auto">
                    <ChatOverlay messages={transcript.filter(line => 
                      line.includes('🎤 You:') || line.includes('🤖 Host:')
                    ).slice(-5)} />
                  </div>
                </div>
                <div className="absolute top-2 right-2 w-64">
                  <DebugPanel />
                </div>
              </LiveKitRoom>
            ) : (
              <div className="text-center">
                <div className="text-purple-400 mb-2">🎤</div>
                <p className="text-purple-300 font-semibold">Connecting...</p>
                <p className="text-purple-400 text-sm mt-1">Setting up voice connection</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Right Sidebar - Game Info */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="w-full lg:w-96 flex flex-col gap-4 min-h-0 flex-1 h-1/2 lg:flex-none lg:h-auto"
        >
          {/* Player Card */}
          <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md rounded-xl p-6 border border-purple-500/20 flex-shrink-0">
            <h2 className="text-2xl font-bold text-white mb-4">
              {gameState.player_name}
            </h2>

            {/* Round Progress */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <p className="text-purple-300 text-sm font-semibold">
                    Round Progress
                  </p>
                  <span className="text-white font-bold">
                    {gameState.current_round}/{gameState.max_rounds}
                  </span>
                </div>
                <div className="w-full bg-purple-900/50 rounded-full h-3 overflow-hidden border border-purple-500/30">
                  <motion.div
                    className="bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 h-full rounded-full"
                    initial={{ width: 0 }}
                    animate={{
                      width: `${
                        (gameState.current_round / gameState.max_rounds) *
                        100
                      }%`,
                    }}
                    transition={{ duration: 0.5 }}
                  ></motion.div>
                </div>
              </div>

              {/* Status Badge */}
              <div className="pt-3 border-t border-purple-500/20">
                <p className="text-purple-400 text-xs uppercase tracking-widest mb-2">
                  Current Status
                </p>
                <span
                  className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                    gameState.phase === 'awaiting_improv'
                      ? 'bg-green-500/20 text-green-300'
                      : gameState.phase === 'reacting'
                      ? 'bg-yellow-500/20 text-yellow-300'
                      : gameState.phase === 'done'
                      ? 'bg-blue-500/20 text-blue-300'
                      : 'bg-purple-500/20 text-purple-300'
                  }`}
                >
                  {gameState.phase.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Game Rules Panel */}
          <div className="flex-1 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md rounded-xl p-4 border border-purple-500/20 overflow-hidden flex flex-col min-h-0">
            <h3 className="text-purple-200 font-bold mb-3 text-sm uppercase tracking-wider flex-shrink-0">
              📋 Game Rules
            </h3>
            <div 
              ref={transcriptContainerRef}
              className="flex-1 overflow-y-auto space-y-3 custom-scrollbar min-h-0 bg-purple-900/30 rounded p-4"
            >
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {/* How to Play */}
                <div className="bg-purple-800/30 rounded-lg p-3 border border-purple-500/30">
                  <h4 className="text-purple-200 font-bold text-sm mb-2 flex items-center gap-2">
                    🎭 How to Play
                  </h4>
                  <ul className="text-purple-300 text-xs space-y-1.5 leading-relaxed">
                    <li>• The host will give you improv scenarios</li>
                    <li>• Act out the scenario in character</li>
                    <li>• The host will react and give feedback</li>
                    <li>• Complete 3 rounds total</li>
                  </ul>
                </div>

                {/* Tips */}
                <div className="bg-blue-800/30 rounded-lg p-3 border border-blue-500/30">
                  <h4 className="text-blue-200 font-bold text-sm mb-2 flex items-center gap-2">
                    💡 Tips for Success
                  </h4>
                  <ul className="text-blue-300 text-xs space-y-1.5 leading-relaxed">
                    <li>• Commit fully to your character</li>
                    <li>• Add specific details to make it funny</li>
                    <li>• Don't rush - explore the moment</li>
                    <li>• Embrace the absurdity</li>
                    <li>• Have fun and be creative!</li>
                  </ul>
                </div>

                {/* Feedback Types */}
                <div className="bg-pink-800/30 rounded-lg p-3 border border-pink-500/30">
                  <h4 className="text-pink-200 font-bold text-sm mb-2 flex items-center gap-2">
                    ⭐ Feedback Types
                  </h4>
                  <ul className="text-pink-300 text-xs space-y-1.5 leading-relaxed">
                    <li>• Supportive - You nailed it!</li>
                    <li>• Constructive - Room to improve</li>
                    <li>• Mixed - Some good, some not</li>
                    <li>• All feedback helps you grow</li>
                  </ul>
                </div>

                {/* Controls */}
                <div className="bg-green-800/30 rounded-lg p-3 border border-green-500/30">
                  <h4 className="text-green-200 font-bold text-sm mb-2 flex items-center gap-2">
                    🎮 Controls
                  </h4>
                  <ul className="text-green-300 text-xs space-y-1.5 leading-relaxed">
                    <li>• 🎤 Toggle microphone on/off</li>
                    <li>• 🔊 Toggle background music</li>
                    <li>• 💬 Test message button</li>
                    <li>• 🔄 Restart game anytime</li>
                  </ul>
                </div>

                {/* Current Status */}
                {gameStarted && (
                  <div className="bg-yellow-800/30 rounded-lg p-3 border border-yellow-500/30">
                    <h4 className="text-yellow-200 font-bold text-sm mb-2 flex items-center gap-2">
                      📊 Your Progress
                    </h4>
                    <div className="text-yellow-300 text-xs space-y-1.5">
                      <p>Player: <span className="font-bold">{gameState.player_name}</span></p>
                      <p>Round: <span className="font-bold">{gameState.current_round}/{gameState.max_rounds}</span></p>
                      <p>Status: <span className="font-bold capitalize">{gameState.phase.replace(/_/g, ' ')}</span></p>
                    </div>
                  </div>
                )}
              </motion.div>
            </div>
          </div>

          {/* Action Box */}
          {gameState.phase === 'awaiting_improv' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border-2 border-green-500/50 rounded-lg p-4"
            >
              <p className="text-green-300 text-sm font-bold text-center">
                🎤 Your Turn! Improvise Now
              </p>
              <p className="text-green-200/70 text-xs text-center mt-1">
                Speak your improvisation...
              </p>
            </motion.div>
          )}

          {gameState.phase === 'done' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-2 border-purple-500/50 rounded-lg p-4 text-center"
            >
              <p className="text-purple-300 text-sm font-bold">
                🏆 Game Complete!
              </p>
              <p className="text-purple-200/70 text-xs mt-1">
                Thanks for playing Improv Battle
              </p>
            </motion.div>
          )}
        </motion.div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(168, 85, 247, 0.4);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(168, 85, 247, 0.6);
        }
        .delay-2000 {
          animation-delay: 2000ms;
        }
        .delay-4000 {
          animation-delay: 4000ms;
        }
      `}</style>
    </div>
  );
}
