'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { EnhancedViewController } from '@/components/app/enhanced-view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface EnhancedAppProps {
  appConfig: AppConfig;
}

export function EnhancedApp({ appConfig }: EnhancedAppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      <main className="grid h-svh grid-cols-1 place-content-center">
        <EnhancedViewController />
      </main>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
