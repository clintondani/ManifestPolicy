# backend/app.py

from flask import Flask, request, jsonify
from scanner import scan_policy
from flask_cors import CORS
from auth import auth_bp
from db import init_db, save_report
import json
from textwrap import wrap
import requests
from bs4 import BeautifulSoup
import re


app = Flask(__name__)
CORS(app)
app.register_blueprint(auth_bp)

def is_url(text):
    return re.match(r"https?://", text.strip()) is not None

def fetch_policy_from_url(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove scripts & styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")

        # Clean excessive whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()
    except Exception as e:
        print("❌ URL fetch error:", e)
        return None


@app.route('/scan', methods=['POST'])
def scan_text():
    """Scan pasted policy text OR policy URL for shady clauses and DPDP violations."""
    try:
        data = request.get_json()
        raw_input = data.get('text', '').strip()
        username = data.get('username')

        if not raw_input:
            return jsonify({"error": "No input provided"}), 400

        # Detect input type
        if is_url(raw_input):
            fetched_text = fetch_policy_from_url(raw_input)

            if not fetched_text:
                return jsonify({
                            "error": "This website blocks automated access. Please paste the privacy policy text manually."
                        }), 400


            policy_text = fetched_text
            input_type = "url"
            filename = raw_input
        else:
            policy_text = raw_input
            input_type = "text"
            filename = None

        # Scan policy
        result = scan_policy(policy_text)

        # Save report
        save_report(
            input_type=input_type,
            filename=filename,
            shady_clauses=result.get("shady_clauses", []),
            dpdp_violations=result.get("dpdp_violations", []),
            summary=result.get("summary"),
            username=username
        )

        if "error" in result:
            return jsonify(result)

        # Result message
        if not result['shady_clauses'] and not result['dpdp_violations']:
            message = '✅ No shady clauses or DPDP violations found.'
        elif result['shady_clauses'] and not result['dpdp_violations']:
            message = '⚠️ Shady clauses found, but no DPDP violations.'
        elif not result['shady_clauses'] and result['dpdp_violations']:
            message = '⚠️ DPDP violations found, but no shady clauses.'
        else:
            message = '❗ Both shady clauses and DPDP violations detected.'

        return jsonify({
            'message': message,
            'input_type': input_type,
            'summary': result.get('summary'),
            'shady_clauses': result['shady_clauses'],
            'dpdp_violations': result['dpdp_violations']
        })

    except Exception as e:
        print("❌ Error in /scan:", e)
        return jsonify({"error": str(e)}), 500



from utils import extract_text_from_file
from flask import Flask, request, jsonify
from scanner import scan_policy
from werkzeug.utils import secure_filename

import os

# (existing app = Flask... remains unchanged)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    """Handle uploaded privacy policy files (with username support)."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    username = request.form.get('username', 'guest')  #get username from frontend

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type. Please upload a .txt, .pdf, or .docx file.'}), 415

    file_text = extract_text_from_file(file)

    if not file_text or len(file_text.strip().split()) < 30:
        return jsonify({'error': 'The uploaded file does not appear to contain a valid privacy policy.'}), 422

    try:
        #Scan the extracted text
        result = scan_policy(file_text)

        #Save to database including username
        save_report("file", file.filename, result.get("shady_clauses", []), result.get("dpdp_violations", []),result["summary"], username)

        if not result['shady_clauses'] and not result['dpdp_violations']:
            message = '✅ No shady clauses or DPDP violations found.'
        elif result['shady_clauses'] and not result['dpdp_violations']:
            message = '⚠️ Shady clauses found, but no DPDP violations.'
        elif not result['shady_clauses'] and result['dpdp_violations']:
            message = '⚠️ DPDP violations found, but no shady clauses.'
        else:
            message = '❗ Both shady clauses and DPDP violations detected.'

        return jsonify({
            'message': message,
            'summary': result.get('summary', ''),
            'shady_clauses': result['shady_clauses'],
            'dpdp_violations': result['dpdp_violations']
        })

    except Exception as e:
        print("❌ File scan error:", e)
        return jsonify({'error': str(e)}), 500


from db import get_reports
from flask import jsonify, request

@app.route('/history', methods=['GET'])
def history():
    try:
        username = request.args.get("username")
        if not username or username == "null":
            username = None

        reports = get_reports(username=username)

        if not reports:
            return jsonify([])

        formatted = []
        for r in reports:
            formatted.append({
                "id": r["id"],
                "timestamp": r["timestamp"],
                "input_type": r["input_type"],
                "filename": r["filename"],
                "shady_clauses": r["shady_clauses"],
                "dpdp_violations": r["dpdp_violations"],
                "summary":r["summary"],
                "username": r["username"]
            })

        return jsonify(formatted)
    except Exception as e:
        print("❌ Error fetching history:", e)
        return jsonify({"error": "Failed to load history"}), 500
    
from db import get_report_by_id
from flask import send_file
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

@app.route('/report/<int:report_id>', methods=['GET'])
def get_report(report_id):
    try:
        report = get_report_by_id(report_id)

        if not report:
            return jsonify({"error": "Report not found"}), 404

        return jsonify(report)

    except Exception as e:
        print("❌ Error fetching report:", e)
        return jsonify({"error": "Failed to fetch report"}), 500


@app.route('/download/<int:report_id>', methods=['GET'])
def download_report_pdf(report_id):
    """Generate and return a PDF for the given report id (in-memory)."""
    try:
        report = get_report_by_id(report_id)
        if not report:
            return jsonify({"error": "Report not found"}), 404

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Margin and positioning helpers
        left_margin = 20 * mm
        y = height - 20 * mm

        # Header
        p.setFont("Helvetica-Bold", 14)
        p.drawString(left_margin, y, "ManifestPolicy — Report")
        p.setFont("Helvetica", 10)
        y -= 8 * mm
        p.drawString(left_margin, y, f"Report ID: {report['id']}    Generated: {report['timestamp']}")
        y -= 6 * mm
        p.drawString(left_margin, y, f"User: {report.get('username') or 'N/A'}    Type: {report.get('input_type')}")
        if report.get('filename'):
            y -= 6 * mm
            p.drawString(left_margin, y, f"File: {report.get('filename')}")

        # Body
        y -= 10 * mm
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Shady Clauses")
        p.setFont("Helvetica", 10)
        y -= 6 * mm

        if report['shady_clauses']:
            for i, c in enumerate(report['shady_clauses'], start=1):
                if isinstance(c, dict):
                    text = f"{i}. {c.get('clause', '')} — {c.get('reason', '')}"
                else:
                    text = f"{i}. {c}"

                for line in split_text_to_lines(text, width - 2 * left_margin, p, font_size=10):
                    if y < 30 * mm:
                        p.showPage()
                        y = height - 20 * mm
                        p.setFont("Helvetica", 10)
                    p.drawString(left_margin, y, line)
                    y -= 5 * mm
                y -= 2 * mm
        else:
            p.drawString(left_margin, y, "None found")
            y -= 8 * mm

        # DPDP Violations
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "DPDP Violations")
        p.setFont("Helvetica", 10)
        y -= 6 * mm

        if report['dpdp_violations']:
            for i, v in enumerate(report['dpdp_violations'], start=1):
                if isinstance(v, dict):
                    text = f"{i}. {v.get('violation', '')} — {v.get('description', '')}"
                else:
                    text = f"{i}. {v}"

                for line in split_text_to_lines(text, width - 2 * left_margin, p, font_size=10):
                    if y < 30 * mm:
                        p.showPage()
                        y = height - 20 * mm
                        p.setFont("Helvetica", 10)
                    p.drawString(left_margin, y, line)
                    y -= 5 * mm
                y -= 2 * mm
        else:
            p.drawString(left_margin, y, "None found")
            y -= 8 * mm
        
        # Wraps long text
        def draw_wrapped_text(text_obj, text, max_chars=90):
            """
            Wraps long text into multiple lines for PDF.
            """
            if not text:
                text_obj.textLine("Not available")
                return

            lines = wrap(text, max_chars)
            for line in lines:
                text_obj.textLine(line)

        #Summary
        p.setFont("Helvetica-Bold", 12)
        p.drawString(left_margin, y, "Privacy Policy Summary")
        y -= 10 * mm

        summary = report.get("summary", {})

        p.setFont("Helvetica", 10)

        if isinstance(summary, dict) and summary:
            text_obj = p.beginText(left_margin, y)
            text_obj.setLeading(15)

            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("Overview:")
            text_obj.setFont("Helvetica", 10)
            draw_wrapped_text(text_obj, summary.get("overview"))

            text_obj.textLine("")
            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("Data Collected:")
            text_obj.setFont("Helvetica", 10)
            draw_wrapped_text(text_obj, summary.get("data_collected"))

            text_obj.textLine("")
            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("Data Sharing:")
            text_obj.setFont("Helvetica", 10)
            draw_wrapped_text(text_obj, summary.get("data_sharing"))

            text_obj.textLine("")
            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("User Rights:")
            text_obj.setFont("Helvetica", 10)
            draw_wrapped_text(text_obj, summary.get("user_rights"))

            text_obj.textLine("")
            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("Data Retention:")
            text_obj.setFont("Helvetica", 10)
            draw_wrapped_text(text_obj, summary.get("data_retention"))

            p.drawText(text_obj)
            y = text_obj.getY() - 12
        else:
            p.drawString(left_margin, y, "No summary available")
            y -= 10

        # Footer
        p.setFont("Helvetica-Oblique", 8)
        if y < 30 * mm:
            p.showPage()
            y = height - 20 * mm
        p.drawString(left_margin, 15 * mm, "Generated by ManifestPolicy")

        p.showPage()
        p.save()

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"report_{report_id}.pdf", mimetype='application/pdf')
    except Exception as e:
        print("❌ Error generating PDF:", e)
        return jsonify({"error": "Failed to generate PDF"}), 500


# small helper used by PDF generator
def split_text_to_lines(text, max_width, canvas_obj, font_name="Helvetica", font_size=10):
    """Split a long text into lines that fit the page width for the given canvas."""
    canvas_obj.setFont(font_name, font_size)
    words = text.split()
    lines = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if canvas_obj.stringWidth(test, font_name, font_size) <= max_width:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
