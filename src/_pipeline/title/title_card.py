#!/usr/bin/env python3
"""
_pipeline/title/title_card.py
------------------
Generates a title card image for the video using Playwright to render an HTML template.
"""

from pathlib import Path

import random

from utils.global_variables import Variables


class TitleCard:

    TEMPLATE_PATH = Path(__file__).parent / "title_card.html"

    @staticmethod
    async def render(title: str, output_path: Path) -> None:
        from playwright.async_api import async_playwright

        html = TitleCard.TEMPLATE_PATH.read_text(encoding="utf-8")
        views = random.randint(100_000, 1_000_000)
        html = html.replace("{{title}}", title)
        html = html.replace("{{username}}", Variables.USERNAME)
        html = html.replace("{{acronym}}", Variables.ACRONYM)
        html = html.replace("{{views}}", f"{views:,}")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={
                    "width": Variables.TITLE_WIDTH,
                    "height": Variables.TITLE_HEIGHT,
                }
            )
            await page.set_content(html)
            await page.screenshot(
                path=str(output_path), full_page=True, omit_background=True
            )
            await browser.close()
