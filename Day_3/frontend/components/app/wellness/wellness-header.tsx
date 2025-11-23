'use client';

import { Heart, Activity, Apple, Moon, TrendingUp } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';

export interface WellnessStatItem {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: 'great' | 'good' | 'warning' | 'needs-attention';
}

interface WellnessHeaderProps {
  stats?: WellnessStatItem[];
  className?: string;
}

function getStatusColor(status: string) {
  switch (status) {
    case 'great':
      return 'text-emerald-500 dark:text-emerald-400';
    case 'good':
      return 'text-blue-500 dark:text-blue-400';
    case 'warning':
      return 'text-amber-500 dark:text-amber-400';
    case 'needs-attention':
      return 'text-rose-500 dark:text-rose-400';
    default:
      return 'text-foreground';
  }
}

export function WellnessStatCard({
  icon,
  label,
  value,
  status,
}: WellnessStatItem) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-lg bg-card/50 p-3 backdrop-blur-sm transition-all hover:bg-card/80">
      <div className={cn('text-2xl', getStatusColor(status))}>{icon}</div>
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className={cn('text-sm font-bold', getStatusColor(status))}>{value}</p>
    </div>
  );
}

export function WellnessHeader({ stats, className }: WellnessHeaderProps) {
  const defaultStats: WellnessStatItem[] = stats || [
    {
      icon: <Heart size={24} />,
      label: 'Heart Rate',
      value: '72 bpm',
      status: 'good',
    },
    {
      icon: <Activity size={24} />,
      label: 'Activity',
      value: '8,234 steps',
      status: 'great',
    },
    {
      icon: <Apple size={24} />,
      label: 'Nutrition',
      value: '6/8 cups',
      status: 'good',
    },
    {
      icon: <Moon size={24} />,
      label: 'Sleep',
      value: '7.5 hrs',
      status: 'good',
    },
  ];

  return (
    <div
      className={cn(
        'flex flex-col gap-4 bg-gradient-to-b from-primary/10 to-transparent px-4 py-6 md:px-6',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-primary">Today\'s Wellness</h2>
          <p className="text-xs text-muted-foreground">Keep track of your health metrics</p>
        </div>
        <TrendingUp className="text-primary" size={24} />
      </div>

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
        {defaultStats.map((stat, index) => (
          <WellnessStatCard key={index} {...stat} />
        ))}
      </div>
    </div>
  );
}
