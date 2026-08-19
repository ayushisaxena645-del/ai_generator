import os
import json
import re
from flask import Flask, render_template_string, request, jsonify, send_file, Response
from resume_cleaner import clean_resume_text, validate_resume_text, ResumeValidationError
from gemini_analyzer import analyze_resume_with_gemini
from portfolio_builder import generate_portfolio_html

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

WEB_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI-Assisted Resume Portfolio Generator</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #090d16;
      --bg-card: #131b2e;
      --bg-input: #1c263d;
      --accent: #6366f1;
      --accent-hover: #4f46e5;
      --cyan: #06b6d4;
      --green: #10b981;
      --text-main: #f8fafc;
      --text-sub: #94a3b8;
      --border: rgba(255, 255, 255, 0.08);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      min-height: 100vh;
      padding: 1.5rem 1rem;
      font-size: 0.9rem;
    }
    .header {
      text-align: center;
      margin-bottom: 1.5rem;
    }
    .header h1 {
      font-size: 2rem;
      font-weight: 800;
      background: linear-gradient(90deg, #6366f1, #06b6d4);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.35rem;
    }
    .header p { color: var(--text-sub); font-size: 0.95rem; }
    
    .layout-grid {
      display: grid;
      grid-template-columns: 1.25fr 1fr;
      gap: 1.5rem;
      max-width: 1200px;
      margin: 0 auto;
    }
    @media (max-width: 900px) { .layout-grid { grid-template-columns: 1fr; } }
    
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    /* Navigation Tabs */
    .nav-tabs {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
      background: rgba(0,0,0,0.2);
      padding: 0.25rem;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    .tab-btn {
      flex: 1;
      padding: 0.6rem 0.85rem;
      background: transparent;
      border: none;
      color: var(--text-sub);
      font-weight: 600;
      font-size: 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .tab-btn.active {
      background: var(--accent);
      color: #fff;
    }
    
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .form-group {
      margin-bottom: 0.85rem;
    }
    .form-label {
      display: block;
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 0.3rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .form-sublabel {
      font-weight: 400;
      text-transform: none;
      color: var(--text-sub);
    }
    input[type="text"], input[type="email"], textarea {
      width: 100%;
      background: var(--bg-input);
      border: 1px solid var(--border);
      border-radius: 6px;
      color: var(--text-main);
      padding: 0.6rem 0.8rem;
      font-family: inherit;
      font-size: 0.85rem;
    }
    textarea {
      height: 75px;
      resize: vertical;
    }
    input:focus, textarea:focus { outline: none; border-color: var(--accent); }
    
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      width: 100%;
      background: linear-gradient(135deg, var(--accent), var(--accent-hover));
      color: #fff;
      font-weight: 700;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      border: none;
      cursor: pointer;
      font-size: 0.9rem;
      transition: transform 0.2s ease;
      text-decoration: none;
    }
    .btn:hover { transform: translateY(-2px); }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border);
      color: var(--text-main);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.15); }
    .btn-success {
      background: linear-gradient(135deg, #10b981, #059669);
    }
    
    .sample-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(99, 102, 241, 0.08);
      border: 1px dashed var(--accent);
      border-radius: 8px;
      padding: 0.65rem 0.85rem;
      margin-bottom: 1rem;
      font-size: 0.82rem;
    }

    #loading {
      display: none;
      text-align: center;
      padding: 2.5rem;
      color: var(--cyan);
    }
    .spinner {
      width: 36px;
      height: 36px;
      border: 3px solid rgba(255,255,255,0.1);
      border-top-color: var(--cyan);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 0.75rem;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .result-section { display: none; }
    
    .download-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      margin-top: 1.25rem;
    }
    pre {
      background: var(--bg-input);
      padding: 0.85rem;
      border-radius: 6px;
      overflow-x: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      color: var(--cyan);
      max-height: 340px;
    }
  </style>
</head>
<body>

<div class="header">
  <h1>AI-Assisted Resume Portfolio Generator</h1>
  <p>Easy-to-use tool to convert any resume into a beautiful HTML portfolio webpage (portfolio.html).</p>
</div>

