import os
import re

MIN_CHARACTER_LIMIT = 50
MIN_WORD_LIMIT = 10

class ResumeValidationError(Exception):
    """Custom exception raised when resume text fails validation."""
    pass

def read_resume_file(file_path="resume.txt"):
    """
    Reads resume content from a plain text file.
    
    Args:
        file_path (str): Path to the resume text file.
        
    Returns:
        str: Raw text content from the file.
        
    Raises:
        ResumeValidationError: If file does not exist or cannot be read.
    """
    if not os.path.exists(file_path):
        raise ResumeValidationError(
            f"Resume file '{file_path}' was not found. Please ensure 'resume.txt' exists in the working directory."
        )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        raise ResumeValidationError(f"Failed to read file '{file_path}': {str(e)}")

def clean_resume_text(raw_text):
    """
    Cleans raw resume text by removing redundant blank lines, excess spaces,
    and tab characters before passing to the AI model.
    
    Args:
        raw_text (str): Raw input text.
        
    Returns:
        str: Cleaned text.
    """
    if not raw_text:
        return ""
        
    # Standardize newlines
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Replace multiple spaces/tabs with single space on each line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    
    # Remove consecutive empty lines (keep single empty lines as section separators)
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line == "":
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
            
    return "\n".join(cleaned_lines).strip()

def validate_resume_text(text):
    """
    Validates cleaned resume text to ensure it is non-empty and meets minimum length criteria.
    
    Args:
        text (str): Cleaned resume text.
        
    Returns:
        bool: True if valid.
        
    Raises:
        ResumeValidationError: If validation criteria fail.
    """
    if not text or not text.strip():
        raise ResumeValidationError("Resume input is empty. Please provide valid text or text file content.")
        
    cleaned = text.strip()
    words = cleaned.split()
    
    if len(cleaned) < MIN_CHARACTER_LIMIT:
        raise ResumeValidationError(
            f"Resume content is too short ({len(cleaned)} chars). Minimum required is {MIN_CHARACTER_LIMIT} characters."
        )
        
    if len(words) < MIN_WORD_LIMIT:
        raise ResumeValidationError(
            f"Resume content has too few words ({len(words)} words). Minimum required is {MIN_WORD_LIMIT} words."
        )
        
    return True

def prepare_resume_data(file_path_or_text):
    """
    Convenience loader: accepts either a file path or raw text, cleans it, and validates it.
    
    Args:
        file_path_or_text (str): File path or direct string text.
        
    Returns:
        str: Cleaned and validated resume text.
    """
    if os.path.exists(file_path_or_text) and os.path.isfile(file_path_or_text):
        raw = read_resume_file(file_path_or_text)
    else:
        raw = file_path_or_text
        
    cleaned = clean_resume_text(raw)
    validate_resume_text(cleaned)
    return cleaned
