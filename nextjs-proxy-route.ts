/**
 * app/api/pinksync/[...path]/route.ts
 * Next.js App Router proxy — pinksync.vercel.app → Supabase Edge Function
 *
 * Drop this file into the PinkSync Next.js project at:
 * src/app/api/pinksync/[...path]/route.ts  (or app/api/pinksync/[...path]/route.ts)
 *
 * This replaces ALL stub handlers in one file.
 * The Supabase Edge Function does the real work.
 */

import { NextRequest, NextResponse } from "next/server";

const EDGE_URL = process.env.PINKSYNC_EDGE_URL ??
  "https://fibrdmecsgqphnwdkbfv.supabase.co/functions/v1/pinksync-api";

const EDGE_KEY = process.env.SUPABASE_ANON_KEY ?? "";

async function handler(req: NextRequest, { params }: { params: { path: string[] } }) {
  const path = "/" + params.path.join("/");
  const upstream = `${EDGE_URL}${path}${req.nextUrl.search}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${EDGE_KEY}`,
    "X-Request-ID":     req.headers.get("X-Request-ID")     ?? crypto.randomUUID(),
    "X-Correlation-ID": req.headers.get("X-Correlation-ID") ?? crypto.randomUUID(),
  };

  // Forward DeafAUTH token if present
  const authHeader = req.headers.get("Authorization");
  if (authHeader && authHeader !== `Bearer ${EDGE_KEY}`) {
    headers["X-DeafAuth-Token"] = authHeader;
  }

  const body = req.method !== "GET" && req.method !== "HEAD"
    ? await req.text()
    : undefined;

  const res = await fetch(upstream, { method: req.method, headers, body });
  const data = await res.text();

  return new NextResponse(data, {
    status: res.status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "X-Request-ID":     res.headers.get("X-Request-ID")     ?? "",
      "X-Correlation-ID": res.headers.get("X-Correlation-ID") ?? "",
    },
  });
}

export const GET     = handler;
export const POST    = handler;
export const OPTIONS = () => new NextResponse(null, {
  status: 204,
  headers: {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Request-ID, X-Correlation-ID",
  },
});
