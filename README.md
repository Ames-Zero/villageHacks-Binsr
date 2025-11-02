# villageHacks-Binsr

Home inspection report generation prototype for Binsr inspection || Village Hacks 2025

## Overview

This project provides a Python-based solution for generating professional PDF inspection reports in **TREC (Texas Real Estate Commission)** format from structured JSON data. The system converts detailed inspection data into properly formatted, printable PDF documents that comply with official TREC standards.

## Features

- ✅ **TREC-Compliant Formatting** - Generates PDFs matching official Texas Real Estate Commission standards
- ✅ **Automated Headers & Footers** - Consistent headers with Report ID and legend on every page
- ✅ **Dynamic Checkboxes** - I/NI/NP/D checkboxes automatically placed beside each line item
- ✅ **Hierarchical Content Structure** - Sections → Line Items → Comments with proper formatting
- ✅ **HTML Entity Handling** - Automatically converts entities like `&apos;`, `&quot;` to proper characters
- ✅ **Professional Typography** - Times New Roman font family throughout
- ✅ **Media References** - Tracks photos and videos associated with comments
- ✅ **Page Number Management** - Automatic page numbering with total page count

## Project Structure

```
villageHacks-Binsr/
├── helper.py                    # Core PDF generation functions
├── server.py                    # Flask server (if applicable)
├── test_pdf_generation.py       # Test script for PDF generation
├── sections.json                # Sample inspection data
├── inspection.json              # Inspection metadata
├── requirements.txt             # Python dependencies
├── generated_files/             # Output directory for generated PDFs
└── README.md                    # This file
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ames-Zero/villageHacks-Binsr.git
   cd villageHacks-Binsr
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv binsr_env
   source binsr_env/bin/activate  # On Windows: binsr_env\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from helper import generate_trec_pdf_from_json
import json

# Load your inspection data
with open('sections.json', 'r') as f:
    data = json.load(f)

# Define report metadata
metadata = {
    'reportId': 'TREC-2025-001',
    'inspectionDate': '2025-11-01',
    'propertyAddress': '123 Main St, Austin, TX 78701',
    'inspectorName': 'John Inspector',
    'inspectorLicense': 'TREC #12345'
}

# Generate the PDF
output_path = generate_trec_pdf_from_json(
    data, 
    'generated_files/inspection_report.pdf', 
    metadata
)
print(f"PDF generated: {output_path}")
```

### Running the Test Script

```bash
python test_pdf_generation.py
```

This will generate a sample PDF at `generated_files/inspection_report.pdf` using the data from `sections.json`.

## API Reference

### `generate_trec_pdf(sections, metadata, output_path)`

Main function to generate TREC-formatted PDF from structured data.

**Parameters:**
- `sections` (list): List of section dictionaries with line items and comments
- `metadata` (dict): Report metadata including reportId, inspectionDate, propertyAddress, etc.
- `output_path` (str): File path where the PDF should be saved

**Returns:**
- `str`: Path to the generated PDF file

### `generate_trec_pdf_from_json(json_data, output_path, metadata=None)`

Convenience function for generating PDF from JSON structure.

**Parameters:**
- `json_data` (dict): Dictionary containing 'sections' key with section data
- `output_path` (str): File path where the PDF should be saved
- `metadata` (dict, optional): Report metadata (auto-extracted if not provided)

**Returns:**
- `str`: Path to the generated PDF file

## Data Structure

### Section Format
```python
{
  "id": "unique_section_id",
  "name": "Section Name",
  "order": 0,
  "sectionNumber": "I",  # Roman numeral or custom
  "lineItems": [...]
}
```

### Line Item Format
```python
{
  "id": "unique_item_id",
  "name": "Line Item Name",
  "order": 0,
  "inspectionStatus": "I",  # "I", "NI", "NP", or "D"
  "isDeficient": false,
  "comments": [...]
}
```

### Comment Format
```python
{
  "id": "unique_comment_id",
  "label": "Comment Heading",
  "text": "Comment content",
  "commentNumber": "1.1",
  "type": "info",  # or "deficient"
  "photos": [],
  "videos": []
}
```

## PDF Layout Specifications

### Page Setup
- **Size:** US Letter (8.5" × 11")
- **Orientation:** Portrait
- **Font:** Times New Roman family
- **Margins:**
  - Top: 1.25" (header space)
  - Bottom: 0.75" (footer space)
  - Left: 1.75" (content + checkbox column)
  - Right: 0.75"

### Header (Every Page)
1. Report Identification: [ID] (left-aligned)
2. Full-width separator line
3. Status legend: `I=Inspected | NI=Not Inspected | NP=Not Present | D=Deficient`
4. Checkbox column headers in full-width box

### Footer (Every Page)
1. Page X of Y (centered)
2. REI 7-6 (8/9/21) (left-aligned)
3. TREC information (centered)

### Content Layout
- **Two-column structure:**
  - Left: Checkbox column (I/NI/NP/D)
  - Right: Hierarchical content
- **Content hierarchy:**
  1. Section Headers (12pt, bold, uppercase)
  2. Line Item Headers (11pt, bold, lettered A, B, C...)
  3. Comment Labels (10pt, bold, numbered)
  4. Comment Text (10pt, regular, justified)
  5. Media References (9pt, italic)

## Dependencies

- **Flask** >= 2.0 - Web framework (if using server mode)
- **ReportLab** >= 3.5 - PDF generation library

## Development

### Adding New Features

The main PDF generation logic is in `helper.py`. Key components:

- `TRECReportCanvas` - Custom canvas class for headers/footers
- `CheckboxMarker` - Flowable for rendering checkboxes
- `create_styles()` - Paragraph styles configuration
- Helper functions for data processing

### Testing

Run the test script to verify changes:
```bash
python test_pdf_generation.py
```

Check the generated PDF in `generated_files/inspection_report.pdf`

## Troubleshooting

**Issue: Checkboxes not appearing**
- Ensure `CheckboxMarker` flowables are being added before line item headers
- Check that inspection status is being properly determined

**Issue: Font not displaying correctly**
- Times New Roman is a standard PDF font and should always be available
- If issues persist, check ReportLab installation

**Issue: Content cutoff or overlapping**
- Adjust margins in `generate_trec_pdf()` function
- Modify spacing values in style definitions

## Contributing

This is a hackathon project for Village Hacks 2025. Contributions and improvements are welcome!

## License

This project is developed for Binsr inspection report generation.

## Contact

For questions or issues related to this project, please refer to the Village Hacks 2025 event documentation.

## Acknowledgments

- Village Hacks 2025
- Binsr Inspection
- Texas Real Estate Commission (TREC) for format specifications
