import matplotlib.pyplot as plt
import pandas as pd
from charts import fig_to_img, plot_cal_heatmat, plot_sent_bar
from fpdf import Align, FontFace
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


def render_list(elements, pdf):
    for elem in elements:
        pdf.cell(text="*")
        pdf.multi_cell(
            w=0,
            text=elem,
            new_y="NEXT",
            new_x="LMARGIN",
            markdown=True,
        )
        pdf.ln(3)


def render_sentiment_section(pdf, data, df_data_by_day):

    pdf.cell(
        text="Sentiment analysis of YouTube comments can serve several purposes:",
        new_y="NEXT",
        new_x="LMARGIN",
    )
    pdf.ln(5)

    purpose_table = [
        "**Understanding Public Opinion**: It helps understand how viewers perceive a particular video, content creator, or topic. This can be valuable for content creators and businesses looking to ensure that their videos or products are well-received by their target audience.",
        "**Feedback for Content Creators**: Content creators can use sentiment analysis to understand their audience's reactions to their videos. It can help them adjust their content, identify what works well, and what needs improvement.",
        "**Detection of Emotional Trends**: By analyzing sentiments expressed in comments, emotional trends such as anger, joy, sadness, etc., can be spotted. This information can be useful for understanding the emotional impact of a specific video or event.",
        "**Online Reputation Management**: For brands and businesses, sentiment analysis of YouTube comments can help monitor their online reputation. By identifying negative comments or customer concerns, they can intervene quickly to resolve issues and maintain a positive image.",
        "**Influencer Identification**: By analyzing comments, one can identify individuals who have significant influence within a particular community. This can be useful for brands seeking to collaborate with influencers to promote their products or services.",
    ]

    render_list(purpose_table, pdf)

    pdf.ln(5)

    pdf.multi_cell(
        w=0,
        text="The comments are classified into 4 categories described in the table below:",
        new_y="NEXT",
        new_x="LMARGIN",
    )
    pdf.ln(5)

    sentiment_table = [
        ("Positive", "The text expresses an overall positive sentiment."),
        ("Negative", "The text expresses an overall negative sentiment."),
        ("Mixed", "The text expresses both positive and negative sentiments."),
        (
            "Neutral",
            "The text does not express either positive or negative sentiments.",
        ),
    ]

    with pdf.table(first_row_as_headings=False) as table:
        for data_row in sentiment_table:
            row = table.row()
            row.cell(data_row[0], style=FontFace(emphasis="B"))
            for datum in data_row[1:]:
                row.cell(datum, colspan=3)

    pdf.ln(10)
    pdf.cell(text="A. Overall Sentiment Proportion", new_y="NEXT", new_x="LMARGIN")

    fig = plt.figure()
    plot_sent_bar(data)
    pdf.add_fig(fig, legend="Sentiment Proportion")
    pdf.ln(10)

    pdf.cell(text="B. Calendar sentiment intensity", new_y="NEXT", new_x="LMARGIN")
    fig = plot_cal_heatmat(df_data_by_day["POSITIVE"], color="green")
    pdf.add_fig(fig, legend="Heatmap representing positive sentiment by date")
    pdf.ln(10)

    fig = plot_cal_heatmat(df_data_by_day["NEUTRAL"], color="blue")
    pdf.add_fig(fig, legend="Heatmap to represent neutral sentiment by date")
    pdf.ln(10)

    fig = plot_cal_heatmat(df_data_by_day["NEGATIVE"], color="red")
    pdf.add_fig(fig, legend="Heatmap to represent negative sentiment by date")
    pdf.ln(10)

    fig = plot_cal_heatmat(df_data_by_day["MIXED"], color="orange")
    pdf.add_fig(fig, legend="Heatmap to represent mixed sentiment by date")
    pdf.ln(10)
