'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import type { ReceivedChatMessage } from '@livekit/components-react';
import { Day5SplitView } from '@/components/app/day5-split-view';
import { EmailPreview } from '@/components/app/email-preview';
import { CaretRight, CaretLeft } from '@phosphor-icons/react/dist/ssr';

interface EmailData {
  subject: string;
  body: string;
  recipient: string;
  bant_score?: number;
  pain_points?: string[];
  key_interests?: string[];
  conversation_notes?: string;
}

interface SessionWithEmailProps {
  messages: ReceivedChatMessage[];
  className?: string;
}

export const SessionWithEmailPreview: React.FC<SessionWithEmailProps> = ({
  messages,
  className,
}) => {
  const [showEmailPanel, setShowEmailPanel] = useState(false);
  const [emailData, setEmailData] = useState<EmailData | undefined>();
  const [animateEmailBadge, setAnimateEmailBadge] = useState(false);

  // Simulate receiving email data from backend
  useEffect(() => {
    if (messages.length > 0) {
      const hasEnoughContext = messages.length > 5;
      if (hasEnoughContext && !emailData) {
        setAnimateEmailBadge(true);
      }
    }
  }, [messages.length, emailData]);

  const handleEmailReady = (data: EmailData) => {
    setEmailData(data);
    setShowEmailPanel(true);
    setAnimateEmailBadge(false);
  };

  return (
    <div className={`flex h-full w-full gap-0 transition-all duration-300 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 ${className}`}>
      {/* Main Chat View - Takes full width or reduced based on email panel */}
      <motion.div
        animate={{ width: showEmailPanel ? 'calc(100% - 420px)' : '100%' }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="flex-1 overflow-hidden border-r border-slate-700 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950"
      >
        <Day5SplitView messages={messages} />
      </motion.div>

      {/* Email Preview Panel */}
      <AnimatePresence>
        {showEmailPanel && (
          <motion.div
            initial={{ x: 420, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 420, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="w-96 flex-shrink-0 border-l border-slate-700 bg-gradient-to-b from-slate-800 to-slate-900 flex flex-col shadow-2xl"
          >
            {/* Email Panel Header */}
            <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-3 border-b border-slate-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-emerald-300 rounded-full animate-pulse"></div>
                  <h3 className="text-sm font-bold text-white">Email Ready</h3>
                </div>
                <button
                  onClick={() => setShowEmailPanel(false)}
                  className="text-slate-300 hover:text-white transition-colors"
                >
                  ×
                </button>
              </div>
            </div>
            
            <div className="flex-1 overflow-hidden">
              <EmailPreview
                emailData={emailData}
                onSend={() => {
                  console.log('Sending email:', emailData);
                  setShowEmailPanel(false);
                }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      {emailData && !showEmailPanel && (
        <motion.button
          initial={{ x: 0 }}
          animate={{ x: 0 }}
          onClick={() => setShowEmailPanel(!showEmailPanel)}
          className="fixed right-4 top-1/2 -translate-y-1/2 z-30 p-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white rounded-lg shadow-xl transition-all transform hover:scale-110 border border-emerald-400"
        >
          <div className="flex flex-col items-center gap-2">
            <motion.div
              animate={animateEmailBadge ? { scale: [1, 1.2, 1], rotate: [0, 5, -5, 0] } : {}}
              transition={{ duration: 1, repeat: Infinity }}
              className="w-5 h-5 bg-yellow-300 rounded-full flex items-center justify-center text-xs font-bold text-slate-900"
            >
              ✓
            </motion.div>
            <CaretLeft size={18} weight="fill" />
          </div>
        </motion.button>
      )}
    </div>
  );
};
