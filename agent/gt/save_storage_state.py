"""Create fresh Playwright login state for the four WebArena sites."""

from __future__ import annotations

import argparse
import asyncio
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

from agent.gt.probe_auth import SENTINEL_CONFIG

# Selectors match the sign-in forms in the upstream WebArena images.
LOGIN_PATHS = {
    "gitlab": "/users/sign_in",
    "reddit": "/login",
    "shopping": "/customer/account/login/",
    "shopping_admin": "/admin/",
}
SUPPORTED_SITES = tuple(LOGIN_PATHS)


def login_fields(page, site):
    if site == "gitlab":
        return (page.get_by_test_id("username-field"), page.get_by_test_id("password-field"),
                page.get_by_test_id("sign-in-button"))
    if site == "shopping_admin":
        return (page.get_by_placeholder("user name"), page.get_by_placeholder("password"),
                page.get_by_role("button", name="Sign in"))
    username_label, button_name = ("Username", "Log in") if site == "reddit" else ("Email", "Sign In")
    return (page.get_by_label(username_label, exact=True), page.get_by_label("Password", exact=True),
            page.get_by_role("button", name=button_name))


async def create_storage_state(site: str, output_path: Path, headed: bool) -> None:
    if site not in LOGIN_PATHS:
        raise ValueError(f"Unsupported site: {site}")
    prefix = f"WEBARENA_{site.upper()}"
    username = os.getenv(f"{prefix}_USERNAME")
    password = os.getenv(f"{prefix}_PASSWORD")
    if not username or not password:
        raise ValueError(f"Set {prefix}_USERNAME and {prefix}_PASSWORD for your WebArena deployment.")
    sentinel = SENTINEL_CONFIG[site]
    origin = urlsplit(sentinel["url"])
    path = LOGIN_PATHS[site]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=not headed)
        try:
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(f"{origin.scheme}://{origin.netloc}{path}")
            if urlsplit(page.url).netloc != origin.netloc:
                raise ValueError(f"{site}: unexpected login origin; check the WebArena base URL")
            user_field, password_field, submit = login_fields(page, site)
            await user_field.fill(username)
            await password_field.fill(password)
            async with page.expect_navigation(wait_until="domcontentloaded"):
                await submit.click()
            await page.goto(sentinel["url"], wait_until="domcontentloaded")
            await page.get_by_text(sentinel["expected_marker"], exact=False).first.wait_for(state="attached")
            fd, temp = tempfile.mkstemp(dir=output_path.parent, suffix=".json")
            os.close(fd)
            try:
                await context.storage_state(path=temp)
                os.replace(temp, output_path)
            finally:
                Path(temp).unlink(missing_ok=True)
        finally:
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create Playwright storage state for a local WebArena site.")
    parser.add_argument("site", choices=SUPPORTED_SITES)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--headless", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(create_storage_state(args.site, args.output, headed=not args.headless))


if __name__ == "__main__":
    main()
