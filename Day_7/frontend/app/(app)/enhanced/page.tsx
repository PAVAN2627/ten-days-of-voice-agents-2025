import { headers } from 'next/headers';
import { EnhancedApp } from '@/components/app/enhanced-app';
import { getAppConfig } from '@/lib/utils';

export default async function EnhancedPage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <EnhancedApp appConfig={appConfig} />;
}
