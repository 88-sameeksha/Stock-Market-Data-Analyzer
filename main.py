import argparse
from src.analyzer import fetch_stock_data, load_csv_data, run_analysis


def main():
    parser = argparse.ArgumentParser(description="Stock Market Data Analyzer")
    parser.add_argument("--ticker", default="RELIANCE.NS")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2026-01-01",
                        help="End date is exclusive for Yahoo Finance.")
    parser.add_argument("--source", choices=["yfinance", "csv"], default="yfinance")
    parser.add_argument("--csv", default="data/raw/sample_stock_data.csv")
    args = parser.parse_args()

    print("=" * 48)
    print("          STOCK MARKET DATA ANALYZER")
    print("=" * 48)

    try:
        if args.source == "yfinance":
            raw = fetch_stock_data(args.ticker, args.start, args.end)
            if raw is None:
                raise RuntimeError("Could not fetch data. Try CSV mode.")
        else:
            raw = load_csv_data(args.csv)

        data, stats, csv_path, report_path = run_analysis(raw, args.ticker)

        print("\nANALYSIS SUMMARY")
        print(f"Ticker: {args.ticker}")
        print(f"Records: {stats['total_records']}")
        print(f"Highest price: {stats['highest_price']:.2f}")
        print(f"Lowest price: {stats['lowest_price']:.2f}")
        print(f"Total historical return: {stats['total_return']:.2f}%")
        print(f"Annualized volatility: {stats['annualized_volatility']:.2f}%")
        print(f"Maximum drawdown: {stats['maximum_drawdown']:.2f}%")
        print(f"Trend: {stats['trend']}")
        print(f"\nProcessed CSV: {csv_path}")
        print(f"Report: {report_path}")
        print("Charts saved in outputs/charts/")
        print("\nAnalysis completed successfully!")

    except Exception as exc:
        print(f"\nERROR: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
