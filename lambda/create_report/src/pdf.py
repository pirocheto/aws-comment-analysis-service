from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from charts import fig_to_img, plot_cal_heatmat
from fpdf import FPDF, Align, FontFace, TitleStyle
from sections.general import render_general_section
from sections.sentiment import render_sentiment_section
from sections.word_frequencies import render_word_frequencies_section

VIDEO_LINK = "https://www.youtube.com/watch?v="


class PDF(FPDF):
    def __init__(
        self,
        video_id,
        font_family="Helvetica",
        orientation="portrait",
        unit="mm",
        format="A4",
        font_cache_dir="DEPRECATED",
    ) -> None:
        super().__init__(orientation, unit, format, font_cache_dir)

        self.strf_creation_date = self.creation_date.strftime(
            "Created %Y-%m-%d at %H:%M:%S"
        )
        self.video_id = video_id
        self.video_link = VIDEO_LINK + video_id
        self.body_font_size = 11
        self.font_family = font_family
        self.nb_charts = 0

        self.set_font_size(11)
        self.set_margin(20)
        self.set_text_color(80)
        self.set_section_title_styles(
            TitleStyle(
                font_size_pt=20,
                b_margin=10,
                t_margin=10,
            )
        )

    def add_title(self, title, subtitle):
        self.set_title(title)
        self.set_font_size(30)
        self.add_page()
        self.cell(
            w=0,
            text="YOUTUBE COMMENT ANALYSIS",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.ln(5)
        self.set_font(size=20)
        self.cell(
            w=0,
            text=subtitle,
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
        )
        self.set_font(size=self.body_font_size)

    def add_disclosure(self):
        self.cell(
            w=0,
            text="**Disclosure: Automatically Generated Report**",
            new_x="LMARGIN",
            new_y="NEXT",
            align="C",
            markdown=True,
        )
        self.ln(10)
        self.multi_cell(
            w=0,
            text=" " * 10
            + "This report has been automatically generated using data analysis software. It is important to note that the information presented in this report is based on the data available at the time of generation and may be subject to variations or errors. While efforts have been made to ensure the accuracy and consistency of the results, it is recommended to consult other sources and conduct manual verification if necessary."
            "This report is provided for informational purposes only and should not be considered as a sole or definitive source of information. Users are encouraged to exercise their own judgment and due diligence when interpreting the results presented in this report."
            "The author of this report assumes no responsibility for decisions made or actions taken based on the information provided herein. Any use or interpretation of the data presented in this report is solely the responsibility of the user.",
        )

    def header(self):
        self.set_text_color(128)
        if self.page_no() > 1:
            self.set_y(10)
            self.set_font(style="I", size=8)
            self.cell(0, 0, self.video_id, align="L", link=self.video_link)
            self.cell(0, 0, f"{self.strf_creation_date}", align="R")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(style="I", size=8)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def insert_toc_placeholder(self):
        def render_toc(pdf, outline):
            return self.render_toc(outline)

        return super().insert_toc_placeholder(render_toc)

    def render_toc(self, outline):
        self.set_x(self.epw / 2)
        self.set_font(style="B", size=15)
        self.cell(text="Table of contents", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        self.set_font_size(size=12)

        for section in outline:
            n_points = int(
                (
                    self.epw
                    - self.get_string_width(
                        f"{section.name} page {section.page_number}"
                    )
                )
                / self.get_string_width(".")
            )
            self.cell(
                text=f"{section.name} {n_points*'.'} page {section.page_number}",
                new_x="LMARGIN",
                new_y="NEXT",
                link=self.add_link(page=section.page_number),
            )
            self.ln(3)

    def add_sentiment_section(self, sentiments, data_by_day):
        render_sentiment_section(self, sentiments, data_by_day)

    def add_word_frequencies_section(self, word_frequencies):
        render_word_frequencies_section(self, word_frequencies)

    def add_general_section(
        self,
        nb_comments,
        date_first_comment,
        date_last_comment,
        data_by_day,
    ):
        render_general_section(
            self,
            self.video_id,
            self.video_link,
            nb_comments,
            date_first_comment,
            date_last_comment,
            data_by_day,
        )

    def legend(self, text):
        self.nb_charts += 1
        self.set_text_color(128)
        self.set_font(style="I", size=9)
        self.cell(
            text=f"Fig.{self.nb_charts} - {text}",
            w=0,
            align=Align.C,
        )
        self.set_text_color(80)
        self.set_font(size=self.body_font_size)

    def add_fig(self, fig, legend=None):
        img = fig_to_img(fig)
        self.image(img, w=self.epw)
        if legend:
            self.legend(legend)
        self.ln(5)


def create_pdf(
    video_id,
    nb_comments,
    date_first_comment,
    date_last_comment,
    sentiments,
    data_by_day,
    word_frequencies,
):
    df_data_by_day = pd.DataFrame.from_dict(data_by_day, orient="index")
    df_data_by_day.index = pd.to_datetime(df_data_by_day.index)

    pdf = PDF(video_id=video_id)
    pdf.add_title(
        title="YouTube Comment Analysis",
        subtitle=video_id,
    )

    pdf.set_y(pdf.eph / 2)
    pdf.add_disclosure()

    pdf.add_page()
    pdf.insert_toc_placeholder()

    pdf.start_section("I. General")
    pdf.add_general_section(
        nb_comments,
        date_first_comment,
        date_last_comment,
        df_data_by_day["TOTAL"],
    )

    pdf.start_section("II. Sentiment Analysis")
    pdf.add_sentiment_section(sentiments, df_data_by_day)

    pdf.start_section("III. Word Frequencies")
    pdf.add_word_frequencies_section(word_frequencies)

    return pdf
