import { headers } from "next/headers";

import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export async function AppShell({
  me,
  currentPath,
  children,
}: {
  me: { display_name: string; email: string; role_keys: string[]; permissions?: string[] };
  currentPath: string;
  children: React.ReactNode;
}) {
  void headers;
  return (
    <div className="relative flex min-h-screen">
      <Sidebar currentPath={currentPath} permissions={me.permissions ?? []} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar me={me} currentPath={currentPath} />
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </div>
  );
}
