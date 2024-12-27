import requests


class UnsplashService:
    @staticmethod
    def GetImageLinkByParam(param):
        response = requests.get(
            f'https://api.unsplash.com/search/photos?query={param}',
            headers={
                'Authorization': 'Client-ID WHM-dSv9QiBVuEGvC-KY26CuoG_Ac6Ogi7FtQrS1g1w'
            }
        ).json()
        try:
            photo_id = response.get("results")[0].get('id')
        except Exception as e:
            return None

        response = requests.get(
            f'https://api.unsplash.com/photos/{photo_id}/download',
            headers={
                'Authorization': 'Client-ID WHM-dSv9QiBVuEGvC-KY26CuoG_Ac6Ogi7FtQrS1g1w'
            }
        ).json()
        return response.get('url')
