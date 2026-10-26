
# from io import BytesIO

# from pypdf import PdfReader
# from pypdf.errors import PdfReadError


# MAX_PDF_PAGES = 100


# def extract_pdf_text(file_bytes: bytes) -> dict:
#     """Validate a PDF and extract text from its pages."""

#     if not file_bytes.startswith(b"%PDF-"):
#         raise ValueError("The uploaded file is not a valid PDF.")

#     try:
#         reader = PdfReader(BytesIO(file_bytes), strict=False)

#         if reader.is_encrypted:
#             raise ValueError(
#                 "Password-protected PDFs are not supported."
#             )

#         page_count = len(reader.pages)

#         if page_count == 0:
#             raise ValueError("The PDF contains no pages.")

#         if page_count > MAX_PDF_PAGES:
#             raise ValueError(
#                 f"The PDF cannot exceed {MAX_PDF_PAGES} pages."
#             )

#         extracted_pages = []

#         for page in reader.pages:
#             extracted_pages.append(page.extract_text() or "")

#         text = "\n\n".join(extracted_pages).strip()

#         if not text:
#             raise ValueError(
#                 "No readable text was found. "
#                 "The PDF may contain scanned images."
#             )

#         return {
#             "page_count": page_count,
#             "text": text,
#         }

#     except ValueError:
#         raise
#     except (PdfReadError, OSError) as exc:
#         raise ValueError(
#             "The PDF could not be read. Please upload a valid PDF."
#         ) from exc


from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PDF_PAGES = 100


def extract_pdf_text(file_bytes: bytes) -> dict:
    """Validate a PDF and extract text while preserving page numbers."""

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    try:
        reader = PdfReader(BytesIO(file_bytes), strict=False)

        if reader.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        page_count = len(reader.pages)

        if page_count == 0:
            raise ValueError("The PDF contains no pages.")

        if page_count > MAX_PDF_PAGES:
            raise ValueError(
                f"The PDF cannot exceed {MAX_PDF_PAGES} pages."
            )

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()

            pages.append(
                {
                    "page_number": page_number,
                    "text": page_text,
                }
            )

        combined_text = "\n\n".join(
            page["text"]
            for page in pages
            if page["text"]
        ).strip()

        if not combined_text:
            raise ValueError(
                "No readable text was found. "
                "The PDF may contain scanned images."
            )

        return {
            "page_count": page_count,
            "text": combined_text,
            "pages": pages,
        }

    except ValueError:
        raise
    except (PdfReadError, OSError) as exc:
        raise ValueError(
            "The PDF could not be read. Please upload a valid PDF."
        ) from exc
