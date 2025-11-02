"""
TREC Property Inspection Report PDF Generator
Generates PDF reports in Texas Real Estate Commission format.
"""

import os
import html
from typing import List, Dict, Optional, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether, Frame, PageTemplate, Flowable
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black


class TRECReportCanvas(canvas.Canvas):
    """Custom canvas for TREC report with headers and footers."""
    
    def __init__(self, *args, **kwargs):
        self.report_id = kwargs.pop('report_id', '')
        self.checkbox_data = kwargs.pop('checkbox_data', {})
        self.checkbox_positions = []  # Store positions where checkboxes should be drawn
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header()
            self.draw_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header(self):
        """Draw header on every page."""
        self.saveState()
        
        # Report ID - LEFT aligned at top
        self.setFont("Times-Roman", 10)
        self.drawString(0.5 * inch, 10.5 * inch, f"Report Identification: {self.report_id}")
        
        # Draw a line under report ID (full width within margins)
        self.line(0.5 * inch, 10.4 * inch, 8 * inch, 10.4 * inch)
        
        # Column headers - spread across the page width
        y_pos = 10.25 * inch
        self.setFont("Times-Bold", 10)
        
        # Calculate positions for 4 columns
        col_width = 1.75 * inch
        start_x = 0.5 * inch
        
        # I = Inspected
        self.drawString(start_x, y_pos, "I=Inspected")
        
        # NI = Not Inspected
        self.drawString(start_x + col_width, y_pos, "NI=Not Inspected")
        
        # NP = Not Present
        self.drawString(start_x + (col_width * 2), y_pos, "NP=Not Present")
        
        # D = Deficient
        self.drawString(start_x + (col_width * 3), y_pos, "D=Deficient")
        
        # Draw checkbox column headers
        y_pos = 10.05 * inch
        self.setFont("Times-Bold", 9)
        checkbox_x = 0.5 * inch
        
        # Draw a box around the checkbox header area - FULL WIDTH within margins
        box_width = 8 * inch - 0.5 * inch  # From left margin to right margin
        self.rect(checkbox_x - 0.05 * inch, y_pos - 0.05 * inch, 
                 box_width, 0.15 * inch, stroke=1, fill=0)
        
        # Draw checkbox labels (centered in their sections)
        self.drawCentredString(checkbox_x + 0.15 * inch, y_pos, "I")
        self.drawCentredString(checkbox_x + 0.4 * inch, y_pos, "NI")
        self.drawCentredString(checkbox_x + 0.7 * inch, y_pos, "NP")
        self.drawCentredString(checkbox_x + 1.0 * inch, y_pos, "D")
        
        self.restoreState()

    def draw_footer(self, num_pages):
        """Draw footer on every page."""
        self.saveState()
        
        # Page number - centered
        self.setFont("Times-Roman", 10)
        page_text = f"Page {self._pageNumber} of {num_pages}"
        self.drawCentredString(4.25 * inch, 0.6 * inch, page_text)
        
        # TREC reference - left aligned
        self.setFont("Times-Roman", 8)
        self.drawString(0.5 * inch, 0.4 * inch, "REI 7-6 (8/9/21)")
        
        # TREC info - centered
        self.drawCentredString(4.25 * inch, 0.25 * inch, 
                              "Promulgated by the Texas Real Estate Commission - (512) 936-3000 - www.trec.texas.gov")
        
        self.restoreState()


def convert_to_roman(num: int) -> str:
    """Convert integer to Roman numeral."""
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num


