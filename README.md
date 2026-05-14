<div align="center">

<br/>

# 📄 Termwork Generator Pro

### *Automate your engineering termwork — beautifully.*

A high-performance **Flask** web application that dynamically generates multi-page, print-ready Word & PDF documents from smart templates — with a bold Neo-Memphis UI.

<br/>

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Render-10B981?style=for-the-badge&logo=render&logoColor=white)](https://termwork-website.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)

<br/>

</div>

---

## 🌟 What Is This?

**Termwork Generator Pro** eliminates the repetitive, error-prone process of manually formatting engineering practical files. Fill in your details once, list your practical titles, and instantly receive a fully formatted, correctly merged `.docx` and `.pdf` — ready to print and submit.

> Built for **engineering students** who need clean, consistent practical journals — fast.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| ⚡ **Dynamic Generation** | Replaces template placeholders with your form data using `python-docx` & `docxtpl` |
| 📑 **Multi-Page Merging** | Correctly stitches multiple practical pages into one seamless document |
| 📥 **Dual-Format Output** | Instantly download your termwork as both **PDF** and **DOCX** |
| 🧠 **Smart Title Routing** | Auto-selects the correct template based on title length (short / medium / long) |
| 💾 **Persistent Form Data** | Auto-saves your details via `localStorage` — never retype your info again |
| 📱 **Fully Responsive** | Scales perfectly from mobile to ultra-wide desktop via Bootstrap 5 |
| ☁️ **Cloud-Ready** | Keep-alive endpoint prevents Render/Heroku free-tier sleep |
| 🐳 **Docker Support** | Fully containerized with `LibreOffice` for headless PDF conversion on Linux |

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Backend** | Python 3.8+, Flask |
| **Document Engine** | `python-docx`, `docxtpl`, `lxml` |
| **PDF Conversion** | `docx2pdf` (Windows) · `LibreOffice` (Linux/Docker) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Vanilla JS |
| **Deployment** | Render · Docker · Gunicorn |

</div>

---

## 🎨 Design System — Neo-Memphis

The UI is built around a **"Playful Geometric" (Neo-Memphis)** aesthetic:

- 🟩 **Hard Shadows** — `4px 4px 0px 0px #1E293B` rigid offsets replace soft blurs
- 🟣 **Squish Mechanics** — Inputs and buttons use `translate()` + `cubic-bezier` keyframes for a satisfying sticky feel
- 🎨 **Vibrant Palette** — Emerald Green `#10B981` and Vivid Violet accents on a Paper Canvas `#FFFDF5`

---

## 📋 Placeholder Reference

Inside your `template.docx`, use these **exact** curly-brace tags:

```
{{term}}          →  Term / Academic Year
{{subject}}       →  Subject Name
{{name}}          →  Student Name
{{pen}}           →  Permanent Enrolment Number
{{class}}         →  Class (e.g. SY-COMPS-A)
{{batch}}         →  Batch (e.g. B2)
{{semester}}      →  Semester Number
{{checked_by}}    →  Faculty Name
{{title}}         →  Practical Title
{{practical_no}}  →  Practical Number
```

> ⚠️ **Template Routing:** The generator automatically selects `template1.docx` (short), `template.docx` (medium), or `template2.docx` (long) based on your title's character count.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Microsoft Word** — required for `docx2pdf` on Windows
- **Git**

### 1 · Clone the Repository

```bash
git clone https://github.com/meetchauhan17/termwork-website.git
cd termwork-website
```

### 2 · Set Up a Virtual Environment *(recommended)*

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 · Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 · Run the App

```bash
python app.py
```

Open your browser at **`http://127.0.0.1:5000`** 🎉

---

## 🐳 Docker Deployment *(Linux / Cloud)*

```bash
# Build the image
docker build -t termwork-generator .

# Run the container
docker run -p 5000:5000 termwork-generator
```

> Docker uses **LibreOffice** for headless PDF conversion — no Microsoft Word required.

---

## 🔧 How It Works

```
User fills form  →  Flask receives POST  →  Template selected by title length
       ↓
  docxtpl renders placeholders  →  Pages merged with python-docx
       ↓
  docx2pdf / LibreOffice converts  →  Download links served
```

1. **Fill** your student details and practical titles in the web form
2. **Submit** — Flask processes the form and picks the correct template per practical
3. **Merge** — All practical pages are stitched together into one clean document
4. **Convert** — The merged `.docx` is converted to `.pdf` automatically
5. **Download** — Both formats are served instantly for download

---

## 🐞 Troubleshooting

<details>
<summary><strong>📌 docx2pdf freezes / COM error on Windows</strong></summary>

Ensure Microsoft Word is fully installed. Flask uses `pythoncom.CoInitialize()` inside the route thread. Make sure `pywin32` installed correctly:
```bash
pip install pywin32
python -m pywin32_postinstall -install
```
</details>

<details>
<summary><strong>📌 "Template file not found" error</strong></summary>

The app looks for `template.docx`, `template1.docx`, and `template2.docx` in the **root directory** alongside `app.py`. Verify the files exist and have the correct `.docx` extension.
</details>

<details>
<summary><strong>📌 App sleeping on Render (free tier)</strong></summary>

Use [UptimeRobot](https://uptimerobot.com) to ping `/keep-alive` every 5 minutes. The endpoint returns `200 OK` to keep the server active.
</details>

---

## 📁 Project Structure

```
termwork-website/
├── app.py               # Flask application & route logic
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker config (LibreOffice + Gunicorn)
├── template.docx        # Medium-title practical template
├── template1.docx       # Short-title practical template
├── template2.docx       # Long-title practical template
├── static/              # CSS, JS, and assets
├── templates/           # Jinja2 HTML templates
├── temp/                # Temporary working files (auto-cleaned)
└── outputs/             # Generated Termwork.docx & Termwork.pdf
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Crafted with ❤️ by [Meet Chauhan](https://github.com/meetchauhan17)**

*If this saved you time, drop a ⭐ on the repo!*

[![GitHub stars](https://img.shields.io/github/stars/meetchauhan17/termwork-website?style=social)](https://github.com/meetchauhan17/termwork-website/stargazers)

</div>
