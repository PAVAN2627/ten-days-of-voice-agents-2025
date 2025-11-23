'use client';

import { Smiley, SmileyWink, SmileyMeh, SmileySad, SmileyXEyes } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';

export type MoodType = 'great' | 'good' | 'okay' | 'stressed' | 'tired';

interface MoodOption {
  type: MoodType;
  emoji: React.ReactNode;
  label: string;
  color: string;
}

const moods: MoodOption[] = [
  {
    type: 'great',
    emoji: <Smiley size={24} />,
    label: 'Great',
    color: 'text-emerald-500 dark:text-emerald-400',
  },
  {
    type: 'good',
    emoji: <SmileyWink size={24} />,
    label: 'Good',
    color: 'text-blue-500 dark:text-blue-400',
  },
  {
    type: 'okay',
    emoji: <SmileyMeh size={24} />,
    label: 'Okay',
    color: 'text-amber-500 dark:text-amber-400',
  },
  {
    type: 'stressed',
    emoji: <SmileySad size={24} />,
    label: 'Stressed',
    color: 'text-orange-500 dark:text-orange-400',
  },
  {
    type: 'tired',
    emoji: <SmileyXEyes size={24} />,
    label: 'Tired',
    color: 'text-indigo-500 dark:text-indigo-400',
  },
];

interface WellnessMoodTrackerProps {
  onMoodSelect?: (mood: MoodType) => void;
  selectedMood?: MoodType;
  className?: string;
}

export function WellnessMoodTracker({
  onMoodSelect,
  selectedMood,
  className,
}: WellnessMoodTrackerProps) {
  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <p className="text-xs font-semibold text-muted-foreground">How are you feeling?</p>
      <div className="flex gap-2">
        {moods.map((mood) => (
          <button
            key={mood.type}
            onClick={() => onMoodSelect?.(mood.type)}
            className={cn(
              'flex flex-col items-center gap-1 rounded-lg px-3 py-2 transition-all',
              'hover:bg-card/50',
              selectedMood === mood.type
                ? 'bg-card/80 ring-2 ring-primary'
                : 'bg-card/30 hover:bg-card/50'
            )}
            title={mood.label}
          >
            <div className={cn(mood.color)}>{mood.emoji}</div>
            <span className="text-xs text-muted-foreground">{mood.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
