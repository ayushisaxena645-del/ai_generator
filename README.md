# AI-Assisted Resume Portfolio Generator & Analyser

An intelligent AI application built in Python that reads any plain text resume, uses the Google Gemini API to analyze candidate details and calculate ATS scores, and automatically generates a modern, responsive HTML/CSS web portfolio (`portfolio.html`).

---

## 🌟 Key Features

1. **AI Resume Analysis**:
   - **Candidate Extraction**: Automatically identifies Name, Headline, Contact Info, Professional Summary, Work History, Projects, Education, and Certifications.
   - **ATS Candidate Score**: Computes an automated candidate evaluation score (0-100), key candidate strengths, and recommended job roles.
   - **Skill Categorization**: Groups skills into Technical, Soft Skills, Tools & Frameworks, and Languages.

2. **Dynamic Portfolio Webpage Generation (`portfolio.html`)**:
   - Compiles extracted JSON content into a self-contained, responsive HTML5 webpage using custom templates.
   - **Smart Section Hiding**: Automatically hides any sections that have missing or empty data.

3. **Dual Execution Modes**:
   - **Command-Line Interface (CLI)**: Run `python main.py` directly with `resume.txt`.
   - **Interactive Web App (Flask)**: Run `python app.py` for a full web interface where any user can upload or paste a resume, view live analytics, and download their generated portfolio.

---

## 🛠️ Required Technologies

- **Python 3.9+**: Core language for file handling, API calls, JSON processing, and web rendering.
- **Gemini API**: Generative AI model (`gemini-2.5-flash` or `gemini-1.5-flash`) for structured content extraction.
- **JSON**: Standard structured data format exchange.
- **HTML5 & CSS3**: Responsive visual design system with typography, cards, tags, and timeline layouts.
- **Flask**: Web dashboard server for interactive uploads and previews.

---

## 📁 Project Structure

```
ai_assisted_resume_portfolio_generator/
├── main.py                # Command-line entry point
├── app.py                 # Interactive Flask web application
├── resume_cleaner.py      # Input validation & text sanitization module
├── gemini_analyzer.py     # Gemini API integration & fallback logic
├── portfolio_builder.py   # HTML/CSS template engine
├── resume.txt             # Sample resume text input
├── template.html          # Jinja2 HTML portfolio layout template
├── style.css              # Custom modernist CSS design system
├── requirements.txt       # Python package dependencies
├── .env.example           # Environment template for GEMINI_API_KEY
└── README.md              # Project documentation
```

---

## 🚀 Quick Setup Instructions

### 1. Clone & Install Dependencies

Open your terminal in the project directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Your Gemini API Key

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. Create a `.env` file in the project folder (or copy `.env.example` to `.env`):

```bash
cp .env.example .env
```

3. Add your key inside `.env`:

```env
GEMINI_API_KEY=AIzaSyYourActualGeminiApiKeyHere
```

> **Note**: If no API key is provided, the application will automatically fall back to an offline rule-based extraction mode so you can test without crashing!

---

## 💻 How to Run

### Mode A: Command-Line Interface (CLI)

Place your resume text inside `resume.txt` and run:

```bash
python main.py
```

- Sanitizes and validates `resume.txt`.
- Sends the text to Gemini API.
- Outputs terminal summary (ATS Score, Strengths, Recommended Roles).
- Saves full JSON analysis to `resume_analysis.json`.
- Generates `portfolio.html`.

---

### Mode B: Interactive Web Dashboard

To allow anyone to paste or upload their resume via browser:

```bash
python app.py
```

- Open your browser to `http://127.0.0.1:5000`.
- Upload a `.txt` resume or paste raw text.
- Click **Analyze Resume & Build Portfolio**.
- Instantly view candidate scorecard, JSON structure, preview portfolio, and download `portfolio.html`.

---

## 🎯 Verification & Testing

1. Run `python main.py` and verify `portfolio.html` opens cleanly in any web browser.
2. Verify that empty resume sections are omitted cleanly.
3. Test `python app.py` and submit a custom resume text to verify live web dashboard analysis.

---

## 📄 License & Attribution

Built for the AI/ML Student Bootcamp Project Brief.
Developed with Python, Google Gemini API, HTML5, and CSS3.
