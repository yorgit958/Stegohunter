import sys
import pypdf

try:
    with open('STEGO_HUNTER_ARCHITECTURE.pdf', 'rb') as f:
        reader = pypdf.PdfReader(f)
        with open('pdf_content.txt', 'w', encoding='utf-8') as out:
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    out.write(text + '\n')
    print("Successfully wrote PDF content to pdf_content.txt")
except Exception as e:
    print(f"Failed to read PDF: {e}")