def convert_to_letter(num: int) -> str:
    """Convert integer to letter (0->A, 1->B, etc.)."""
    if num < 0:
        return ""
    if num < 26:
        return chr(65 + num)  # 65 is ASCII for 'A'
    # For numbers > 25, use AA, AB, etc.
    return convert_to_letter(num // 26 - 1) + chr(65 + (num % 26))


def escape_html_entities(text: str) -> str:
    """Convert HTML entities to normal characters."""
    if not text:
        return ""
    # Use html.unescape to handle all HTML entities
    text = html.unescape(text)
    return text


def get_comment_text(comment: Dict[str, Any]) -> str:
    """Extract comment text from various possible fields."""
    for field in ['text', 'content', 'commentText', 'value']:
        if comment.get(field):
            return escape_html_entities(comment[field])
    return ""


def get_inspection_status(line_item: Dict[str, Any]) -> str:
    """Determine inspection status from line item data."""
    # First check explicit inspection status
    if line_item.get('inspectionStatus'):
        status = line_item['inspectionStatus'].upper()
        if status in ['I', 'NI', 'NP', 'D']:
            return status
    
    # Check isDeficient flag
    if line_item.get('isDeficient'):
        return 'D'
    
    # Check if there are deficient comments
    comments = line_item.get('comments', [])
    for comment in comments:
        if comment.get('type') == 'deficient' or comment.get('isFlagged'):
            return 'D'
    
    # Default to Inspected if there are comments
    if comments:
        return 'I'
    
    return ''


def create_styles():
    """Create custom paragraph styles for the report."""
    styles = getSampleStyleSheet()
    
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        spaceAfter=12,
        spaceBefore=18,
        textColor=black
    ))
    
    # Line item header style
    styles.add(ParagraphStyle(
        name='LineItemHeader',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=11,
        leading=13,
        spaceAfter=8,
        spaceBefore=12,
        textColor=black
    ))
    
    # Comment label style
    styles.add(ParagraphStyle(
        name='CommentLabel',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10,
        leading=12,
        spaceAfter=4,
        leftIndent=0.25 * inch,
        textColor=black
    ))
    
    # Comment text style
    styles.add(ParagraphStyle(
        name='CommentText',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        spaceAfter=10,
        leftIndent=0.5 * inch,
        alignment=TA_JUSTIFY,
        textColor=black
    ))
    
    # Media reference style
    styles.add(ParagraphStyle(
        name='MediaReference',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=9,
        leading=11,
        spaceAfter=8,
        leftIndent=0.5 * inch,
        textColor=black
    ))
    
    # Sub-field style
    styles.add(ParagraphStyle(
        name='SubField',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=12,
        spaceAfter=6,
        leftIndent=0.25 * inch,
        textColor=black
    ))
    
    return styles


class CheckboxMarker(Flowable):
    """Flowable that draws checkboxes immediately when rendered."""
    
    def __init__(self, status: str):
        Flowable.__init__(self)
        self.status = status
        self.width = 1.25 * inch  # Width of checkbox column
        self.height = 13  # Height to align with line item text
    
    def draw(self):
        """Draw checkboxes at the current position."""
        canvas = self.canv
        
        # Draw checkboxes immediately at current position
        checkbox_size = 10
        checkbox_x = -1.25 * inch  # Offset to the left (in the margin area)
        spacing = 0.25 * inch
        y_base = 3  # Baseline adjustment
        
        statuses = ['I', 'NI', 'NP', 'D']
        for i, stat in enumerate(statuses):
            x = checkbox_x + (i * spacing)
            
            # Draw checkbox square
            canvas.rect(x, y_base, checkbox_size, checkbox_size, stroke=1, fill=0)
            
            # Fill if this is the selected status
            if self.status and stat == self.status.upper():
                # Draw an X inside the box
                canvas.line(x, y_base, x + checkbox_size, y_base + checkbox_size)
                canvas.line(x + checkbox_size, y_base, x, y_base + checkbox_size)


class CheckboxDrawer:
    """Helper class to draw checkboxes on the canvas."""
    
    def __init__(self, canvas_obj):
        self.canvas = canvas_obj
        self.checkbox_size = 10
        self.checkbox_x = 0.5 * inch
        self.spacing = 0.25 * inch
        
    def draw_checkbox_row(self, y_position: float, status: str):
        """Draw a row of checkboxes with one filled based on status."""
        self.canvas.saveState()
        
        statuses = ['I', 'NI', 'NP', 'D']
        for i, stat in enumerate(statuses):
            x = self.checkbox_x + (i * self.spacing)
            
            # Draw checkbox square
            self.canvas.rect(x, y_position - self.checkbox_size, 
                           self.checkbox_size, self.checkbox_size, 
                           stroke=1, fill=0)
            
            # Fill if this is the selected status
            if status and stat == status.upper():
                # Draw an X inside the box
                self.canvas.line(x, y_position - self.checkbox_size,
                               x + self.checkbox_size, y_position)
                self.canvas.line(x + self.checkbox_size, y_position - self.checkbox_size,
                               x, y_position)
        
        self.canvas.restoreState()


