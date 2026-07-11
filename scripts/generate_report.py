#!/usr/bin/env python3
"""
Historical reporting script for the Ollama pipeline.
Parses workflow_summary.json files and generates a markdown trend report.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_workflow_summaries(results_dir='results'):
    """Parse all workflow_summary.json files under results_dir."""
    summaries = []
    results_path = Path(results_dir)

    if not results_path.exists():
        return summaries

    for summary_file in results_path.rglob('workflow_summary.json'):
        try:
            with open(summary_file) as f:
                summaries.append(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Skipping unreadable summary {summary_file}: {e}")

    return sorted(summaries, key=lambda x: x.get('timestamp', ''), reverse=True)


def calculate_trends(summaries):
    """Calculate basic statistics and trends from historical summaries."""
    if len(summaries) < 3:
        return {'status': 'insufficient_data', 'run_count': len(summaries)}

    recent = summaries[:5]
    older = summaries[5:10] if len(summaries) > 5 else []

    file_type_counts = defaultdict(int)
    for s in summaries:
        for f in s.get('files_created', []):
            suffix = Path(f).suffix or 'no-extension'
            file_type_counts[suffix] += 1

    recent_count = len(recent)
    older_count = len(older)

    trend_direction = "stable"
    if older_count > 0:
        if recent_count > older_count:
            trend_direction = "improving"
        elif recent_count < older_count:
            trend_direction = "declining"

    return {
        'status': 'ok',
        'run_count': len(summaries),
        'recent_runs': recent_count,
        'file_type_counts': dict(file_type_counts),
        'trend_direction': trend_direction,
    }


def generate_markdown_report(summaries, trends):
    """Generate a markdown report from summaries and calculated trends."""
    report = ["# Historical Analysis Report", ""]
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append(f"Total runs analyzed: {len(summaries)}")
    report.append("")

    if trends.get('status') == 'insufficient_data':
        report.append("## Insufficient Data")
        report.append("")
        report.append(
            f"Only {trends['run_count']} run(s) recorded so far. "
            "At least 3 runs are needed for trend analysis. "
            "Keep running the workflow to build history."
        )
        return "\n".join(report)

    report.append("## Executive Summary")
    report.append("")
    report.append(f"- Total workflow runs recorded: {trends['run_count']}")
    report.append(f"- Runs in recent window: {trends['recent_runs']}")

    trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}
    emoji = trend_emoji.get(trends['trend_direction'], "➡️")
    report.append(f"- Overall activity trend: {emoji} {trends['trend_direction']}")
    report.append("")

    report.append("## Trends")
    report.append("")
    report.append("| Metric | Value | Trend |")
    report.append("|--------|-------|-------|")
    report.append(f"| Total runs | {trends['run_count']} | {emoji} |")
    report.append(f"| Recent runs (last 5) | {trends['recent_runs']} | {emoji} |")
    report.append("")

    report.append("## File Types Analyzed")
    report.append("")
    report.append("| File Type | Count |")
    report.append("|-----------|-------|")
    for ftype, count in sorted(trends['file_type_counts'].items(), key=lambda x: -x[1]):
        report.append(f"| {ftype} | {count} |")
    report.append("")

    report.append("## Recommendations")
    report.append("")
    if trends['trend_direction'] == "declining":
        report.append("- Activity has slowed recently. Verify the workflow is still triggering as expected.")
    elif trends['trend_direction'] == "improving":
        report.append("- Activity is increasing. Consider adding cleanup for old result directories.")
    else:
        report.append("- Activity is stable. No immediate action needed.")

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Generate historical trend report")
    parser.add_argument("--results-dir", default="results", help="Directory containing workflow_summary.json files")
    parser.add_argument("--output", default="historical_report.md", help="Output markdown file path")
    args = parser.parse_args()

    summaries = parse_workflow_summaries(args.results_dir)
    trends = calculate_trends(summaries)
    report = generate_markdown_report(summaries, trends)

    with open(args.output, 'w') as f:
        f.write(report)

    print(f"Report written to {args.output}")
    print(report)


if __name__ == "__main__":
    main()

