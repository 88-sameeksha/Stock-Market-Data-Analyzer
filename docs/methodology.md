# Methodology

1. Retrieve historical OHLCV data from Yahoo Finance or load a CSV.
2. Normalize column names, parse dates, validate closing prices, sort records, and remove duplicate dates.
3. Calculate daily percentage returns using `pct_change()`.
4. Calculate 20- and 50-observation simple moving averages.
5. Calculate rolling 20-observation standard deviation of daily returns.
6. Annualize the standard deviation of daily returns using the conventional square-root-of-252 scaling.
7. Calculate drawdown relative to the running maximum closing price.
8. Export processed observations, charts, and a text summary.

The sample CSV is illustrative synthetic data. It is not actual market data. The sample has fewer than 20 observations, so moving-average and rolling-volatility fields remain unavailable until sufficient observations exist.
