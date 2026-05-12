from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import cm, mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable, SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer,
)
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DRAWING_POSITIONS_FILE = BASE_DIR / "config" / "drawing_positions.json"
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("pdfs")
EXCEL_FILE = INPUT_DIR / "data.xlsx"
IMAGE_FILE = INPUT_DIR / "Drawing1.png"
PDF_FONT_NAME = "Roboto"
PDF_FONT_FALLBACK = "Roboto"
PDF_FONT_FAMILY = [
    (
        "Roboto",
        [
            BASE_DIR / "static" / "fonts" / "Roboto-Regular.ttf",
            INPUT_DIR / "fonts" / "Roboto-Regular.ttf",
            Path("Roboto-Regular.ttf"),
        ],
    ),
    (
        "ArialNarrow",
        [
            INPUT_DIR / "ARIALN.TTF",
            INPUT_DIR / "arialn.ttf",
            INPUT_DIR / "Arial Narrow.ttf",
            INPUT_DIR / "fonts" / "ARIALN.TTF",
            INPUT_DIR / "fonts" / "arialn.ttf",
            INPUT_DIR / "fonts" / "Arial Narrow.ttf",
            Path("ARIALN.TTF"),
            Path("arialn.ttf"),
            Path("Arial Narrow.ttf"),
            Path(r"C:\Windows\Fonts\ARIALN.TTF"),
            Path(r"C:\Windows\Fonts\arialn.ttf"),
        ],
    ),
    (
        "Arial",
        [
            INPUT_DIR / "arial.ttf",
            INPUT_DIR / "Arial.ttf",
            INPUT_DIR / "fonts" / "arial.ttf",
            INPUT_DIR / "fonts" / "Arial.ttf",
            Path("arial.ttf"),
            Path("Arial.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
        ],
    ),
]
_FONT_REGISTERED = False
MAIN_TITLE_FONT_SIZE = 15
PRIMARY_HEADER_FONT_SIZE = 8
TABLE_HEADER_FONT_SIZE = 8
GENERAL_TEXT_FONT_SIZE = 7.5

LABEL_POSITIONS = {
    "A": {"x": 357, "y_offset": 30,  "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "B": {"x": 435, "y_offset": 60,  "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "C": {"x": 315, "y_offset": 67,  "rotation": 5,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "D": {"x": 345, "y_offset": 90,  "rotation": -30,  "font_size": GENERAL_TEXT_FONT_SIZE},
    "E": {"x": 435, "y_offset": 115, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "F": {"x": 250, "y_offset": 115, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "G": {"x": 357, "y_offset": 123, "rotation": -35,  "font_size": GENERAL_TEXT_FONT_SIZE},
    "H": {"x": 265, "y_offset": 137, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "I": {"x": 315, "y_offset": 150, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "J": {"x": 250, "y_offset": 175, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "K": {"x": 338, "y_offset": 182, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "L": {"x": 435, "y_offset": 185, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "M": {"x": 447, "y_offset": 215, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "N": {"x": 220, "y_offset": 217, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "O": {"x": 346, "y_offset": 225, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "P": {"x": 410, "y_offset": 228, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "Q": {"x": 457, "y_offset": 235, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "R": {"x": 467, "y_offset": 278, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "S": {"x": 354, "y_offset": 280, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "T": {"x": 387, "y_offset": 280, "rotation": 90,  "font_size": GENERAL_TEXT_FONT_SIZE},
    "U": {"x": 443, "y_offset": 295, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "V": {"x": 403, "y_offset": 297, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "W": {"x": 403, "y_offset": 307, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "X": {"x": 445, "y_offset": 325, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "Y": {"x": 370, "y_offset": 333, "rotation": 90,   "font_size": GENERAL_TEXT_FONT_SIZE},
    "Z": {"x": 335, "y_offset": 370, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
    "AA": {"x": 335, "y_offset": 397, "rotation": 0,    "font_size": GENERAL_TEXT_FONT_SIZE},
}

def load_drawing_label_positions() -> dict:
    if not DRAWING_POSITIONS_FILE.exists():
        return {"Drawing1": LABEL_POSITIONS}

    with DRAWING_POSITIONS_FILE.open("r", encoding="utf-8") as config_file:
        configured_positions = json.load(config_file)

    drawing_positions = {"Drawing1": LABEL_POSITIONS}
    for drawing_key, overrides in configured_positions.items():
        merged_positions = {
            label: dict(position)
            for label, position in LABEL_POSITIONS.items()
        }
        for label, position in overrides.items():
            merged_positions[label] = {
                "font_size": GENERAL_TEXT_FONT_SIZE,
                **position,
            }
        drawing_positions[drawing_key] = merged_positions
    return drawing_positions


DRAWING_LABEL_POSITIONS = load_drawing_label_positions()

# Gap between stacked sub-tables in the right panel (points)
INTER_TABLE_GAP = 6
LABEL_Y_ADJUST = -10
RIGHT_TABLE_VERTICAL_LABELS = ["MAST", "BRACKET ASSLY", "MISC. ASSLY"]


def register_pdf_fonts() -> None:
    global PDF_FONT_NAME, _FONT_REGISTERED
    if _FONT_REGISTERED:
        return

    for font_name, font_files in PDF_FONT_FAMILY:
        for font_file in font_files:
            if font_file.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(font_file)))
                PDF_FONT_NAME = font_name
                _FONT_REGISTERED = True
                return

    PDF_FONT_NAME = PDF_FONT_FALLBACK
    _FONT_REGISTERED = True


class ImageWithLabel(Flowable):
    def __init__(
        self,
        image_path: Path,
        width: float,
        height: float,
        label_texts: dict,
        label_positions: dict = None,
    ):
        super().__init__()
        self.image_path = str(image_path)
        self.width = width
        self.height = height
        self.label_texts = label_texts or {}
        self.label_positions = label_positions or LABEL_POSITIONS

    def draw(self):
        self.canv.drawImage(self.image_path, 0, 0, width=self.width, height=self.height)
        self.canv.setFillColor(colors.red)

        for key, cfg in self.label_positions.items():
            # text = key + " - "+self.label_texts.get(key, "")
            try:
                val = float(self.label_texts.get(key, 0))
                text = f"{key} - {val:.2f}"
            except ValueError:
                # Fallback if the value cannot be converted to a number
                text = f"{key} - {self.label_texts.get(key, '0.00')}"
            if not text:
                continue

            x = cfg["x"]
            y = self.height - cfg["y_offset"] + LABEL_Y_ADJUST
            rotation = cfg.get("rotation", 0)
            font_size = cfg.get("font_size", GENERAL_TEXT_FONT_SIZE)

            self.canv.setFont(PDF_FONT_NAME, font_size)
            self.canv.saveState()
            self.canv.translate(x, y)
            self.canv.rotate(rotation)
            self.canv.drawString(0, 0, text)
            self.canv.restoreState()

    def wrap(self, availWidth, availHeight):
        return self.width, self.height


def get_excel_field(row, key: str) -> str:
    lowered = key.strip().lower()
    for col in row.index:
        if str(col).strip().lower() == lowered:
            value = row[col]
            if pd.isna(value):
                return ""
            return str(value)
    return ""


def sanitize_filename(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name.strip())
    return safe or "output"


def get_label_texts(row) -> dict:
    return {key: get_excel_field(row, key) for key in get_label_positions(row)}


def get_drawing_key(row) -> str:
    drawing_name = get_excel_field(row, "Drawing").strip()
    if not drawing_name:
        return IMAGE_FILE.stem
    return Path(drawing_name).stem


def get_label_positions(row) -> dict:
    drawing_key = get_drawing_key(row)
    for configured_key, positions in DRAWING_LABEL_POSITIONS.items():
        if configured_key.strip().lower() == drawing_key.lower():
            return positions
    return LABEL_POSITIONS


def get_drawing_image(row) -> Path:
    drawing_name = get_drawing_key(row)
    if not drawing_name:
        return IMAGE_FILE

    drawing_path = Path(drawing_name)
    if drawing_path.suffix:
        image_path = INPUT_DIR / drawing_path.name
    else:
        image_path = INPUT_DIR / f"{drawing_name}.png"

    if not image_path.exists():
        raise FileNotFoundError(
            f"Drawing image not found for Drawing='{drawing_name}': {image_path}"
        )
    return image_path


def fill_label_value_table(table_data: list, row) -> list:
    filled_data = []
    for table_row in table_data:
        filled_row = list(table_row)
        if len(filled_row) >= 2 and not str(filled_row[1]).strip():
            value = get_excel_field(row, str(filled_row[0]))
            if value:
                filled_row[1] = value
        filled_data.append(filled_row)
    return filled_data


def fill_nested_tables_from_excel(nested_tables_data: list, row) -> list:
    return [fill_label_value_table(table_data, row) for table_data in nested_tables_data]


def fill_bottom_table_from_excel(bottom_table_data: list, row) -> list:
    filled_data = [list(table_row) for table_row in bottom_table_data]
    if len(filled_data) < 2:
        return filled_data

    for col_index, header in enumerate(filled_data[0]):
        value = get_excel_field(row, str(header))
        if value:
            filled_data[1][col_index] = value

    first_cell_value = get_excel_field(row, str(filled_data[1][0]))
    if first_cell_value:
        filled_data[1][0] = first_cell_value

    return filled_data


def make_paragraph(text: str, style) -> Paragraph:
    return Paragraph(str(text or ""), style)


def make_vertical_paragraph(text: str, style) -> Paragraph:
    vertical_text = "<br/>".join(str(text or ""))
    return Paragraph(vertical_text, style)


def add_wrap_points(text: str) -> str:
    parts = str(text or "").split("<br/>")
    return "<br/>".join(part.replace("/", "/ ") for part in parts)


def get_header_value(header_values: dict, key: str, default: str = "") -> str:
    if header_values is not None and key in header_values:
        return str(header_values.get(key) or "")
    return default


def get_header_row_value(header_values: dict, key: str, row_data, column_name: str) -> str:
    if header_values is not None and key in header_values:
        return str(header_values.get(key) or "")
    return get_excel_field(row_data, column_name)


def get_table_paragraph_styles(
    styles,
    header_font_size: float = TABLE_HEADER_FONT_SIZE,
    data_font_size: float = GENERAL_TEXT_FONT_SIZE,
):
    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=header_font_size,
        leading=header_font_size + 1,
        alignment=TA_CENTER,
        wordWrap="CJK",
    )
    data_style = ParagraphStyle(
        "TableData",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=data_font_size,
        leading=data_font_size + 1,
        alignment=TA_CENTER,
        wordWrap="CJK",
    )
    return header_style, data_style


def get_top_table_paragraph_styles(styles):
    top_first_row_style = ParagraphStyle(
        "TopTableFirstRow",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=MAIN_TITLE_FONT_SIZE,
        leading=MAIN_TITLE_FONT_SIZE + 2,
        alignment=TA_CENTER,
        wordWrap="CJK",
    )
    top_data_style = ParagraphStyle(
        "TopTableData",
        parent=styles["Normal"],
        fontName=PDF_FONT_NAME,
        fontSize=PRIMARY_HEADER_FONT_SIZE-1,
        leading=PRIMARY_HEADER_FONT_SIZE + 1,
        alignment=TA_CENTER,
        wordWrap="CJK",
    )
    return top_first_row_style, top_data_style


def build_sub_table(
    table_data: list,
    col_width: float,
    table_height: float,
    vertical_label: str,
) -> Table:
    """
    Build a single sub-table that auto-sizes its rows.
    col_width is the available width for the table (including padding already
    subtracted by the caller).
    """
    styles = getSampleStyleSheet()
    row_height = table_height / len(table_data)
    data_font_size = max(GENERAL_TEXT_FONT_SIZE, min(9, row_height * 0.55))
    header_style, data_style = get_table_paragraph_styles(
        styles,
        TABLE_HEADER_FONT_SIZE,
        data_font_size,
    )
    left_header_style = ParagraphStyle(
        "TableHeaderLeft",
        parent=header_style,
        alignment=TA_LEFT,
    )
    left_data_style = ParagraphStyle(
        "TableDataLeft",
        parent=data_style,
        alignment=TA_LEFT,
    )

    has_style_header = len(table_data) > 1 and any(
        str(cell).strip().lower() == "style" for cell in table_data[0]
    )
    wrapped_table_data = []
    for row_index, row in enumerate(table_data):
        is_header_row = has_style_header and row_index in (0, 1)
        style = header_style if is_header_row else data_style
        first_data_style = left_header_style if is_header_row else left_data_style
        first_cell = make_vertical_paragraph(vertical_label, header_style) if row_index == 0 else ""
        wrapped_table_data.append(
            [first_cell]
            + [
                make_paragraph(
                    add_wrap_points(cell) if has_style_header and col_index == 1 else cell,
                    first_data_style if col_index == 0 else style,
                )
                for col_index, cell in enumerate(row)
            ]
        )

    num_cols = len(table_data[0])
    vertical_col_width = min(11, col_width * 0.06)
    remaining_width = col_width - vertical_col_width
    if num_cols == 2:
        data_col_widths = [remaining_width * 0.58, remaining_width * 0.42]
    elif num_cols == 4:
        data_col_widths = [
            remaining_width * 0.36,
            remaining_width * 0.32,
            remaining_width * 0.16,
            remaining_width * 0.16,
        ]
    else:
        data_col_widths = [remaining_width / num_cols] * num_cols

    t = Table(
        wrapped_table_data,
        colWidths=[vertical_col_width] + data_col_widths,
        rowHeights=[row_height] * len(table_data),
        hAlign="LEFT",
    )
    table_style = [
        ("SPAN",        (0, 0), (0, -1)),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE",    (0, 0), (-1, -1), data_font_size),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",       (1, 0), (1, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING",(0, 0), (-1, -1), 1),
        ("TOPPADDING",  (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0,0), (-1, -1), 1),
    ]
    if has_style_header:
        table_style.extend([
            ("BACKGROUND", (1, 0), (-1, 1), colors.lightgrey),
            ("FONTNAME",   (1, 0), (-1, 1), PDF_FONT_NAME),
            ("SPAN", (1, 0), (1, 1)),
            ("SPAN", (2, 0), (2, 1)),
            ("SPAN", (3, 0), (4, 0)),
        ])

    t.setStyle(TableStyle(table_style))
    return t


def build_right_panel(
    nested_tables_data: list,   # list of 2-D arrays, one per sub-table
    panel_width: float,         # full width available for the right cell
    panel_height: float,        # full height available for the right cell
    padding: float = 8,
) -> Table:
    """
    Stack multiple independent sub-tables with spacers between them.
    The wrapper table uses the full available panel width so each sub-table
    fills the allotted space instead of shrinking.
    """
    inner_width = panel_width - 2 * padding
    inner_height = panel_height - 2 * padding
    total_gap_height = INTER_TABLE_GAP * max(0, len(nested_tables_data) - 1)
    available_table_height = max(0, inner_height - total_gap_height)
    total_table_rows = sum(len(tdata) for tdata in nested_tables_data)

    flowables = []
    row_heights = []
    for i, tdata in enumerate(nested_tables_data):
        if i > 0:
            flowables.append(Spacer(1, INTER_TABLE_GAP))
            row_heights.append(INTER_TABLE_GAP)
        vertical_label = (
            RIGHT_TABLE_VERTICAL_LABELS[i]
            if i < len(RIGHT_TABLE_VERTICAL_LABELS)
            else f"TABLE {i + 1}"
        )
        table_height = available_table_height * len(tdata) / total_table_rows
        flowables.append(build_sub_table(tdata, inner_width, table_height, vertical_label))
        row_heights.append(table_height)

    wrapper = Table(
        [[item] for item in flowables],
        colWidths=[inner_width],
        rowHeights=row_heights,
        hAlign="LEFT",
    )
    wrapper.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
    ]))
    return wrapper


def create_layout_pdf(
    output_path: Path,
    image_path: Path,
    label_texts: dict,
    row_data,
    label_positions: dict = None,
    header_title: str = None,
    header_values: dict = None,
    nested_tables_data: list = None,   # ← now a LIST of table-data arrays
):
    """
    Build the one-page layout PDF.

    nested_tables_data: list of independent 2-D table arrays to stack in the
    right panel.  Each sub-table may have a different number of columns.
    Defaults to three demo tables matching the Railway CAD reference layout.
    """
    register_pdf_fonts()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    header_values = dict(header_values or {})
    if header_title and "header_title" not in header_values:
        header_values["header_title"] = header_title
    header_title = get_header_value(
        header_values,
        "header_title",
        "GROUP No: DOUBLING CUM ELECTRIFICATION BETWEEN GUNTUR - TENALI SECTION K.M - 0.00 TO K.M - 25.00",
    )

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # ------------------------------------------------------------------ #
    # Default: three separate tables as seen in the reference PDF          #
    # ------------------------------------------------------------------ #
    if nested_tables_data is None:
        nested_tables_data = [
            # Table 1 – two columns with 16 rows
            [
                ["LOCATION No.",     " "],
                ["MAST TYPE",     " "],
                ["MAST LENGTH",      " "],
                ["REV.DEF.IN mm",        " "],
                ["NATURE OF SOIL",    " "],
                ["SOIL PRESSURE",        " "],
                ["FOUNDATION REF.",       " "],
                ["ANCHOR BLOCK",       " "],
                ["SUPER MAST",      " "],
                ["RC/FEEDER HT. (m)",       " "],
                ["CATENARY HT. (m)",      " "],
                ["CONTACT HT. (m)",  " "],
                ["SPAN (m)",        " "],
                ["VERSINES / RADIUS",         " "],
                ["SUPER ELEVATION",     " "],
            ],
            # Table 2 – four columns with 10 rows
            [
                ["",      "DRG NO", "Style",   ""],
                ["",      "",       "DN.MAIN", "UP.MAIN"],
                ["CANTILEVER ASSY.", "9200", "--", "02"],
                ["STAY ARM", "2400", "--", "12(1.98)"],
                ["STANDARD BRACKET", "2040", "--", "--"],
                ["LARGE BRACKET", "2080", "--", "10(3.10)"],
                ["REGISTERD ARM", "2420", "--", "05(1.75)"],
                ["RAISED REG. ARM", "2430", "--", "--"],
                ["STEADY ARM", "2390", "--", "02"],
                ["JUMPER", "1010", "--", "01"],
                ["INSULATOR", "---", "--", "A-54"],
                ["DROPPER", "9207", "", ""],
            ],
            # Table 3 – four columns with 10 rows
            [
                ["",      "DRG NO", "Style",   ""],
                ["",      "",       "DN.MAIN", "UP.MAIN"],
                ["GUY ROD", "ETI/OHE/P/5000", "--", "--"],
                ["TERMINATION", "1005", "--", "--"],
                ["ANCHOR", "1006", "--", "--"],
                ["FEEDER/RC-SUSPN.", "1008", "--", "--"],
                ["GUIDE TUBE MTG .", "ETI /OHE/G/1505", "--", "--"],
                ["SPS FOR RC/FEEDER SUSP.", "ETI / C / P /", "--", "--"],
                ["SPS FOR BKT .MTG.", "1001", "--", "14"],
                ["NUMBER PLATE .MTG.", "ETI/OHE/G/01701", "--", "04"],
                ["STRUCTURE BOND", "ETI/OHE/P/7000", "--", "01"],
            ],
        ]

    nested_tables_data = fill_nested_tables_from_excel(nested_tables_data, row_data)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=10,
        bottomMargin=10,
    )

    styles = getSampleStyleSheet()
    header_style, data_style = get_table_paragraph_styles(styles)
    top_first_row_style, top_data_style = get_top_table_paragraph_styles(styles)

    page_width, page_height = landscape(A4)
    usable_width  = page_width  - doc.leftMargin - doc.rightMargin
    usable_height = page_height - doc.topMargin  - doc.bottomMargin

    top_height    = usable_height * 0.12
    middle_height = usable_height * 0.80
    bottom_height = usable_height * 0.05
    col_widths    = [usable_width * 0.67, usable_width * 0.33]

    # Create top table. Row 1 uses full width; row 2 contains a 70% left
    # table and a 30% right table.
    header_second_row_width = usable_width * 0.70
    header_right_width = usable_width - header_second_row_width
    header_col_widths = [
    header_second_row_width * 0.25,   # col 0 — VOLTRIO / RVNL
    header_second_row_width * 0.20,   # col 1 — SUBMITTED
    header_second_row_width * 0.40,   # col 2 — APPROVED S.E.D (increased)
    header_second_row_width * 0.15,   # col 3 — AS ERECTED (reduced)
]
    header_row_heights = [top_height * 0.25, top_height * 0.75]
    header_second_row_height = header_row_heights[1]

    first_col_split = Table(
        [
            [make_paragraph(get_header_value(header_values, "company_line_1", "VOLTRIO SOLUTIONS"), top_data_style)],
            [make_paragraph(get_header_value(header_values, "company_line_2", "Rail Vikas Nigam Limited"), top_data_style)],
        ],
        colWidths=[header_col_widths[0]],
        rowHeights=[header_second_row_height / 2] * 2,
    )
    first_col_split.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING",(0, 0), (-1, -1), 1),
        ("TOPPADDING",  (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0,0), (-1, -1), 1),
    ]))
     
    second_col_split = Table(
    [
        [make_paragraph(get_header_value(header_values, "submitted_title", "SUBMITTED"), top_data_style)],
        [make_paragraph("", top_data_style)],
        [make_paragraph("for "+ get_header_value(header_values, "company_line_1", "VOLTRIO SOLUTIONS"), top_data_style)],
    ],
    colWidths=[header_col_widths[1]],
    rowHeights=[
        header_second_row_height * 0.15,  # SUBMITTED — small
        header_second_row_height * 0.65,  # empty — tall
        header_second_row_height * 0.20,  # For VOLTRIO SOLUTIONS — small
    ],
)
    second_col_split.setStyle(TableStyle([
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    third_col_split = Table(
    [
        [make_paragraph(get_header_value(header_values, "approved_title", "APPROVED S.E.D"), top_data_style), "", ""],  # spans all 3
        [make_paragraph("", top_data_style), make_paragraph("", top_data_style), make_paragraph("", top_data_style)],
        [
            make_paragraph(get_header_value(header_values, "approved_signatory_1", "RE(Ele) / PMC / GNT"), top_data_style),
            make_paragraph(get_header_value(header_values, "approved_signatory_2", "AM / E / RVNL / BZA"), top_data_style),
            make_paragraph(get_header_value(header_values, "approved_signatory_3", "JGM / E / RVNL / BZA"), top_data_style),
        ],
    ],
    colWidths=[header_col_widths[2] / 3] * 3,
    rowHeights=[
        header_second_row_height * 0.15,  # APPROVED S.E.D — small
        header_second_row_height * 0.65,  # empty — tall
        header_second_row_height * 0.20,  # labels — small
    ],
)
    third_col_split.setStyle(TableStyle([
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
        # Merge first row across all 3 columns
        ("SPAN",         (0, 0), (2, 0)),
    ]))
    fourth_col_split = Table(
    [
        [make_paragraph(get_header_value(header_values, "as_erected_title", "AS ERECTED"), top_data_style)],
        [make_paragraph("", top_data_style)],
        [make_paragraph(get_header_value(header_values, "as_erected_footer", "For ED/ Ele /RVNL / SC"), top_data_style)],
    ],
    colWidths=[header_col_widths[3]],
    rowHeights=[
        header_second_row_height * 0.15,  # SUBMITTED — small
        header_second_row_height * 0.65,  # empty — tall
        header_second_row_height * 0.20,  # For VOLTRIO SOLUTIONS — small
    ],
)
    fourth_col_split.setStyle(TableStyle([
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    header_second_row_table = Table(
        [
            [
                first_col_split,
                second_col_split,
                third_col_split,
                fourth_col_split,
            ],
        ],
        colWidths=header_col_widths,
        rowHeights=[header_second_row_height],
    )
    header_second_row_table.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE",    (0, 0), (-1, -1), PRIMARY_HEADER_FONT_SIZE),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",(0, 0), (-1, -1), 4),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0,0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0,  0), 0),
        ("RIGHTPADDING",(0, 0), (0,  0), 0),
        ("TOPPADDING",  (0, 0), (0,  0), 0),
        ("BOTTOMPADDING",(0,0), (0,  0), 0),
        ("LEFTPADDING", (2, 0), (2,  0), 0),
        ("RIGHTPADDING",(2, 0), (2,  0), 0),
        ("TOPPADDING",  (2, 0), (2,  0), 0),
        ("BOTTOMPADDING",(2,0), (2,  0), 0),
    ]))

    header_right_table = Table(
        [
            [make_paragraph("SECTION", top_data_style), make_paragraph(get_header_row_value(header_values, "section", row_data, "SECTION"), top_data_style)],
            [make_paragraph("LAYOUT No", top_data_style), make_paragraph(get_header_row_value(header_values, "layout_no", row_data, "LAYOUT No"), top_data_style)],
            [make_paragraph("CHAINAGE", top_data_style), make_paragraph(get_header_row_value(header_values, "chainage", row_data, "CHAINAGE"), top_data_style)],
            [make_paragraph("WIND PRESSURE", top_data_style), make_paragraph(get_header_row_value(header_values, "wind_pressure", row_data, "WIND PRESSURE"), top_data_style)],
        ],
        colWidths=[header_right_width / 2] * 2,
        rowHeights=[header_second_row_height / 4] * 4,
    )
    header_right_table.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE",    (0, 0), (-1, -1), PRIMARY_HEADER_FONT_SIZE),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING",(0, 0), (-1, -1), 1),
        ("TOPPADDING",  (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0,0), (-1, -1), 1),
    ]))

    header_second_row_layout = Table(
        [[header_second_row_table, header_right_table]],
        colWidths=[header_second_row_width, header_right_width],
        rowHeights=[header_second_row_height],
    )
    header_second_row_layout.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",(0, 0), (-1, -1), 0),
        ("TOPPADDING",  (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0,0), (-1, -1), 0),
    ]))

    header_table = Table(
        [
            [make_paragraph(header_title, top_first_row_style)],
            [header_second_row_layout],
        ],
        colWidths=[usable_width],
        rowHeights=header_row_heights,
    )
    header_table.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE",    (0, 0), (-1, -1), PRIMARY_HEADER_FONT_SIZE),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",       (0, 0), (0,  0), "LEFT"),
        ("ALIGN",       (0, 1), (0,  1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",(0, 0), (-1, -1), 4),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0,0), (-1, -1), 4),
        ("LEFTPADDING", (0, 1), (0,  1), 0),
        ("RIGHTPADDING",(0, 1), (0,  1), 0),
        ("TOPPADDING",  (0, 1), (0,  1), 0),
        ("BOTTOMPADDING",(0,1), (0,  1), 0),
    ]))

    # ------------------------------------------------------------------ #
    # Bottom table with 7 columns and 2 rows                               #
    # ------------------------------------------------------------------ #
    bottom_table_data = [
        ["ITEM", "STAY INSULATOR ", "BKT . INSULATOR", "9 - TONNE INSULATOR ", "S.S WIRE ROPE", "CONTACT WIRE", "CATENARY WIRE"],
        ["MAKE / YEAR", " ", " ", " ", " ", " ", " "],
    ]
    bottom_table_data = fill_bottom_table_from_excel(bottom_table_data, row_data)

    bottom_table = Table(
        [
            [make_paragraph(cell, header_style) for cell in bottom_table_data[0]],
            [make_paragraph(cell, data_style) for cell in bottom_table_data[1]],
        ],
        colWidths=[usable_width / 7] * 7,
        rowHeights=[bottom_height / 2] * 2,
    )
    bottom_table.setStyle(TableStyle([
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND",  (0, 0), (-1,  0), colors.lightgrey),
        ("FONTNAME",    (0, 0), (-1,  0), PDF_FONT_NAME),
        ("FONTSIZE",    (0, 0), (-1, -1), GENERAL_TEXT_FONT_SIZE),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",(0, 0), (-1, -1), 3),
        ("TOPPADDING",  (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0,0), (-1, -1), 3),
    ]))

    # ------------------------------------------------------------------ #
    # Left cell: engineering drawing with overlaid labels                  #
    # ------------------------------------------------------------------ #
    image_flowable = ImageWithLabel(
        image_path,
        width=col_widths[0] - 12,   # subtract left+right padding of outer cell
        height=middle_height - 12,
        label_texts=label_texts,
        label_positions=label_positions,
    )

    # ------------------------------------------------------------------ #
    # Right cell: multiple sub-tables stacked with gaps                   #
    # ------------------------------------------------------------------ #
    right_panel = build_right_panel(
        nested_tables_data,
        panel_width=col_widths[1],
        panel_height=middle_height,
        padding=6,
    )

    # ------------------------------------------------------------------ #
    # Outer layout table                                                   #
    # ------------------------------------------------------------------ #
    outer_table = Table(
        [
            [header_table, ""],
            [image_flowable, right_panel],
            [bottom_table, ""],
        ],
        colWidths=col_widths,
        rowHeights=[top_height, middle_height, bottom_height],
    )

    outer_table.setStyle(TableStyle([
        ("SPAN",           (0, 0), (1, 0)),
        ("SPAN",           (0, 2), (1, 2)),
        ("BOX",            (0, 0), (-1, -1), 1, colors.black),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.darkgrey),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("VALIGN",         (1, 1), (1,  1),  "TOP"),   # right panel: top-align
        ("ALIGN",          (0, 0), (-1,  0), "CENTER"),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 2), (0,  2), 0),
        ("RIGHTPADDING",   (0, 2), (0,  2), 0),
        ("TOPPADDING",     (0, 2), (0,  2), 0),
        ("BOTTOMPADDING",  (0, 2), (0,  2), 0),
    ]))

    doc.build([outer_table])


def generate_all_pdfs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"Excel file not found: {EXCEL_FILE}")
    if not IMAGE_FILE.exists():
        raise FileNotFoundError(f"Image file not found: {IMAGE_FILE}")

    df = pd.read_excel(EXCEL_FILE)

    for index, row in df.iterrows():
        label_texts = get_label_texts(row)
        base_name   = get_excel_field(row, "FileName")
        file_type   = get_excel_field(row, "Type")

        if base_name:
            safe_name = sanitize_filename(base_name)
            if file_type:
                safe_type  = sanitize_filename(file_type)
                output_file = OUTPUT_DIR / f"{safe_name}_{safe_type}.pdf"
            else:
                output_file = OUTPUT_DIR / f"{safe_name}.pdf"
        else:
            output_file = OUTPUT_DIR / f"output_{index + 1}.pdf"

        drawing_image = get_drawing_image(row)
        label_positions = get_label_positions(row)

        create_layout_pdf(output_file, drawing_image, label_texts, row, label_positions)
        print(f"Created {output_file}")


if __name__ == "__main__":
    generate_all_pdfs()
