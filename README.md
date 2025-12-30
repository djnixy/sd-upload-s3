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

## How to Check if it's Working

### 1. Test Connection Button
After applying your settings, go to the **txt2img** or **img2img** tab. You will see a new accordion titled **S3 Uploader** at the bottom of the script section (or sidebar).
- Click the **Test S3 Connection** button.
- If everything is configured correctly, it will display a success message.
- If there's an error, it will show the error returned by the S3 provider.

### 2. Check Console Logs
When you generate an image, the extension logs its progress to the terminal/console where you started Stable Diffusion Forge.
- Look for lines starting with `S3 Uploader:`.
- Success example: `S3 Uploader: Successfully uploaded 00001-12345678.png to my-bucket`
- Failure example: `S3 Uploader: S3 Client Error: An error occurred (403) when calling the PutObject operation: Forbidden`

### 3. Verify in S3 Console
The most definitive way to check is to log into your S3 provider's web console (AWS, MinIO, DigitalOcean) and verify that the files are appearing in your bucket.

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

- **Connection Refused:** Check if your `Endpoint URL` is correct and reachable from the machine running Stable Diffusion.
- **Access Denied (403):** Ensure your S3 credentials have `s3:PutObject` and `s3:ListBucket` (for testing) permissions.
- **SSL Error:** If using a self-hosted S3 without a valid certificate, you might need to troubleshoot your local SSL configuration or use `http` (not recommended for production).

## Security & Credentials

By default, all configuration values are stored in the `config.json` file in the Stable Diffusion Forge root directory. For higher security and easier deployment (e.g., Docker), you can set any or all configuration values as environment variables.

### Using Environment Variables
All settings can be overridden with environment variables. If an environment variable is set, it will take precedence over the UI setting:

- `S3_UPLOADER_ENABLED` - Enable/disable S3 upload (true/false, 1/0, yes/no, on/off)
- `S3_UPLOADER_ENDPOINT_URL` - S3 endpoint URL
- `S3_UPLOADER_ACCESS_KEY_ID` - S3 access key
- `S3_UPLOADER_SECRET_ACCESS_KEY` - S3 secret key
- `S3_UPLOADER_BUCKET_NAME` - S3 bucket name
- `S3_UPLOADER_REGION_NAME` - S3 region (default: us-east-1)
- `S3_UPLOADER_USE_SSL` - Use SSL (true/false, default: true)
- `S3_UPLOADER_PATH_STYLE` - Use path-style addressing (true/false, default: false)

Example (Linux):
```bash
export S3_UPLOADER_ENABLED="true"
export S3_UPLOADER_ENDPOINT_URL="http://localhost:9000"
export S3_UPLOADER_ACCESS_KEY_ID="your_key"
export S3_UPLOADER_SECRET_ACCESS_KEY="your_secret"
export S3_UPLOADER_BUCKET_NAME="my-bucket"
export S3_UPLOADER_USE_SSL="false"
export S3_UPLOADER_PATH_STYLE="true"
./webui.sh
```

Example (Docker):
```yaml
environment:
  - S3_UPLOADER_ENABLED=true
  - S3_UPLOADER_ENDPOINT_URL=http://minio:9000
  - S3_UPLOADER_ACCESS_KEY_ID=minioadmin
  - S3_UPLOADER_SECRET_ACCESS_KEY=minioadmin
  - S3_UPLOADER_BUCKET_NAME=sd-images
  - S3_UPLOADER_USE_SSL=false
  - S3_UPLOADER_PATH_STYLE=true
```
