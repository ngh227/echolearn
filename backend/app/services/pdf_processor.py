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

    @staticmethod
    def test_pdf_extraction(pdf_file_path):
        """
        Test the extraction of text from a PDF file and print the output.
        
        :param pdf_file_path: Path to the PDF file
        """
        try:
            # Open the PDF file
            with open(pdf_file_path, 'rb') as pdf_file:
                print(f"Extracting text from {pdf_file_path}...")
                
                # Extract text from the entire PDF
                extracted_text = PDFProcessor.extract_text(pdf_file)
                if extracted_text:
                    print("Extracted Text:")
                    print(extracted_text)
                else:
                    print("No text extracted or an error occurred.")
                    
                # Get the number of pages
                page_count = PDFProcessor.get_page_count(pdf_file)
                if page_count is not None:
                    print(f"Total Pages: {page_count}")
                else:
                    print("Could not get page count.")
        except Exception as e:
            print(f"Error opening PDF file: {str(e)}")

# Example usage
if __name__ == "__main__":
    PDFProcessor.test_pdf_extraction('/Users/maeve/Documents/animal-data/USA-SMR-1-2023-AQUA.pdf')
# PDFProcessor.test_pdf_extraction('path/to/your/USA-SMR-1-2023-AQUA.pdf')
