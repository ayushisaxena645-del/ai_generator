import sys
import os
import json
from resume_cleaner import prepare_resume_data, ResumeValidationError
from gemini_analyzer import analyze_resume_with_gemini
from portfolio_builder import generate_portfolio_html

def main():
    print("=" * 60)
    print("        AI-ASSISTED RESUME PORTFOLIO GENERATOR          ")
    print("=" * 60)

    # 1. Determine input file
    input_source = "resume.txt"
    if len(sys.argv) > 1:
        input_source = sys.argv[1]

    print(f"\n[STEP 1] Reading and validating text file: {input_source}")
    try:
        cleaned_text = prepare_resume_data(input_source)
        print(f"[SUCCESS] Resume text sanitized ({len(cleaned_text)} characters).")
    except ResumeValidationError as e:
        print(f"\n[ERROR] Resume Validation Failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error reading file: {str(e)}")
        sys.exit(1)

    # 2. Extract portfolio content using Gemini AI
    print("\n[STEP 2] Sending resume content to Gemini API...")
    portfolio_data = analyze_resume_with_gemini(cleaned_text)

    # Set UTF-8 encoding for Windows terminal output
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "-" * 60)
    print("               PORTFOLIO CONTENT GENERATED               ")
    print("-" * 60)
    print(f" Name        : {portfolio_data.get('name', 'N/A')}")
    print(f" Headline    : {portfolio_data.get('headline', 'N/A')}")
    print(f" Summary     : {portfolio_data.get('summary', 'N/A')[:80]}...")
    print("-" * 60)

    # 3. Export JSON data
    json_path = "portfolio_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(portfolio_data, f, indent=2)
    print(f"\n[STEP 3] Saved structured portfolio JSON data to: {os.path.abspath(json_path)}")

    # 4. Generate portfolio.html
    print("\n[STEP 4] Generating portfolio webpage (portfolio.html)...")
    try:
        output_file = "portfolio.html"
        generate_portfolio_html(portfolio_data, output_path=output_file)
        print(f"\n✨ SUCCESS! Created portfolio webpage:")
        print(f"   file:///{os.path.abspath(output_file).replace('\\', '/')}")
    except Exception as e:
        print(f"[ERROR] Portfolio HTML generation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
