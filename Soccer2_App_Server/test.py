
import base64
import json

import functions_framework

from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import translate_v2 as translate
from google.cloud import vision

vision_client = vision.ImageAnnotatorClient()

project_id = os.environ.get("GCP_PROJECT")

image = vision.Image(
    source=vision.ImageSource(gcs_image_uri=f"gs://{bucket}/{filename}")
)
text_detection_response = vision_client.text_detection(image=image)
