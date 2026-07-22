import { NextResponse } from 'next/server';
import { query } from '@/lib/db/neon';

export async function GET() {
  try {
    // Signals by Campaign
    const campaignResult = await query(
      `SELECT campaign_id, COUNT(*) as count 
       FROM retirement_signal_searches 
       WHERE campaign_id IS NOT NULL 
       GROUP BY campaign_id 
       ORDER BY count DESC 
       LIMIT 5`,
      []
    );

    // Signal Classification
    const classificationResult = await query(
      `SELECT 
        CASE 
          WHEN confidence_score >= 0.8 THEN 'Hot'
          WHEN confidence_score >= 0.5 THEN 'Moderate'
          ELSE 'Nurture'
        END as category,
        COUNT(*) as count
       FROM retirement_signal_searches 
       GROUP BY category`,
      []
    );

    // Leads Pipeline
    const pipelineResult = await query(
      `SELECT 
        (SELECT COUNT(*) FROM retirement_signal_searches) as signals,
        (SELECT COUNT(*) FROM retirement_signal_searches WHERE person_name IS NOT NULL) as named,
        (SELECT COUNT(*) FROM extracted_leads) as enriched,
        (SELECT COUNT(*) FROM extracted_leads WHERE professional_email IS NOT NULL) as valid_email,
        (SELECT COUNT(*) FROM outreach_queue) as contacted`,
      []
    );

    // Daily Signal Trend (last 7 days)
    const trendResult = await query(
      `SELECT 
        DATE(created_at) as date,
        COUNT(*) as count
       FROM retirement_signal_searches 
       WHERE created_at >= NOW() - INTERVAL '7 days'
       GROUP BY DATE(created_at)
       ORDER BY date ASC`,
      []
    );

    return NextResponse.json({
      signalsByCampaign: campaignResult.rows.map(r => ({
        campaign: r.campaign_id,
        count: parseInt(r.count),
      })),
      signalClassification: classificationResult.rows.map(r => ({
        category: r.category,
        count: parseInt(r.count),
      })),
      leadsPipeline: pipelineResult.rows[0] || {},
      dailyTrend: trendResult.rows.map(r => ({
        date: r.date,
        count: parseInt(r.count),
      })),
    });
  } catch (error) {
    console.error('Analytics API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch analytics', details: error.message },
      { status: 500 }
    );
  }
}
