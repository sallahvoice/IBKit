"""CLI entry point for IBkit."""

import argparse

try:
    from backend.domain.company import Company
except ImportError:
    Company = None


def main():
    """Parse arguments and create a company from ticker."""
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--ticker", type=str, help="company ticker")
    args = ap.parse_args()
    if Company and args.ticker:
        Company.create_company_from_ticker(args.ticker)
    elif not Company:
        print("Error: Could not import Company from domain.company.")


if __name__ == "__main__":
    main()