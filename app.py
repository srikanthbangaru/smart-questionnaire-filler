# app.py

import re
import streamlit as st
from io import BytesIO
from docx import Document

# Sample Pre-loaded Answers based on Section/Category
preloaded_answers = {
    "General Info": {
        "full name": "ABC Industrial Services",
        "established since": "March 1998",
        "street address": "123 Main Street, Houston, TX",
        "country": "USA",
        "telephone": "(123) 456-7890",
        "fax": "(123) 456-7891",
        "bank relations": "First National Bank"
    },
    "Financial": {
        "turnover": "$45 Million",
        "line of credit": "Yes, $5 Million available",
        "bondable": "Yes, backed by Surety"
    },
    "QA": {
        "iso9001 certified": "Yes",
        "quality manager": "John Smith, 15 years experience"
    },
    "HSE": {
        "hse plan": "Attached HSE Plan v2024",
        "emr rating": "0.72"
    }
}

# Function to predict section based on keywords
def predict_section(text):
    text = text.lower()
    if any(keyword in text for keyword in ["financial", "revenue", "turnover", "credit", "bond"]):
        return "Financial"
    elif any(keyword in text for keyword in ["quality", "iso", "qa"]):
        return "QA"
    elif any(keyword in text for keyword in ["hse", "safety", "environmental"]):
        return "HSE"
    else:
        return "General Info"

# Function to find best answer match
def find_best_answer(section, question_text):
    section_answers = preloaded_answers.get(section, {})
    for key, answer in section_answers.items():
        if key in question_text.lower():
            return answer
    return "[Answer Needed]"

# Streamlit Web App
st.title("📄 Smart Questionnaire Auto-Filler with Review (Preserve Format + Tables)")

uploaded_file = st.file_uploader("Upload a DOCX file", type=["docx"])

if uploaded_file is not None:
    original_doc = Document(uploaded_file)

    st.write("### Review AI-Suggested Answers")
    reviewed_answers = {}
    extracted_questions = []

    # Scan paragraphs for questions
    for para in original_doc.paragraphs:
        text = para.text.strip()
        if text and ":" in text:
            question_part = text.split(":")[0]
            section = predict_section(text)
            suggested_answer = find_best_answer(section, question_part)
            extracted_questions.append((para, question_part, suggested_answer))

    # Scan tables for questions
    for table in original_doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text and ":" in text:
                    question_part = text.split(":")[0]
                    section = predict_section(text)
                    suggested_answer = find_best_answer(section, question_part)
                    extracted_questions.append((cell, question_part, suggested_answer))

    for idx, (container, question, suggested_answer) in enumerate(extracted_questions):
        user_answer = st.text_input(f"{question}", value=suggested_answer, key=f"q{idx}")
        reviewed_answers[question] = user_answer

    if st.button("Download Final Filled Questionnaire"):
        # Modify document
        for container, question, _ in extracted_questions:
            if question in reviewed_answers:
                parts = container.text.split(":")
                container.text = f"{parts[0]}: {reviewed_answers[question]}"

        buffer = BytesIO()
        original_doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="Download Filled Questionnaire",
            data=buffer,
            file_name="Filled_Questionnaire.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# requirements.txt

# streamlit
# python-docx
