from Config import ANTI_PLAGIAT_API, X_USER_ID, AI_MODELS
import aiofiles
import asyncio
import httpx  # Using async HTTP client
import base64
from .UserActionService import UserActionService
import os


class AntiplagiatService:
    def __init__(self, path_to_file, external_id):
        self.path_to_file = path_to_file
        self.document_id = None
        self.external_id=external_id

    async def _file_to_base64(self):
        """Convert file to base64-encoded string."""
        async with aiofiles.open(self.path_to_file, 'rb') as file:
            binary_content = await file.read()
        base64_encoded = base64.b64encode(binary_content).decode('utf-8')
        return base64_encoded

    def _get_file_extension(self):
        """Extract file extension dynamically from the file path."""
        return os.path.splitext(self.path_to_file)[1]

    async def proceed_document(self):
        """Upload the document and get its ID."""
        base64_data = await self._file_to_base64()
        file_extension = self._get_file_extension()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{ANTI_PLAGIAT_API}/document",
                    headers={
                        'x-file-extension': file_extension,
                        'x-user-id': X_USER_ID,
                    },
                    json=base64_data  # Wrap in dictionary
                )
                response.raise_for_status()
                self.document_id = response.json().get('id')
                if not self.document_id:
                    raise ValueError(
                        "Failed to retrieve document ID from response.")
            except httpx.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                raise

    async def _get_document_status(self):
        """Retrieve the status of the document."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{ANTI_PLAGIAT_API}/document/{self.document_id}/status",
                    headers={
                        'x-user-id': X_USER_ID,
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"HTTP error occurred: {e}")

    async def check_document(self, timeout=2000):
        """Check the document status and get the result URL when ready."""
        start_time = asyncio.get_event_loop().time()

        while True:
            # Check for timeout
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > timeout:
                raise TimeoutError("Document check timed out.")

            document_object = None
            status = None
            try:
                document_object = await self._get_document_status()
                status = document_object.get('state')
            except Exception as e:
                print(f"Error retrieving document status: {e}")

            # If the document is ready (state == 2), return the report link
            if status == 2:
                UserActionService.CreateUserAction(
                    input_tokens=0,
                    output_tokens=0,
                    prompt='antiplagiat',
                    model_open_ai_name=AI_MODELS.GPT_4_O.value,
                    action_type_name='antiplagiat_helper',
                    user_external_id=self.external_id
                )
                return document_object.get('webReportLink')

            # Add a delay to prevent excessive API requests
            await asyncio.sleep(20)
