# backend/utils.py

import re

def clean_text(text):
    # Remove extra spaces, line breaks, symbols, etc.
    text = text.lower()
    text = re.sub(r'\n+', ' ', text)                # Remove newlines
    text = re.sub(r'\s+', ' ', text)                # Collapse whitespace
    text = re.sub(r'[^\w\s.,]', '', text)           # Remove symbols except punctuation
    return text.strip()

import fitz  # PyMuPDF

def extract_text_from_file(file):
    if file.filename.endswith('.txt'):
        return file.read().decode('utf-8')
    
    elif file.filename.endswith('.pdf'):
        text = ""
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    else:
        return ""
