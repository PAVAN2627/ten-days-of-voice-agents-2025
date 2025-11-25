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
  const isAgent = messageOrigin === 'remote';
  const isCustomer = messageOrigin === 'local';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn(
        'group flex w-full flex-col gap-1 py-2 px-2 rounded-lg transition-colors',
        isAgent && 'hover:bg-blue-50 dark:hover:bg-blue-950',
        isCustomer && 'hover:bg-green-50 dark:hover:bg-green-950',
        className
      )}
      {...props}
    >
      <header
        className={cn(
          'text-muted-foreground flex items-center gap-2 text-sm font-semibold',
          isAgent ? 'flex-row text-blue-600 dark:text-blue-400' : 'flex-row-reverse text-green-600 dark:text-green-400'
        )}
      >
        <div className={cn('flex items-center gap-1', isAgent ? 'order-1' : 'order-2')}>
          {isAgent ? <span>🎤</span> : <span>👤</span>}
          {name && <strong>{name}</strong>}
          {!name && <strong>{isAgent ? 'Priya (Agent)' : 'You (Customer)'}</strong>}
        </div>
        <span className="font-mono text-xs opacity-0 transition-opacity ease-linear group-hover:opacity-100 flex-1">
          {hasBeenEdited && '*'}
          {time.toLocaleTimeString(locale, { timeStyle: 'short' })}
        </span>
      </header>
      <span
        className={cn(
          'max-w-3xl rounded-xl px-4 py-2 text-sm leading-relaxed',
          isAgent
            ? 'bg-blue-100 dark:bg-blue-900 text-gray-900 dark:text-white rounded-bl-none'
            : 'bg-green-100 dark:bg-green-900 text-gray-900 dark:text-white rounded-br-none ml-auto'
        )}
      >
        {message}
      </span>
    </li>
  );
};
