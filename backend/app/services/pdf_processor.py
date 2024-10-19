# app/services/pdf_processor.py
import PyPDF2
import io

class PDFProcessor:
    @staticmethod
    def extract_text(pdf_file):
        """
        Extract text from a PDF file.
        """
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None
        return text.strip()

    @staticmethod
    def get_page_count(pdf_file):
        """
        Get the number of pages in a PDF file.
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return len(pdf_reader.pages)
        except Exception as e:
            print(f"Error getting page count: {str(e)}")
            return None

    @staticmethod
    def extract_text_from_page(pdf_file, page_number):
        """
        Extract text from a specific page of a PDF file.
        
        :param pdf_file: A file-like object containing the PDF data
        :param page_number: The page number to extract text from (0-based index)
        :return: A string containing the text extracted from the specified page
        """
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            if 0 <= page_number < len(pdf_reader.pages):
                return pdf_reader.pages[page_number].extract_text().strip()
            else:
                print(f"Page number {page_number} is out of range.")
                return None
        except Exception as e:
            print(f"Error extracting text from page {page_number}: {str(e)}")
            return None