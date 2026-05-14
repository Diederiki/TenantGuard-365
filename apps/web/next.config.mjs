/**
 * Content-Security-Policy for the web app.
 *
 * Next.js 14 ships hydration JSON inside <script> tags and MUI emotion
 * injects inline styles. To stay strict without breaking either, we allow
 * 'self' + 'unsafe-inline' for scripts/styles. The plan in Phase 28 is to
 * move to a nonce-based CSP via Next middleware — until then this is the
 * pragmatic baseline. Connect-src includes the API origin (configurable
 * via NEXT_PUBLIC_API_URL).
 */
const apiOrigin = process.env.NEXT_PUBLIC_API_URL || "";
const connectSrc = ["'self'", apiOrigin].filter(Boolean).join(" ");

const csp = [
  "default-src 'self'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  // Inline allowed today; Phase 28 swaps to nonces.
  "script-src 'self' 'unsafe-inline'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  `connect-src ${connectSrc}`,
  "object-src 'none'",
  "frame-src 'none'",
  "worker-src 'self' blob:",
  "manifest-src 'self'",
].join("; ");

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    instrumentationHook: false,
  },
  // Same-origin proxy for the API so browser cookies + CSP stay simple.
  // /api/*   → API container's /api/*
  // /auth/*  → API container's /auth/*
  // /healthz → API container's /healthz
  // The upstream URL is taken from API_PROXY_URL (server-side env) so it
  // can differ in dev (http://api:8000) vs. behind a real reverse proxy
  // (https://api.example.com).
  async rewrites() {
    const upstream = process.env.API_PROXY_URL || "http://api:8000";
    return [
      { source: "/api/:path*", destination: `${upstream}/api/:path*` },
      { source: "/auth/:path*", destination: `${upstream}/auth/:path*` },
      { source: "/healthz", destination: `${upstream}/healthz` },
      { source: "/readyz", destination: `${upstream}/readyz` },
    ];
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "same-origin" },
          {
            key: "Permissions-Policy",
            value:
              "camera=(), microphone=(), geolocation=(), interest-cohort=(), payment=(), usb=(), bluetooth=(), accelerometer=(), gyroscope=()",
          },
          { key: "Content-Security-Policy", value: csp },
          { key: "Cross-Origin-Opener-Policy", value: "same-origin" },
          { key: "Cross-Origin-Resource-Policy", value: "same-site" },
          {
            key: "Strict-Transport-Security",
            value: "max-age=63072000; includeSubDomains; preload",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
