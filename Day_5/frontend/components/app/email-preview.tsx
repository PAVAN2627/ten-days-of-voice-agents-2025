'use client';

import React, { useState } from 'react';
import { 
  Copy, 
  PaperPlaneRight, 
  X, 
  Spinner 
} from '@phosphor-icons/react/dist/ssr';

interface EmailData {
  subject: string;
  body: string;
  recipient: string;
  bant_score?: number;
  pain_points?: string[];
  key_interests?: string[];
  conversation_notes?: string;
}

interface EmailPreviewProps {
  emailData?: EmailData;
  onClose?: () => void;
  onSend?: () => void;
}

export function EmailPreview({ emailData, onClose, onSend }: EmailPreviewProps) {
  const [copied, setCopied] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(false);

  if (!emailData) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No email to preview</p>
      </div>
    );
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(`Subject: ${emailData.subject}\n\n${emailData.body}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleSend = async () => {
    setIsSending(true);
    try {
      const response = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipient: emailData.recipient,
          subject: emailData.subject,
          body: emailData.body,
          bant_score: emailData.bant_score,
          pain_points: emailData.pain_points,
          key_interests: emailData.key_interests,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send email');
      }

      setSendSuccess(true);
      setTimeout(() => {
        setSendSuccess(false);
        onSend?.();
      }, 2000);
    } catch (err) {
      console.error('Email send error:', err);
      alert('Failed to send email. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  const bant_level = emailData.bant_score ? (
    emailData.bant_score >= 75 ? "Strong fit" : emailData.bant_score >= 50 ? "Good fit" : "Potential"
  ) : "Unqualified";

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full transition-colors ${
            sendSuccess ? 'bg-emerald-500' : 'bg-emerald-500'
          }`}></div>
          <div>
            <h3 className="text-white font-semibold">Follow-up Email Draft</h3>
            <p className="text-sm text-gray-400">{sendSuccess ? 'Sent!' : 'Ready to send'}</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        )}
      </div>

      {/* Email Container */}
      <div className="flex-1 overflow-y-auto">
        {/* Recipient & Score */}
        <div className="bg-slate-700/50 rounded-lg p-4 mb-4 border border-slate-600">
          <div className="flex justify-between items-start mb-3">
            <div>
              <p className="text-xs text-gray-400 mb-1">To:</p>
              <p className="text-white font-medium">{emailData.recipient}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400 mb-1">Lead Score</p>
              <p className={`text-sm font-bold ${
                emailData.bant_score! >= 75 ? 'text-emerald-400' :
                emailData.bant_score! >= 50 ? 'text-blue-400' :
                'text-yellow-400'
              }`}>
                {bant_level} {emailData.bant_score && `(${emailData.bant_score}/100)`}
              </p>
            </div>
          </div>
        </div>

        {/* Subject */}
        <div className="bg-slate-700/50 rounded-lg p-4 mb-4 border border-slate-600">
          <p className="text-xs text-gray-400 mb-2">Subject:</p>
          <p className="text-white font-semibold">{emailData.subject}</p>
        </div>

        {/* Pain Points & Interests */}
        {(emailData.pain_points?.length || emailData.key_interests?.length) && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            {emailData.pain_points && emailData.pain_points.length > 0 && (
              <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
                <p className="text-xs font-semibold text-red-400 mb-2">Pain Points</p>
                <ul className="space-y-1">
                  {emailData.pain_points.map((point, idx) => (
                    <li key={idx} className="text-xs text-gray-300">• {point}</li>
                  ))}
                </ul>
              </div>
            )}
            {emailData.key_interests && emailData.key_interests.length > 0 && (
              <div className="bg-blue-500/10 rounded-lg p-3 border border-blue-500/30">
                <p className="text-xs font-semibold text-blue-400 mb-2">Key Interests</p>
                <ul className="space-y-1">
                  {emailData.key_interests.map((interest, idx) => (
                    <li key={idx} className="text-xs text-gray-300">• {interest}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Email Body */}
        <div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600 font-mono text-sm leading-relaxed">
          <div className="text-gray-300 whitespace-pre-wrap">
            {emailData.body}
          </div>
        </div>

        {/* Conversation Notes if available */}
        {emailData.conversation_notes && (
          <div className="mt-4 bg-purple-500/10 rounded-lg p-4 border border-purple-500/30">
            <p className="text-xs font-semibold text-purple-400 mb-2">Conversation Highlights</p>
            <p className="text-sm text-gray-300">{emailData.conversation_notes}</p>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-6 pt-4 border-t border-slate-700">
        <button
          onClick={handleCopy}
          disabled={isSending}
          className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white rounded-lg transition-colors text-sm"
        >
          <Copy size={16} />
          {copied ? 'Copied!' : 'Copy Email'}
        </button>
        {onSend && (
          <button
            onClick={handleSend}
            disabled={isSending || sendSuccess}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 disabled:from-emerald-700 disabled:to-teal-700 text-white rounded-lg font-semibold transition-all transform hover:scale-105 disabled:scale-100 text-sm"
          >
            {isSending ? (
              <>
                <Spinner size={16} className="animate-spin" />
                Sending...
              </>
            ) : sendSuccess ? (
              <>
                <PaperPlaneRight size={16} />
                Sent!
              </>
            ) : (
              <>
                <PaperPlaneRight size={16} />
                Send Email
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export function EmailPreviewPanel({ emailData, onSend }: { emailData?: EmailData; onSend?: () => void }) {
  return (
    <div className="h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-xl border border-slate-700 overflow-hidden flex flex-col">
      <EmailPreview emailData={emailData} onSend={onSend} />
    </div>
  );
}
