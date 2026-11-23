#!/usr/bin/env python3
"""Probe whether a saved storage-state file still holds a valid authenticated session.

Exit code 0 = healthy (authenticated), 1 = unhealthy (session expired or invalid).

Example:
    python -m agent.gt.probe_auth gitlab --storage-state runtime_auth_state_placeholder.json
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright


SENTINEL_CONFIG: dict[str, dict] = {
    'gitlab': {
        'url': 'http://localhost:8023/-/profile',
        'bad_url_patterns': ['/users/sign_in', '/users/sign_up'],
        'expected_marker': 'Main settings',
    },
    'reddit': {
        'url': 'http://localhost:9999/user/MarvelsGrantMan136/account',
        'bad_url_patterns': ['/login', '/registration'],
        'expected_marker': 'Credentials',
    },
    'shopping': {
        'url': 'http://localhost:7770/customer/account/',
        'bad_url_patterns': ['/customer/account/login'],
        'expected_marker': 'Contact Information',
    },
    'shopping_admin': {
        'url': 'http://localhost:7780/admin/admin/system_account/index/',
        'bad_url_patterns': ['/admin/auth'],
        'expected_marker': 'Account Information',
    },
}


async def probe(site: str, storage_state_path: Path, timeout_ms: int = 15000) -> tuple[bool, str]:
    """Return (healthy, reason)."""
    config = SENTINEL_CONFIG.get(site)
    if config is None:
        return False, f'unknown site: {site}'

    if not storage_state_path.exists():
        return False, f'storage state file not found: {storage_state_path}'

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context(
                storage_state=str(storage_state_path),
                viewport={'width': 1280, 'height': 720},
            )
            page = await context.new_page()
            try:
                response = await page.goto(config['url'], timeout=timeout_ms, wait_until='domcontentloaded')
            except Exception as exc:
                return False, f'navigation failed: {exc}'

            final_url = page.url
            if response is not None and response.status >= 400:
                return False, f'sentinel returned HTTP {response.status}: {final_url}'

            for bad_pattern in config['bad_url_patterns']:
                if bad_pattern in final_url:
                    return False, f'redirected to login: {final_url}'

            page_content = await page.content()
            if config['expected_marker'].lower() not in page_content.lower():
                return False, f"expected marker {config['expected_marker']!r} not found in page"

            return True, 'ok'
        finally:
            await browser.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Probe auth session health for a site.')
    parser.add_argument('site', choices=sorted(SENTINEL_CONFIG.keys()), help='Site to probe.')
    parser.add_argument('--storage-state', required=True, type=Path, help='Path to storage state JSON.')
    parser.add_argument('--timeout', type=int, default=15000, help='Navigation timeout in ms.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    healthy, reason = asyncio.run(probe(args.site, args.storage_state, timeout_ms=args.timeout))
    if healthy:
        print(f'probe OK: {args.site}')
        sys.exit(0)
    else:
        print(f'probe FAILED: {args.site}: {reason}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
