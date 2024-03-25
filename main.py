from src.connections.connection import upload_to_s3, extract_text_json, save_uploaded_file, insertToMongo
import streamlit as st
from random import randint
from pdf2image import convert_from_path

AWS_BUCKET = 'fua-filestorage'

def convert_pdf_to_images(pdf_file):
    image = convert_from_path(pdf_file)[0]
    value = randint(0, 100000)
    image_file = f"image_{value}.jpg"
    image.save(image_file)
    return (image, image_file)

def init_session_state():
    session_state = st.session_state
    if not hasattr(session_state, "extracted_text"):
        session_state.extracted_text = ""

def main():
    st.title("DataExtractor Pro")
    
    init_session_state()


    # Step 1: File Upload
    st.header("Step 1: File Upload")
    file = st.file_uploader("Upload file", type=["pdf", "png"])
    if file:
        if file.type == 'application/pdf':
            file_name = save_uploaded_file(file)
            [image, image_file] = convert_pdf_to_images(file_name)
            
            st.image(image, caption='Image Uploaded Sucessfully!')

            if st.button("Next Step"):
                st.success("Proceed to Next Steps")
        elif file.type.startswith('image/'):
            st.image(file, caption='Uploaded Image')
            image_file = save_uploaded_file(file)
            
    # Step 2: Hit API
    st.header("Step 2: Extract Text From File")
    if st.button("Click to Extract Text"):
        extracted_text = extract_text_json(image_path=image_file)
        if extracted_text:
            st.session_state.extracted_text = extracted_text
            st.text_area("Extracted Text", extracted_text, height=250)

        proceed_option = st.radio(
            "Do you want to upload the extracted text or reload the image?",
            ('Yes, upload', 'No, reload the image'))

        if proceed_option == 'Yes, upload':
            st.success("Proceeding to upload extracted text...")
        elif proceed_option == 'No, reload the image':
            st.warning("Please reload the image.")
            
    else:
        st.info("Click the button above to extract text from your image.")

    # Step 3: Upload to S3 and save to MongoDB
    st.header("Step 3: Upload File to Database")
    if st.button("Upload and Save"):
            uploaded = upload_to_s3(file_path=image_file, bucket_name=AWS_BUCKET, object_name=image_file)
            if uploaded:
                st.success("Image uploaded to S3.")
                extracted_text = st.session_state.extracted_text
                json_payload = {
                    "fileUrl": f'https://fua-filestorage.s3.eu-west-2.amazonaws.com/{image_file}',
                    "extractedText": extracted_text
                }
                insertToMongo(json_document=json_payload)

if __name__ == "__main__":
    main()

