import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from statsmodels.tsa.stattools import adfuller
import warnings
warnings.filterwarnings("ignore")

# === GLOBAL SETTINGS ===
ticker = "SPY"  # Note: VIXY has had extreme reverse splits that can cause data issues
start_date = "2010-01-01"
end_date = "2025-10-01"
initial_capital = 10_000
cost_per_trade = 0.001  # 0.1% per trade (applied to notional value)
stop_loss = -0.03        # -3% stop
take_profit = 0.05       # +5% take profit

print("="*70)
print("MEAN REVERSION BACKTEST")
print("="*70)
print(f"Note: {ticker} has undergone multiple reverse splits (1:10, 1:5, 1:4)")
print("which can cause historical price data anomalies. This backtest uses")
print("adjusted prices and return-based analysis for accuracy.\n")

# === DATA ===
print(f"📊 Downloading {ticker} data from {start_date} to {end_date}...")
df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# Use Adj Close which properly handles splits and dividends
df['Close'] = df['Adj Close'].copy()
df['returns'] = df['Close'].pct_change()
df = df.dropna()

# Sanity check for data quality
if df['Close'].max() / df['Close'].min() > 10000:
    print("⚠️ Warning: Extreme price range detected. Data may have split adjustment issues.")

print(f"✓ Loaded {len(df)} trading days")
print(f"Price range: ${df['Close'].min():.2f} - ${df['Close'].max():.2f}")
print(f"Recent price: ${df['Close'].iloc[-1]:.2f}")

# === Stationarity Check ===
adf_result = adfuller(df['Close'].dropna())
adf_p = adf_result[1]
print(f"\nADF p-value (stationarity test): {adf_p:.4f}")
if adf_p > 0.05:
    print("⚠️ Warning: Price series is likely non-stationary. Mean reversion may not be reliable.\n")
else:
    print("✓ Series is stationary - mean reversion may be viable.\n")

