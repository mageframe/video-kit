import aiohttp
import asyncio
import os
import ssl
from typing import Optional, Dict
import aiofiles


class KieClient:
    """Client for interacting with Kie.ai API."""

    UPLOAD_BASE_URL = "https://kieai.redpandaai.co"
    API_BASE_URL = "https://api.kie.ai"

    def __init__(self):
        self.api_key = os.getenv("KIE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "KIE_API_KEY environment variable not set. "
                "Please set it in the .env file or via the API Key modal in the UI."
            )

        # SSL context for macOS certificate issues
        # For production, use proper SSL verification
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
        }

    async def upload_file(self, file_path: str, upload_path: str = "fight-videos") -> str:
        """
        Upload a file to Kie.ai and return the file URL.

        Args:
            file_path: Local path to the file to upload
            upload_path: Remote upload path on Kie.ai

        Returns:
            str: URL of the uploaded file
        """
        url = f"{self.UPLOAD_BASE_URL}/api/file-stream-upload"

        # Read file
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()

        # Prepare form data
        filename = os.path.basename(file_path)
        form = aiohttp.FormData()
        form.add_field('file', file_content, filename=filename, content_type='image/jpeg')
        form.add_field('uploadPath', upload_path)
        form.add_field('fileName', filename)

        # Upload
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.post(
                url,
                headers=self._get_headers(),
                data=form
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"File upload failed: {response.status} - {error_text}")

                result = await response.json()

                # Handle different response formats
                if "data" in result:
                    data = result["data"]
                    # Try different URL field names
                    if "downloadUrl" in data:
                        return data["downloadUrl"]
                    elif "fileUrl" in data:
                        return data["fileUrl"]
                    elif "url" in data:
                        return data["url"]
                elif "fileUrl" in result:
                    return result["fileUrl"]
                elif "downloadUrl" in result:
                    return result["downloadUrl"]
                else:
                    raise Exception(f"Unexpected upload response format: {result}")

    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 5,
        quality: str = "720p",
        aspect_ratio: str = "16:9",
        watermark: str = "",
        model: str = "runway"
    ) -> str:
        """
        Generate a video using Runway or Sora 2 API on Kie.ai.

        Args:
            prompt: Text prompt for video generation
            image_url: Optional image URL for image-to-video
            duration: Video duration in seconds (5 or 10)
            quality: Video quality ("720p" or "1080p")
            aspect_ratio: Video aspect ratio
            watermark: Optional watermark text
            model: Model to use ("runway" or "sora2")

        Returns:
            str: Task ID for polling status
        """
        if model == "sora2":
            return await self._generate_video_sora2(prompt, image_url, aspect_ratio)
        else:
            return await self._generate_video_runway(prompt, image_url, duration, quality, aspect_ratio, watermark)

    async def _generate_video_runway(
        self,
        prompt: str,
        image_url: Optional[str],
        duration: int,
        quality: str,
        aspect_ratio: str,
        watermark: str
    ) -> str:
        """Generate video using Runway API."""
        url = f"{self.API_BASE_URL}/api/v1/runway/generate"

        payload = {
            "prompt": prompt,
            "duration": duration,
            "quality": quality,
            "aspectRatio": aspect_ratio,
            "waterMark": watermark,
        }

        if image_url:
            payload["imageUrl"] = image_url

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.post(
                url,
                headers={**self._get_headers(), "Content-Type": "application/json"},
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Video generation failed: {response.status} - {error_text}")

                result = await response.json()
                return result["data"]["taskId"]

    async def _generate_video_sora2(
        self,
        prompt: str,
        image_url: Optional[str],
        aspect_ratio: str
    ) -> str:
        """Generate video using Sora 2 API."""
        url = f"{self.API_BASE_URL}/api/v1/jobs/createTask"

        # Map aspect ratio format
        aspect_map = {
            "16:9": "landscape",
            "9:16": "portrait",
            "1:1": "square"
        }
        sora_aspect = aspect_map.get(aspect_ratio, "landscape")

        payload = {
            "model": "sora-2-image-to-video",
            "input": {
                "prompt": prompt,
                "aspect_ratio": sora_aspect,
                "n_frames": "10",
                "remove_watermark": True
            }
        }

        if image_url:
            payload["input"]["image_urls"] = [image_url]

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.post(
                url,
                headers={**self._get_headers(), "Content-Type": "application/json"},
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Sora 2 generation failed: {response.status} - {error_text}")

                result = await response.json()

                # Sora 2 uses different response format
                if "data" in result and "taskId" in result["data"]:
                    return result["data"]["taskId"]
                elif "taskId" in result:
                    return result["taskId"]
                else:
                    raise Exception(f"Unexpected Sora 2 response format: {result}")

    async def get_task_status(self, task_id: str, model: str = "sora2") -> Dict:
        """
        Get the status of a video generation task.

        Args:
            task_id: Task ID from generate_video
            model: Model used ("runway" or "sora2")

        Returns:
            Dict with task status information
        """
        # Sora 2 uses different endpoint
        if model == "sora2":
            url = f"{self.API_BASE_URL}/api/v1/jobs/recordInfo"
        else:
            url = f"{self.API_BASE_URL}/api/v1/runway/record-detail"

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.get(
                url,
                headers=self._get_headers(),
                params={"taskId": task_id}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Status check failed: {response.status} - {error_text}")

                result = await response.json()

                # Return the data section
                if "data" in result:
                    return result["data"]
                else:
                    return result

    async def download_video(self, video_url: str, output_path: str) -> None:
        """
        Download a video from Kie.ai to local storage.

        Args:
            video_url: URL of the video to download
            output_path: Local path to save the video
        """
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_context)) as session:
            async with session.get(video_url) as response:
                if response.status != 200:
                    raise Exception(f"Video download failed: {response.status}")

                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Write video file
                async with aiofiles.open(output_path, 'wb') as f:
                    await f.write(await response.read())
