import os


def test_convert_ppt_to_pdf():
    from ppt_to_image import convert_ppt_to_pdf

    # Test converting a sample PPT file to PDF
    ppt_file = "tests/sample.pptx"  # Ensure this file exists in your test directory
    assert os.path.exists(ppt_file), f"Test file {ppt_file} does not exist"
    pdf_content = convert_ppt_to_pdf(ppt_file)

    assert pdf_content is not None, "PDF content should not be None"
    assert isinstance(pdf_content, bytes), "PDF content should be of type bytes"
    assert len(pdf_content) > 0, "PDF content should not be empty"


def test_convert_pdf_to_images():
    # Test converting a sample PDF file to images
    pdf_file = "tests/sample.pdf"  # Ensure this file exists in your test directory
    assert os.path.exists(pdf_file), f"Test file {pdf_file} does not exist"

    from ppt_to_image import convert_pdf_to_images

    images = convert_pdf_to_images(pdf_file)

    assert isinstance(images, list), "Images should be returned as a list"
    assert len(images) > 0, "There should be at least one image generated from the PDF"
