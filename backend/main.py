# import the inference-sdk
from inference_sdk import InferenceHTTPClient
import os
from dotenv import load_dotenv

load_dotenv()

# initialize the client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# infer on a local image
result = CLIENT.infer("cookie.jpg", model_id="snack-detection-ypprq/2")
print(result)
