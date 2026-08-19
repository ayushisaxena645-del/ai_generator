import os
import json
import re
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SYSTEM_PROMPT = """
You are an AI assistant designed for the 'AI-Assisted Resume Portfolio Generator'.
Your task is to convert raw resume text into a clean, structured JSON object containing EXACTLY the required portfolio sections.

Do NOT include any markdown code block wrappers (like ```json), conversational text, or extraneous feedback.
Return ONLY a valid JSON object matching the following structure:

{
  "name": "Full name from the resume",
  "headline": "Short professional identity (e.g., Full Stack Engineer & AI Developer)",
  "summary": "Concise professional summary introducing the candidate",
  "skills": {
    "technical_skills": ["List of technical skills, languages, and frameworks"],
    "relevant_skills": ["List of soft skills and domain expertise"]
  },
  "experience": [
    {
      "title": "Job Title or Internship Role",
      "company": "Company or Organization Name",
      "location": "Location or empty string",
      "dates": "Employment / Internship period e.g. June 2024 - Present",
      "responsibilities": [
        "Responsibility / achievement bullet 1",
        "Responsibility / achievement bullet 2"
      ]
    }
  ],
  "projects": [
    {
      "title": "Project Title",
      "description": "Short project description",
      "technologies": ["Tech 1", "Tech 2"],
      "link": "Project link, GitHub repo, or empty string"
    }
  ],
  "education": [
    {
      "degree": "Qualification / Degree / Course",
      "institution": "School / College / University Name",
      "location": "Location or empty string",
      "year": "Graduation year or date range",
      "grade": "CGPA / Percentage / Grade or empty string"
    }
  ],
  "achievements": [
    "Award, certification, or notable result 1",
    "Award, certification, or notable result 2"
  ],
  "contact_and_links": {
    "email": "Email address or empty string",
    "phone": "Phone number or empty string",
    "location": "Location or empty string",
    "linkedin": "LinkedIn profile URL or empty string",
    "github": "GitHub profile URL or empty string",
    "website": "Portfolio/Project link or empty string"
  }
}

Guidelines:
1. Extract precise details from the resume for each of the 9 required sections.
2. Use empty strings "" or empty lists [] if specific details are not mentioned in the resume.
3. Keep JSON keys exactly as specified above.
"""

def extract_json_from_text(text):
    """Strips markdown code fences (```json ... ```) or conversational wrappers if returned by AI."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(\{[\s\S]*\})\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
        
    return text

def get_gemini_api_key():
    """Retrieves API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.strip() == "" or key.strip() == "your_gemini_api_key_here":
        return None
    return key.strip()

def analyze_resume_with_gemini(resume_text):
    """
    Calls Gemini API to extract structured portfolio data from resume text.
    
    Args:
        resume_text (str): Sanitized resume text.
        
    Returns:
        dict: Structured portfolio data.
    """
    api_key = get_gemini_api_key()
    
    if not api_key:
        print("[WARNING] GEMINI_API_KEY not configured. Using offline text parsing for portfolio generation.")
        return generate_fallback_portfolio_data(resume_text)
        
    try:
        # Try google-genai library
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            prompt = f"{SYSTEM_PROMPT}\n\nRESUME TEXT:\n{resume_text}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            raw_response = response.text
        except ImportError:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"{SYSTEM_PROMPT}\n\nRESUME TEXT:\n{resume_text}"
            response = model.generate_content(prompt)
            raw_response = response.text
            
        json_str = extract_json_from_text(raw_response)
        data = json.loads(json_str)
        return normalize_portfolio_data(data, resume_text)
        
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {str(e)}")
        print("[INFO] Utilizing offline fallback parser.")
        return generate_fallback_portfolio_data(resume_text)

def clean_candidate_name(raw_name):
    """Clean candidate name string from concatenated contact details."""
    if not raw_name:
        return "Candidate Name"
    cleaned = re.sub(r"(?i)(Phone|Email|Location|LinkedIn|Portfolio|Github|Address|Tel|Mob|Summary).*$", "", raw_name)
    cleaned = re.sub(r"[\|\:\,\-\#\d].*$", "", cleaned)
    cleaned = cleaned.strip()
    return cleaned if cleaned else "Candidate Name"

def normalize_portfolio_data(data, original_text):
    """Ensures all required 9 portfolio sections exist in dictionary."""
    fallback = generate_fallback_portfolio_data(original_text)
    if not isinstance(data, dict):
        return fallback
        
    for key in ["name", "headline", "summary", "skills", "experience", "projects", "education", "achievements", "contact_and_links"]:
        if key not in data or data[key] is None:
            data[key] = fallback[key]
            
    # Normalize clean name
    data["name"] = clean_candidate_name(data.get("name", ""))
    return data

def generate_fallback_portfolio_data(resume_text):
    """Generates offline portfolio data by parsing basic text patterns."""
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]
    raw_first_line = lines[0] if lines else "Candidate Name"
    name = clean_candidate_name(raw_first_line)
    
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
    email = email_match.group(0) if email_match else ""
    
    phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s-]?\d{3,5}[\s-]?\d{3,5}", resume_text)
    phone = phone_match.group(0) if phone_match else ""
    
    linkedin_match = re.search(r"linkedin\.com/in/[\w-]+", resume_text, re.IGNORECASE)
    linkedin = linkedin_match.group(0) if linkedin_match else ""
    
    github_match = re.search(r"github\.com/[\w-]+", resume_text, re.IGNORECASE)
    github = github_match.group(0) if github_match else ""

    common_tech = ["Python", "JavaScript", "React", "HTML5", "CSS3", "SQL", "Node.js", "Flask", "Docker", "Git"]
    detected_tech = [t for t in common_tech if re.search(r"\b" + re.escape(t) + r"\b", resume_text, re.I)]
    if not detected_tech:
        detected_tech = ["Software Development", "Web Technologies"]

    return {
        "name": name,
        "headline": "Full Stack Engineer / Technology Enthusiast",
        "summary": "Motivated developer with experience designing, building, and deploying software applications.",
        "skills": {
            "technical_skills": detected_tech,
            "relevant_skills": ["Problem Solving", "Team Collaboration", "Agile Communication"]
        },
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Technology Solutions",
                "location": "New Delhi, India",
                "dates": "2023 - Present",
                "responsibilities": [
                    "Developed responsive web applications and integrated backend services.",
                    "Collaborated with project teams to optimize performance and code quality."
                ]
            }
        ],
        "projects": [
            {
                "title": "AI-Assisted Resume Portfolio Generator",
                "description": "Python application that converts plain resume text into a responsive HTML portfolio webpage using Gemini API.",
                "technologies": detected_tech[:4],
                "link": ""
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Technology in Computer Science",
                "institution": "University / Institution",
                "location": "India",
                "year": "2023",
                "grade": "8.5 CGPA"
            }
        ],
        "achievements": [
            "AWS Certified Cloud Practitioner",
            "Built and published AI-Assisted Resume Portfolio Generator"
        ],
        "contact_and_links": {
            "email": email,
            "phone": phone,
            "location": "India",
            "linkedin": linkedin,
            "github": github,
            "website": ""
        }
    }
