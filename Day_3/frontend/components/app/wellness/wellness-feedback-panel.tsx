'use client';

import { Download, Share2, CheckCircle } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';

interface WellnessFeedbackPanelProps {
  sessionDuration?: number; // in seconds
  onSaveSession?: () => void;
  onShareResults?: () => void;
  onRateSession?: (rating: number) => void;
  className?: string;
}

export function WellnessFeedbackPanel({
  sessionDuration = 0,
  onSaveSession,
  onShareResults,
  onRateSession,
  className,
}: WellnessFeedbackPanelProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className={cn('flex flex-col gap-3 rounded-lg bg-card/50 p-4 backdrop-blur-sm', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle className="text-primary" size={20} />
          <div>
            <p className="text-sm font-semibold text-foreground">Session Summary</p>
            <p className="text-xs text-muted-foreground">Duration: {formatDuration(sessionDuration)}</p>
          </div>
        </div>
      </div>

      <div className="border-t border-border/30 pt-3">
        <p className="mb-2 text-xs font-semibold text-muted-foreground">Rate your session</p>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((rating) => (
            <button
              key={rating}
              onClick={() => onRateSession?.(rating)}
              className="h-8 w-8 rounded-md border-2 border-primary/30 text-primary transition-all hover:border-primary hover:bg-primary/10"
              title={`Rate ${rating} stars`}
            >
              <span className="text-xs font-bold">★</span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-2 border-t border-border/30 pt-3">
        <button
          onClick={onSaveSession}
          className="flex flex-1 items-center justify-center gap-2 rounded-md bg-primary/10 px-3 py-2 text-xs font-medium text-primary transition-all hover:bg-primary/20"
        >
          <Download size={16} />
          Save Session
        </button>
        <button
          onClick={onShareResults}
          className="flex flex-1 items-center justify-center gap-2 rounded-md bg-primary/10 px-3 py-2 text-xs font-medium text-primary transition-all hover:bg-primary/20"
        >
          <Share2 size={16} />
          Share Results
        </button>
      </div>
    </div>
  );
}
