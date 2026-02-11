"""
Matplotlib visualizations for the CityBike platform.
Updated to meet specific assignment requirements:
1. Bar chart: Revenue by User Type
2. Line chart: Monthly trip volume trend
3. Histogram: Trip duration distribution
4. Box plot: Trip duration comparison by User Type
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "figures"


def set_plot_style() -> None:
    """Apply a clean global style for all charts."""
    plt.style.use("ggplot")
    plt.rcParams.update({
        "figure.figsize": (10, 6),
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
    })
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _save_figure(fig: plt.Figure, filename: str) -> None:
    """Save a Matplotlib figure to the figures directory."""
    path = OUTPUT_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved {path.name}")


# ---------------------------------------------------------------------------
# 1. Bar Chart: Revenue by User Type 
# ---------------------------------------------------------------------------
def plot_revenue_by_user_type(system) -> None:
    """Bar chart showing total revenue per user type."""
    if "fare" not in system.trips.columns:
        print("[WARNING] Fares not computed. Skipping revenue chart.")
        return

    revenue = system.trips.groupby("user_type")["fare"].sum()

    fig, ax = plt.subplots()
    bars = ax.bar(revenue.index, revenue.values, color=["#F8B195", "#6C5B7B"])
    
    ax.set_title("Total Revenue by User Type")
    ax.set_xlabel("User Type")
    ax.set_ylabel("Revenue ($)")

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'${height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom')

    _save_figure(fig, "01_bar_revenue.png")


# ---------------------------------------------------------------------------
# 2. Line Chart: Monthly trip trend
# ---------------------------------------------------------------------------
def plot_monthly_trend(system) -> None:
    """Line chart showing trip volume over time."""
    df = system.trips.copy()
    
    df['month_year'] = df['start_time'].dt.to_period('M')
    
    trend = df.groupby('month_year').size()

    x_dates = trend.index.astype(str)

    fig, ax = plt.subplots()
    ax.plot(x_dates, trend.values, marker='o', linestyle='-', color='purple', linewidth=2)
    
    ax.set_title("Monthly Trip Volume Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Trips")
    plt.xticks(rotation=45)
    
    _save_figure(fig, "02_line_trend.png")


# ---------------------------------------------------------------------------
# 3. Histogram: Trip Duration Distribution 
# ---------------------------------------------------------------------------
def plot_duration_histogram(system) -> None:
    """Histogram showing distribution of trip durations."""
    data = system.trips[system.trips['duration_minutes'] < 60]['duration_minutes']

    fig, ax = plt.subplots()
    ax.hist(data, bins=30, color='#4ECDC4', edgecolor='white', alpha=0.8)
    
    ax.set_title("Trip Duration Distribution (Trips < 60 min)")
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Frequency")
    
    _save_figure(fig, "03_hist_duration.png")


# ---------------------------------------------------------------------------
# 4. Box Plot: Duration by User Type 
# ---------------------------------------------------------------------------
def plot_duration_boxplot(system) -> None:
    """Box plot comparing trip duration between Casual and Member users."""

    df_filtered = system.trips[system.trips['duration_minutes'] < 60]
    
    casual_data = df_filtered[df_filtered['user_type'] == 'casual']['duration_minutes']
    member_data = df_filtered[df_filtered['user_type'] == 'member']['duration_minutes']
    
    data_to_plot = [casual_data, member_data]

    fig, ax = plt.subplots()
    ax.boxplot(data_to_plot, labels=['Casual', 'Member'], patch_artist=True,
               boxprops=dict(facecolor='#FFD700', color='black'),
               medianprops=dict(color='black'))
    
    ax.set_title("Trip Duration Comparison: Casual vs Member")
    ax.set_ylabel("Duration (minutes)")
    
    _save_figure(fig, "04_boxplot_duration.png")


# ---------------------------------------------------------------------------
# Run all plots
# ---------------------------------------------------------------------------
def generate_all_plots(system) -> None:
    """Generate and save all visualizations."""
    print("Generating visualizations...")
    set_plot_style()

    # 1. Bar Chart
    plot_revenue_by_user_type(system) 

    # 2. Line Chart
    plot_monthly_trend(system)

    # 3. Histogram
    plot_duration_histogram(system)

    # 4. Box Plot
    plot_duration_boxplot(system)

    print(f"All plots saved to {OUTPUT_DIR}")


    