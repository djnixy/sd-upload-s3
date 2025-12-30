
import gradio as gr
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
import logging
from modules import shared, scripts
from modules.script_callbacks import on_ui_settings, on_image_saved, ImageSaveParams

logging.basicConfig(level=logging.INFO)

def add_s3_settings():
    section = ('s3_uploader', "S3 Uploader")
    shared.opts.add_option("s3_uploader_enabled", shared.OptionInfo(False, "Enable S3 Upload", gr.Checkbox, section=section))
    shared.opts.add_option("s3_uploader_endpoint_url", shared.OptionInfo("", "S3 Endpoint URL (e.g., https://s3.amazonaws.com)", gr.Textbox, section=section))
    shared.opts.add_option("s3_uploader_access_key_id", shared.OptionInfo("", "S3 Access Key ID", gr.Textbox, {"type": "password"}, section=section))
    shared.opts.add_option("s3_uploader_secret_access_key", shared.OptionInfo("", "S3 Secret Access Key", gr.Textbox, {"type": "password"}, section=section))
    shared.opts.add_option("s3_uploader_bucket_name", shared.OptionInfo("", "S3 Bucket Name", gr.Textbox, section=section))
    shared.opts.add_option("s3_uploader_region_name", shared.OptionInfo("", "S3 Region Name (optional)", gr.Textbox, section=section))

on_ui_settings(add_s3_settings)

def on_image_saved_callback(params: ImageSaveParams):
    if not shared.opts.s3_uploader_enabled:
        return

    endpoint_url = shared.opts.s3_uploader_endpoint_url
    access_key_id = shared.opts.s3_uploader_access_key_id
    secret_access_key = shared.opts.s3_uploader_secret_access_key
    bucket_name = shared.opts.s3_uploader_bucket_name
    region_name = shared.opts.s3_uploader_region_name

    if not all([endpoint_url, access_key_id, secret_access_key, bucket_name]):
        logging.warning("S3 Uploader: Missing one or more required S3 configuration fields in Settings.")
        return

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name if region_name else None
        )
    except Exception as e:
        logging.error(f"S3 Uploader: Error creating S3 client: {e}")
        return

    image_path = params.filename
    image_name = os.path.basename(image_path)

    try:
        s3_client.upload_file(image_path, bucket_name, image_name)
        logging.info(f"S3 Uploader: Successfully uploaded {image_name} to {bucket_name}")
    except NoCredentialsError:
        logging.error("S3 Uploader: Credentials not available.")
    except ClientError as e:
        logging.error(f"S3 Uploader: An error occurred: {e}")
    except Exception as e:
        logging.error(f"S3 Uploader: An unexpected error occurred: {e}")

on_image_saved(on_image_saved_callback)

class S3UploaderScript(scripts.Script):
    def title(self):
        return "S3 Uploader"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        # UI is now in the settings page
        return []
