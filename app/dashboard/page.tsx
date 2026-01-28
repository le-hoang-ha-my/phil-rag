import { getCurrentUser } from '@/lib/supabase/server';

export default async function DashboardPage() {
  const user = await getCurrentUser();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Welcome back!</h1>
        <p className="text-muted-foreground mt-2">
          Logged in as {user?.email}
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="p-6 border rounded-lg bg-white dark:bg-slate-900">
          <h3 className="font-semibold">Documents</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="p-6 border rounded-lg bg-white dark:bg-slate-900">
          <h3 className="font-semibold">Chat Sessions</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="p-6 border rounded-lg bg-white dark:bg-slate-900">
          <h3 className="font-semibold">Total Amount</h3>
          <p className="text-3xl font-bold mt-2">$0</p>
        </div>
      </div>
    </div>
  );
}