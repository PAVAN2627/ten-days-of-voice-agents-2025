'use client';

import { useEffect, useState } from 'react';

interface BreathingAnimationProps {
  isActive?: boolean;
  cycleLength?: number; // in seconds
}

export function BreathingAnimation({ isActive = false, cycleLength = 4 }: BreathingAnimationProps) {
  const [scale, setScale] = useState(1);

  useEffect(() => {
    if (!isActive) return;

    const interval = setInterval(() => {
      const now = Date.now() % (cycleLength * 1000);
      const progress = now / (cycleLength * 1000);

      // Breathing cycle: inhale 1s, hold 1s, exhale 1s, hold 1s
      let currentScale = 1;
      if (progress < 0.25) {
        currentScale = 1 + progress * 0.5; // Inhale
      } else if (progress < 0.5) {
        currentScale = 1.25; // Hold
      } else if (progress < 0.75) {
        currentScale = 1.25 - (progress - 0.5) * 0.5; // Exhale
      } else {
        currentScale = 1; // Hold
      }

      setScale(currentScale);
    }, 50);

    return () => clearInterval(interval);
  }, [isActive, cycleLength]);

  return (
    <div className="flex items-center justify-center">
      <div
        className="h-16 w-16 rounded-full bg-gradient-to-br from-primary/30 to-accent/20 transition-transform duration-100"
        style={{ transform: `scale(${scale})` }}
      >
        <div className="flex h-full items-center justify-center text-2xl text-primary">
          ◉
        </div>
      </div>
    </div>
  );
}

interface ProgressRingProps {
  value: number; // 0-100
  size?: number;
  strokeWidth?: number;
}

export function ProgressRing({ value = 0, size = 120, strokeWidth = 8 }: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        className="text-card-foreground/10"
      />
      {/* Progress circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="text-primary transition-all duration-500 ease-out"
      />
    </svg>
  );
}

interface HeartbeatAnimationProps {
  isActive?: boolean;
  bpm?: number; // beats per minute
}

export function HeartbeatAnimation({ isActive = false, bpm = 72 }: HeartbeatAnimationProps) {
  const beatDuration = (60 / bpm) * 1000; // Convert to milliseconds

  return (
    <div className="flex items-center justify-center">
      {isActive ? (
        <div className="relative h-12 w-12">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="absolute inset-0 h-full w-full text-red-500"
            style={{
              animation: `heartbeat ${beatDuration}ms infinite`,
            }}
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
          <style>{`
            @keyframes heartbeat {
              0%, 10%, 20%, 50%, 100% { transform: scale(1); }
              5%, 15% { transform: scale(1.1); }
            }
          `}</style>
        </div>
      ) : (
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="h-12 w-12 text-muted-foreground"
        >
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
      )}
    </div>
  );
}
