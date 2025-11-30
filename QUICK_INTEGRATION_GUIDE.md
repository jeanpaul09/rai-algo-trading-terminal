# Quick Integration Guide - Get Real Data in 5 Minutes

## The Fastest Path to Real Data

### Option 1: Use the Implementation File (Recommended)

```bash
# 1. Replace the stub with the real implementation
cp api_server_implementation.py api_server.py

# 2. Start API server
python api_server.py

# 3. In another terminal, start dashboard with API URL
cd ui/web
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

**That's it!** The implementation automatically:
- ✅ Discovers strategies from `rai_algo/strategies/`
- ✅ Loads blueprints from `blueprints/`
- ✅ Loads backtest results from `backtest_results/` (if you save them)
- ✅ Connects to LiveTrader instances

### Option 2: Manual Integration

If you want to customize, see `api_server_implementation.py` for:
- How to discover strategies
- How to load backtest results
- How to connect LiveTrader instances

## Saving Backtest Results

To see experiments in the dashboard, save your backtest results:

```python
from BACKTEST_STORAGE_EXAMPLE import save_backtest_result

# After running a backtest
save_backtest_result(
    result=backtest_result,  # Your BacktestResult object
    strategy_name="MyStrategy",
    market="BTC/USD",
    start_date="2024-01-01",
    end_date="2024-03-31",
)
```

Results are saved to `backtest_results/` and automatically loaded by the API server.

## What You'll See

Once connected:
- **Dashboard**: Real strategy counts, metrics, equity curves
- **Strategy Lab**: All discovered strategies with their metrics
- **Experiment Lab**: All saved backtest results
- **Live Lab**: Status from active LiveTrader instances

## Troubleshooting

**No strategies showing?**
- Check `rai_algo/strategies/` has Python files
- Check `blueprints/` has JSON files
- Check API server logs for errors

**No experiments showing?**
- Make sure you're saving backtest results
- Check `backtest_results/` directory exists
- Verify JSON files are valid

**Live trading not showing?**
- Make sure LiveTrader instances are registered
- Check traders are actually running
- Verify status endpoint returns data

## Next Steps

1. Run some backtests and save results
2. Start a LiveTrader instance
3. Watch the dashboard populate with real data!


