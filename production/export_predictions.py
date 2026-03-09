"""
Export detailed prediction results to CSV for analysis.

Shows complete documentation of:
- What we predicted
- What actually happened
- Whether we were correct
"""

import sys
import os
import csv
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.db import get_connection

# Windows UTF-8 fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def export_predictions_to_csv(filename='prediction_results.csv'):
    """Export all predictions with full details to CSV."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            prediction_timestamp,
            ticker,
            day0_date,
            day0_return,
            day0_direction,
            day0_volume_ratio,
            day0_catalyst,
            reversion_prob_day2,
            confidence_tier,
            predicted_direction,
            actual_return_day1,
            actual_return_day2,
            actual_return_day3,
            actual_reverted_day2,
            scored_at,
            model_version
        FROM forward_predictions
        ORDER BY day0_date DESC, prediction_timestamp DESC
    """)

    rows = cursor.fetchall()

    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Prediction Time',
            'Ticker',
            'Move Date',
            'Original Move %',
            'Direction (1=Up, -1=Down)',
            'Volume Ratio',
            'Catalyst',
            'Predicted Reversion Prob',
            'Confidence',
            'Predicted Will Revert (1=Yes)',
            'Actual Return Day 1',
            'Actual Return Day 2',
            'Actual Return Day 3',
            'Actually Reverted (1=Yes)',
            'Scored At',
            'Model Version'
        ])

        # Data
        for row in rows:
            writer.writerow(row)

    conn.close()

    print(f"✓ Exported {len(rows)} predictions to {filename}")
    return filename


def show_detailed_predictions():
    """Show detailed prediction table in terminal."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ticker,
            day0_date,
            day0_return,
            day0_direction,
            day0_volume_ratio,
            day0_catalyst,
            reversion_prob_day2,
            confidence_tier,
            actual_reverted_day2,
            scored_at
        FROM forward_predictions
        ORDER BY day0_date DESC, prediction_timestamp DESC
        LIMIT 50
    """)

    predictions = cursor.fetchall()

    print("\n" + "=" * 140)
    print(" " * 50 + "DETAILED PREDICTION RESULTS")
    print("=" * 140)
    print()

    if not predictions:
        print("No predictions yet.")
        conn.close()
        return

    # Header
    print(f"{'Ticker':<7} {'Date':<12} {'Move':<10} {'Dir':<5} {'Vol':<6} {'Catalyst':<10} "
          f"{'Prob':<7} {'Conf':<7} {'Result':<8} {'Scored':<20}")
    print("-" * 140)

    scored_count = 0
    correct_count = 0

    import struct

    for row in predictions:
        ticker, date, move, direction, vol_ratio, catalyst, prob, conf, result, scored = row

        # Convert binary data if needed
        if isinstance(prob, bytes):
            try:
                prob = struct.unpack('d', prob)[0]
            except:
                prob = None
        if isinstance(move, bytes):
            try:
                move = struct.unpack('d', move)[0]
            except:
                move = None
        if isinstance(vol_ratio, bytes):
            try:
                vol_ratio = struct.unpack('d', vol_ratio)[0]
            except:
                vol_ratio = None

        # Format values
        move_str = f"{move*100:+.1f}%" if move else "N/A"
        dir_str = "UP" if direction == 1 else "DOWN" if direction == -1 else "?"
        vol_str = f"{vol_ratio:.1f}x" if vol_ratio else "N/A"
        prob_str = f"{prob*100:.0f}%" if prob else "N/A"

        if result is not None:
            result_str = "✓ YES" if result == 1 else "✗ NO"
            scored_count += 1
            if result == 1:
                correct_count += 1
        else:
            result_str = "Pending"

        scored_str = scored[:19] if scored else "Not yet"

        print(f"{ticker:<7} {date:<12} {move_str:<10} {dir_str:<5} {vol_str:<6} {catalyst or 'unknown':<10} "
              f"{prob_str:<7} {conf:<7} {result_str:<8} {scored_str:<20}")

    print("-" * 140)
    print(f"\nTotal: {len(predictions)} predictions")

    if scored_count > 0:
        win_rate = (correct_count / scored_count) * 100
        print(f"Scored: {scored_count} ({correct_count} correct, {scored_count - correct_count} wrong)")
        print(f"Win Rate: {win_rate:.1f}%")
    else:
        print("Scored: 0 (all pending)")

    print()
    conn.close()


if __name__ == "__main__":
    # Show detailed table
    show_detailed_predictions()

    # Offer to export
    export = input("\nExport to CSV? (y/n): ").strip().lower()
    if export == 'y':
        filename = export_predictions_to_csv()
        print(f"\nYou can now open {filename} in Excel or Google Sheets for detailed analysis!")
