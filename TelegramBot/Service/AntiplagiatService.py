import aiofiles
from Config import ANTI_PLAGIAT_API, X_USER_ID
import requests
import base64


class AntiplagiatService:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file

    async def encode_document(self,):
        async with aiofiles.open(self.file_path, 'r') as f:
            content = await f.read()
            return base64.b64encode(content)

    async def proceed_document(self,):
        document = await self.encode_document()
        response = requests.post(f"{ANTI_PLAGIAT_API}/document",
                                 headers={
                                     'x-user-id': X_USER_ID,
                                 },
                                 data=document)
        self.document_id = response.json()['document_id']
        return response.json()

    def get_document_status(self,):
        response = requests.get(f"{ANTI_PLAGIAT_API}/{self.document_id}/status",
                                headers={
                                    'x-user-id': X_USER_ID,
                                })
        return response.json()['status']

    async def check_document(self,):
        status = self.get_document_status()
        while status != 'done':
            response = requests.get(f"{ANTI_PLAGIAT_API}/{self.document_id}/result",
                                    headers={
                                        'x-user-id': X_USER_ID,
                                    })
            return response.json()
        return status
