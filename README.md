# Remote Uploader Extension for Stable Diffusion WebUI Forge

This extension allows you to automatically upload images generated in the Stable Diffusion WebUI Forge to an S3-compatible storage service and/or a remote server via SCP.

## Features

- **Dual Uploaders:** Upload to S3-compatible object storage and/or a remote server via SCP. You can use either or both simultaneously.
- **S3 Compatibility:** Works with AWS S3, Minio, DigitalOcean Spaces, and other S3-compatible services.
- **SCP Upload:** Securely copy images to a remote host using SSH key authentication.
- **Easy Configuration:** Configure all settings directly in the WebUI's "Settings" tab.
- **Automatic Uploads:** Images are uploaded immediately after generation.
- **Automatic Dependency Installation:** The required `boto3` library is installed automatically.

## Installation

1.  **Clone the Repository:**
    Navigate to the `extensions` directory of your Stable Diffusion WebUI Forge installation and clone this repository.
    ```bash
    cd extensions
    git clone https://github.com/djnixy/sd-webui-remote-uploader.git
    ```
    *(Note: Replace with the actual repository URL.)*

2.  **Restart the WebUI:**
    Restart the Stable Diffusion WebUI Forge. The required `boto3` library will be installed automatically on the first run.

## Configuration

1.  **Open the WebUI:**
    Launch the Stable Diffusion WebUI Forge in your browser.

2.  **Navigate to the Settings Tab:**
    Click on the "Settings" tab in the main menu.

3.  **Find the Uploader Sections:**
    In the left-hand menu of the Settings tab, you will find sections for "S3 Uploader" and "SCP Uploader."

4.  **Configure Your Settings:**
    You can enable and configure either or both of the uploaders.

    ### S3 Uploader
    - **Enable S3 Upload:** Check this box to enable S3 uploads.
    - **S3 Endpoint URL:** The URL of your S3-compatible service (e.g., `https://s3.amazonaws.com`).
    - **S3 Access Key ID:** Your S3 access key.
    - **S3 Secret Access Key:** Your S3 secret key.
    - **S3 Bucket Name:** The name of the S3 bucket for image storage.
    - **S3 Region Name (optional):** The AWS region of your bucket (e.g., `us-east-1`).
    - **Use SSL:** Whether to use SSL for the connection.
    - **Use Path Style Addressing:** Important for services like MinIO.

    ### SCP Uploader
    - **Enable SCP Upload:** Check this box to enable SCP uploads.
    - **SCP Host (user@host):** The remote server address, including the username (e.g., `myuser@myserver.com`).
    - **SCP Remote Path:** The absolute path to the destination directory on the remote server.
    - **Path to SSH Private Key:** The absolute path to your SSH private key on the machine running the WebUI.

5.  **Apply Settings:**
    Click the "Apply settings" button at the top of the page to save your configuration.

## How to Check if it's Working

### 1. Test Connection Buttons
In the settings page, under each uploader's section, you will find a "Test Connection" button.
- Click the **Test S3 Connection** or **Test SCP Connection** button.
- A success message indicates that your configuration is correct.
- An error message will provide details if the connection fails.

### 2. Check Console Logs
When you generate an image, the extension logs its progress to the terminal/console.
- Look for lines starting with `S3 Uploader:` or `SCP Uploader:`.
- **Success example (S3):** `S3 Uploader: Successfully uploaded 00001-12345678.png to my-bucket`
- **Success example (SCP):** `SCP Uploader: Successfully uploaded 00001-12345678.png`
- If both are enabled, you will see logs for both upload processes.

### 3. Verify on Remote
- **S3:** Log into your S3 provider's web console to see the uploaded files in your bucket.
- **SCP:** SSH into your remote server and check the destination directory to confirm the files are there.

## Provider Specific Notes

- **MinIO:**
    - **Endpoint URL:** Use `http://your-ip:9000` or `https://your-minio-domain.com`.
    - **Use Path Style Addressing:** Enable this if you get "Bucket Not Found" or connection errors.
    - **Use SSL:** Disable this if you are using `http`.
- **DigitalOcean Spaces:**
    - **Endpoint URL:** `https://[region].digitaloceanspaces.com` (e.g., `https://nyc3.digitaloceanspaces.com`).
    - **Region:** Should match the region in the endpoint (e.g., `nyc3`).
- **AWS S3:**
    - **Endpoint URL:** `https://s3.[region].amazonaws.com` (e.g., `https://s3.us-east-1.amazonaws.com`).
    - **Region:** e.g., `us-east-1`.

## Troubleshooting

- **S3 Connection Refused:** Check your `Endpoint URL` and network connectivity.
- **S3 Access Denied (403):** Ensure your credentials have `s3:PutObject` and `s3:ListBucket` permissions.
- **SCP Connection Timed Out/Failed:**
    - Verify the `SCP Host` is correct and reachable.
    - Ensure your SSH key is not password-protected or that an SSH agent is configured correctly.
    - Check that the `Path to SSH Private Key` is the absolute path and is readable by the user running the WebUI.
- **SCP Permission Denied:** The user specified in `SCP Host` must have write permissions for the `SCP Remote Path` on the remote server.

## Security & Credentials

All configuration values can be set as environment variables for higher security and easier deployment (e.g., Docker). Environment variables take precedence over UI settings.

### S3 Environment Variables
- `S3_UPLOADER_ENABLED`: `true` or `false`
- `S3_UPLOADER_ENDPOINT_URL`: S3 endpoint URL
- `S3_UPLOADER_ACCESS_KEY_ID`: S3 access key
- `S3_UPLOADER_SECRET_ACCESS_KEY`: S3 secret key
- `S3_UPLOADER_BUCKET_NAME`: S3 bucket name
- `S3_UPLOADER_REGION_NAME`: S3 region (default: `us-east-1`)
- `S3_UPLOADER_USE_SSL`: `true` or `false`
- `S3_UPLOADER_PATH_STYLE`: `true` or `false`

### SCP Environment Variables
- `SCP_UPLOADER_ENABLED`: `true` or `false`
- `SCP_UPLOADER_HOST`: Remote host (e.g., `user@host.com`)
- `SCP_UPLOADER_PATH`: Remote destination path
- `SCP_UPLOADER_KEY_PATH`: Path to the SSH private key

### Example (Docker Compose)
```yaml
services:
  webui:
    image: your-forge-image
    environment:
      # S3 Settings
      - S3_UPLOADER_ENABLED=true
      - S3_UPLOADER_ENDPOINT_URL=http://minio:9000
      - S3_UPLOADER_ACCESS_KEY_ID=minioadmin
      - S3_UPLOADER_SECRET_ACCESS_KEY=minioadmin
      - S3_UPLOADER_BUCKET_NAME=sd-images
      # SCP Settings
      - SCP_UPLOADER_ENABLED=true
      - SCP_UPLOADER_HOST=user@remoteserver
      - SCP_UPLOADER_PATH=/home/user/sd-images
      - SCP_UPLOADER_KEY_PATH=/root/.ssh/id_rsa
    volumes:
      - /path/to/your/ssh/key:/root/.ssh/id_rsa:ro
```
