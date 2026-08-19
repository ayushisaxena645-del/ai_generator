import streamlit as st
import tempfile
import os

from resume_cleaner import prepare_resume_data, ResumeValidationError
from gemini_analyzer import analyze_resume_with_gemini
from portfolio_builder import generate_portfolio_html

st.set_page_config(
    page_title="AI Resume Portfolio Generator",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI-Assisted Resume Portfolio Generator")
st.write("Upload your resume and generate your AI-powered portfolio.")

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["txt"]
)

if uploaded_file is not None:

    if st.button("🚀 Generate Portfolio"):

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".txt",
            mode="wb"
        ) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name

        try:
            with st.spinner("Analyzing your resume with Gemini AI..."):

                cleaned_text = prepare_resume_data(temp_path)

                portfolio_data = analyze_resume_with_gemini(
                    cleaned_text
                )

                generate_portfolio_html(
                    portfolio_data,
                    output_path="portfolio.html"
                )

            st.success("🎉 Portfolio generated successfully!")

            st.subheader("Portfolio Details")

            st.write(
                "**Name:**",
                portfolio_data.get("name", "N/A")
            )

            st.write(
                "**Headline:**",
                portfolio_data.get("headline", "N/A")
            )

            st.write(
                "**Summary:**",
                portfolio_data.get("summary", "N/A")
            )

            if os.path.exists("portfolio.html"):
                with open("portfolio.html", "r", encoding="utf-8") as f:
                    html = f.read()

                st.components.v1.html(
                    html,
                    height=800,
                    scrolling=True
                )

        except ResumeValidationError as e:
            st.error(f"Resume validation failed: {e}")

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