<div class="layout-grid">

  <!-- LEFT PANEL: NAVIGATION & INPUT MODES -->
  <div class="card">
    
    <!-- NAVIGATION TABS -->
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('uploadTab', this)">⚡ 1-Click Upload / Paste</button>
      <button class="tab-btn" onclick="switchTab('sectionsTab', this)">✍️ 9 Portfolio Sections</button>
    </div>

    <!-- TAB 1: 1-CLICK UPLOAD / PASTE TEXT -->
    <div id="uploadTab" class="tab-content active">
      <div class="sample-bar">
        <span>💡 Need sample data to test?</span>
        <button class="btn btn-secondary" style="font-size: 0.75rem; padding: 0.3rem 0.6rem; width: auto;" onclick="loadSampleResume()">Load Sample Resume</button>
      </div>

      <div style="margin-bottom: 0.85rem; display: flex; gap: 0.5rem; align-items: center;">
        <input type="file" id="fileInput" accept=".txt" style="display: none;" onchange="handleFileUpload(event)">
        <button class="btn btn-secondary" style="font-size: 0.8rem; padding: 0.5rem 0.85rem;" onclick="document.getElementById('fileInput').click()">📁 Select resume.txt File</button>
        <span id="fileName" style="font-size: 0.8rem; color: var(--text-sub);">No file loaded</span>
      </div>

      <div class="form-group">
        <label class="form-label">Or Paste Full Resume Text Below:</label>
        <textarea id="fullResumeText" style="height: 280px;" placeholder="Paste raw resume text here..."></textarea>
      </div>

      <button class="btn btn-success" onclick="generateFromFullText()">✨ Generate Portfolio Webpage (portfolio.html)</button>
    </div>

    <!-- TAB 2: DIRECT 9 PORTFOLIO SECTIONS FORM -->
    <div id="sectionsTab" class="tab-content">
      <form id="portfolioForm" onsubmit="event.preventDefault(); submitDirectPortfolio();">
        
        <!-- 1. NAME -->
        <div class="form-group">
          <label class="form-label">1. Name <span class="form-sublabel">(Full candidate name)</span></label>
          <input type="text" id="name" placeholder="e.g. Ayush Sharma" required>
        </div>

        <!-- 2. HEADLINE -->
        <div class="form-group">
          <label class="form-label">2. Headline <span class="form-sublabel">(Short professional identity)</span></label>
          <input type="text" id="headline" placeholder="e.g. Full Stack Developer & AI Engineer">
        </div>

        <!-- 3. PROFESSIONAL SUMMARY -->
        <div class="form-group">
          <label class="form-label">3. Professional Summary <span class="form-sublabel">(Concise introduction)</span></label>
          <textarea id="summary" placeholder="e.g. Goal-oriented Full Stack Developer with 3+ years of experience building scalable applications..."></textarea>
        </div>

        <!-- 4. SKILLS -->
        <div class="form-group">
          <label class="form-label">4. Skills <span class="form-sublabel">(Technical & relevant skills, comma separated)</span></label>
          <textarea id="skills" placeholder="e.g. Python, JavaScript, React, HTML5, CSS3, SQL, Docker, Problem Solving"></textarea>
        </div>

        <!-- 5. EDUCATION -->
        <div class="form-group">
          <label class="form-label">5. Education <span class="form-sublabel">(Qualifications, degree, institution, year, grade)</span></label>
          <textarea id="education" placeholder="e.g. B.Tech in Computer Science | GLA University | 2019 - 2023 | Grade: 8.7 CGPA"></textarea>
        </div>

        <!-- 6. EXPERIENCE -->
        <div class="form-group">
          <label class="form-label">6. Experience <span class="form-sublabel">(Internships, job titles, companies, dates & responsibilities)</span></label>
          <textarea id="experience" style="height: 85px;" placeholder="e.g. Software Engineer at TechNova (2024 - Present): Developed real-time analytics dashboard in React & Flask."></textarea>
        </div>

        <!-- 7. PROJECTS -->
        <div class="form-group">
          <label class="form-label">7. Projects <span class="form-sublabel">(Project titles, descriptions & technologies)</span></label>
          <textarea id="projects" style="height: 85px;" placeholder="e.g. AI Resume Portfolio Generator: Python app using Gemini API to parse text into HTML portfolios."></textarea>
        </div>

        <!-- 8. ACHIEVEMENTS -->
        <div class="form-group">
          <label class="form-label">8. Achievements <span class="form-sublabel">(Awards, certifications or notable results)</span></label>
          <textarea id="achievements" placeholder="e.g. AWS Certified Cloud Practitioner (2024), Google AI Fundamentals"></textarea>
        </div>

        <!-- 9. CONTACT AND LINKS -->
        <div class="form-group">
          <label class="form-label">9. Contact and Links <span class="form-sublabel">(Email, phone, location, LinkedIn, GitHub)</span></label>
          <div class="grid-2" style="margin-bottom: 0.5rem;">
            <input type="email" id="email" placeholder="Email: ayush@example.com">
            <input type="text" id="phone" placeholder="Phone: +91 9876543210">
          </div>
          <div class="grid-2">
            <input type="text" id="linkedin" placeholder="LinkedIn: linkedin.com/in/ayushsharma">
            <input type="text" id="github" placeholder="GitHub: github.com/ayushsharma">
          </div>
        </div>

        <button type="submit" class="btn btn-success">✨ Generate Portfolio Webpage (portfolio.html)</button>

      </form>
    </div>

  </div>

  <!-- RIGHT PANEL: PORTFOLIO GENERATION OUTPUT -->
  <div class="card">
    <div class="card-title">🌐 Portfolio Webpage Output</div>

    <div id="loading">
      <div class="spinner"></div>
      <p id="loadingMsg">Generating portfolio content with Gemini API...</p>
    </div>

    <div id="placeholderText" style="color: var(--text-sub); padding: 4rem 1rem; text-align: center; font-size: 0.9rem;">
      Paste your resume or fill the form on the left, then click <strong style="color: var(--cyan);">Generate Portfolio Webpage</strong>.
    </div>

    <div id="resultSection" class="result-section">
      <div style="margin-bottom: 1rem; background: rgba(16, 185, 129, 0.1); border: 1px solid var(--green); padding: 0.75rem; border-radius: 8px;">
        <div style="color: var(--green); font-weight: 700; font-size: 0.85rem;">🎉 SUCCESS! Portfolio Generated</div>
        <h3 id="resCandidateName" style="color: #fff; font-size: 1.15rem; margin-top: 0.2rem;">Candidate Name</h3>
        <p id="resCandidateHeadline" style="color: var(--cyan); font-weight: 600; font-size: 0.88rem;"></p>
      </div>

      <div style="margin-bottom: 1rem;">
        <div style="font-size: 0.78rem; font-weight: 700; color: var(--accent); margin-bottom: 0.4rem;">STRUCTURED 9-SECTION PORTFOLIO DATA:</div>
        <pre id="jsonOutput"></pre>
      </div>

      <div style="font-weight: 700; font-size: 0.82rem; color: var(--text-sub); margin-bottom: 0.4rem;">DOWNLOAD & VIEW OPTIONS:</div>
      <div class="download-grid">
        <a id="previewBtn" href="#" target="_blank" class="btn btn-success">🌐 Open Portfolio</a>
        <a id="downloadHtmlBtn" href="#" download="portfolio.html" class="btn">⬇ Download portfolio.html</a>
        <a id="downloadJsonBtn" href="#" download="portfolio_data.json" class="btn btn-secondary">📄 Download JSON Data</a>
        <button onclick="window.open('/portfolio_preview', '_blank').print()" class="btn btn-secondary">🖨️ Print / Save PDF</button>
      </div>
    </div>
  </div>

