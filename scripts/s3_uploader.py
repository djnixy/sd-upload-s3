
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

    # Add a button to test the connection
    with gr.Row(elem_id="s3_uploader_test_connection"):
        test_button = gr.Button("Test S3 Connection", variant="secondary")
        test_output = gr.Textbox(label="Test Result", interactive=False)

    test_button.click(
        fn=test_connection,
        inputs=[],
        outputs=[test_output],
    )

on_ui_settings(add_s3_settings)

def get_config_value(env_var, ui_value, default=None, value_type=str):
    """Get configuration value from environment variable or UI setting."""
    env_value = os.environ.get(env_var)
    if env_value is not None:
        if value_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        return value_type(env_value)
    return ui_value if ui_value is not None else default

def verify_s3_configuration():
    # Check for required environment variables
    missing_vars = []
    if not get_config_value("S3_UPLOADER_ENDPOINT_URL", shared.opts.s3_uploader_endpoint_url):
        missing_vars.append("S3_UPLOADER_ENDPOINT_URL")
    if not get_config_value("S3_UPLOADER_ACCESS_KEY_ID", shared.opts.s3_uploader_access_key_id):
        missing_vars.append("S3_UPLOADER_ACCESS_KEY_ID")
    if not get_config_value("S3_UPLOADER_SECRET_ACCESS_KEY", shared.opts.s3_uploader_secret_access_key):
        missing_vars.append("S3_UPLOADER_SECRET_ACCESS_KEY")
    if not get_config_value("S3_UPLOADER_BUCKET_NAME", shared.opts.s3_uploader_bucket_name):
        missing_vars.append("S3_UPLOADER_BUCKET_NAME")

    if missing_vars:
        return f"Missing required S3 configuration: {', '.join(missing_vars)}"

    # Test the S3 connection
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return "Failed to create S3 client. Check your credentials and endpoint URL."

        # Check if the bucket exists
        s3_client.head_bucket(Bucket=get_config_value("S3_UPLOADER_BUCKET_NAME", shared.opts.s3_uploader_bucket_name))

        return "S3 configuration verified successfully."
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return "S3 bucket not found. Please check the bucket name."
        else:
            return f"S3 connection failed: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

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

def test_connection():
    return verify_s3_configuration()

# Verify S3 configuration at startup
startup_verification_result = verify_s3_configuration()
if "successfully" not in startup_verification_result:
    logger.warning(f"S3 Uploader: {startup_verification_result}")
else:
    logger.info(f"S3 Uploader: {startup_verification_result}")

