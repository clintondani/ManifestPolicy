# ManifestPolicy 🛡️

> A privacy policy compliance scanner that detects shady clauses and checks for violations under **India's Digital Personal Data Protection (DPDP) Act, 2023**.

---

## What It Does

Most people never read privacy policies. ManifestPolicy reads them for you — and flags anything suspicious.

- 🔍 **Scans** privacy policies from pasted text, uploaded files, or URLs
- ⚠️ **Detects** shady clauses like data selling, breach disclaimers, and silent collection
- 🇮🇳 **Checks** compliance against India's DPDP Act 2023 (11 sections)
- 📄 **Summarises** the policy in plain English
- 📥 **Exports** full scan reports as downloadable PDFs
- 🕑 **Saves** scan history per user account
- 🧩 **Chrome Extension** for scanning any webpage instantly

---

## Tech Stack

| Layer        | Technology                              |
|--------------|-----------------------------------------|
| Backend      | Python, Flask, Flask-CORS               |
| Database     | SQLite                                  |
| NLP          | sumy (TextRank summarisation)           |
| PDF Parsing  | PyMuPDF (fitz)                          |
| PDF Export   | ReportLab                               |
| Web Scraping | Requests, BeautifulSoup4                |
| Frontend     | HTML, CSS, Vanilla JavaScript           |
| Extension    | Chrome Extension (Manifest v3)          |

---

## Features

- ✅ Paste text, enter a URL, or upload `.txt` / `.pdf` files
- ✅ Detects 5 types of shady clauses
- ✅ Checks 11 DPDP Act sections for violations
- ✅ AI-powered extractive summarisation
- ✅ Structured summary: overview, data collected, sharing, rights, retention
- ✅ User authentication (signup / login)
- ✅ Scan history saved per user
- ✅ Download reports as PDF
- ✅ Chrome extension for live page scanning
- ✅ Guest mode (scan without logging in)
- ✅ Responsive design (mobile friendly)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip
- Git
- Google Chrome (for the extension)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/manifestpolicy.git
cd manifestpolicy
```

### Step 2 — Set Up a Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env if needed
```

### Step 5 — Initialise the Database

```bash
python backend/init_db_run.py
```

### Step 6 — Run the Backend

```bash
python backend/app.py
```

The server starts at: `http://localhost:5000`

### Step 7 — Open the Frontend

Open `frontend/index_new.html` directly in your browser.
Or serve it with any static file server.

---

## Installing the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (toggle in the top right)
3. Click **Load unpacked**
4. Select the `extension/` folder from this project
5. The ManifestPolicy icon will appear in your toolbar

> ⚠️ Make sure the Flask backend is running before using the extension.

---

## Usage

### Web App

1. Go to `frontend/login_new.html` — log in or continue as guest
2. Paste a privacy policy, enter a URL, or upload a file
3. Click **Scan Policy**
4. View the summary, shady clauses, and DPDP violations
5. Download the report as PDF from the History section

### Chrome Extension

1. Visit any website (e.g. a company's privacy policy page)
2. Click the ManifestPolicy extension icon
3. Click **Scan This Page**
4. See the compliance result instantly

---

## Project Structure

| Folder / File         | Purpose                                      |
|-----------------------|----------------------------------------------|
| `backend/app.py`      | Flask routes: `/scan`, `/upload`, `/history` |
| `backend/scanner.py`  | Pattern matching for clauses & violations    |
| `backend/summarizer.py` | TextRank summarisation engine              |
| `backend/auth.py`     | User signup & login endpoints               |
| `backend/db.py`       | SQLite read/write helpers                   |
| `backend/utils.py`    | Text cleaning, PDF/TXT file extraction      |
| `frontend/`           | Browser-based UI (HTML, CSS, JS)            |
| `extension/`          | Chrome extension files                      |
| `samples/`            | Example privacy policies for testing        |

---

## Sample Test

To test the scanner quickly, paste the content of `samples/Privacy_Policy_ExampleCorp.txt` into the scanner. It contains several intentional violations and shady clauses.

---

## Future Improvements

- [ ] Switch to a more robust LLM-based clause detection (Claude / Gemini API)
- [ ] Support `.docx` file uploads
- [ ] Add risk score / compliance percentage meter
- [ ] Email notifications for high-risk policies
- [ ] Multi-language policy support
- [ ] Comparison between two privacy policies
- [ ] Public API for developers to integrate into their own apps
- [ ] Deploy to cloud (Render, Railway, or Vercel + Fly.io)

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Author

Built as a final-year project.  
Feel free to fork, use, or contribute!
