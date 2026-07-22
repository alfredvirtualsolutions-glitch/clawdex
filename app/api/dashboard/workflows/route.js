import { NextResponse } from 'next/server';
import { query } from '@/lib/db/neon';

export async function GET() {
  try {
    const result = await query(
      `SELECT 
        job_id,
        campaign_id,
        run_cycle,
        status,
        signals_verified,
        results_collected,
        created_at,
        completed_at
       FROM search_jobs 
       ORDER BY created_at DESC 
       LIMIT 10`,
      []
    );

    const workflows = result.rows.map(row => ({
      id: row.job_id,
      name: `${row.campaign_id || 'Campaign'} - ${row.run_cycle || 'Cycle'}`,
      type: determineWorkflowType(row),
      status: row.status || 'pending',
      progress: calculateProgress(row.signals_verified, row.results_collected),
      createdAt: row.created_at,
      completedAt: row.completed_at,
    }));

    return NextResponse.json({ workflows });
  } catch (error) {
    console.error('Workflows API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch workflows', details: error.message },
      { status: 500 }
    );
  }
}

function determineWorkflowType(row) {
  if (row.signals_verified > 0) return 'Enrich';
  if (row.results_collected > 0) return 'Search';
  return 'Outreach';
}

function calculateProgress(verified, collected) {
  if (!collected || collected === 0) return 0;
  return Math.min(Math.round((verified / collected) * 100), 100);
}
