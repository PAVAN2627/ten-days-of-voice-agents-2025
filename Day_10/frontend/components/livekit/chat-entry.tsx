import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });
  const isLocal = messageOrigin === 'local';

  // Don't render if message is empty
  if (!message || message.trim() === '') {
    return null;
  }

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn(
        'group flex w-full flex-col gap-1.5 mb-4',
        isLocal ? 'items-end' : 'items-start',
        className
      )}
      {...props}
    >
      <header
        className={cn(
          'flex items-center gap-2 text-sm px-2',
          isLocal ? 'flex-row-reverse text-right' : 'flex-row text-left'
        )}
      >
        <strong className={cn(
          'font-semibold',
          isLocal ? 'text-blue-600 dark:text-blue-400' : 'text-green-600 dark:text-green-400'
        )}>
          {isLocal ? '🎤 You' : '🤖 Host'}
        </strong>
        <span className="font-mono text-xs text-muted-foreground opacity-0 transition-opacity ease-linear group-hover:opacity-100">
          {hasBeenEdited && '*'}
          {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
        </span>
      </header>
      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-2.5 shadow-sm',
          isLocal 
            ? 'bg-blue-500 text-white rounded-br-md' 
            : 'bg-gradient-to-br from-green-600 to-green-700 text-white rounded-bl-md border border-green-500/30'
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message}
        </p>
      </div>
    </li>
  );
};
