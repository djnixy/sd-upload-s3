# S3 Uploader Extension for Stable Diffusion WebUI Forge

This extension allows you to automatically upload images generated in the Stable Diffusion WebUI Forge to an S3-compatible storage service.

## Features

- **S3 Compatibility:** Works with AWS S3, Minio, DigitalOcean Spaces, and other S3-compatible services.
- **Easy Configuration:** Configure your S3 settings directly in the WebUI.
- **Automatic Uploads:** Images are uploaded to your specified S3 bucket immediately after generation.

## Installation

1.  **Download the Extension:**
    Download the `s3-uploader` directory and place it in the `extensions` directory of your Stable Diffusion WebUI Forge installation.

2.  **Install Dependencies:**
    This extension requires the `boto3` library. If you don't have it installed, you can install it using pip:
    ```bash
    pip install boto3
    ```

3.  **Restart the WebUI:**
    Restart the Stable Diffusion WebUI Forge to load the extension.

## Configuration

1.  **Open the WebUI:**
    Launch the Stable Diffusion WebUI Forge in your browser.

2.  **Find the S3 Uploader Section:**
    In the `txt2img` or `img2img` tabs, you'll find an accordion menu labeled "S3 Uploader."

3.  **Configure Your S3 Settings:**
    - **Enable S3 Upload:** Check this box to enable the extension.
    - **S3 Endpoint URL:** The URL of your S3-compatible service (e.g., `https://s3.amazonaws.com`, `https://s3.digitalocean.com`).
    - **S3 Access Key ID:** Your S3 access key.
    - **S3 Secret Access Key:** Your S3 secret key.
    - **S3 Bucket Name:** The name of the S3 bucket where you want to store your images.
    - **S3 Region Name (optional):** The AWS region of your bucket (e.g., `us-east-1`). This is usually not required for non-AWS S3 services.

4.  **Generate an Image:**
    Once you've configured your settings, generate an image. If the settings are correct, the image will be uploaded to your S3 bucket, and you'll see a confirmation message in the console.

## Troubleshooting

- **"ModuleNotFoundError: No module named 'boto3'":**
  This means the `boto3` library is not installed. Follow the installation instructions to install it.

- **"NoCredentialsError: Unable to locate credentials":**
  This error indicates that your S3 access key and secret key are incorrect or not properly configured. Double-check your credentials in the S3 Uploader settings.

- **"ClientError: An error occurred (403) when calling the HeadBucket operation: Forbidden":**
  This usually means that your access key does not have the necessary permissions to access the specified bucket. Ensure your S3 user has the required permissions (e.g., `s3:PutObject`).

- **"ClientError: An error occurred (404) when calling the HeadBucket operation: Not Found":**
  The specified bucket does not exist. Make sure you've created the bucket in your S3 service and that the bucket name is spelled correctly.
