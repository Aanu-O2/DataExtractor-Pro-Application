from pymongo.mongo_client import MongoClient
import boto3
import base64
import requests
from openai import OpenAI
import os
import requests
import json

AWS_KEY = "AKIATWM3QQCHNRQEIRWT"
AWS_SECRET_KEY = "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"
AWS_REGION = "eu-west-2"
api_key = "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"

def insertToMongo(json_document):
    url = "https://ap-south-1.aws.data.mongodb-api.com/app/data-ygjjn/endpoint/data/v1/action/insertOne"

    payload = json.dumps({
    "collection": "text_data",
    "database": "textExtractor",
    "dataSource": "textExtractor",
    "document": json_document
    })
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Request-Headers': '*',
        'api-key': 'T21nYGzO87xEWVskiZ1X2xbXMByN1ufvF2qldJVAXEnvbhbdSeMuR7lDepvNHmTo',
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response)
    return response


def upload_to_s3(file_path, bucket_name, object_name):
    print(file_path, object_name)
    s3_client = boto3.client(
        "s3", aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        # Upload file
        s3_client.upload_file(file_path, bucket_name, object_name)
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_text_json(image_path):
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the Text from the image in format of Json, return only Json not other text",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    text = response.choices[0].message.content.replace("```json\n", "").replace("\n```", "")
    return text

def save_uploaded_file(uploaded_file):
    # Save the uploaded file to a temporary location
    if uploaded_file is not None:
        with open(os.path.join("", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join("", uploaded_file.name)
    return None