# === STRATEGY FUNCTION ===
def backtest_mean_reversion(window, z_entry, z_exit, dynamic_position=False, filter_vol=True):
    data = df.copy()
    data['mean'] = data['Close'].ewm(span=window, adjust=False).mean()
    data['std'] = data['Close'].ewm(span=window, adjust=False).std()
    
    # Avoid division by zero
    data['z_score'] = np.where(data['std'] > 0, 
                                (data['Close'] - data['mean']) / data['std'], 
                                0)

    # Volatility filter
    if filter_vol:
        data['volatility'] = data['returns'].rolling(10).std()
        vol_threshold = data['volatility'].quantile(0.9)
        data.loc[data['volatility'] > vol_threshold, 'z_score'] = 0

    # Signal logic: -1 (short), 0 (neutral), 1 (long)
    data['signal'] = 0
    data.loc[data['z_score'] < -z_entry, 'signal'] = 1   # Oversold - buy
    data.loc[data['z_score'] > z_entry, 'signal'] = -1    # Overbought - sell
    data.loc[abs(data['z_score']) < z_exit, 'signal'] = 0  # Exit zone
    
    # Forward fill position (hold until exit signal)
    data['position'] = data['signal'].replace(0, method='ffill').fillna(0)

    # Dynamic position sizing (based on z-score strength)
    if dynamic_position:
        position_size = np.clip(-data['z_score'] / z_entry, -1, 1)
        data['position'] = np.sign(data['position']) * abs(position_size)

    # Calculate returns on position (use next day's return)
    data['position_lag'] = data['position'].shift(1).fillna(0)
    data['strategy_raw'] = data['position_lag'] * data['returns']
    
    # Apply stop loss / take profit
    data['strategy_clipped'] = np.clip(data['strategy_raw'], stop_loss, take_profit)

    # Calculate trading costs based on position changes
    data['position_change'] = abs(data['position'].diff().fillna(0))
    data['trade_cost'] = cost_per_trade * data['position_change']
    data['strategy_net'] = data['strategy_clipped'] - data['trade_cost']

    # Portfolio growth (cumulative product of returns)
    data['equity_curve'] = initial_capital * (1 + data['strategy_net']).cumprod()
    
    # Buy and hold benchmark
    data['buy_hold_curve'] = initial_capital * (1 + data['returns']).cumprod()

    # Performance metrics
    final_value = data['equity_curve'].iloc[-1]
    total_return = (final_value / initial_capital - 1) * 100
    
    # CAGR
    years = len(data) / 252
    cagr = ((final_value / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
    
    # Sharpe ratio (annualized)
    if data['strategy_net'].std() > 0:
        sharpe = np.sqrt(252) * data['strategy_net'].mean() / data['strategy_net'].std()
    else:
        sharpe = 0
    
    # Max drawdown
    cummax = data['equity_curve'].cummax()
    drawdown = (data['equity_curve'] - cummax) / cummax
    max_drawdown = drawdown.min() * 100
    
    # Win rate (percentage of profitable days)
    winning_days = (data['strategy_net'] > 0).sum()
    losing_days = (data['strategy_net'] < 0).sum()
    win_rate = winning_days / (winning_days + losing_days) * 100 if (winning_days + losing_days) > 0 else 0

    return {
        'total_return': total_return,
        'cagr': cagr,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'final_value': final_value,
        'data': data
    }

# === PARAMETER GRID SEARCH ===
windows = [10, 20, 30, 50]
z_entries = [1.0, 1.5, 2.0]
z_exits = [0.3, 0.5, 0.7]

results = []
print("🔍 Optimizing parameters...")

for w, ze, zx in product(windows, z_entries, z_exits):
    try:
        result = backtest_mean_reversion(w, ze, zx, dynamic_position=False, filter_vol=True)
        results.append({
            'Window': w,
            'Z_Entry': ze,
            'Z_Exit': zx,
            'Return': result['total_return'],
            'CAGR': result['cagr'],
            'Sharpe': result['sharpe'],
            'MaxDD': result['max_drawdown'],
            'WinRate': result['win_rate']
        })
    except Exception as e:
        print(f"Error with params (w={w}, ze={ze}, zx={zx}): {e}")
        continue

results_df = pd.DataFrame(results)

# Sanity check for results
if results_df['Return'].max() > 10000:  # More than 10,000% return is suspicious
    print("⚠️ Warning: Unrealistic returns detected. There may be data quality issues.")
    print("This often happens with VIXY due to extreme reverse splits.")
    print("Results should be interpreted with caution.\n")

print(f"\n=== Top 5 Parameter Combinations (by Sharpe) ===")
top_5 = results_df.sort_values(by='Sharpe', ascending=False).head()
print(top_5.to_string(index=False, float_format='%.2f'))

best = results_df.sort_values(by='Sharpe', ascending=False).iloc[0]

print(f"\n=== Optimal Parameters ===")
print(f"Window: {int(best.Window)} | Z_Entry: {best.Z_Entry} | Z_Exit: {best.Z_Exit}")
print(f"Sharpe: {best.Sharpe:.2f} | Return: {best.Return:.2f}% | Max DD: {best.MaxDD:.2f}%")

# === FINAL MODEL WITH BEST PARAMS ===
final_result = backtest_mean_reversion(
    int(best.Window), 
    best.Z_Entry, 
    best.Z_Exit, 
    dynamic_position=True,
    filter_vol=True
)
best_df = final_result['data']
buy_hold_return = (best_df['buy_hold_curve'].iloc[-1] / initial_capital - 1) * 100

print(f"\n{'='*70}")
print(f"FINAL BACKTEST RESULTS ({ticker})")
print(f"{'='*70}")
print(f"Period: {best_df.index[0].strftime('%Y-%m-%d')} to {best_df.index[-1].strftime('%Y-%m-%d')}")
print(f"Initial Capital: ${initial_capital:,.0f}")
print(f"\nStrategy Performance:")
print(f"  Final Value:      ${final_result['final_value']:,.2f}")
print(f"  Total Return:     {final_result['total_return']:+.2f}%")
print(f"  CAGR:             {final_result['cagr']:+.2f}%")
print(f"  Sharpe Ratio:     {final_result['sharpe']:.2f}")
print(f"  Max Drawdown:     {final_result['max_drawdown']:.2f}%")
print(f"  Win Rate:         {final_result['win_rate']:.1f}%")
print(f"\nBuy & Hold Benchmark:")
print(f"  Final Value:      ${best_df['buy_hold_curve'].iloc[-1]:,.2f}")
print(f"  Total Return:     {buy_hold_return:+.2f}%")
print(f"\nOutperformance:     {final_result['total_return'] - buy_hold_return:+.2f}%")
print(f"{'='*70}")

# === TRADE LOG ===
print("\n📊 Generating Trade Log...")
trades = []
in_position = False
entry_price = None
entry_date = None
position_type = None

for i in range(len(best_df)):
    current_pos = best_df['position'].iloc[i]
    price = best_df['Close'].iloc[i]
    date = best_df.index[i]
    
    # Entry: position changes from 0 to non-zero
    if not in_position and current_pos != 0:
        in_position = True
        entry_price = price
        entry_date = date
        position_type = 'Long' if current_pos > 0 else 'Short'
    
    # Exit: position changes to 0 or reverses
    elif in_position and (current_pos == 0 or np.sign(current_pos) != np.sign(best_df['position'].iloc[i-1])):
        exit_price = price
        exit_date = date
        
        # Calculate P&L
        if position_type == 'Long':
            pnl_pct = (exit_price - entry_price) / entry_price * 100
        else:  # Short
            pnl_pct = (entry_price - exit_price) / entry_price * 100
        
        hold_days = (exit_date - entry_date).days
        
        trades.append({
            'Entry Date': entry_date.strftime('%Y-%m-%d'),
            'Exit Date': exit_date.strftime('%Y-%m-%d'),
            'Days': hold_days,
            'Type': position_type,
            'Entry': entry_price,
            'Exit': exit_price,
            'Return %': pnl_pct
        })
        
        # Check if immediately entering new position
        if current_pos != 0:
            in_position = True
            entry_price = price
            entry_date = date
            position_type = 'Long' if current_pos > 0 else 'Short'
        else:
            in_position = False

trades_df = pd.DataFrame(trades)

if not trades_df.empty:
    print(f"\n{'='*70}")
    print("TRADE SUMMARY")
    print(f"{'='*70}")
    print(f"Total Trades:       {len(trades_df)}")
    print(f"Winning Trades:     {(trades_df['Return %'] > 0).sum()} ({(trades_df['Return %'] > 0).sum() / len(trades_df) * 100:.1f}%)")
    print(f"Losing Trades:      {(trades_df['Return %'] < 0).sum()} ({(trades_df['Return %'] < 0).sum() / len(trades_df) * 100:.1f}%)")
    print(f"Avg Return:         {trades_df['Return %'].mean():+.2f}%")
    print(f"Avg Win:            {trades_df[trades_df['Return %'] > 0]['Return %'].mean():+.2f}%")
    print(f"Avg Loss:           {trades_df[trades_df['Return %'] < 0]['Return %'].mean():+.2f}%")
    print(f"Best Trade:         {trades_df['Return %'].max():+.2f}%")
    print(f"Worst Trade:        {trades_df['Return %'].min():+.2f}%")
    print(f"Avg Hold Period:    {trades_df['Days'].mean():.1f} days")
    print(f"\nLast 10 Trades:")
    print(trades_df.tail(10).to_string(index=False, float_format='%.2f'))
else:
    print("No completed trades found.")

# === PLOTS ===
fig = plt.figure(figsize=(16, 14))
gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.25)

# Price & Signals (spans both columns)
ax1 = fig.add_subplot(gs[0, :])
ax1.set_title(f"{ticker} Mean Reversion Strategy | Window={int(best.Window)}, Z_Entry=±{best.Z_Entry}, Z_Exit=±{best.Z_Exit}", 
              fontsize=14, fontweight='bold')
ax1.plot(best_df['Close'], label='Price', color='#2E86AB', alpha=0.8, linewidth=1.5)
ax1.plot(best_df['mean'], label=f'{int(best.Window)}-period EMA', color='#F77F00', linewidth=2)

# Bollinger-style bands
upper_band = best_df['mean'] + 2 * best_df['std']
lower_band = best_df['mean'] - 2 * best_df['std']
ax1.fill_between(best_df.index, lower_band, upper_band,
                 color='gray', alpha=0.15, label='±2σ Band')

# Plot signals
buy_signals = best_df[(best_df['signal'] == 1) & (best_df['signal'].shift(1) != 1)]
sell_signals = best_df[(best_df['signal'] == -1) & (best_df['signal'].shift(1) != -1)]

ax1.scatter(buy_signals.index, buy_signals['Close'],
            label='Buy Signal', marker='^', color='#06D6A0', s=120, zorder=5, edgecolors='black', linewidths=0.5)
ax1.scatter(sell_signals.index, sell_signals['Close'],
            label='Sell Signal', marker='v', color='#EF476F', s=120, zorder=5, edgecolors='black', linewidths=0.5)

ax1.set_ylabel('Price ($)', fontsize=11)
ax1.set_yscale('log')  # Log scale helps with extreme price ranges
ax1.legend(loc='best', fontsize=9)
ax1.grid(alpha=0.3, linestyle='--')

# Z-Score (spans both columns)
ax2 = fig.add_subplot(gs[1, :])
ax2.plot(best_df['z_score'], label='Z-Score', color='#8338EC', alpha=0.8, linewidth=1.5)
ax2.axhline(y=best.Z_Entry, color='#EF476F', linestyle='--', linewidth=1.5, label=f'Entry: ±{best.Z_Entry}')
ax2.axhline(y=-best.Z_Entry, color='#EF476F', linestyle='--', linewidth=1.5)
ax2.axhline(y=best.Z_Exit, color='#06D6A0', linestyle='--', linewidth=1.5, label=f'Exit: ±{best.Z_Exit}')
ax2.axhline(y=-best.Z_Exit, color='#06D6A0', linestyle='--', linewidth=1.5)
ax2.axhline(y=0, color='black', linestyle='-', alpha=0.4, linewidth=0.8)
ax2.fill_between(best_df.index, -best.Z_Entry, best.Z_Entry, alpha=0.1, color='gray')
ax2.set_ylabel('Z-Score', fontsize=11)
ax2.set_title('Mean Reversion Z-Score', fontsize=12)
ax2.legend(loc='best', fontsize=9)
ax2.grid(alpha=0.3, linestyle='--')

# Equity Curves (spans both columns)
ax3 = fig.add_subplot(gs[2, :])
ax3.plot(best_df['equity_curve'], label='Mean Reversion Strategy', color='#8338EC', linewidth=2.5)
ax3.plot(best_df['buy_hold_curve'], label='Buy & Hold', color='gray', linestyle='--', linewidth=2, alpha=0.7)
ax3.fill_between(best_df.index, initial_capital, best_df['equity_curve'], 
                 where=(best_df['equity_curve'] >= initial_capital), 
                 alpha=0.2, color='green')
ax3.fill_between(best_df.index, initial_capital, best_df['equity_curve'], 
                 where=(best_df['equity_curve'] < initial_capital), 
                 alpha=0.2, color='red')
ax3.axhline(y=initial_capital, color='black', linestyle=':', alpha=0.5)
ax3.set_ylabel('Portfolio Value ($)', fontsize=11)
ax3.set_title(f'Equity Curve | Final: ${final_result["final_value"]:,.0f} ({final_result["total_return"]:+.1f}%)', 
              fontsize=12)
ax3.legend(loc='best', fontsize=9)
ax3.grid(alpha=0.3, linestyle='--')
ax3.set_yscale('log')  # Log scale for better visualization

# Drawdown chart (left)
ax4 = fig.add_subplot(gs[3, 0])
cummax = best_df['equity_curve'].cummax()
drawdown_curve = (best_df['equity_curve'] - cummax) / cummax * 100
ax4.fill_between(best_df.index, drawdown_curve, 0, color='red', alpha=0.3)
ax4.plot(best_df.index, drawdown_curve, color='darkred', linewidth=1.5)
ax4.set_ylabel('Drawdown (%)', fontsize=10)
ax4.set_xlabel('Date', fontsize=10)
ax4.set_title(f'Drawdown Over Time | Max: {final_result["max_drawdown"]:.2f}%', fontsize=11)
ax4.grid(alpha=0.3, linestyle='--')

# Monthly returns distribution (right)
ax5 = fig.add_subplot(gs[3, 1])
monthly_returns = best_df.groupby(best_df.index.to_period('M'))['strategy_net'].apply(lambda x: (1 + x).prod() - 1) * 100
ax5.hist(monthly_returns, bins=30, color='#8338EC', alpha=0.7, edgecolor='black')
ax5.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax5.axvline(x=monthly_returns.mean(), color='red', linestyle='-', linewidth=2, label=f'Mean: {monthly_returns.mean():.2f}%')
ax5.set_xlabel('Monthly Return (%)', fontsize=10)
ax5.set_ylabel('Frequency', fontsize=10)
ax5.set_title('Distribution of Monthly Returns', fontsize=11)
ax5.legend(fontsize=9)
ax5.grid(alpha=0.3, linestyle='--', axis='y')

plt.tight_layout()
plt.show()

print(f"\n✓ Analysis complete!")

# === ADDITIONAL ANALYSIS ===
print(f"\n{'='*70}")
print("ADDITIONAL INSIGHTS")
print(f"{'='*70}")

# Monthly returns distribution
best_df['year_month'] = best_df.index.to_period('M')
monthly_returns = best_df.groupby('year_month')['strategy_net'].apply(lambda x: (1 + x).prod() - 1) * 100
print(f"\nMonthly Return Statistics:")
print(f"  Avg Monthly Return:   {monthly_returns.mean():+.2f}%")
print(f"  Monthly Std Dev:      {monthly_returns.std():.2f}%")
print(f"  Best Month:           {monthly_returns.max():+.2f}%")
print(f"  Worst Month:          {monthly_returns.min():+.2f}%")
print(f"  Positive Months:      {(monthly_returns > 0).sum()} / {len(monthly_returns)} ({(monthly_returns > 0).sum() / len(monthly_returns) * 100:.1f}%)")

# Annual returns
best_df['year'] = best_df.index.year
annual_returns = best_df.groupby('year')['strategy_net'].apply(lambda x: (1 + x).prod() - 1) * 100
print(f"\nAnnual Returns by Year:")
for year, ret in annual_returns.items():
    print(f"  {year}: {ret:+7.2f}%")

# Trade analysis by direction
if not trades_df.empty:
    long_trades = trades_df[trades_df['Type'] == 'Long']
    short_trades = trades_df[trades_df['Type'] == 'Short']
    
    print(f"\nTrade Analysis by Direction:")
    print(f"  Long Trades:  {len(long_trades)} trades | Avg Return: {long_trades['Return %'].mean():+.2f}% | Win Rate: {(long_trades['Return %'] > 0).sum() / len(long_trades) * 100:.1f}%")
    print(f"  Short Trades: {len(short_trades)} trades | Avg Return: {short_trades['Return %'].mean():+.2f}% | Win Rate: {(short_trades['Return %'] > 0).sum() / len(short_trades) * 100:.1f}%")

# Drawdown analysis
cummax = best_df['equity_curve'].cummax()
drawdown = (best_df['equity_curve'] - cummax) / cummax * 100
drawdown_periods = []
in_drawdown = False
start_dd = None

for i, dd in enumerate(drawdown):
    if dd < -1 and not in_drawdown:  # Entered drawdown
        in_drawdown = True
        start_dd = best_df.index[i]
    elif dd >= -0.5 and in_drawdown:  # Recovered
        in_drawdown = False
        drawdown_periods.append({
            'start': start_dd,
            'end': best_df.index[i],
            'days': (best_df.index[i] - start_dd).days,
            'depth': drawdown[start_dd:best_df.index[i]].min()
        })

if drawdown_periods:
    print(f"\nDrawdown Analysis:")
    print(f"  Number of Drawdowns > 1%: {len(drawdown_periods)}")
    avg_recovery = np.mean([dd['days'] for dd in drawdown_periods])
    print(f"  Avg Recovery Time:        {avg_recovery:.0f} days")
    longest_dd = max(drawdown_periods, key=lambda x: x['days'])
    print(f"  Longest Drawdown:         {longest_dd['days']} days (from {longest_dd['start'].strftime('%Y-%m-%d')})")
    deepest_dd = min(drawdown_periods, key=lambda x: x['depth'])
    print(f"  Deepest Drawdown:         {deepest_dd['depth']:.2f}% (on {deepest_dd['start'].strftime('%Y-%m-%d')})")

print(f"{'='*70}")