</div>

<script>
function switchTab(tabId, btn) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');
}

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (file) {
    document.getElementById('fileName').innerText = file.name;
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById('fullResumeText').value = e.target.result;
    };
    reader.readAsText(file);
  }
}

function loadSampleResume() {
  const sampleText = `Ayush Sharma
Email: ayush.sharma@example.com | Phone: +91 9876543210 | Location: New Delhi, India
LinkedIn: linkedin.com/in/ayushsharma-dev | GitHub: github.com/ayushsharma-code

PROFESSIONAL SUMMARY
Dynamic Full Stack Developer & AI Enthusiast with 3+ years of experience building web applications and intelligent systems using Python, JavaScript, React, Flask, and Gemini API.

SKILLS
Python, JavaScript, React.js, Flask, Node.js, HTML5, CSS3, SQL, Docker, Git, Problem Solving

WORK EXPERIENCE
Software Engineer | TechNova Solutions, New Delhi (June 2024 - Present)
- Developed real-time web applications using React and Flask, increasing client user engagement by 35%.
- Integrated Google Gemini API into customer support workflows.

PROJECTS
AI-Assisted Resume Portfolio Generator
- Developed a Python application using Gemini API to convert plain text resumes into responsive HTML portfolio webpages.

EDUCATION
Bachelor of Technology (B.Tech) in Computer Science | GLA University (2019 - 2023) | CGPA: 8.7/10

ACHIEVEMENTS
AWS Certified Cloud Practitioner, Google AI Foundations Certification`;
  
  document.getElementById('fullResumeText').value = sampleText;
  document.getElementById('fileName').innerText = "Sample Resume Loaded";
}

