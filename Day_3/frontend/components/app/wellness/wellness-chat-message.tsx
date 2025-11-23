'use client';

import { cn } from '@/lib/utils';

export type MessageCategory = 'default' | 'meditation' | 'fitness' | 'nutrition' | 'mental-health' | 'sleep';

interface MessageCategoryConfig {
  bgColor: string;
  borderColor: string;
  textColor: string;
  iconBgColor: string;
}

const categoryConfig: Record<MessageCategory, MessageCategoryConfig> = {
  default: {
    bgColor: 'bg-card/50',
    borderColor: 'border-primary/30',
    textColor: 'text-foreground',
    iconBgColor: 'bg-primary/20',
  },
  meditation: {
    bgColor: 'bg-purple-50/50 dark:bg-purple-950/30',
    borderColor: 'border-purple-300/50 dark:border-purple-700/50',
    textColor: 'text-purple-900 dark:text-purple-100',
    iconBgColor: 'bg-purple-200/50 dark:bg-purple-800/50',
  },
  fitness: {
    bgColor: 'bg-orange-50/50 dark:bg-orange-950/30',
    borderColor: 'border-orange-300/50 dark:border-orange-700/50',
    textColor: 'text-orange-900 dark:text-orange-100',
    iconBgColor: 'bg-orange-200/50 dark:bg-orange-800/50',
  },
  nutrition: {
    bgColor: 'bg-green-50/50 dark:bg-green-950/30',
    borderColor: 'border-green-300/50 dark:border-green-700/50',
    textColor: 'text-green-900 dark:text-green-100',
    iconBgColor: 'bg-green-200/50 dark:bg-green-800/50',
  },
  'mental-health': {
    bgColor: 'bg-blue-50/50 dark:bg-blue-950/30',
    borderColor: 'border-blue-300/50 dark:border-blue-700/50',
    textColor: 'text-blue-900 dark:text-blue-100',
    iconBgColor: 'bg-blue-200/50 dark:bg-blue-800/50',
  },
  sleep: {
    bgColor: 'bg-indigo-50/50 dark:bg-indigo-950/30',
    borderColor: 'border-indigo-300/50 dark:border-indigo-700/50',
    textColor: 'text-indigo-900 dark:text-indigo-100',
    iconBgColor: 'bg-indigo-200/50 dark:bg-indigo-800/50',
  },
};

interface WellnessChatMessageProps {
  category?: MessageCategory;
  icon?: React.ReactNode;
  message: string;
  timestamp?: string;
  className?: string;
}

function getCategoryLabel(category: MessageCategory): string {
  const labels: Record<MessageCategory, string> = {
    default: 'General',
    meditation: 'Meditation',
    fitness: 'Fitness',
    nutrition: 'Nutrition',
    'mental-health': 'Mental Health',
    sleep: 'Sleep',
  };
  return labels[category];
}

export function WellnessChatMessage({
  category = 'default',
  icon,
  message,
  timestamp,
  className,
}: WellnessChatMessageProps) {
  const config = categoryConfig[category];

  return (
    <div className={cn('rounded-lg border p-4 backdrop-blur-sm', config.bgColor, config.borderColor, className)}>
      <div className="flex gap-3">
        {icon && (
          <div className={cn('flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg', config.iconBgColor)}>
            <div className={cn('text-lg', config.textColor)}>{icon}</div>
          </div>
        )}

        <div className="flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className={cn('text-xs font-semibold', config.textColor)}>
              {getCategoryLabel(category)}
            </p>
            {timestamp && <p className="text-xs text-muted-foreground">{timestamp}</p>}
          </div>
          <p className={cn('mt-1 text-sm leading-relaxed', config.textColor)}>
            {message}
          </p>
        </div>
      </div>
    </div>
  );
}
