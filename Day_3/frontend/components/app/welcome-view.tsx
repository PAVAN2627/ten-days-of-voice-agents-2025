import { Heartbeat, Leaf, Heart, Moon } from '@phosphor-icons/react';
import { Button } from '@/components/livekit/button';

function WelcomeImage() {
  return (
    <div className="relative mb-4 h-20 w-20">
      {/* Outer wellness ring */}
      <svg
        viewBox="0 0 80 80"
        className="absolute inset-0 h-full w-full animate-spin"
        style={{ animationDuration: '3s' }}
      >
        <circle
          cx="40"
          cy="40"
          r="38"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-primary/30"
          strokeDasharray="5,5"
        />
      </svg>

      {/* Center wellness symbol - lotus flower */}
      <div className="flex h-full w-full items-center justify-center">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="text-primary"
        >
          <path d="M12 2C10.9 2 10 2.9 10 4C10 5.1 10.9 6 12 6C13.1 6 14 5.1 14 4C14 2.9 13.1 2 12 2M12 8C8.69 8 6 10.69 6 14C6 17.31 8.69 20 12 20C15.31 20 18 17.31 18 14C18 10.69 15.31 8 12 8M3.5 10C2.12 10 1 11.12 1 12.5C1 13.88 2.12 15 3.5 15C4.88 15 6 13.88 6 12.5C6 11.12 4.88 10 3.5 10M20.5 10C19.12 10 18 11.12 18 12.5C18 13.88 19.12 15 20.5 15C21.88 15 23 13.88 23 12.5C23 11.12 21.88 10 20.5 10M8 18C6.62 18 5.5 19.12 5.5 20.5C5.5 21.88 6.62 23 8 23C9.38 23 10.5 21.88 10.5 20.5C10.5 19.12 9.38 18 8 18M16 18C14.62 18 13.5 19.12 13.5 20.5C13.5 21.88 14.62 23 16 23C17.38 23 18.5 21.88 18.5 20.5C18.5 19.12 17.38 18 16 18Z" />
        </svg>
      </div>
    </div>
  );
}

interface WelcomeInfoChipProps {
  icon: React.ReactNode;
  text: string;
}

function WelcomeInfoChip({ icon, text }: WelcomeInfoChipProps) {
  return (
    <div className="flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
      <span className="text-sm">{icon}</span>
      <span>{text}</span>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-gradient-to-b from-primary/5 to-transparent flex flex-col items-center justify-center text-center">
        <WelcomeImage />

        <h1 className="text-foreground text-2xl font-bold md:text-3xl">
          Your Personal Health & Wellness Companion
        </h1>

        <p className="text-muted-foreground mt-2 max-w-prose leading-6">
          Get personalized health advice, wellness tips, and support for your well-being journey
        </p>

        {/* Wellness feature chips */}
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <WelcomeInfoChip icon={<Heartbeat size={16} />} text="Fitness Coaching" />
          <WelcomeInfoChip icon={<Heart size={16} />} text="Mental Health" />
          <WelcomeInfoChip icon={<Leaf size={16} />} text="Nutrition Guide" />
          <WelcomeInfoChip icon={<Moon size={16} />} text="Sleep Support" />
        </div>

        <Button variant="primary" size="lg" onClick={onStartCall} className="mt-8 w-64 font-mono">
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Your wellness journey starts here.{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://docs.livekit.io/agents/start/voice-ai/"
            className="underline"
          >
            Learn more
          </a>
          .
        </p>
      </div>
    </div>
  );
};