def generate_trec_pdf(sections: List[Dict], metadata: Dict, output_path: str) -> str:
    """
    Generates a TREC Property Inspection Report PDF.
    
    Args:
        sections: List of section dictionaries with lineItems and comments
        metadata: Dictionary with reportId, inspectionDate, etc.
        output_path: Path where PDF should be saved
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # Validate input
    if not sections:
        raise ValueError("Sections list cannot be empty")
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Sort sections by order
    sorted_sections = sorted(sections, key=lambda x: x.get('order', 0))
    
    # Extract report ID
    report_id = metadata.get('reportId', metadata.get('report_id', 'N/A'))
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=1.25 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=1.75 * inch,  # Leave space for checkboxes
        rightMargin=0.75 * inch
    )
    
    # Create styles
    styles = create_styles()
    
    # Build story (list of flowables)
    story = []
    
    # Track checkbox positions for later drawing
    checkbox_positions = []
    
    # Process each section
    for section_idx, section in enumerate(sorted_sections):
        # Get section number (use sectionNumber field or generate Roman numeral)
        if section.get('sectionNumber'):
            section_num = section['sectionNumber']
        else:
            section_num = convert_to_roman(section_idx + 1)
        
        # Section header
        section_name = section.get('name', '').upper()
        section_header = f"{section_num}. {section_name}"
        story.append(Paragraph(section_header, styles['SectionHeader']))
        
        # Sort and process line items
        line_items = section.get('lineItems', [])
        sorted_line_items = sorted(line_items, key=lambda x: x.get('order', 0))
        
        for item_idx, line_item in enumerate(sorted_line_items):
            # Line item letter
            item_letter = convert_to_letter(item_idx)
            
            # Line item name
            item_name = line_item.get('name', line_item.get('title', ''))
            line_item_header = f"{item_letter}. {item_name}"
            
            # Create a container for line item and its content
            line_item_content = []
            
            # Determine inspection status
            status = get_inspection_status(line_item)
            
            # Add checkbox marker (invisible flowable that registers position)
            line_item_content.append(CheckboxMarker(status))
            
            # Add line item header
            line_item_content.append(Paragraph(line_item_header, styles['LineItemHeader']))
            
            # Process comments
            comments = line_item.get('comments', [])
            sorted_comments = sorted(comments, key=lambda x: x.get('order', 0))
            
            for comment in sorted_comments:
                # Comment label
                comment_label = comment.get('label', '')
                comment_number = comment.get('commentNumber', '')
                
                if comment_label:
                    label_text = f"{comment_number}. {comment_label}" if comment_number else comment_label
                    line_item_content.append(Paragraph(label_text, styles['CommentLabel']))
                
                # Comment text
                comment_text = get_comment_text(comment)
                if comment_text:
                    # Handle line breaks
                    comment_text = comment_text.replace('\n', '<br/>')
                    line_item_content.append(Paragraph(comment_text, styles['CommentText']))
                
                # Media references
                photos = comment.get('photos', [])
                videos = comment.get('videos', [])
                total_media = len(photos) + len(videos)
                
                if total_media > 0:
                    media_text = f"See attached media ({total_media} item{'s' if total_media > 1 else ''})"
                    line_item_content.append(Paragraph(media_text, styles['MediaReference']))
            
            # Add spacing between line items
            line_item_content.append(Spacer(1, 0.1 * inch))
            
            # Try to keep line items together when possible
            try:
                story.append(KeepTogether(line_item_content))
            except:
                # If KeepTogether fails (content too large), add items individually
                story.extend(line_item_content)
        
        # Add extra space after each section
        story.append(Spacer(1, 0.2 * inch))
    
    # Build the PDF with custom canvas
    def create_canvas(filename, **kwargs):
        return TRECReportCanvas(
            filename,
            report_id=report_id,
            checkbox_data=checkbox_positions,
            **kwargs
        )
    
    doc.build(story, canvasmaker=create_canvas)
    
    # Now we need to add checkboxes - this requires a second pass
    # For now, we'll use a custom canvas that draws checkboxes at page build time
    # The checkbox positions need to be calculated during the build process
    
    return output_path


def generate_trec_pdf_from_json(json_data: Dict, output_path: str, metadata: Dict = None) -> str:
    """
    Convenience function to generate PDF from JSON data structure.
    
    Args:
        json_data: Dictionary containing 'sections' key with list of sections
        output_path: Path where PDF should be saved
        metadata: Optional metadata dict, extracted from json_data if not provided
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # Extract sections
    sections = json_data.get('sections', [])
    
    # Extract or use provided metadata
    if metadata is None:
        metadata = {
            'reportId': json_data.get('reportId', json_data.get('report_id', 'N/A')),
            'inspectionDate': json_data.get('inspectionDate', ''),
            'propertyAddress': json_data.get('propertyAddress', ''),
            'inspectorName': json_data.get('inspectorName', ''),
            'inspectorLicense': json_data.get('inspectorLicense', '')
        }
    
    return generate_trec_pdf(sections, metadata, output_path)


# Example usage
if __name__ == "__main__":
    import json
    
    # Load sections from JSON file
    with open('sections.json', 'r') as f:
        data = json.load(f)
    
    # Metadata for the report
    metadata = {
        'reportId': 'TREC-2025-001',
        'inspectionDate': '2025-11-01',
        'propertyAddress': '123 Main St, Austin, TX 78701',
        'inspectorName': 'John Inspector',
        'inspectorLicense': 'TREC #12345'
    }
    
    # Generate PDF
    output_file = 'generated_files/inspection_report.pdf'
    result = generate_trec_pdf_from_json(data, output_file, metadata)
    print(f"PDF generated successfully: {result}")
