import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { SignInForm } from "./SignInForm";

export const dynamic = "force-dynamic";

export default function SignInPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-md items-center justify-center px-6">
      <Card className="w-full">
        <CardHeader>
          <p className="mb-1 text-xs font-medium uppercase tracking-widest text-brand-400">
            TenantGuard / Internal
          </p>
          <CardTitle>Sign in</CardTitle>
          <CardDescription>
            Production deployments authenticate via Microsoft Entra ID. Local
            development supports mock sign-in as a seeded user.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SignInForm />
        </CardContent>
      </Card>
    </main>
  );
}