async function generateFromFullText() {
  const text = document.getElementById('fullResumeText').value;
  if (!text || text.trim().length < 20) {
    alert("Please enter resume text or click 'Load Sample Resume'.");
    return;
  }

  showLoading("Analyzing resume text with Gemini API...");

  try {
    const res = await fetch('/api/parse_text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: text })
    });
    const data = await res.json();
    
    if (!data.success) {
      hideLoading();
      alert("Error: " + data.error);
      return;
    }

    const d = data.data;
    // Auto-fill sections tab fields
    document.getElementById('name').value = d.name || "";
    document.getElementById('headline').value = d.headline || "";
    document.getElementById('summary').value = d.summary || "";
    
    const tech = (d.skills && d.skills.technical_skills) ? d.skills.technical_skills.join(", ") : "";
    const rel = (d.skills && d.skills.relevant_skills) ? d.skills.relevant_skills.join(", ") : "";
    document.getElementById('skills').value = [tech, rel].filter(Boolean).join(", ");

    if (d.education && d.education.length > 0) {
      document.getElementById('education').value = d.education.map(e => `${e.degree || ''} | ${e.institution || ''} (${e.year || ''})`).join("\\n");
    }

    if (d.experience && d.experience.length > 0) {
      document.getElementById('experience').value = d.experience.map(e => `${e.title || ''} at ${e.company || ''} (${e.dates || ''}): ${(e.responsibilities || []).join('; ')}`).join("\\n");
    }

    if (d.projects && d.projects.length > 0) {
      document.getElementById('projects').value = d.projects.map(p => `${p.title || ''}: ${p.description || ''}`).join("\\n");
    }

    if (d.achievements && d.achievements.length > 0) {
      document.getElementById('achievements').value = d.achievements.join(", ");
    }

    if (d.contact_and_links) {
      document.getElementById('email').value = d.contact_and_links.email || "";
      document.getElementById('phone').value = d.contact_and_links.phone || "";
      document.getElementById('linkedin').value = d.contact_and_links.linkedin || "";
      document.getElementById('github').value = d.contact_and_links.github || "";
    }

    displayResults(d);

  } catch (err) {
    hideLoading();
    alert("Generation failed: " + err.message);
  }
}

