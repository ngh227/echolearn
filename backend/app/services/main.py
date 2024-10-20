from test_embedding import PDFProcessingWorkflow
import os

def main():
    workflow = PDFProcessingWorkflow()

    while True:
        print("\nPDF Processing Menu:")
        print("1. Upload and process a new PDF")
        print("2. Exit")
        
        choice = input("Enter your choice (1-2): ")

        if choice == '1':
            file_path = input("Enter the full path to your PDF file: ").strip()
            
            if not os.path.exists(file_path):
                print("File not found. Please check the path and try again.")
                continue
            
            if not file_path.lower().endswith('.pdf'):
                print("Please provide a PDF file.")
                continue
            
            try:
                doc_id, questions, s3_uri = workflow.run_workflow(file_path)
                
                if doc_id:
                    print(f"\nFile uploaded and processed successfully!")
                    print(f"Document ID: {doc_id}")
                    print(f"S3 URI: {s3_uri}")
                    print("\nGenerated questions:")
                    for i, question in enumerate(questions, 1):
                        print(f"{i}. {question}")
                else:
                    print("Failed to process the document.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
        
        elif choice == '2':
            print("Exiting the program. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()