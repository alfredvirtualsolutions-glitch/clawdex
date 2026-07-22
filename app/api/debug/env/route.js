import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    hasNeonUrl: !!process.env.NEON_DATABASE_URL,
    neonUrlPrefix: process.env.NEON_DATABASE_URL ? process.env.NEON_DATABASE_URL.substring(0, 20) + '...' : 'NOT SET',
    allEnvKeys: Object.keys(process.env).filter(key => key.includes('NEON') || key.includes('DATABASE')),
  });
}
