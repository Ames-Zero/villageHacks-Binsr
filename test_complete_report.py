#!/usr/bin/env python3
"""
Test script to generate a complete TREC inspection report.

This demonstrates the new functions:
1. fill_top_fields_from_json() - Fills client info, address, inspector, date in blank template
2. merge_pdfs() - Merges the filled template with the detailed report
3. generate_complete_trec_report() - Does both steps automatically
"""

import os
import sys
from helper import generate_complete_trec_report

def main():
    """Generate complete TREC inspection report."""
    
    # Define paths
    json_path = 'inspection.json'
    template_path = 'TREC_Template_Blank.pdf'
    filled_pdf_path = 'TREC_Sample_Filled.pdf'  # Optional - for pages 2-4
    output_path = 'generated_files/complete_inspection_report.pdf'
    
    # Check if required files exist
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found!")
        print("Please ensure inspection.json exists in the current directory.")
        return 1
    
    if not os.path.exists(template_path):
        print(f"❌ Error: {template_path} not found!")
        print("Please ensure TREC_Template_Blank.pdf exists in the current directory.")
        return 1
    
    # Check if filled PDF exists (optional)
    if not os.path.exists(filled_pdf_path):
        print(f"ℹ️  Note: {filled_pdf_path} not found. Will use only page 1 from blank template.")
        filled_pdf_path = None
    else:
        print(f"ℹ️  Using filled PDF: {filled_pdf_path} for pages 2-4")
    
    # Create output directory if needed
    os.makedirs('generated_files', exist_ok=True)
    
    # Generate the complete report
    try:
        result = generate_complete_trec_report(
            json_path=json_path,
            template_path=template_path,
            output_path=output_path,
            filled_pdf_path=filled_pdf_path
        )
        print(f"✅ SUCCESS! Complete report saved to: {result}")
        return 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

