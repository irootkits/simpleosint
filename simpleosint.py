#!/usr/bin/env python3
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional
import requests
from requests.exceptions import RequestException
DEFAULT_TIMEOUT = 10
DEFAULT_WORKERS = 10
MAX_USERNAME_LENGTH = 50
DEFAULT_HEADERS = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) " "AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/120.0 Safari/537.36")}
PLATFORMS = {
    "GitHub": "https://github.com/{username}",
    "Facebook": "https://www.facebook.com/{username}",
    "TikTok": "https://www.tiktok.com/@{username}",
    "Snapchat": "https://www.snapchat.com/add/{username}",
    "Instagram": "https://www.instagram.com/{username}/",
    "RootMe": "https://www.root-me.org/{username}",
    "HackTheBox": "https://www.hackthebox.com/home/users/profile/{username}",
    "Reddit": "https://www.reddit.com/user/{username}",
    "Pornhub": "https://www.pornhub.com/users/{username}",
    "Telegram": "https://t.me/{username}",
    "Roblox": "https://www.roblox.com/users/{username}/profile",
    "MSN_Search": "https://www.bing.com/search?q={username}+site:msn.com",
}
def print_err(msg: str) -> None:
    print(msg)
def check_url_exists(session: requests.Session, url: str, timeout: int) -> Optional[bool]:
    try:
        r = session.get(url, timeout=timeout, headers=DEFAULT_HEADERS, allow_redirects=True)
        status = r.status_code
        text = r.text[:4096]
        if status == 200:
            lowered = text.lower()
            if any(x in lowered for x in ("not found", "page not found", "error 404", "profil introuvable", "page introuvable", "no results found")):
                return False
            return True
        elif status in (301, 302):
            location = r.headers.get("Location", "")
            if location:
                if any(x in location for x in ("login", "signup", "home.php")):
                    return None
                return True
            return None
        elif status == 404:
            return False
        elif status in (429, 403):
            return None
        else:
            return None
    except RequestException:
        return None
def probe_platform(session: requests.Session, platform: str, username: str, timeout: int) -> Dict[str, str]:
    try:
        template = PLATFORMS.get(platform)
        if template is None:
            return {"platform": platform, "status": "UNKNOWN", "url": ""}
        url = template.format(username=username)
        exists = check_url_exists(session, url, timeout=timeout)
        if exists is True:
            return {"platform": platform, "status": "FOUND", "url": url}
        elif exists is False:
            return {"platform": platform, "status": "NOT_PWN", "url": url}
        else:
            return {"platform": platform, "status": "ERROR_CRSH", "url": url}
    except Exception:
        traceback.print_exc()
        return {"platform": platform, "status": "ERROR_CRSH", "url": ""}
def run_checks(username: str, timeout: int, workers: int) -> Dict[str, Dict[str, str]]:
    results: Dict[str, Dict[str, str]] = {}
    with requests.Session() as session:
        session.headers.update(DEFAULT_HEADERS)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(probe_platform, session, platform, username, timeout): platform for platform in PLATFORMS}
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    res = future.result()
                    results[platform] = res
                except Exception:
                    results[platform] = {"platform": platform, "status": "ERROR_CRSH", "url": ""}
    return results
def main():
    while True:
        username = input("user: ").strip()
        if username == "$who":
            print("its a simple osint tools by tony")
            continue
        if len(username) > MAX_USERNAME_LENGTH:
            print_err("ERREUR TRO LONG FILSDEP (>{} caractères).".format(MAX_USERNAME_LENGTH))
            continue
        try:
            start = time.time()
            results = run_checks(username, timeout=DEFAULT_TIMEOUT, workers=DEFAULT_WORKERS)
            elapsed = time.time() - start
            print("\nRésultats pour le pseudo : {}".format(username))
            for platform, data in results.items():
                status = data.get("status", "UNKNOWN")
                url = data.get("url", "")
                if status == "FOUND":
                    print(f"[FOUND] {platform}: {url}")
                elif status == "NOT_PWN":
                    print(f"[NOT PWN] {platform}: ERREUR NOT PWN")
                elif status == "ERROR_CRSH":
                    print(f"[CRSH] {platform}: ERREUR CRSH (chp lv sa marche pa)")
                else:
                    print(f"[UNKNOWN] {platform}: statut inconnu")
            print("temp: {:.2f}s".format(elapsed))
        except Exception:
            traceback.print_exc()
            print_err("erreur tu bug tro.")
if __name__ == "__main__":
    main()
