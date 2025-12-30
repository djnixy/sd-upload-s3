# S3 Uploader Extension for Stable Diffusion WebUI Forge

This extension allows you to automatically upload images generated in the Stable Diffusion WebUI Forge to an S3-compatible storage service.

## Features

- **S3 Compatibility:** Works with AWS S3, Minio, DigitalOcean Spaces, and other S3-compatible services.
- **Easy Configuration:** Configure your S3 settings directly in the WebUI's "Settings" tab.
- **Automatic Uploads:** Images are uploaded to your specified S3 bucket immediately after generation.
- **Automatic Dependency Installation:** The required `boto3` library is installed automatically.

## Installation

1.  **Clone the Repository:**
    Navigate to the `extensions` directory of your Stable Diffusion WebUI Forge installation and clone this repository.
    ```bash
    cd extensions
    git clone https://your-repository-url/sd-webui-s3-uploader.git
    ```
    *(Note: Replace `your-repository-url/sd-webui-s3-uploader.git` with the actual repository URL.)*

2.  **Restart the WebUI:**
    Restart the Stable Diffusion WebUI Forge. The required `boto3` library will be installed automatically on the first run.

## Configuration

1.  **Open the WebUI:**
    Launch the Stable Diffusion WebUI Forge in your browser.

2.  **Navigate to the Settings Tab:**
    Click on the "Settings" tab in the main menu.

3.  **Find the S3 Uploader Section:**
    In the left-hand menu of the Settings tab, find and click on "S3 Uploader."

4.  **Configure Your S3 Settings:**
    - **Enable S3 Upload:** Check this box to enable the extension.
    - **S3 Endpoint URL:** The URL of your S3-compatible service (e.g., `https://s3.amazonaws.com`, `https://s3.digitalocean.com`).
    - **S3 Access Key ID:** Your S3 access key.
    - **S3 Secret Access Key:** Your S3 secret key.
    - **S3 Bucket Name:** The name of the S3 bucket where you want to store your images.
    - **S3 Region Name (optional):** The AWS region of your bucket (e.g., `us-east-1`). This is usually not required for non-AWS S3 services.

5.  **Apply Settings:**
    Click the "Apply settings" button at the top of the page to save your configuration.

6.  **Generate an Image:**
    Once you've configured and applied your settings, generate an image. If the settings are correct, the image will be uploaded to your S3 bucket, and you'll see a confirmation message in the console.

## Troubleshooting

- **"NoCredentialsError: Unable to locate credentials":**
  This error indicates that your S3 access key and secret key are incorrect or not properly configured. Double-check your credentials in the S3 Uploader settings.

- **"ClientError: An error occurred (403) when calling the HeadBucket operation: Forbidden":**
  This usually means that your access key does not have the necessary permissions to access the specified bucket. Ensure your S3 user has the required permissions (e.g., `s3:PutObject`).

- **"ClientError: An error occurred (404) when calling the HeadBucket operation: Not Found":**
  The specified bucket does not exist. Make sure you've created the bucket in your S3 service and that the bucket name is spelled correctly.
