import os
import subprocess
from time import sleep

from pdf2image import convert_from_path


def convert_ppt_to_images(ppt_file, output_dir="output"):
    """
    Convert PowerPoint slides to images via PDF intermediate
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Step 1: Convert PPT to PDF using LibreOffice
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
        sleep(4)  # Wait for conversion to complete
        # Step 2: Convert PDF pages to images
        print("Converting PDF to images...")
        ppt_file = ppt_file.replace("/app/input/", "")
        pdf_name = ppt_file.replace(".pptx", "").replace(".ppt", "")
        pdf_file = os.path.join(output_dir, pdf_name + ".pdf")
        images = convert_from_path(pdf_file, dpi=300)

        # Step 3: Save each page as an image
        for i, image in enumerate(images, 1):
            image_path = os.path.join(output_dir, f"slide_{i:03d}.png")
            image.save(image_path, "PNG")
            print(f"Saved slide {i} as {image_path}")

        # Clean up PDF file
        if os.path.exists(pdf_file):
            os.remove(pdf_file)

        print(f"Successfully saved {len(images)} slides to {output_dir}")

    except Exception as e:
        print(f"Error converting presentation: {e}")


def main():
    print("Hello from ppt-to-txt!")

    # Look for PPT files in the input directory
    input_dir = "/app/input"
    output_dir = "/app/output"

    if not os.path.exists(input_dir):
        print("No input directory found. Please mount your files to /app/input")
        return

    # Find PPT files
    ppt_files = [f for f in os.listdir(input_dir) if f.endswith((".ppt", ".pptx"))]

    if not ppt_files:
        print("No PowerPoint files found in input directory")
        return

    for ppt_file in ppt_files:
        full_path = os.path.join(input_dir, ppt_file)
        print(f"Processing: {ppt_file}")

        # Create output subdirectory for this presentation
        file_output_dir = os.path.join(output_dir, os.path.splitext(ppt_file)[0])
        convert_ppt_to_images(full_path, file_output_dir)


if __name__ == "__main__":
    main()
