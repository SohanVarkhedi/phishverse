"""
PHISHVERSE – run_campaign.py
Campaign-mode launcher. Loads a campaign, filters events, runs the game,
and saves the result to analytics/results/.

Usage:
    python run_campaign.py --campaign hr_campaign --employee emp01
    python run_campaign.py --campaign finance_campaign --employee emp04
    python run_campaign.py --campaign employee_campaign --employee emp07
    python run_campaign.py --list          (list available campaigns)
    python run_campaign.py                 (free play — all events)

Free play (no --campaign flag) runs the full game as normal, no result saved.
"""

import sys
import argparse
from analytics.campaign_loader import CampaignLoader


def parse_args():
    parser = argparse.ArgumentParser(
        prog="run_campaign.py",
        description="PHISHVERSE Campaign Launcher",
    )
    parser.add_argument(
        "--campaign", "-c",
        type=str,
        default=None,
        metavar="CAMPAIGN_ID",
        help="Campaign ID to run (e.g. hr_campaign). Omit for free play.",
    )
    parser.add_argument(
        "--employee", "-e",
        type=str,
        default="",
        metavar="EMPLOYEE_ID",
        help="Employee ID for result tracking (e.g. emp01).",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available campaign IDs and exit.",
    )
    return parser.parse_args()


def print_campaign_info(campaign):
    print()
    print("=" * 50)
    print(f"  PHISHVERSE CAMPAIGN MODE")
    print("=" * 50)
    print(f"  Campaign : {campaign.name}")
    print(f"  Dept     : {campaign.department}")
    print(f"  Events   : {', '.join(campaign.enabled_events)}")
    print(f"  Pass score: {campaign.pass_score}")
    print(f"  Duration : {campaign.duration_days} days")
    print("=" * 50)
    print()


def main():
    args = parse_args()

    # ── List mode ─────────────────────────────────────────────────────────────
    if args.list:
        available = CampaignLoader.list_available()
        if not available:
            print("No campaigns found in campaigns/ directory.")
            sys.exit(0)
        print("\nAvailable campaigns:")
        for cid in available:
            c = CampaignLoader.load(cid)
            print(f"  {cid:<30} dept={c.department:<12} events={len(c.enabled_events)}")
        print()
        sys.exit(0)

    # ── Campaign mode ─────────────────────────────────────────────────────────
    campaign = None
    if args.campaign:
        try:
            campaign = CampaignLoader.load(args.campaign)
        except FileNotFoundError as e:
            print(f"\nERROR: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"\nINVALID CAMPAIGN: {e}")
            sys.exit(1)

        if args.employee and not campaign.has_employee(args.employee):
            print(f"\nWARNING: Employee '{args.employee}' is not in campaign "
                  f"'{campaign.campaign_id}' employee list.")
            print("Proceeding anyway — result will still be saved.\n")

        print_campaign_info(campaign)

    else:
        print("\n[PHISHVERSE] Free-play mode — all events enabled. No result saved.\n")

    # ── Launch game ───────────────────────────────────────────────────────────
    # Import here so pygame init happens after arg parsing
    from main import Game
    Game(campaign=campaign, employee_id=args.employee).run()


if __name__ == "__main__":
    main()
