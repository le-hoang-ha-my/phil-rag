import { getCurrentUser } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function Home() {
  const user = await getCurrentUser();

  // Redirect authenticated users to dashboard
  if (user) {
    redirect('/dashboard');
  }

  // Redirect unauthenticated users to login
  redirect('/login');
}
