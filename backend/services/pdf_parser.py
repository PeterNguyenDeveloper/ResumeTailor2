import PyPDF2
import io
import datetime

# Helper function to get timestamp for print statements
def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text from the PDF
    """
    text = ""

    try:
        print(f"[{get_timestamp()}] Opening PDF file: {pdf_path}", flush=True)
        with open(pdf_path, 'rb') as file:
            print(f"[{get_timestamp()}] Creating PDF reader", flush=True)
            reader = PyPDF2.PdfReader(file)

            print(f"[{get_timestamp()}] PDF has {len(reader.pages)} pages", flush=True)

            # Extract text from each page
            for page_num in range(len(reader.pages)):
                print(f"[{get_timestamp()}] Extracting text from page {page_num+1}", flush=True)
                page = reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text
                print(f"[{get_timestamp()}] Extracted {len(page_text)} characters from page {page_num+1}", flush=True)

        print(f"[{get_timestamp()}] Total extracted text: {len(text)} characters", flush=True)

    except Exception as e:
        print(f"[{get_timestamp()}] ERROR extracting text from PDF: {str(e)}", flush=True)
        raise Exception(f"Error extracting text from PDF: {str(e)}")

    return text

