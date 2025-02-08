import os
import vertexai

from vertexai.generative_models import GenerativeModel, Part
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")

vertexai.init(project=PROJECT_ID, location="us-central1")

vision_model = GenerativeModel("gemini-2.0-flash-001")

# Generate text
# response = vision_model.generate_content(
#     [
#         Part.from_uri(
#             "gs://cloud-samples-data/video/animals.mp4", mime_type="video/mp4"
#         ),
#         """You are a fraud detection expert. Your task is to:
#         1) Extract important details like bank account information to help next steps in verification that the user made the right transfer to the right account.
#         2) Analyse the behaviours and actions of the individual in the video to detect any suspicious activity.
#         3) Respond concisely with the required information from the video.""",
#     ]
# )

def analyze_video(gcs_uri: str):
    response = vision_model.generate_content(
        [
            Part.from_uri(gcs_uri, mime_type="video/mp4"),
            """You are a fraud detection expert. Your task is to:
        1) Extract important details like bank account information to help next steps in verification that the user made the right transfer to the right account.
        2) Analyse the behaviours and actions of the individual in the video to detect any suspicious activity.
        3) Respond concisely with the required information from the video.""",
        ]
    )
    return response.text

if __name__ == "__main__":
    # For testing: replace with the URI returned from your upload endpoint.
    gcs_uri = "gs://your-bucket-name/uploads/videos/animals.mp4"
    analysis = analyze_video(gcs_uri)
    print(analysis)

