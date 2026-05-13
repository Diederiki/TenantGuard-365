import { NextRequest, NextResponse } from "next/server";

/**
 * Middleware: stick demo mode in a cookie so sidebar Links don't need to
 * propagate `?demo=1`. When any request arrives with `?demo=1`, set the
 * `tg365_demo` cookie and continue. Subsequent navigation reads the cookie
 * and renders demo fixtures.
 */
export function middleware(request: NextRequest) {
  const demoParam = request.nextUrl.searchParams.get("demo");
  if (demoParam !== "1") {
    return NextResponse.next();
  }
  const alreadySet = request.cookies.get("tg365_demo")?.value === "1";
  const response = NextResponse.next();
  if (!alreadySet) {
    response.cookies.set("tg365_demo", "1", {
      path: "/",
      sameSite: "lax",
      httpOnly: false,
      maxAge: 60 * 60 * 8, // 8 hours
    });
  }
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)"],
};
