from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CHART_DIR = BASE_DIR / "outputs" / "charts"
REPORT_DIR = BASE_DIR / "outputs" / "reports"

for folder in (RAW_DIR, PROCESSED_DIR, CHART_DIR, REPORT_DIR):
    folder.mkdir(parents=True, exist_ok=True)


def fetch_stock_data(ticker, start_date, end_date):
    """Download historical data. Yahoo Finance end date is exclusive."""
    try:
        data = yf.download(
            ticker, start=start_date, end=end_date,
            auto_adjust=True, progress=False
        )
        if data.empty:
            raise ValueError("No data returned. Check ticker/date range.")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data.reset_index()
    except Exception as exc:
        print(f"Data fetching failed: {exc}")
        return None


def load_csv_data(file_path):
    data = pd.read_csv(file_path)
    if data.empty:
        raise ValueError("CSV file is empty.")
    return data


def clean_stock_data(data):
    data = data.copy()
    data.columns = [
        str(c).strip().lower().replace(" ", "_") for c in data.columns
    ]
    if "date" not in data.columns and "datetime" in data.columns:
        data.rename(columns={"datetime": "date"}, inplace=True)
    if "close" not in data.columns and "adj_close" in data.columns:
        data.rename(columns={"adj_close": "close"}, inplace=True)
    if "date" not in data.columns or "close" not in data.columns:
        raise ValueError("Input must contain Date and Close columns.")

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for col in ("open", "high", "low", "close", "volume"):
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    data.dropna(subset=["date", "close"], inplace=True)
    data = data[data["close"] > 0]
    data.sort_values("date", inplace=True)
    data.drop_duplicates(subset=["date"], keep="last", inplace=True)
    data.reset_index(drop=True, inplace=True)

    if len(data) < 2:
        raise ValueError("At least two valid observations are required.")
    return data


def calculate_indicators(data):
    data = data.copy()
    data["daily_return"] = data["close"].pct_change() * 100
    data["SMA_20"] = data["close"].rolling(20, min_periods=20).mean()
    data["SMA_50"] = data["close"].rolling(50, min_periods=50).mean()
    data["volatility_20"] = data["daily_return"].rolling(
        20, min_periods=20
    ).std()
    data["running_peak"] = data["close"].cummax()
    data["drawdown"] = (data["close"] / data["running_peak"] - 1) * 100
    return data


def generate_statistics(data):
    returns = data["daily_return"].dropna()
    if returns.empty:
        raise ValueError("Not enough data for return analysis.")

    last_price = float(data["close"].iloc[-1])
    first_price = float(data["close"].iloc[0])
    if len(data) >= 50 and pd.notna(data["SMA_50"].iloc[-1]):
        trend = (
            "Above 50-day moving average"
            if last_price > data["SMA_50"].iloc[-1]
            else "Below 50-day moving average"
        )
    else:
        trend = "Insufficient data for 50-day trend"

    return {
        "first_date": data["date"].iloc[0].strftime("%Y-%m-%d"),
        "last_date": data["date"].iloc[-1].strftime("%Y-%m-%d"),
        "total_records": len(data),
        "highest_price": float(data["close"].max()),
        "lowest_price": float(data["close"].min()),
        "first_close": first_price,
        "last_close": last_price,
        "total_return": (last_price / first_price - 1) * 100,
        "average_daily_return": float(returns.mean()),
        "daily_volatility": float(returns.std()),
        "annualized_volatility": float(returns.std() * np.sqrt(252)),
        "maximum_drawdown": float(data["drawdown"].min()),
        "best_daily_return": float(returns.max()),
        "worst_daily_return": float(returns.min()),
        "trend": trend,
    }


def save_processed_data(data, ticker):
    path = PROCESSED_DIR / f"{ticker}_analysis.csv"
    data.to_csv(path, index=False)
    return path


def _save_plot(filename):
    plt.tight_layout()
    plt.savefig(CHART_DIR / filename, dpi=200, bbox_inches="tight")
    plt.close()


def plot_stock_price(data, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(data["date"], data["close"], label="Adjusted Close")
    plt.title(f"{ticker} Historical Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Adjusted closing price")
    plt.legend()
    plt.grid(alpha=0.3)
    _save_plot(f"{ticker}_stock_price.png")


def plot_moving_averages(data, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(data["date"], data["close"], label="Adjusted Close", alpha=0.65)
    plt.plot(data["date"], data["SMA_20"], label="20-Day SMA")
    plt.plot(data["date"], data["SMA_50"], label="50-Day SMA")
    plt.title(f"{ticker} Moving Average Analysis")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(alpha=0.3)
    _save_plot(f"{ticker}_moving_averages.png")


def plot_returns_distribution(data, ticker):
    plt.figure(figsize=(10, 6))
    sns.histplot(data["daily_return"].dropna(), bins=30, kde=True)
    plt.title(f"{ticker} Daily Returns Distribution")
    plt.xlabel("Daily return (%)")
    plt.ylabel("Frequency")
    plt.grid(alpha=0.2)
    _save_plot(f"{ticker}_returns_distribution.png")


def plot_volatility(data, ticker):
    plt.figure(figsize=(12, 6))
    plt.plot(data["date"], data["volatility_20"])
    plt.title(f"{ticker} 20-Day Rolling Volatility")
    plt.xlabel("Date")
    plt.ylabel("Daily return standard deviation (%)")
    plt.grid(alpha=0.3)
    _save_plot(f"{ticker}_volatility.png")


def generate_report(stats, ticker):
    path = REPORT_DIR / f"{ticker}_report.txt"
    report = f"""STOCK MARKET ANALYSIS REPORT
========================================
Ticker: {ticker}
Period: {stats['first_date']} to {stats['last_date']}
Records: {stats['total_records']}

PRICE ANALYSIS
Highest price: {stats['highest_price']:.2f}
Lowest price: {stats['lowest_price']:.2f}
First adjusted close: {stats['first_close']:.2f}
Last adjusted close: {stats['last_close']:.2f}

PERFORMANCE
Total historical return: {stats['total_return']:.2f}%
Average daily return: {stats['average_daily_return']:.4f}%
Best daily return: {stats['best_daily_return']:.2f}%
Worst daily return: {stats['worst_daily_return']:.2f}%

RISK
Daily volatility: {stats['daily_volatility']:.4f}%
Annualized volatility: {stats['annualized_volatility']:.2f}%
Maximum drawdown: {stats['maximum_drawdown']:.2f}%

TREND
{stats['trend']}

DISCLAIMER
Educational analysis only. Not financial advice.
Historical performance does not guarantee future results.
"""
    path.write_text(report, encoding="utf-8")
    return path


def run_analysis(raw_data, ticker):
    data = clean_stock_data(raw_data)
    data = calculate_indicators(data)
    stats = generate_statistics(data)
    csv_path = save_processed_data(data, ticker)
    plot_stock_price(data, ticker)
    plot_moving_averages(data, ticker)
    plot_returns_distribution(data, ticker)
    plot_volatility(data, ticker)
    report_path = generate_report(stats, ticker)
    return data, stats, csv_path, report_path
