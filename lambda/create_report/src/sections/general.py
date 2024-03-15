from datetime import datetime

from charts import plot_cal_heatmat
from fpdf import FontFace


def add_general_table(
    pdf,
    video_id,
    video_link,
    nb_comments,
    date_first_comment,
    date_last_comment,
):
    def convert_date(str_date):
        input_date_format = "%Y-%m-%d %H:%M:%S+00:00"
        output_date_format = "%Y-%m-%d at %H:%M:%S"
        date = datetime.strptime(str_date, input_date_format)
        new_date_str = date.strftime(output_date_format)
        return new_date_str

    with pdf.table(first_row_as_headings=False) as table:
        row = table.row()
        row.cell("Video", style=FontFace(emphasis="B"))
        row.cell(str(video_id), link=video_link)

        row = table.row()
        row.cell("Total Comments", style=FontFace(emphasis="B"))
        row.cell(str(nb_comments))

        row = table.row()
        row.cell("Date First Comment", style=FontFace(emphasis="B"))
        row.cell(convert_date(date_first_comment))

        row = table.row()
        row.cell("Date Last Comment", style=FontFace(emphasis="B"))
        row.cell(convert_date(date_last_comment))

    pdf.ln(10)


def render_general_section(
    pdf,
    video_id,
    video_link,
    nb_comments,
    date_first_comment,
    date_last_comment,
    data_by_day,
):
    add_general_table(
        pdf,
        video_id,
        video_link,
        nb_comments,
        date_first_comment,
        date_last_comment,
    )

    fig = plot_cal_heatmat(data_by_day, color="grey")
    pdf.add_fig(fig, legend="Heatmap to represent number of comment by date")
