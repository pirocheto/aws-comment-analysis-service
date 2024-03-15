import calplot
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image
from wordcloud import WordCloud

sentiment_colors = [
    "#9fc5a4",
    "#8ea1ee",
    "#f0c7b0",
    "#f0e1b0",
]


def fig_to_img(fig):
    canvas = FigureCanvas(fig)
    canvas.draw()
    img = Image.fromarray(np.asarray(canvas.buffer_rgba()))
    return img


def plot_sent_bar(data, ax=None):

    if ax is None:
        ax = plt.gca()

    labels = data.keys()
    values = data.values()

    total = sum(values)
    percents = [value / total * 100 for value in values]

    bar_labels = [
        f"{value} ({percent:.2f}%)" for value, percent in zip(values, percents)
    ]

    bars = ax.bar(labels, values, color=sentiment_colors)
    ax.bar_label(bars, bar_labels, padding=5, fontsize=12)

    ax.get_yaxis().set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", bottom=False)

    return ax


def plot_cal_heatmat(data, color):
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        None,
        ["lightyellow", color],
    )

    fig, _ = calplot.calplot(
        data,
        tight_layout=False,
        colorbar=False,
        linewidth=0.5,
        linecolor="#dddddd",
        vmin=0,
        cmap=cmap,
        edgecolor="black",
        fillcolor="white",
        dropzero=False,
    )
    return fig


def plot_word_cloud(frequencies, color="black"):
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        None,
        ["lightgrey", color],
    )
    fig = plt.figure(figsize=(8, 4))
    wc = WordCloud(
        background_color="white",
        include_numbers=True,
        random_state=42,
        colormap=cmap,
        margin=0,
        max_words=50,
        height=200,
        width=400,
    )
    wc.generate_from_frequencies(frequencies)
    plt.tight_layout()
    plt.imshow(wc)
    plt.axis("off")
    return fig


# import matplotlib.pyplot as plt
# import pandas as pd

# colors = [
#     "#f0e1b0",
#     "#f0c7b0",
#     "#8ea1ee",
#     "#9fc5a4",
# ]


# def plot_sent_percent(df, ax=None):

#     if ax is None:
#         ax = plt.gca()

#     sents = df.value_counts("Sentiment").sort_index()
#     values = sents.values
#     labels = sents.index

#     total = sum(values)
#     percents = [value / total * 100 for value in values]

#     bars = ax.barh(
#         labels,
#         values,
#         color=colors,
#         # color="white",
#         # edgecolor="black",
#         height=0.5,
#     )

#     for i, bar in enumerate(bars):
#         width = bar.get_width()
#         percent = percents[i]
#         ax.text(
#             width,
#             bar.get_y() + bar.get_height() / 2,
#             f"  {width} ({percent:.2f}%)",
#             ha="left",
#             va="center",
#         )

#     ax.get_xaxis().set_visible(False)
#     ax.spines["right"].set_visible(False)
#     ax.spines["top"].set_visible(False)
#     ax.spines["left"].set_visible(False)
#     ax.spines["bottom"].set_visible(False)
#     ax.tick_params(axis="y", left=False)

#     return ax


# def plot_sent_timeline(df, ax=None):

#     if ax is None:
#         ax = plt.gca()

#     # Convert 'publishedat' column to datetime
#     df["publishedAt"] = pd.to_datetime(df["publishedAt"])

#     # Extract month from 'publishedat' column
#     df["month"] = df["publishedAt"].dt.month
#     df["year"] = df["publishedAt"].dt.year
#     df["year_month"] = df["publishedAt"].dt.strftime("%Y-%m")

#     sents = df.groupby(["year_month", "Sentiment"]).size().unstack(fill_value=0)
#     # sents = (sents.div(sents.sum(axis=1), axis=0) * 100).round(2)
#     ax = sents.plot.bar(rot=30, color=colors, ax=ax, stacked=True)

#     # sents = df["year_month"].value_counts().sort_index()
#     # ax = sents.plot(ax=ax, rot=30)

#     ax.spines["right"].set_visible(False)
#     ax.spines["top"].set_visible(False)
#     ax.spines["left"].set_visible(False)
#     # ax.spines["bottom"].set_visible(False)
#     ax.spines["bottom"].set_alpha(0.3)
#     # ax.set_yticks([])
#     ax.tick_params(axis="x", bottom=False, left=False)
#     ax.tick_params(axis="y", bottom=False, left=False)
#     # ax.legend().remove()
#     ax.set_xlabel(None)
#     ax.yaxis.grid(True, alpha=0.5)
#     ax.set_axisbelow(True)
#     return ax
