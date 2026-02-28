#!/usr/bin/env python3
"""
Comprehensive PDF extractor: text + OCR for image-based pages.
Extracts every word from every page of every PDF in the repository.
"""
import fitz  # PyMuPDF
import os
import sys
import io
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

OUTPUT_DIR = "/home/user/j/extracted_texts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# All PDF paths
PDF_PATHS = []

# Root directory PDFs
root = "/home/user/j"
for f in os.listdir(root):
    if f.endswith(".pdf"):
        PDF_PATHS.append(os.path.join(root, f))

# OCR zip extracted PDFs
ocr_dir = "/home/user/j/ocr_pdfs"
if os.path.isdir(ocr_dir):
    for f in os.listdir(ocr_dir):
        if f.endswith(".pdf"):
            PDF_PATHS.append(os.path.join(ocr_dir, f))

PDF_PATHS.sort()

def extract_text_from_page(page):
    """Extract text from a page. If text is minimal, OCR the page image."""
    text = page.get_text("text").strip()

    # If we got substantial text, return it
    if len(text) > 50:
        return text

    # Otherwise, try OCR
    if HAS_OCR:
        try:
            # Render page to image at high DPI for better OCR
            mat = fitz.Matrix(3, 3)  # 3x zoom = ~216 DPI
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            ocr_text = pytesseract.image_to_string(img, lang='eng')
            if ocr_text.strip():
                return f"[OCR] {ocr_text.strip()}"
        except Exception as e:
            return f"[OCR FAILED: {e}] {text}"

    return text if text else "[EMPTY PAGE]"


def extract_pdf(pdf_path):
    """Extract all text from all pages of a PDF."""
    basename = os.path.basename(pdf_path)
    print(f"\n{'='*80}")
    print(f"PROCESSING: {basename}")
    print(f"{'='*80}")

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"  ERROR opening: {e}")
        return None

    total_pages = len(doc)
    print(f"  Pages: {total_pages}")

    all_text = []
    all_text.append(f"{'='*80}")
    all_text.append(f"DOCUMENT: {basename}")
    all_text.append(f"Total Pages: {total_pages}")
    all_text.append(f"{'='*80}\n")

    for page_num in range(total_pages):
        page = doc[page_num]
        text = extract_text_from_page(page)

        all_text.append(f"\n--- PAGE {page_num + 1} of {total_pages} ---\n")
        all_text.append(text)

        # Progress indicator
        if (page_num + 1) % 10 == 0 or page_num == 0:
            print(f"  Page {page_num + 1}/{total_pages} extracted ({len(text)} chars)")

    doc.close()

    full_text = "\n".join(all_text)

    # Save to file
    out_name = basename.replace(".pdf", ".txt")
    out_path = os.path.join(OUTPUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"  SAVED: {out_path} ({len(full_text)} chars)")
    return full_text


def main():
    print(f"Found {len(PDF_PATHS)} PDF files to process")
    print(f"OCR available: {HAS_OCR}")
    print()

    results = {}
    for pdf_path in PDF_PATHS:
        text = extract_pdf(pdf_path)
        if text:
            results[os.path.basename(pdf_path)] = text

    # Write combined output
    combined_path = os.path.join(OUTPUT_DIR, "ALL_PDFS_COMBINED.txt")
    with open(combined_path, "w", encoding="utf-8") as f:
        for name, text in results.items():
            f.write(text)
            f.write("\n\n")

    print(f"\n\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total PDFs processed: {len(results)}")
    print(f"Combined output: {combined_path}")
    total_chars = sum(len(t) for t in results.values())
    print(f"Total characters extracted: {total_chars:,}")


if __name__ == "__main__":
    main()
