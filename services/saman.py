from fastapi import HTTPException
import httpx
from decouple import config

from config.saman import SamanConfig


class SamanService:
    
    redirect_url = "https://your-domain.com/callback"
    
    def __init__(self, config: SamanConfig):
        self.config = config
        self.redirect_url = config.redirect_url
    
    async def get_token(self, amount: int, res_num: str):
        payload = {
            "action": "token",
            "TerminalId": self.config.terminal_id,
            "Amount": amount,
            "ResNum": res_num,
            "RedirectUrl": self.redirect_url,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://sep.shaparak.ir/onlinepg/onlinepg",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Referer": config("DOMAIN"),
                    "Origin": config("DOMAIN")
                }
            )
            data = resp.json()

        if data.get("status") != 1 or not data.get("token"):
            raise HTTPException(
                status_code=400,
                detail=f"Token request failed: {data.get('errorDesc') or data}"
            )
        return data["token"]
    
    async def verify_transaction(self, ref_num: str) -> dict:
        payload = {
            "RefNum": ref_num,
            "TerminalNumber": self.config.terminal_id,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://sep.shaparak.ir/verifyTxnRandomSessionkey/ipg/VerifyTransaction",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            return resp.json()