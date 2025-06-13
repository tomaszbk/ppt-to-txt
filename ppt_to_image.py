import os
import subprocess
from pathlib import Path
from time import sleep

from pdf2image import convert_from_path
from PIL.Image import Image


def convert_ppt_to_pdf(ppt_path: Path):
    """
    Convert PowerPoint slides to images via PDF intermediate.
    Returns a list of image file paths.
    """
    output_dir = "./output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    ppt_filename: str = os.path.basename(ppt_path)

    print("Converting to PDF...")
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            ppt_path,
        ],
        check=True,
    )

    pdf_name = ppt_filename.replace(".pptx", "").replace(".ppt", "")
    pdf_file = os.path.join(output_dir, f"{pdf_name}.pdf")
    print(f"Looking for PDF at: {pdf_file}")

    retries = 0
    max_retries = 10
    while not os.path.exists(pdf_file) and retries < max_retries:
        print(
            f"Waiting for PDF file to be created: {pdf_file} (attempt {retries + 1}/{max_retries})"
        )
        sleep(0.5)
        retries += 1

    if not os.path.exists(pdf_file):
        raise FileNotFoundError(
            f"PDF file not created after {max_retries} attempts: {pdf_file}"
        )

    print(f"PDF conversion completed for {ppt_path}")

    with open(pdf_file, "rb") as f:
        file = f.read()
    return file


def convert_pdf_to_images(pdf_file) -> list[Image]:
    print(f"Converting PDF {pdf_file} to images...")
    images = convert_from_path(pdf_file, dpi=150)
    print(f"PDF to image conversion complete. Number of images: {len(images)}")
    return images
