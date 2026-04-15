"""
Visualization Module for People Analytics

Generates publication-quality charts for all three analytics modules:
- Sentiment analysis: heatmaps, distribution plots, trend lines
- Headcount forecasting: time series with confidence intervals
- ONA: network graphs, community detection, influence maps
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap


# Color palette
COLORS = {
    "primary": "#2563eb",
    "success": "#059669",
    "warning": "#d97706",
    "danger": "#dc2626",
    "neutral": "#6b7280",
    "positive": "#059669",
    "negative": "#dc2626",
    "bg": "#f8fafc",
}

DEPT_COLORS = {
    "Engineering": "#2563eb", "Product": "#7c3aed", "Sales": "#dc2626",
    "Marketing": "#d97706", "HR": "#059669", "Finance": "#0891b2",
    "Operations": "#4b5563", "Customer Success": "#db2777",
}


def plot_sentiment_heatmap(sentiment_by_dept: pd.DataFrame,
                           save_path: str = None) -> plt.Figure:
    """Heatmap of sentiment scores across departments."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Select numeric columns for the heatmap
    numeric_cols = ["mean_sentiment", "pct_positive", "pct_negative", "pct_neutral"]
    available_cols = [c for c in numeric_cols if c in sentiment_by_dept.columns]

    data = sentiment_by_dept[available_cols]

    cmap = LinearSegmentedColormap.from_list("sentiment", ["#dc2626", "#fbbf24", "#059669"])
    im = ax.imshow(data.values, cmap=cmap, aspect="auto")

    ax.set_xticks(range(len(available_cols)))
    ax.set_xticklabels([c.replace("_", " ").title() for c in available_cols], rotation=45, ha="right")
    ax.set_yticks(range(len(data.index)))
    ax.set_yticklabels(data.index)

    # Add value labels
    for i in range(len(data.index)):
        for j in range(len(available_cols)):
            val = data.values[i, j]
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)

    plt.colorbar(im, ax=ax, label="Score")
    ax.set_title("Sentiment Analysis by Department", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_sentiment_distribution(df: pd.DataFrame,
                                save_path: str = None) -> plt.Figure:
    """Distribution of sentiment scores."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Histogram of compound scores
    scores = df["sentiment_compound"].dropna()
    axes[0].hist(scores, bins=30, color=COLORS["primary"], alpha=0.7, edgecolor="white")
    axes[0].axvline(x=0, color=COLORS["danger"], linestyle="--", alpha=0.5)
    axes[0].set_xlabel("Sentiment Score")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Distribution of Sentiment Scores")

    # Label breakdown
    labels = df["sentiment_label"].value_counts()
    colors = [COLORS.get(l, COLORS["neutral"]) for l in labels.index]
    axes[1].bar(labels.index, labels.values, color=colors, edgecolor="white")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Sentiment Label Distribution")

    plt.suptitle("Employee Sentiment Overview", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_sentiment_trends(trend_df: pd.DataFrame,
                          save_path: str = None) -> plt.Figure:
    """Sentiment trends over survey periods."""
    fig, ax = plt.subplots(figsize=(10, 5))

    if "group" in trend_df.columns:
        for group in trend_df["group"].unique():
            group_data = trend_df[trend_df["group"] == group].sort_values("period")
            color = DEPT_COLORS.get(group, COLORS["neutral"])
            ax.plot(group_data["period"], group_data["mean_sentiment"],
                    marker="o", label=group, color=color, linewidth=2)
    else:
        ax.plot(trend_df.index, trend_df["mean_sentiment"],
                marker="o", color=COLORS["primary"], linewidth=2)

    ax.axhline(y=0, color=COLORS["neutral"], linestyle="--", alpha=0.3)
    ax.set_xlabel("Survey Period")
    ax.set_ylabel("Mean Sentiment Score")
    ax.set_title("Sentiment Trends Over Time", fontsize=14, fontweight="bold")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_headcount_forecast(historical: pd.DataFrame,
                            forecast_df: pd.DataFrame,
                            department: str,
                            save_path: str = None) -> plt.Figure:
    """Time series plot with forecast and confidence intervals."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Historical
    dept_hist = historical[historical["department"] == department].sort_values("date")
    ax.plot(pd.to_datetime(dept_hist["date"]), dept_hist["headcount"],
            color=COLORS["primary"], linewidth=2, label="Historical")

    # Forecast
    dept_fc = forecast_df[forecast_df["department"] == department]
    for model in dept_fc["model"].unique():
        model_data = dept_fc[dept_fc["model"] == model].sort_values("forecast_date")
        dates = pd.to_datetime(model_data["forecast_date"])

        color = COLORS["success"] if "trend" in model else COLORS["warning"]
        ax.plot(dates, model_data["forecast_headcount"],
                color=color, linewidth=2, linestyle="--",
                label=f"Forecast ({model.replace('_', ' ').title()})")

        ax.fill_between(dates, model_data["ci_lower"], model_data["ci_upper"],
                        alpha=0.15, color=color)

    ax.set_xlabel("Date")
    ax.set_ylabel("Headcount")
    ax.set_title(f"Headcount Forecast — {department}", fontsize=14, fontweight="bold")
    ax.legend()
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_scenario_comparison(scenario_df: pd.DataFrame,
                             save_path: str = None) -> plt.Figure:
    """Bar chart comparing scenario outcomes."""
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS["danger"] if nc < 0 else COLORS["success"]
              for nc in scenario_df["net_change"]]

    bars = ax.barh(scenario_df["scenario"], scenario_df["net_change"],
                   color=colors, edgecolor="white", height=0.6)

    # Add value labels
    for bar, pct in zip(bars, scenario_df["pct_change"]):
        width = bar.get_width()
        ax.text(width + (5 if width >= 0 else -5), bar.get_y() + bar.get_height() / 2,
                f"{pct:+.1f}%", va="center", ha="left" if width >= 0 else "right",
                fontsize=10, fontweight="bold")

    ax.axvline(x=0, color=COLORS["neutral"], linestyle="-", linewidth=0.5)
    ax.set_xlabel("Net Headcount Change")
    ax.set_title("Scenario Comparison — 12-Month Impact", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_network_graph(adjacency_matrix: pd.DataFrame,
                       node_metrics: pd.DataFrame = None,
                       save_path: str = None) -> plt.Figure:
    """Visualize the collaboration network as a node-link diagram."""
    fig, ax = plt.subplots(figsize=(10, 10))

    nodes = adjacency_matrix.index.tolist()
    n = len(nodes)
    matrix = adjacency_matrix.values.astype(float)

    # Circular layout
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)

    # Draw edges
    max_weight = matrix.max()
    for i in range(n):
        for j in range(i + 1, n):
            weight = matrix[i][j] + matrix[j][i]
            if weight > 0:
                alpha = min(weight / max_weight * 0.8, 0.8)
                linewidth = max(0.5, weight / max_weight * 4)
                ax.plot([x[i], x[j]], [y[i], y[j]],
                        color=COLORS["neutral"], alpha=alpha,
                        linewidth=linewidth, zorder=1)

    # Draw nodes
    for i, node in enumerate(nodes):
        color = DEPT_COLORS.get(node, COLORS["primary"])
        size = 800
        if node_metrics is not None and "total_interactions" in node_metrics.columns:
            node_data = node_metrics[node_metrics["department"] == node]
            if not node_data.empty:
                size = 400 + node_data["total_interactions"].iloc[0] * 0.5

        ax.scatter(x[i], y[i], s=size, c=color, zorder=2, edgecolors="white", linewidth=2)
        ax.annotate(node, (x[i], y[i]), textcoords="offset points",
                    xytext=(0, 15), ha="center", fontsize=9, fontweight="bold")

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Organizational Collaboration Network", fontsize=14, fontweight="bold")

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_influence_map(influence_df: pd.DataFrame,
                       save_path: str = None) -> plt.Figure:
    """Scatter plot of centrality metrics colored by role."""
    fig, ax = plt.subplots(figsize=(10, 8))

    role_colors = {
        "connector": COLORS["success"],
        "hub": COLORS["primary"],
        "bottleneck": COLORS["danger"],
        "peripheral": COLORS["neutral"],
    }

    for role in influence_df["role"].unique():
        role_data = influence_df[influence_df["role"] == role]
        color = role_colors.get(role, COLORS["neutral"])
        ax.scatter(
            role_data["degree_centrality"],
            role_data["betweenness_centrality"],
            s=role_data["influence_score"] * 2000 + 100,
            c=color, label=role.title(), alpha=0.7,
            edgecolors="white", linewidth=1.5
        )
        for _, row in role_data.iterrows():
            ax.annotate(row["department"], (row["degree_centrality"], row["betweenness_centrality"]),
                        textcoords="offset points", xytext=(8, 5), fontsize=8)

    ax.set_xlabel("Degree Centrality (breadth of connections)")
    ax.set_ylabel("Betweenness Centrality (bridge importance)")
    ax.set_title("Department Influence Map", fontsize=14, fontweight="bold")
    ax.legend(title="Role")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig
