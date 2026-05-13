# =============================================================================
# apps/web — Next.js 14 (App Router) frontend
# Multi-stage: deps → builder → runner. Standalone output, non-root.
# =============================================================================

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install --no-audit --no-fund --loglevel=error

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS dev
WORKDIR /app
ENV NODE_ENV=development \
    NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:20-alpine AS prod
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
RUN addgroup -S -g 10001 tg365 && adduser -S -u 10001 -G tg365 tg365
COPY --from=builder --chown=tg365:tg365 /app/.next/standalone ./
COPY --from=builder --chown=tg365:tg365 /app/.next/static ./.next/static
COPY --from=builder --chown=tg365:tg365 /app/public ./public
USER tg365
EXPOSE 3000
CMD ["node", "server.js"]
