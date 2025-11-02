import os
import uuid
import io
from typing import Dict, Any
from flask import Flask, request, jsonify, send_from_directory, url_for, abort

try:
	from reportlab.pdfgen import canvas
	REPORTLAB_AVAILABLE = True
except Exception:
	REPORTLAB_AVAILABLE = False

app = Flask(__name__)

# Directory to store generated PDF files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(BASE_DIR, "generated_files")
os.makedirs(GENERATED_DIR, exist_ok=True)


def _save_pdf_bytes(pdf_bytes: bytes, filename: str) -> str:
	"""Save bytes to a file in GENERATED_DIR and return absolute path."""
	path = os.path.join(GENERATED_DIR, filename)
	with open(path, "wb") as f:
		f.write(pdf_bytes)
	return path


def _render_pdf_text(text: str) -> bytes:
	"""Render simple PDF in-memory using reportlab. Raises NotImplementedError if reportlab is not available.

	This is a tiny helper to generate a placeholder PDF. Your project can replace or extend this
	with richer PDF-generation logic in the helper functions below.
	"""
	if not REPORTLAB_AVAILABLE:
		raise NotImplementedError("reportlab is required for PDF generation; please install it or replace this helper")

	buf = io.BytesIO()
	p = canvas.Canvas(buf)
	p.setFont("Helvetica", 12)
	# Simple layout: write text lines
	y = 800
	for line in text.splitlines():
		p.drawString(40, y, line[:90])
		y -= 16
		if y < 40:
			p.showPage()
			y = 800
	p.showPage()
	p.save()
	buf.seek(0)
	return buf.read()


def generate_trec_pdf(data: Dict[str, Any]) -> str:
	"""Placeholder: generate PDF for TREC based on input JSON.

	Accepts parsed JSON as a dict. Returns the absolute path to the generated PDF file.

	Replace the internals of this function with your actual logic.
	"""
	# Simple placeholder behavior: create a short PDF summarizing the payload
	summary_lines = ["TREC PDF placeholder"]
	summary_lines.append("")
	summary_lines.append("Input JSON keys:")
	for k, v in data.items():
		summary_lines.append(f"- {k}: {str(v)[:80]}")

	pdf_bytes = _render_pdf_text("\n".join(summary_lines))
	filename = f"trec_{uuid.uuid4().hex}.pdf"
	return _save_pdf_bytes(pdf_bytes, filename)


def generate_binsr_pdf(data: Dict[str, Any]) -> str:
	"""Placeholder: generate PDF for BINSR based on input JSON.

	Replace the internals of this function with your actual logic.
	Returns absolute path to generated PDF file.
	"""
	summary_lines = ["BINSR PDF placeholder"]
	summary_lines.append("")
	summary_lines.append("Input JSON keys:")
	for k, v in data.items():
		summary_lines.append(f"- {k}: {str(v)[:80]}")

	pdf_bytes = _render_pdf_text("\n".join(summary_lines))
	filename = f"binsr_{uuid.uuid4().hex}.pdf"
	return _save_pdf_bytes(pdf_bytes, filename)


@app.route("/generate_trec", methods=["POST"])
def route_generate_trec():
	"""Endpoint to generate a TREC PDF.

	Expects JSON body. Returns JSON containing the filepath and filename.
	"""
	data = request.get_json(force=True, silent=True)
	if data is None:
		return jsonify({"error": "Invalid or missing JSON body"}), 400

	try:
		pdf_path = generate_trec_pdf(data)
	except NotImplementedError as e:
		return jsonify({"error": str(e)}), 501
	except Exception as e:
		return jsonify({"error": f"Generation failed: {e}"}), 500

	filename = os.path.basename(pdf_path)
	return jsonify({"filepath": pdf_path, "filename": filename}), 200


@app.route("/generate_binsr_pdf", methods=["POST"])
def route_generate_binsr_pdf():
	"""Endpoint to generate a BINSR PDF.

	Expects JSON body. Returns JSON containing the filepath and filename.
	"""
	data = request.get_json(force=True, silent=True)
	if data is None:
		return jsonify({"error": "Invalid or missing JSON body"}), 400

	try:
		pdf_path = generate_binsr_pdf(data)
	except NotImplementedError as e:
		return jsonify({"error": str(e)}), 501
	except Exception as e:
		return jsonify({"error": f"Generation failed: {e}"}), 500

	filename = os.path.basename(pdf_path)
	return jsonify({"filepath": pdf_path, "filename": filename}), 200


if __name__ == "__main__":
	# Run a dev server. Use a proper WSGI server for production.
	app.run(host="0.0.0.0", port=5000, debug=True)

