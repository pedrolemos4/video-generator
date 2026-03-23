# utils/telegram.py
import httpx
from pathlib import Path
from utils.utils import Utils
from utils.global_variables import Variables


class Telegram:

    @staticmethod
    async def send_message(video_path: Path = None, caption: str = "") -> None:
        if video_path is None:
            response = await Telegram._send_message(caption)

            if response.status_code != 200:
                Utils.log(
                    f"Telegram send failed: {response.status_code} — {response.text}",
                    "⚠️",
                )
            else:
                Utils.log(f"Message sent to Telegram", "📤")
        else:
            Utils.log(
                f"Video is {video_path.stat().st_size / (1024 * 1024):.2f}MB — too large for Telegram, sending notification instead",
                "⚠️",
            )
            response = await Telegram._send_message(
                f"✅ Video is ready but too large to send ({video_path.stat().st_size / (1024 * 1024):.1f}MB).\n\n{caption}"
            )

            if response.status_code != 200:
                Utils.log(
                    f"Telegram send failed: {response.status_code} — {response.text}",
                    "⚠️",
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
