import { NextResponse } from 'next/server';
import { query } from '@/lib/db/neon';

export async function GET() {
  try {
    // Agents Online - count of active search_jobs today
    const agentsResult = await query(
      `SELECT COUNT(DISTINCT job_id) as count 
       FROM search_jobs 
       WHERE DATE(created_at) = CURRENT_DATE`,
      []
    );

    // Workflows Running - count with status='running'
    const workflowsResult = await query(
      `SELECT COUNT(*) as count 
       FROM search_jobs 
       WHERE status = 'running'`,
      []
    );

    // Signals Today - count added in last 24h
    const signalsResult = await query(
      `SELECT COUNT(*) as count 
       FROM retirement_signal_searches 
       WHERE created_at >= NOW() - INTERVAL '24 hours'`,
      []
    );

    // Success Rate - (verified_signals / total_signals) * 100
    const successResult = await query(
      `SELECT 
        COUNT(*) FILTER (WHERE verification_status = 'verified') as verified,
        COUNT(*) as total
       FROM retirement_signal_searches`,
      []
    );

    const verified = parseInt(successResult.rows[0]?.verified || 0);
    const total = parseInt(successResult.rows[0]?.total || 0);
    const successRate = total > 0 ? ((verified / total) * 100).toFixed(1) : 0;

    // System Health
    const systemHealth = parseFloat(successRate) > 80 ? 'Excellent' : 'Degraded';

    return NextResponse.json({
      agentsOnline: parseInt(agentsResult.rows[0]?.count || 0),
      workflowsRunning: parseInt(workflowsResult.rows[0]?.count || 0),
      signalsToday: parseInt(signalsResult.rows[0]?.count || 0),
      successRate: parseFloat(successRate),
      systemHealth,
    });
  } catch (error) {
    console.error('Stats API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats', details: error.message },
      { status: 500 }
    );
  }
}
