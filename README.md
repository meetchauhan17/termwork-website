<h1 align="center">
  <br>
  Termwork Generator Pro
  <br>
</h1>

<h4 align="center">A high-performance Flask application that dynamically generates multi-page Word and PDF documents from templates using a beautiful Neo-Memphis interface.</h4>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#the-design-system">The Design System</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#troubleshooting">Troubleshooting</a>
</p>

---

## Key Features

* **Dynamic Document Generation:** Instantly replaces template placeholders (`{{term}}`, `{{name}}`, etc.) based on user form inputs using `python-docx`.
* **Multi-Page Merging:** Correctly handles multi-page practical assignments utilizing `docxcompose` to merge documents seamlessly without corruption.
* **Instant PDF Conversion:** Leverages `docx2pdf` to output print-ready formats securely on Windows COM instances.
* **Smart Persistent Storage:** Utilizes local browser storage (`localStorage`) to auto-save form data securely and recall it instantly via the "Load Last Data" bridge.
* **Fully Responsive Utility:** Architected utilizing pure CSS constraints and Bootstrap 5 so the application scales perfectly from Ultra-Wide Desktop to narrow Mobile devices.
* **Cloud Persistence mechanism:** A `keep_alive.py` logic wrapper is implemented guaranteeing remote server deployments (e.g. Render/Heroku) do not sleep during inactivity.

## The Design System
The frontend has been completely rebuilt using the **"Playful Geometric" (Neo-Memphis)** aesthetic:
- **High-Fidelity Pop Art:** Replaced soft shadows with hard `4px 4px 0px 0px #1E293B` rigid offsets.
- **Physical "Squish" Mechanics:** Interacting with inputs and buttons utilizes robust `translate()` and `cubic-bezier` keyframes mimicking realistic sticky mechanics.
- **Vibrant Accent Layering:** Anchored around Emerald Green (`#10B981`) and Vivid Violet palettes against a classic `#FFFDF5` Paper Canvas.

## Installation

### Prerequisites
- Python 3.8+
- Microsoft Word installed (required *specifically* for the `docx2pdf` native COM execution step)
- Git

### Local Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/meetchauhan17/termwork-website.git
   cd termwork-website
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Provide the Anchor Template**
   Ensure an actual Word file named `template.docx` exists in the application root directory alongside `app.py`.

4. **Boot the Application**
   ```bash
   python app.py
   ```

5. Access the generator at `http://127.0.0.1:5000`

---

## How to Use & Placeholder Tags

To have the Python core replace your variables properly, you must use the EXACT curly-brace terminology inside your Microsoft Word `template.docx`:

- `{{term}}`
- `{{subject}}`
- `{{name}}`
- `{{pen}}`
- `{{class}}`
- `{{batch}}`
- `{{semester}}`
- `{{checked_by}}`
- `{{title}}`
- `{{practical_no}}`

When submitting the form, the generator will read how many practicals you selected, clone the anchor template for each title provided, merge the files sequentially, convert it to a PDF via the COM thread, and present a direct download link instantly.

## Troubleshooting

>**Docx2pdf Freezing / COM Error**
> Ensure you are running this on a Windows Machine with Microsoft Office/Word completely installed. If Flask hangs or throws threading COM errors during conversion, our `pythoncom.CoInitialize()` has been properly integrated into the routing logic—just ensure `pywin32` was successfully installed from `requirements.txt`.

> **"Template file not found" Error**
> The app explicitly looks for `template.docx` inside the root folder alongside `app.py`. Check for typos or file extension `.docx` issues.

---

<p align="center">
  Crafted with ❤️ by <a href="https://github.com/meetchauhan17">Meet Chauhan</a>
</p>
