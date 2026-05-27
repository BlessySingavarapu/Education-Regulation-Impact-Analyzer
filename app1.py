import streamlit as st
#import read_pdf
#import extract_text_from_url
#import clean_text
#import split_text
#import generate_analysis
#import detect_stakeholders

st.set_page_config(page_title="ERIA", layout="wide")

st.title("📘 ERIA - Education Regulation Analyzer")

option = st.radio("Choose Input Type", ["PDF", "URL"])

text = ""

# 📥 Input handling

import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")
    text = " ".join([p.get_text() for p in paragraphs])

    return text

import PyPDF2

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    return text

import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9., ]', '', text)
    return text
import google.generativeai as genai

genai.configure(api_key="AIzaSyBkR8N2U6_Io3zBXuuwZlF6r0wJ_JgoY1M")

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_analysis(text):

    prompt = f"""
    You are an education policy expert.

    Analyze the regulation and provide:

    1. Simple Summary (easy language)
    2. Purpose of regulation
    3. Stakeholders affected
    4. Short-term impact
    5. Medium-term impact
    6. Long-term impact
    7. Risks & challenges

    Text:
    {text}
    """

    response = model.generate_content(prompt)
    return response.text

def detect_stakeholders(text):
    stakeholders = []

    if "student" in text:
        stakeholders.append("Students")
    if "faculty" in text:
        stakeholders.append("Faculty")
    if "university" in text:
        stakeholders.append("Universities")
    if "college" in text:
        stakeholders.append("Colleges")

    return stakeholders

def split_text(text, chunk_size=2000):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])

    return chunks

if option == "PDF":
    file = st.file_uploader("Upload PDF", type="pdf")
    if file:
        text = read_pdf(file)

elif option == "URL":
    url = st.text_input("Enter URL")
    if url:
        text = extract_text_from_url(url)

# 🚀 Processing
if text:
    st.info("Processing document...")

    clean = clean_text(text)
    chunks = split_text(clean)

    final_output = ""

    for chunk in chunks[:2]:  # limit for demo
        result = generate_analysis(chunk)
        final_output += result + "\n\n"
        time.sleep(60)  # wait 60 seconds before next request

    stakeholders = detect_stakeholders(clean)

    st.success("Analysis Complete ✅")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 AI Analysis")
        st.write(final_output)

    with col2:
        st.subheader("👥 Stakeholders")
        st.write(stakeholders)
