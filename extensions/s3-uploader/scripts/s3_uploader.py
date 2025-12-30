
import gradio as gr
import modules.scripts as scripts
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
import logging
from modules.script_callbacks import on_image_saved, ImageSaveParams

logging.basicConfig(level=logging.INFO)

class S3UploaderScript(scripts.Script):
    def __init__(self):
        super().__init__()
        self.s3_enabled = False
        self.s3_endpoint_url = ""
        self.s3_access_key_id = ""
        self.s3_secret_access_key = ""
        self.s3_bucket_name = ""
        self.s3_region_name = ""
        on_image_saved(self.on_image_saved_callback)

    def title(self):
        return "S3 Uploader"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("S3 Uploader", open=False):
            s3_enabled = gr.Checkbox(label="Enable S3 Upload", value=False)
            s3_endpoint_url = gr.Textbox(label="S3 Endpoint URL (e.g., https://s3.amazonaws.com)", placeholder="e.g., https://s3.digitalocean.com")
            s3_access_key_id = gr.Textbox(label="S3 Access Key ID", type="password")
            s3_secret_access_key = gr.Textbox(label="S3 Secret Access Key", type="password")
            s3_bucket_name = gr.Textbox(label="S3 Bucket Name")
            s3_region_name = gr.Textbox(label="S3 Region Name (optional)")

        return [s3_enabled, s3_endpoint_url, s3_access_key_id, s3_secret_access_key, s3_bucket_name, s3_region_name]

    def postprocess(self, p, processed, s3_enabled, s3_endpoint_url, s3_access_key_id, s3_secret_access_key, s3_bucket_name, s3_region_name):
        self.s3_enabled = s3_enabled
        self.s3_endpoint_url = s3_endpoint_url
        self.s3_access_key_id = s3_access_key_id
        self.s3_secret_access_key = s3_secret_access_key
        self.s3_bucket_name = s3_bucket_name
        self.s3_region_name = s3_region_name

    def on_image_saved_callback(self, params: ImageSaveParams):
        if not self.s3_enabled:
            return

        if not all([self.s3_endpoint_url, self.s3_access_key_id, self.s3_secret_access_key, self.s3_bucket_name]):
            logging.warning("S3 Uploader: Missing one or more required S3 configuration fields.")
            return

        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=self.s3_endpoint_url,
                aws_access_key_id=self.s3_access_key_id,
                aws_secret_access_key=self.s3_secret_access_key,
                region_name=self.s3_region_name if self.s3_region_name else None
            )
        except Exception as e:
            logging.error(f"S3 Uploader: Error creating S3 client: {e}")
            return

        image_path = params.filename
        image_name = os.path.basename(image_path)

        try:
            s3_client.upload_file(image_path, self.s3_bucket_name, image_name)
            logging.info(f"S3 Uploader: Successfully uploaded {image_name} to {self.s3_bucket_name}")
        except NoCredentialsError:
            logging.error("S3 Uploader: Credentials not available.")
        except ClientError as e:
            logging.error(f"S3 Uploader: An error occurred: {e}")
        except Exception as e:
            logging.error(f"S3 Uploader: An unexpected error occurred: {e}")
