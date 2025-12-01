'use client';

import dynamic from 'next/dynamic';

const ImprovisationBattle = dynamic(
  () => import('@/components/improv-battle'),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-gradient-to-br from-purple-950 via-black to-purple-900 flex items-center justify-center">
        <div className="text-purple-300">Loading Game...</div>
      </div>
    ),
  }
);

export default function Home() {
  return <ImprovisationBattle />;
}
