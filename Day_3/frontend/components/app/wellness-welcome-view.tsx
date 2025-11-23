import {
  Heart,
  Activity,
  Apple,
  Moon,
  Flower,
} from '@phosphor-icons/react';
import { Button } from '@/components/livekit/button';

function WellnessWelcomeIcon() {
  return (
    <div className="relative mb-4 h-20 w-20">
      {/* Outer wellness ring (animated in CSS) */}
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

      {/* Center lotus-inspired wellness symbol */}
      <div className="flex h-full w-full items-center justify-center text-primary">
        <Flower size={48} weight="fill" />
      </div>
    </div>
  );
}

interface WellnessInfoChipProps {
  icon: React.ReactNode;
  text: string;
}

function WellnessInfoChip({ icon, text }: WellnessInfoChipProps) {
  return (
    <div className="flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
      <span className="text-sm">{icon}</span>
      <span>{text}</span>
    </div>
  );
}

interface WellnessWelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WellnessWelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WellnessWelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-gradient-to-b from-primary/5 to-transparent flex flex-col items-center justify-center text-center">
        <WellnessWelcomeIcon />

        <h1 className="text-foreground text-2xl font-bold md:text-3xl">
          Your Personal Health & Wellness Companion
        </h1>

        <p className="text-muted-foreground mt-2 max-w-prose leading-6">
          Get personalized health advice, wellness tips, and support for your well-being journey
        </p>

        {/* Wellness feature chips */}
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <WellnessInfoChip icon={<Activity size={16} />} text="Fitness Coaching" />
          <WellnessInfoChip icon={<Heart size={16} />} text="Mental Health" />
          <WellnessInfoChip icon={<Apple size={16} />} text="Nutrition Guide" />
          <WellnessInfoChip icon={<Moon size={16} />} text="Sleep Support" />
        </div>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-8 w-64 font-mono"
        >
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
