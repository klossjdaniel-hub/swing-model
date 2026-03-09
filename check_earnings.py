import sqlite3

conn = sqlite3.connect('data/swing_model.db')
c = conn.cursor()

c.execute('SELECT MIN(report_date), MAX(report_date), COUNT(*) FROM earnings_raw')
date_range = c.fetchone()
print(f'Earnings date range: {date_range[0]} to {date_range[1]} ({date_range[2]} total)')

c.execute('SELECT report_date, COUNT(*) FROM earnings_raw GROUP BY report_date ORDER BY report_date')
print('\nEarnings by report date:')
for row in c.fetchall():
    print(f'  {row[0]}: {row[1]} reports')

c.execute('SELECT year, quarter, COUNT(*) FROM earnings_raw GROUP BY year, quarter ORDER BY year, quarter')
print('\nEarnings by quarter:')
for row in c.fetchall():
    print(f'  {row[0]} Q{row[1]}: {row[2]} reports')

conn.close()
