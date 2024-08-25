import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the API key
genai.configure(api_key=api_key)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to ask a question to the generative AI
def ask_question_to_ai(question, document_text):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content([document_text, question])
    return response.text

# Function to upload an image and generate content
def upload_image_and_generate_content(uploaded_file, prompt):
    # Save the uploaded image to a temporary file
    temp_file_path = f"temp_{uploaded_file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Upload image to Gemini and generate content
    sample_file = genai.upload_file(path=temp_file_path, display_name=uploaded_file.name)
    response = genai.GenerativeModel(model_name="gemini-1.5-flash").generate_content([prompt, sample_file])
    
    # Delete the temporary file
    os.remove(temp_file_path)
    
    return sample_file.display_name, response.text

# Streamlit app layout
st.title("Generative AI with Google Gemini")

# Sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose Feature", ["PDF Question Answering", "Image Upload and Content Generation"])

if option == "PDF Question Answering":
    st.header("PDF Question Answering")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        st.write("File uploaded successfully. Extracting text...")
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.write("Text extracted. You can now ask questions about the content.")
        
        question = st.text_input("Ask a question about the PDF")
        
        if st.button("Submit"):
            if question:
                with st.spinner("Getting the answer..."):
                    answer = ask_question_to_ai(question, pdf_text)
                    st.write(f"**Answer:** {answer}")
            else:
                st.warning("Please enter a question.")
    
elif option == "Image Upload and Content Generation":
    st.header("Image Upload and Content Generation")
    uploaded_file = st.file_uploader("Choose an image to upload", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        # Content Generation
        prompt = st.text_area("Enter a prompt to describe the uploaded image:")
        
        if st.button("Generate Content"):
            if prompt:
                with st.spinner("Generating content..."):
                    display_name, response_text = upload_image_and_generate_content(uploaded_file, prompt)
                    st.write(f"**Uploaded file**: {display_name}")
                    st.write(f"**Generated Content:** {response_text}")
            else:
                st.warning("Please enter a prompt to generate content.")

        # Drop if exist the uploaded image
        if os.path.exists(uploaded_file.name):
            os.remove(uploaded_file.name)