from charts import plot_word_cloud


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


def render_word_frequencies_section(pdf, word_frequencies):

    pdf.multi_cell(
        w=0,
        text=" " * 6
        + '"Word frequency" also known as "word occurrence frequency," refers to the number of times a particular word appears in a given text corpus. This measure is often used in text analysis and natural language processing (NLP) to understand trends, themes, and language characteristics within a set of documents.',
        new_y="NEXT",
        new_x="LMARGIN",
    )

    pdf.ln(5)

    pdf.cell(
        w=0,
        text="Calculating word frequency for YouTube comments offers several advantages:",
        new_y="NEXT",
        new_x="LMARGIN",
    )

    purposes = [
        "**Understanding Main Themes**: By analyzing word frequency, you can identify the main topics discussed in the comments. This can help you understand what interests your audience and the questions or subjects they are most passionate about.",
        "**Detecting Trends**: Word frequency can reveal emerging trends in comments. You can identify words or phrases that occur frequently, which may indicate recurring concerns or popular topics among viewers.",
        "**Identifying Sentiments**: Certain words or expressions may indicate specific feelings or emotions. By analyzing the frequency of words associated with positive or negative sentiments, you can assess the overall opinion of viewers toward the video.",
        "**Feedback on Content**: By understanding which words frequently appear in comments, you can gain insights into how the video content is perceived. Positive words may indicate a favorable reception, while negative words may signal areas where improvements are needed.",
        "**Engagement with the Audience**: Using information on word frequency, you can adjust your content strategy to better meet the needs and interests of your audience. This can increase engagement and foster a closer relationship with viewers.",
    ]

    render_list(purposes, pdf)

    fig = plot_word_cloud(word_frequencies["POSITIVE"], color="green")
    pdf.add_fig(fig, legend="Wordcloud for positive word frequencies")

    fig = plot_word_cloud(word_frequencies["NEGATIVE"], color="red")
    pdf.add_fig(fig, legend="Wordcloud for negative word frequencies")

    fig = plot_word_cloud(word_frequencies["MIXED"], color="yellow")
    pdf.add_fig(fig, legend="Wordcloud for mixed word frequencies")

    fig = plot_word_cloud(word_frequencies["NEUTRAL"], color="blue")
    pdf.add_fig(fig, legend="Wordcloud for neutral word frequencies")
