import unittest
import tempfile
import os
from unittest.mock import patch, mock_open
from backend.file_processing import extract_text


class TestFileProcessing(unittest.TestCase):
    """Test cases for file_processing module"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        
    def test_extract_text_txt(self):
        """Test text extraction from .txt files."""
        test_content = "This is a test text file.\nWith multiple lines."
        txt_file = os.path.join(self.temp_dir, "test.txt")
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        result = extract_text(txt_file)
        self.assertEqual(result.strip(), test_content.strip())
    
    def test_extract_text_unsupported_file(self):
        """Test extraction from unsupported file type."""
        unsupported_file = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_file, 'w') as f:
            f.write("dummy content")
        
        result = extract_text(unsupported_file)
        self.assertIsNone(result)
    
    @patch('backend.file_processing.Document')
    def test_extract_text_docx(self, mock_doc):
        """Test text extraction from .docx files."""
        mock_doc_instance = mock_doc.return_value
        mock_para1 = type('Paragraph', (), {'text': 'First paragraph'})()
        mock_para2 = type('Paragraph', (), {'text': 'Second paragraph'})()
        mock_doc_instance.paragraphs = [mock_para1, mock_para2]
        
        result = extract_text("test.docx")
        expected = "First paragraph\nSecond paragraph"
        self.assertEqual(result, expected)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('backend.file_processing.PdfReader')
    def test_extract_text_pdf(self, mock_pdf_reader, mock_file):
        """Test text extraction from .pdf files."""
        mock_page1 = type('Page', (), {})()
        mock_page1.extract_text = lambda: 'Text from page 1'
        mock_page2 = type('Page', (), {})()
        mock_page2.extract_text = lambda: 'Text from page 2'
        mock_pdf_reader_instance = mock_pdf_reader.return_value
        mock_pdf_reader_instance.pages = [mock_page1, mock_page2]
        
        result = extract_text("test.pdf")
        expected = "Text from page 1\nText from page 2"
        self.assertEqual(result, expected)
    
    @patch('backend.file_processing.Presentation')
    def test_extract_text_pptx(self, mock_presentation):
        """Test text extraction from .pptx files."""
        mock_shape1 = type('Shape', (), {'text': 'Slide 1 text'})()
        mock_shape2 = type('Shape', (), {'text': 'Slide 2 text'})()
        mock_slide = type('Slide', (), {'shapes': [mock_shape1, mock_shape2]})()
        mock_presentation_instance = mock_presentation.return_value
        mock_presentation_instance.slides = [mock_slide]
        
        result = extract_text("test.pptx")
        expected = "Slide 1 text\nSlide 2 text"
        self.assertEqual(result, expected)
    
    @patch('backend.file_processing.load_workbook')
    def test_extract_text_xlsx(self, mock_workbook):
        """Test text extraction from .xlsx files."""
        mock_cell1 = type('Cell', (), {})()
        mock_cell1.value = 'Cell A1'
        mock_cell2 = type('Cell', (), {})()
        mock_cell2.value = 'Cell B1'
        mock_row = [mock_cell1, mock_cell2]
        
        mock_sheet = type('Sheet', (), {})()
        mock_sheet.iter_rows = lambda: [mock_row]
        mock_workbook_instance = mock_workbook.return_value
        mock_workbook_instance.worksheets = [mock_sheet]
        
        result = extract_text("test.xlsx")
        expected = "Cell A1\nCell B1"
        self.assertEqual(result, expected)
    
    def test_extract_text_file_not_found(self):
        """Test extraction from non-existent file."""
        result = extract_text("/non/existent/file.txt")
        self.assertIsNone(result)
    
    def test_extract_text_with_encoding_error(self):
        """Test extraction when encoding error occurs."""
        # Create a file with problematic content
        test_file = os.path.join(self.temp_dir, "test_encoding.txt")
        with open(test_file, 'wb') as f:
            f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8 sequence
        
        result = extract_text(test_file)
        # Should handle the error gracefully and return None or valid text
        self.assertIsNotNone(result)  # Should not crash


if __name__ == '__main__':
    unittest.main()
