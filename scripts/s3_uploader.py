
import gradio as gr
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from botocore.config import Config
import logging
from modules import shared, scripts
from modules.script_callbacks import on_ui_settings, on_image_saved, ImageSaveParams

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def add_s3_settings():
    section = ('s3_uploader', "S3 Uploader")
    shared.opts.add_option("s3_uploader_enabled", shared.OptionInfo(False, "Enable S3 Upload (Env: S3_UPLOADER_ENABLED)", gr.Checkbox, section=section))
    shared.opts.add_option("s3_uploader_endpoint_url", shared.OptionInfo("", "S3 Endpoint URL (Env: S3_UPLOADER_ENDPOINT_URL)", gr.Textbox, section=section))
    shared.opts.add_option("s3_uploader_access_key_id", shared.OptionInfo("", "S3 Access Key ID (Env: S3_UPLOADER_ACCESS_KEY_ID)", gr.Textbox, {"type": "password"}, section=section))
    shared.opts.add_option("s3_uploader_secret_access_key", shared.OptionInfo("", "S3 Secret Access Key (Env: S3_UPLOADER_SECRET_ACCESS_KEY)", gr.Textbox, {"type": "password"}, section=section))
    shared.opts.add_option("s3_uploader_bucket_name", shared.OptionInfo("", "S3 Bucket Name (Env: S3_UPLOADER_BUCKET_NAME)", gr.Textbox, section=section))
    shared.opts.add_option("s3_uploader_region_name", shared.OptionInfo("us-east-1", "S3 Region Name (Env: S3_UPLOADER_REGION_NAME)", gr.Textbox, section=section))
    shared.opts.add_option("s3_uploader_use_ssl", shared.OptionInfo(True, "Use SSL (Env: S3_UPLOADER_USE_SSL)", gr.Checkbox, section=section))
    shared.opts.add_option("s3_uploader_path_style", shared.OptionInfo(False, "Use Path Style Addressing (Env: S3_UPLOADER_PATH_STYLE)", gr.Checkbox, section=section))

on_ui_settings(add_s3_settings)

def get_config_value(env_var, ui_value, default=None, value_type=str):
    """Get configuration value from environment variable or UI setting."""
    env_value = os.environ.get(env_var)
    if env_value is not None:
        if value_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        return value_type(env_value)
    return ui_value if ui_value is not None else default

def get_s3_client():
    # Check environment variables first, fall back to UI settings
    endpoint_url = get_config_value("S3_UPLOADER_ENDPOINT_URL", shared.opts.s3_uploader_endpoint_url)
    access_key_id = get_config_value("S3_UPLOADER_ACCESS_KEY_ID", shared.opts.s3_uploader_access_key_id)
    secret_access_key = get_config_value("S3_UPLOADER_SECRET_ACCESS_KEY", shared.opts.s3_uploader_secret_access_key)
    region_name = get_config_value("S3_UPLOADER_REGION_NAME", shared.opts.s3_uploader_region_name, "us-east-1")
    use_ssl = get_config_value("S3_UPLOADER_USE_SSL", shared.opts.s3_uploader_use_ssl, True, bool)
    path_style = get_config_value("S3_UPLOADER_PATH_STYLE", shared.opts.s3_uploader_path_style, False, bool)

    if not all([endpoint_url, access_key_id, secret_access_key]):
        return None

    s3_config = Config(
        s3={'addressing_style': 'path' if path_style else 'auto'},
        region_name=region_name if region_name and region_name != "auto" else None
    )

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            use_ssl=use_ssl,
            config=s3_config
        )
        return s3_client
    except Exception as e:
        logger.error(f"S3 Uploader: Error creating S3 client: {e}")
        return None

def on_image_saved_callback(params: ImageSaveParams):
    # Check if S3 upload is enabled (env var or UI setting)
    enabled = get_config_value("S3_UPLOADER_ENABLED", getattr(shared.opts, "s3_uploader_enabled", False), False, bool)
    if not enabled:
        return

    bucket_name = get_config_value("S3_UPLOADER_BUCKET_NAME", getattr(shared.opts, "s3_uploader_bucket_name", ""))
    if not bucket_name:
        logger.warning("S3 Uploader: Bucket name is not configured.")
        return

    s3_client = get_s3_client()
    if not s3_client:
        logger.error("S3 Uploader: S3 client could not be initialized. Check your settings.")
        return

    image_path = params.filename
    if not os.path.exists(image_path):
        # In some cases, the file might not be written to disk yet if it's a memory-only save?
        # But normally on_image_saved implies it's on disk.
        logger.warning(f"S3 Uploader: Image file not found at {image_path}")
        return

    image_name = os.path.basename(image_path)

    try:
        logger.info(f"S3 Uploader: Uploading {image_name} to {bucket_name}...")
        s3_client.upload_file(image_path, bucket_name, image_name)
        logger.info(f"S3 Uploader: Successfully uploaded {image_name} to {bucket_name}")
    except NoCredentialsError:
        logger.error("S3 Uploader: Credentials not available.")
    except ClientError as e:
        logger.error(f"S3 Uploader: S3 Client Error: {e}")
    except Exception as e:
        logger.error(f"S3 Uploader: Unexpected error during upload: {e}")

on_image_saved(on_image_saved_callback)

class S3UploaderScript(scripts.Script):
    def title(self):
        return "S3 Uploader"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion("S3 Uploader", open=False):
            with gr.Row():
                test_btn = gr.Button("Test S3 Connection", variant="secondary")
                test_output = gr.Textbox(label="Test Result", interactive=False)
            
            def test_connection():
                client = get_s3_client()
                if not client:
                    return "Error: Could not initialize client. Check Settings (Endpoint, Keys)."
                
                bucket_name = get_config_value("S3_UPLOADER_BUCKET_NAME", getattr(shared.opts, "s3_uploader_bucket_name", ""))
                if not bucket_name:
                    return "Error: Bucket name not configured."
                
                try:
                    # Try to list objects (limited to 1) to verify connection and bucket access
                    client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                    return f"Success! Connected to {bucket_name}."
                except Exception as e:
                    return f"Connection Failed: {str(e)}"

            test_btn.click(fn=test_connection, outputs=[test_output])
            
        return [test_btn, test_output]
