# utils/telegram.py
import httpx
from pathlib import Path
from utils.global_variables import Variables
from utils.utils import Utils


class Telegram:

    @staticmethod
    async def send_video(video_path: Path, caption: str = "") -> None:
        size_mb = video_path.stat().st_size / (1024 * 1024)

        if size_mb > 50:
            Utils.log(
                f"Video is {size_mb:.2f}MB — too large for Telegram, sending notification instead",
                "⚠️",
            )
            await Telegram._send_message(
                f"✅ Video is ready but too large to send ({size_mb:.1f}MB).\n\n{caption}"
            )
            return

        url = f"https://api.telegram.org/bot{Variables.TELEGRAM_BOT_TOKEN}/sendVideo"

        async with httpx.AsyncClient(timeout=120) as client:
            with open(video_path, "rb") as f:
                response = await client.post(
                    url,
                    data={"chat_id": Variables.TELEGRAM_CHANNEL_ID, "caption": caption},
                    files={"video": f},
                )

        if response.status_code != 200:
            Utils.log(
                f"Telegram send failed: {response.status_code} — {response.text}", "⚠️"
            )
        else:
            Utils.log(f"Video sent to Telegram: {video_path.name}", "📤")

    @staticmethod
    async def _send_message(text: str) -> None:
        url = f"https://api.telegram.org/bot{Variables.TELEGRAM_BOT_TOKEN}/sendMessage"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                data={"chat_id": Variables.TELEGRAM_CHANNEL_ID, "text": text},
            )

        if response.status_code != 200:
            Utils.log(
                f"Telegram message failed: {response.status_code} — {response.text}",
                "⚠️",
            )
        else:
            Utils.log("Telegram notification sent", "📤")
