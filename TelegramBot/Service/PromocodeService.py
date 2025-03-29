import uuid
from .API import PromocodeAPI

class PromocodeService:
    @staticmethod
    def ActivatePromocode(external_id: int, promocode_text: uuid):
        response = PromocodeAPI.ActivatePromocode(external_id, promocode_text)
        print(response.json())
        return response.status_code
