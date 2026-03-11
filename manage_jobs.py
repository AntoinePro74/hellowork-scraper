#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manage job offers database: view, filter, and apply to offers.
"""

import argparse
import logging
from tabulate import tabulate
from scraper.database.db_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def list_offers(db: DatabaseManager, filter_type: str):
    """List job offers with optional filtering."""
    try:
        if filter_type == "new":
            query = "SELECT url, title, company, new_offer, applied FROM job_offers WHERE new_offer = True ORDER BY scraped_at DESC;"
            title = "NEW OFFERS (new_offer = True)"
        elif filter_type == "applied":
            query = "SELECT url, title, company, new_offer, applied FROM job_offers WHERE applied = True ORDER BY scraped_at DESC;"
            title = "APPLIED OFFERS (applied = True)"
        else:
            query = "SELECT url, title, company, new_offer, applied FROM job_offers ORDER BY scraped_at DESC;"
            title = "ALL OFFERS"

        db.cursor.execute(query)
        rows = db.cursor.fetchall()

        if not rows:
            print(f"\n{title}")
            print("No offers found.")
            return

        # Format for display
        headers = ["URL", "Title", "Company", "New", "Applied"]
        formatted_rows = [
            (row[0][:60] + "..." if len(row[0]) > 60 else row[0],
             row[1][:40] + "..." if len(row[1]) > 40 else row[1],
             row[2] or "N/A",
             "✓" if row[3] else " ",
             "✓" if row[4] else " ")
            for row in rows
        ]

        print(f"\n{title}")
        print(tabulate(formatted_rows, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(rows)} offers\n")

    except Exception as e:
        logger.error(f"Error listing offers: {e}")


def apply_offer(db: DatabaseManager, url: str):
    """Mark an offer as applied."""
    try:
        success = db.mark_applied(url)
        if success:
            print(f"\n✓ Offer marked as applied: {url}\n")
        else:
            print(f"\n✗ Offer not found: {url}\n")
    except Exception as e:
        logger.error(f"Error applying offer: {e}")


def show_stats(db: DatabaseManager):
    """Show database statistics."""
    try:
        # Total offers
        db.cursor.execute("SELECT COUNT(*) FROM job_offers;")
        total = db.cursor.fetchone()[0]

        # New offers
        db.cursor.execute("SELECT COUNT(*) FROM job_offers WHERE new_offer = True;")
        new_count = db.cursor.fetchone()[0]

        # Applied offers
        db.cursor.execute("SELECT COUNT(*) FROM job_offers WHERE applied = True;")
        applied = db.cursor.fetchone()[0]

        # Inactive (old offers not applied)
        db.cursor.execute("SELECT COUNT(*) FROM job_offers WHERE new_offer = False AND applied = False;")
        inactive = db.cursor.fetchone()[0]

        # Display stats
        stats_data = [
            ["Total offers", total],
            ["New offers (to apply)", new_count],
            ["Applied offers", applied],
            ["Inactive offers (old, not applied)", inactive],
        ]

        print("\n" + "=" * 60)
        print("JOB OFFERS STATISTICS")
        print("=" * 60)
        print(tabulate(stats_data, headers=["Metric", "Count"], tablefmt="grid"))
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Error showing stats: {e}")


def main():
    parser = argparse.ArgumentParser(description="Manage job offers database")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list command
    list_parser = subparsers.add_parser("list", help="List job offers")
    list_parser.add_argument(
        "--new",
        action="store_true",
        help="Show only new offers (new_offer=True)"
    )
    list_parser.add_argument(
        "--applied",
        action="store_true",
        help="Show only applied offers (applied=True)"
    )

    # apply command
    apply_parser = subparsers.add_parser("apply", help="Mark an offer as applied")
    apply_parser.add_argument("url", help="URL of the offer to mark as applied")

    # stats command
    subparsers.add_parser("stats", help="Show database statistics")

    args = parser.parse_args()

    # Initialize database
    db = DatabaseManager()
    db.connect()
    db.create_table()

    try:
        if args.command == "list":
            if args.new:
                list_offers(db, "new")
            elif args.applied:
                list_offers(db, "applied")
            else:
                list_offers(db, "all")

        elif args.command == "apply":
            apply_offer(db, args.url)

        elif args.command == "stats":
            show_stats(db)

        else:
            parser.print_help()

    finally:
        db.close()


if __name__ == "__main__":
    main()
