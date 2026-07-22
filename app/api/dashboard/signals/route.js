import { NextResponse } from 'next/server';
import { query } from '@/lib/db/neon';

export async function GET() {
  try {
    const result = await query(
      `SELECT 
        id,
        signal_type,
        person_name,
        organization_name,
        business_name,
        campaign_id,
        confidence_score,
        created_at
       FROM retirement_signal_searches 
       ORDER BY created_at DESC 
       LIMIT 10`,
      []
    );

    const signals = result.rows.map(row => ({
      id: row.id,
      type: row.signal_type || 'unknown',
      title: formatSignalTitle(row),
      campaign: row.campaign_id || 'General',
      timeAgo: formatTimeAgo(row.created_at),
      score: categorizeScore(row.confidence_score),
      createdAt: row.created_at,
    }));

    return NextResponse.json({ signals });
  } catch (error) {
    console.error('Signals API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch signals', details: error.message },
      { status: 500 }
    );
  }
}

function formatSignalTitle(row) {
  const name = row.person_name || 'Unknown';
  const org = row.organization_name || row.business_name || row.signal_type || '';
  return org ? `${name} · ${org}` : name;
}

function formatTimeAgo(timestamp) {
  if (!timestamp) return 'just now';
  const now = new Date();
  const then = new Date(timestamp);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

function categorizeScore(score) {
  if (!score) return 'Nurture';
  if (score >= 0.8) return 'Hot';
  if (score >= 0.5) return 'Moderate';
  return 'Nurture';
}
