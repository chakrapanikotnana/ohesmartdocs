import os
import tempfile
import zipfile
from pathlib import Path

from app.new import get_label_texts, get_label_positions, create_layout_pdf
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

font_path = os.path.join(BASE_DIR, "static", "fonts", "Roboto-Regular.ttf")

pdfmetrics.registerFont(TTFont("Roboto", font_path))

def generate_pdfs(df):
    temp_dir = Path(tempfile.mkdtemp())
    output_files = []

    base_dir = Path(os.getcwd())
    image_dir = base_dir / "images"

    for i, row in df.iterrows():
        try:
            file_name = str(row.get("FileName")).strip()
            drawing_name = str(row.get("Drawing")).strip()

            possible_extensions = [".png", ".jpg", ".jpeg"]

            image_path = None

            for ext in possible_extensions:
                temp_path = image_dir / (drawing_name + ext)
                if temp_path.exists():
                    image_path = temp_path
                    break

            # If not found even after trying extensions
            if image_path is None:
                raise Exception(f"Image not found: {drawing_name} (tried .png/.jpg/.jpeg)")

            output_pdf = temp_dir / f"{file_name}.pdf"

            
            create_layout_pdf(
            output_pdf,
            image_path,
            get_label_texts(row),
            row,
            get_label_positions(row)
)

            output_files.append(output_pdf)

        except Exception as e:
            raise Exception(f"Row {i+1}: {str(e)}")

    # Create ZIP
    zip_path = temp_dir / "output.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for pdf in output_files:
            zipf.write(pdf, pdf.name)

    return zip_path