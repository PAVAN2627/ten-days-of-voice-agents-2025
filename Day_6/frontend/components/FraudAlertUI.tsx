import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Phone, PhoneOff, Send, AlertCircle } from 'lucide-react';

interface Message {
  id: string;
  type: 'agent' | 'user';
  content: string;
  timestamp: Date;
}

interface FraudCase {
  id: string;
  userName: string;
  cardEnding: string;
  transactionAmount: string;
  transactionLocation: string;
}

const FraudAlertUI = () => {
  const [currentPage, setCurrentPage] = useState<'welcome' | 'call' | 'fraud'>('welcome');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isCallActive, setIsCallActive] = useState(false);
  const [isMicActive, setIsMicActive] = useState(false);
  const [currentFraudCase, setCurrentFraudCase] = useState<FraudCase | null>(null);
  const [userInput, setUserInput] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  const [fraudStatus, setFraudStatus] = useState<'pending' | 'safe' | 'fraud'>('pending');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Simulated agent response
  const addAgentMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'agent',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);

    // Play notification sound
    if (audioRef.current) {
      audioRef.current.play().catch(() => {});
    }
  };

  const addUserMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleStartCall = () => {
    setCurrentPage('call');
    setMessages([]);
    setIsCallActive(true);
    setFraudStatus('pending');
    setIsVerified(false);

    // Simulate agent greeting
    setTimeout(() => {
      addAgentMessage("Hello! I'm calling from SecureBank Fraud Department. We've detected a suspicious transaction on your account. Can you please provide the last 4 digits of your card?");
    }, 1000);
  };

  const handleSendMessage = () => {
    if (!userInput.trim()) return;

    addUserMessage(userInput);
    
    // Simulate agent responses
    const input = userInput.toLowerCase();
    
    if (!isVerified && input.includes('3333')) {
      setCurrentFraudCase({
        id: 'FC004',
        userName: 'Neha Gupta',
        cardEnding: '3333',
        transactionAmount: '₹4,72,000',
        transactionLocation: 'Fashion India Online Store, Pune',
      });
      setIsVerified(true);
      
      setTimeout(() => {
        addAgentMessage("Great! I found your account for Neha Gupta. Now, to complete the verification, please answer this security question: In what city were you born?");
      }, 800);
    } else if (isVerified && !input.includes('jaipur') && input.length > 0) {
      setTimeout(() => {
        addAgentMessage("That doesn't match our records. Please try again.");
      }, 800);
    } else if (isVerified && input.includes('jaipur')) {
      setTimeout(() => {
        setCurrentPage('fraud');
        addAgentMessage("Perfect! Your identity has been verified. Now let me tell you about the suspicious transaction we detected. This transaction is from Fashion India Online Store for ₹4,72,000 in Pune, Maharashtra. Did you authorize this transaction?");
      }, 800);
    } else if (currentPage === 'fraud') {
      if (input.includes('yes')) {
        setFraudStatus('safe');
        setTimeout(() => {
          addAgentMessage("Thank you for confirming. Your account is secure and this case is now closed. Have a great day!");
        }, 800);
      } else if (input.includes('no')) {
        setFraudStatus('fraud');
        setTimeout(() => {
          addAgentMessage("I've marked this transaction as fraudulent. Your card has been blocked immediately, and we're raising a dispute. You'll receive a replacement card within 5-7 business days.");
        }, 800);
      }
    }

    setUserInput('');
  };

  const handleEndCall = () => {
    setIsCallActive(false);
    setCurrentPage('welcome');
    setMessages([]);
    setCurrentFraudCase(null);
    setIsVerified(false);
    setFraudStatus('pending');
  };

  // ============= WELCOME PAGE =============
  if (currentPage === 'welcome') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center p-4">
        <audio ref={audioRef} src="data:audio/wav;base64,UklGRi4AAAAARKwAAIhYAQAiYgAASLeWAABiYgA=" />
        
        <div className="max-w-md w-full">
          {/* Logo Section */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-500 rounded-full mb-6 shadow-xl">
              <AlertCircle size={40} className="text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">SecureBank</h1>
            <p className="text-blue-100 text-lg">Fraud Alert System</p>
          </div>

          {/* Card Section */}
          <div className="bg-white bg-opacity-95 rounded-3xl p-8 shadow-2xl space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome</h2>
              <p className="text-gray-600">Advanced Fraud Detection Voice Agent</p>
            </div>

            {/* Feature List */}
            <div className="space-y-4 py-6 border-y border-gray-200">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 flex items-center justify-center mt-0.5">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <p className="text-gray-800 font-semibold">Real-time Verification</p>
                  <p className="text-gray-600 text-sm">Two-step customer verification</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 flex items-center justify-center mt-0.5">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <p className="text-gray-800 font-semibold">AI-Powered Analysis</p>
                  <p className="text-gray-600 text-sm">Intelligent fraud detection</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 flex items-center justify-center mt-0.5">
                  <span className="text-white text-sm">✓</span>
                </div>
                <div>
                  <p className="text-gray-800 font-semibold">Voice Authentication</p>
                  <p className="text-gray-600 text-sm">Natural conversation flow</p>
                </div>
              </div>
            </div>

            {/* Start Button */}
            <button
              onClick={handleStartCall}
              className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold py-4 rounded-full transition transform hover:scale-105 shadow-lg flex items-center justify-center space-x-2"
            >
              <Phone size={20} />
              <span>Start Call</span>
            </button>

            {/* Footer Info */}
            <p className="text-center text-gray-500 text-sm">
              This is a demo of our fraud alert system. For real issues, contact your bank directly.
            </p>
          </div>

          {/* Background decoration */}
          <div className="mt-8 text-center text-blue-200 opacity-50">
            <p className="text-sm">Day 6 - Advanced Goal</p>
          </div>
        </div>
      </div>
    );
  }

  // ============= CALL PAGE =============
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex flex-col p-4">
      {/* Header */}
      <div className="max-w-4xl mx-auto w-full mb-4">
        <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-red-500 flex items-center justify-center">
              <AlertCircle size={24} className="text-white" />
            </div>
            <div>
              <p className="text-white font-semibold">SecureBank Fraud Alert</p>
              <p className={`text-sm ${isCallActive ? 'text-green-300' : 'text-red-300'}`}>
                {isCallActive ? '● Call Active' : '● Call Ended'}
              </p>
            </div>
          </div>
          <button
            onClick={handleEndCall}
            className="bg-red-500 hover:bg-red-600 text-white p-3 rounded-full transition transform hover:scale-110"
          >
            <PhoneOff size={20} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto w-full flex-1 grid grid-cols-1 lg:grid-cols-3 gap-4">
        
        {/* Chat Messages - Full width on mobile, 2 cols on desktop */}
        <div className="lg:col-span-2 flex flex-col space-y-4">
          {/* Messages Container */}
          <div className="bg-white bg-opacity-95 rounded-2xl p-6 flex-1 overflow-y-auto shadow-xl">
            <div className="space-y-4">
              {messages.length === 0 && (
                <div className="h-full flex items-center justify-center text-gray-400 text-center">
                  <p>Waiting for agent response...</p>
                </div>
              )}
              
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.type === 'agent' ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-sm xl:max-w-md px-4 py-3 rounded-2xl ${
                      msg.type === 'agent'
                        ? 'bg-gradient-to-r from-blue-100 to-blue-50 text-gray-800 rounded-tl-none'
                        : 'bg-gradient-to-r from-green-500 to-green-600 text-white rounded-tr-none'
                    }`}
                  >
                    <p className="text-sm lg:text-base">{msg.content}</p>
                    <p className={`text-xs mt-1 ${msg.type === 'agent' ? 'text-blue-500' : 'text-green-100'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          {isCallActive && (
            <div className="bg-white bg-opacity-95 rounded-2xl p-4 shadow-xl">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type your response..."
                  className="flex-1 bg-gray-100 border-2 border-gray-300 focus:border-blue-500 rounded-full px-4 py-3 focus:outline-none transition"
                />
                <button
                  onClick={handleSendMessage}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white p-3 rounded-full transition transform hover:scale-110"
                >
                  <Send size={20} />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Fraud Case Info Panel */}
        {currentFraudCase && (
          <div className="lg:col-span-1">
            <div className="bg-white bg-opacity-95 rounded-2xl p-6 shadow-xl space-y-4 h-fit sticky top-4">
              <h3 className="text-lg font-bold text-gray-800 border-b-2 border-blue-200 pb-2">
                Transaction Details
              </h3>

              <div>
                <p className="text-gray-600 text-sm font-semibold">Customer Name</p>
                <p className="text-gray-900 text-lg font-bold">{currentFraudCase.userName}</p>
              </div>

              <div>
                <p className="text-gray-600 text-sm font-semibold">Card Ending</p>
                <p className="text-gray-900 font-mono text-lg">●●●●●●●●{currentFraudCase.cardEnding}</p>
              </div>

              <div>
                <p className="text-gray-600 text-sm font-semibold">Amount</p>
                <p className="text-red-600 text-xl font-bold">{currentFraudCase.transactionAmount}</p>
              </div>

              <div>
                <p className="text-gray-600 text-sm font-semibold">Location</p>
                <p className="text-gray-900 text-sm">{currentFraudCase.transactionLocation}</p>
              </div>

              {/* Status Badge */}
              <div className="pt-4 border-t-2 border-gray-200">
                <p className="text-gray-600 text-sm font-semibold mb-2">Status</p>
                <div className={`px-4 py-2 rounded-full text-center font-bold text-white ${
                  fraudStatus === 'pending' ? 'bg-yellow-500' :
                  fraudStatus === 'safe' ? 'bg-green-500' :
                  'bg-red-500'
                }`}>
                  {fraudStatus === 'pending' ? '⏳ Verifying...' :
                   fraudStatus === 'safe' ? '✓ Transaction Safe' :
                   '✗ Fraudulent'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Waiting State Panel */}
        {!currentFraudCase && (
          <div className="lg:col-span-1">
            <div className="bg-white bg-opacity-95 rounded-2xl p-6 shadow-xl h-fit sticky top-4">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center animate-pulse">
                  <Mic size={32} className="text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-800">Agent Connected</h3>
                <p className="text-gray-600 text-sm">
                  Please answer the verification questions to confirm your identity.
                </p>
                <div className="flex items-center space-x-2 text-blue-600 text-sm">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <span>Listening...</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FraudAlertUI;
