# utils/telegram.py
import httpx
from pathlib import Path

from utils.global_variables import Variables


class Telegram:

    @staticmethod
    async def send_video(video_path: Path, caption: str = "") -> None:
        url = f"https://api.telegram.org/bot{Variables.TELEGRAM_BOT_TOKEN}/sendVideo"

        async with httpx.AsyncClient() as client:
            with open(video_path, "rb") as f:
                await client.post(
                    url,
                    data={
                        "chat_id": Variables.TELEGRAM_CHANNEL_ID,
                        "caption": caption,
                    },
                    files={"video": f},
                )