async function submitDirectPortfolio() {
  const payload = {
    name: document.getElementById('name').value,
    headline: document.getElementById('headline').value,
    summary: document.getElementById('summary').value,
    skills_raw: document.getElementById('skills').value,
    education_raw: document.getElementById('education').value,
    experience_raw: document.getElementById('experience').value,
    projects_raw: document.getElementById('projects').value,
    achievements_raw: document.getElementById('achievements').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    linkedin: document.getElementById('linkedin').value,
    github: document.getElementById('github').value
  };

  showLoading("Building portfolio.html from your 9 section inputs...");

  try {
    const res = await fetch('/api/generate_direct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    hideLoading();

    if (!data.success) {
      alert("Error: " + data.error);
      return;
    }

    displayResults(data.data);
  } catch (err) {
    hideLoading();
    alert("Generation failed: " + err.message);
  }
}

function showLoading(msg) {
  document.getElementById('placeholderText').style.display = 'none';
  document.getElementById('resultSection').style.display = 'none';
  document.getElementById('loadingMsg').innerText = msg;
  document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('placeholderText').style.display = 'block';
}

function displayResults(json) {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('resCandidateName').innerText = json.name || "Candidate Name";
  document.getElementById('resCandidateHeadline').innerText = json.headline || "Professional Headline";
  document.getElementById('jsonOutput').innerText = JSON.stringify(json, null, 2);

  document.getElementById('previewBtn').href = '/portfolio_preview';
  document.getElementById('downloadHtmlBtn').href = '/download_portfolio';
  document.getElementById('downloadJsonBtn').href = '/download_json';

  document.getElementById('resultSection').style.display = 'block';
}
</script>

</body>
</html>
"""

latest_portfolio_cache = None
latest_html_cache = ""

@app.route("/")
def home():
    return render_template_string(WEB_UI_HTML)

@app.route("/api/parse_text", methods=["POST"])
def api_parse_text():
    global latest_portfolio_cache, latest_html_cache
    try:
        req_data = request.get_json()
        raw_text = req_data.get("resume_text", "")
        cleaned = clean_resume_text(raw_text)
        validate_resume_text(cleaned)
        
        portfolio_data = analyze_resume_with_gemini(cleaned)
        latest_portfolio_cache = portfolio_data
        portfolio_html = generate_portfolio_html( portfolio_data, output_path="portfolio.html")
        
        return jsonify({"success": True, "data": portfolio_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/generate_direct", methods=["POST"])
def api_generate_direct():
    global latest_portfolio_cache, latest_html_cache
    try:
        p = request.get_json()
        
        skills_list = [s.strip() for s in p.get("skills_raw", "").split(",") if s.strip()]
        
        edu_lines = [l.strip() for l in p.get("education_raw", "").split("\n") if l.strip()]
        education_list = []
        for line in edu_lines:
            parts = line.split("|")
            degree = parts[0].strip() if len(parts) > 0 else line
            institution = parts[1].strip() if len(parts) > 1 else ""
            year = parts[2].strip() if len(parts) > 2 else ""
            grade = parts[3].strip() if len(parts) > 3 else ""
            education_list.append({"degree": degree, "institution": institution, "year": year, "grade": grade})

        exp_lines = [l.strip() for l in p.get("experience_raw", "").split("\n") if l.strip()]
        experience_list = []
        for line in exp_lines:
            experience_list.append({
                "title": line,
                "company": "",
                "dates": "",
                "responsibilities": []
            })

        proj_lines = [l.strip() for l in p.get("projects_raw", "").split("\n") if l.strip()]
        projects_list = []
        for line in proj_lines:
            projects_list.append({
                "title": line,
                "description": "",
                "technologies": [],
                "link": ""
            })

        ach_list = [a.strip() for a in p.get("achievements_raw", "").split(",") if a.strip()]

        portfolio_data = {
            "name": p.get("name", "Candidate Name"),
            "headline": p.get("headline", "Professional Identity"),
            "summary": p.get("summary", ""),
            "skills": {
                "technical_skills": skills_list,
                "relevant_skills": []
            },
            "experience": experience_list if experience_list else [],
            "projects": projects_list if projects_list else [],
            "education": education_list if education_list else [],
            "achievements": ach_list if ach_list else [],
            "contact_and_links": {
                "email": p.get("email", ""),
                "phone": p.get("phone", ""),
                "location": "",
                "linkedin": p.get("linkedin", ""),
                "github": p.get("github", ""),
                "website": ""
            }
        }
        
        latest_portfolio_cache = portfolio_data
        latest_html_cache = generate_portfolio_html(portfolio_data, output_path="portfolio.html")
        
        return jsonify({"success": True, "data": portfolio_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/portfolio_preview")
def portfolio_preview():
    global latest_html_cache
    if not latest_html_cache and os.path.exists("portfolio.html"):
        with open("portfolio.html", "r", encoding="utf-8") as f:
            latest_html_cache = f.read()
    if not latest_html_cache:
        return "No portfolio generated yet.", 404
    return Response(latest_html_cache, mimetype="text/html")

@app.route("/download_portfolio")
def download_portfolio():
    if os.path.exists("portfolio.html"):
        return send_file("portfolio.html", as_attachment=True, download_name="portfolio.html")
    return "Portfolio file not found.", 404

@app.route("/download_json")
def download_json():
    global latest_portfolio_cache
    if latest_portfolio_cache:
        return Response(
            json.dumps(latest_portfolio_cache, indent=2),
            mimetype="application/json",
            headers={"Content-disposition": "attachment; filename=portfolio_data.json"}
        )
    return "No portfolio data found.", 404

if __name__ == "__main__":
    import sys
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("\nStarting AI-Assisted Resume Portfolio Generator on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False,use_reloader=False)
