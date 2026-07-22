import { NextResponse } from 'next/server';
import { query } from '@/lib/db/neon';

export async function GET() {
  try {
    // Get all tables
    const tablesResult = await query(
      `SELECT table_name 
       FROM information_schema.tables 
       WHERE table_schema = 'public'
       ORDER BY table_name`,
      []
    );

    const schemas = {};

    // Get columns for each table
    for (const table of tablesResult.rows) {
      const columnsResult = await query(
        `SELECT column_name, data_type, is_nullable
         FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = $1
         ORDER BY ordinal_position`,
        [table.table_name]
      );
      schemas[table.table_name] = columnsResult.rows;
    }

    return NextResponse.json({
      tables: tablesResult.rows.map(r => r.table_name),
      schemas,
    });
  } catch (error) {
    console.error('Schema API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch schema', details: error.message },
      { status: 500 }
    );
  }
}
