from config import OUT_DIR
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="tab10")

_LOCATION_ORDER = ["local", "cloud", "webapi"]
_SIZE_ORDER = ["50kb", "100kb"]


def _save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_latency_distribution(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("Latency Distribution (REQUEST_SENT → TRANSFER_COMPLETE)", fontsize=13, fontweight="bold")

    sns.boxplot(
        data=df, 
        x="location", y="latency_ms", hue="size",
        order=_LOCATION_ORDER, hue_order=_SIZE_ORDER,
        native_scale=False,
        ax=ax,
    )
    
    ax.set_xlabel("Location")
    ax.set_ylabel("Latency (ms)")
    ax.legend(title="File size")

    plt.tight_layout()
    _save(fig, "latency_distribution.png")


def plot_throughput(df: pd.DataFrame) -> None:
    df = df.dropna(subset=["throughput_kbs"])
    
    summary = (
        df.groupby(["location", "size"], observed=True)["throughput_kbs"]
        .mean()
        .round(2)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("Mean Throughput (bytes ÷ transfer time)", fontsize=13, fontweight="bold")

    sns.barplot(
        data=summary,
        x="location", y="throughput_kbs", hue="size",
        order=_LOCATION_ORDER, hue_order=_SIZE_ORDER,
        edgecolor="black", linewidth=0.6,
        ax=ax
    )

    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f kb/s", padding=4, fontsize=8)

    ax.set_xlabel("Location")
    ax.set_ylabel("Throughput (kb/s)")
    ax.legend(title="File Size")
 
    plt.tight_layout()
    _save(fig, "throughput_comparison.png")


def plot_latency_vs_throughput(df: pd.DataFrame) -> None:
    df = df.dropna(subset=["throughput_kbs"])
    if df.empty:
        return None

    markers ={"local": "o", "cloud": "s", "webapi": "^"}

    fig, ax = plt.subplots(figsize=(9, 6))
    
    for (location, size), group in df.groupby(["location", "size"], observed=True):
        ax.scatter(
            group["throughput_kbs"], group["latency_ms"],
            label=f"{location} / {size}",
            marker=markers[location],
            alpha=0.65, s=45, edgecolors="none",
        )

    ax.set_xlabel("Throughput (kbps)")
    ax.set_ylabel("Latency (ms)")
    ax.legend(title="Location / Size")
 
    plt.tight_layout()
    _save(fig, "latency_vs_throughput.png")


def plot_latency_percentiles(df: pd.DataFrame) -> None:
    summary = (
        df.groupby(["location", "size"], observed=True)["latency_ms"]
        .agg(
            lat_p50_ms=lambda x: x.quantile(0.50),
            lat_p95_ms=lambda x: x.quantile(0.95),
            lat_p99_ms=lambda x: x.quantile(0.99),
        )
        .round(2)
    )

    percentiles = {
        "p50": "lat_p50_ms",
        "p95": "lat_p95_ms",
        "p99": "lat_p99_ms",
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    fig.suptitle("Latency Percentiles by Location and File Size (ms)",
                 fontsize=13, fontweight="bold")

    for ax, (label, col) in zip(axes, percentiles.items()):
        pivot = summary[col].unstack(level="size")

        sns.heatmap(
            pivot,
            annot=True, fmt=".0f",
            cmap="YlOrRd",
            linewidths=0.5,
            ax=ax,
            cbar=False,
        )

        ax.set_title(label)
        ax.set_xlabel("File size")
        ax.set_ylabel("Location")

    plt.tight_layout()
    _save(fig, "latency_percentiles.png")


def plot_effective_throughput(df: pd.DataFrame) -> None:
    df = df.dropna(subset=["throughput_kbs", "throughput_real_kbs"])

    raw = (
        df.groupby(["location", "size"], observed=True)["throughput_kbs"]
        .mean().round(2).reset_index()
        .rename(columns={"throughput_kbs": "throughput"})
    )
    raw["type"] = "Raw"

    effective = (
        df.groupby(["location", "size"], observed=True)["throughput_real_kbs"]
        .mean().round(2).reset_index()
        .rename(columns={"throughput_real_kbs": "throughput"})
    )
    effective["type"] = "Effective"

    combined = pd.concat([raw, effective])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Raw vs Effective Throughput (KB/s)  [base64 overhead × 0.75]",
                 fontsize=13, fontweight="bold")

    for ax, size in zip(axes, _SIZE_ORDER):
        subset = combined[combined["size"] == size]

        sns.barplot(
            data=subset,
            x="location", y="throughput", hue="type",
            order=_LOCATION_ORDER, hue_order=["Raw", "Effective"],
            edgecolor="black", linewidth=0.6,
            ax=ax,
        )

        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f KB/s", padding=4, fontsize=8)

        ax.set_title(size)
        ax.set_xlabel("Location")
        ax.set_ylabel("Throughput (KB/s)")
        ax.legend(title="Throughput")

    plt.tight_layout()
    _save(fig, "effective_throughput.png")