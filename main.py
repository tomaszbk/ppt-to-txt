import os
import subprocess
from time import sleep
import asyncio
from slide_summary import analyze_slide
from pdf2image import convert_from_path


def convert_ppt_to_images(ppt_file, output_dir="output"):
    """
    Convert PowerPoint slides to images via PDF intermediate.
    Returns a list of image file paths.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        print(f"Converting {ppt_file} to PDF...")
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                ppt_file,
            ],
            check=True,
        )
        print(f"PDF conversion completed for {ppt_file}")
        sleep(4)

        ppt_file_name = os.path.basename(ppt_file)
        pdf_name = ppt_file_name.replace(".pptx", "").replace(".ppt", "")
        pdf_file = os.path.join(output_dir, pdf_name + ".pdf")
        print(f"Looking for PDF at: {pdf_file}")
        if not os.path.exists(pdf_file):
            print(f"PDF file not found: {pdf_file}")
            return []

        print(f"Converting PDF {pdf_file} to images...")
        images = convert_from_path(pdf_file, dpi=150)
        print(f"PDF to image conversion complete. Number of images: {len(images)}")

        image_paths = []
        for i, image in enumerate(images, 1):
            image_path = os.path.join(output_dir, f"slide_{i:03d}.png")
            image.save(image_path, "PNG")
            print(f"Saved slide {i} as {image_path}")
            image_paths.append(image_path)

        if os.path.exists(pdf_file):
            os.remove(pdf_file)
            print(f"Deleted intermediate PDF: {pdf_file}")

        print(f"Successfully saved {len(image_paths)} slides to {output_dir}")
        return image_paths

    except Exception as e:
        print(f"Error converting presentation: {e}")
        return []


def summarize_slides(image_paths, output_dir):
    """
    Summarize each slide image using the LLM and save the summaries to a text file.
    """
    summaries = []
    for i, image_path in enumerate(image_paths, 1):
        try:
            print(f"Summarizing slide {i}...")
            summary = asyncio.run(analyze_slide(image_path))
            summaries.append(f"Slide {i}:\n{summary}\n")
        except Exception as e:
            print(f"Error summarizing slide {i}: {e}")
            summaries.append(f"Slide {i}:\n[Error al resumir]\n")

    summary_path = os.path.join(output_dir, "slides_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.writelines(summaries)
    print(f"Resumen guardado en {summary_path}")


def main():
    print("Hello from ppt-to-txt!")

    input_dir = "/app/input"
    output_dir = "/app/output"

    if not os.path.exists(input_dir):
        print("No input directory found. Please mount your files to /app/input")
        return

    ppt_files = [f for f in os.listdir(input_dir) if f.endswith((".ppt", ".pptx"))]

    if not ppt_files:
        print("No PowerPoint files found in input directory")
        return

    for ppt_file in ppt_files:
        full_path = os.path.join(input_dir, ppt_file)
        print(f"Processing: {ppt_file}")

        file_output_dir = os.path.join(output_dir, os.path.splitext(ppt_file)[0])
        image_paths = convert_ppt_to_images(full_path, file_output_dir)
        if image_paths:
            summarize_slides(image_paths, file_output_dir)


if __name__ == "__main__":
    main()
