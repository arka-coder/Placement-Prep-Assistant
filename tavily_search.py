"""
Tavily web-search helper for Placement Prep Assistant.

Provides:
  - get_useful_links(query)           → up to 3 curated educational article links
  - get_youtube_recommendations(query) → up to 3 structured YouTube video dicts

Design decisions:
  - Completely decoupled from RAG pipeline — imported independently.
  - Fails silently: any error returns [] so the app never crashes.
  - All functions return STRUCTURED DICTS — never raw HTML strings.
    The caller (app.py) is solely responsible for rendering.
  - Query is enriched with topic keywords to surface relevant content.
  - YouTube thumbnail URLs use the standard ytimg.com format keyed on video ID.
"""

import os
import re
import logging
from typing import List, Dict

logger = logging.getLogger("tavily_search")

# Trusted educational domains — results outside these are discarded
TRUSTED_DOMAINS = [
    "geeksforgeeks.org",
    "w3schools.com",
    "programiz.com",
    "javatpoint.com",
    "tutorialspoint.com",
]


def _get_tavily_key() -> str:
    """Read TAVILY_API_KEY from st.secrets (Streamlit Cloud) or os.getenv (local)."""
    try:
        import streamlit as st
        return st.secrets.get("TAVILY_API_KEY", "") or os.getenv("TAVILY_API_KEY", "")
    except Exception:
        return os.getenv("TAVILY_API_KEY", "")


def get_useful_links(query: str) -> List[Dict[str, str]]:
    """
    Search Tavily for beginner-friendly tutorials related to *query*
    and return up to 3 clean, structured link objects.

    Args:
        query: The user's original question (e.g. "What is overfitting?")

    Returns:
        List of dicts, each with "title" and "url" keys.
        Returns [] on any error so the caller is never affected.

    Example:
        >>> get_useful_links("What is a stack data structure?")
        [
            {"title": "Stack Data Structure - GeeksforGeeks", "url": "https://..."},
            {"title": "Stack - W3Schools", "url": "https://..."},
        ]
    """
    tavily_key = _get_tavily_key().strip()
    if not tavily_key:
        logger.warning("TAVILY_API_KEY not set — skipping link recommendations")
        return []

    try:
        from tavily import TavilyClient  # imported lazily so missing package = silent []

        client = TavilyClient(api_key=tavily_key)

        # Enrich the query to bias toward tutorial/explanation pages
        enriched_query = f"{query} explained tutorial for beginners"

        logger.info("Tavily search | query='%s'", enriched_query)

        response = client.search(
            query=enriched_query,
            search_depth="basic",       # fast + cheap
            max_results=6,              # fetch 6, we filter and keep best 3
            include_domains=TRUSTED_DOMAINS,
        )

        raw_results = response.get("results", [])
        logger.info("Tavily returned %d raw results", len(raw_results))

        links: List[Dict[str, str]] = []
        seen_urls: set = set()

        for item in raw_results:
            title = (item.get("title") or "").strip()
            url   = (item.get("url")   or "").strip()

            if not title or not url:
                continue

            # Deduplicate by URL
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Extra safety: only keep trusted-domain results
            if not any(domain in url for domain in TRUSTED_DOMAINS):
                logger.debug("Filtered out non-trusted URL: %s", url)
                continue

            links.append({"title": title, "url": url})

            if len(links) == 3:          # stop once we have 3 good links
                break

        logger.info("Returning %d curated link(s)", len(links))
        return links

    except ImportError:
        logger.error("tavily-python not installed. Run: pip install tavily-python")
        return []
    except Exception as exc:
        logger.error("Tavily search failed: %s", exc)
        return []


# ── YouTube video ID extractor ─────────────────────────────────────────────────
_YT_ID_RE = re.compile(
    r"""(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_\-]{11})"""
)

def _extract_video_id(url: str) -> str:
    """Return the 11-char YouTube video ID from a URL, or '' if not found."""
    m = _YT_ID_RE.search(url)
    return m.group(1) if m else ""


def _thumbnail_url(video_id: str) -> str:
    """Return the best-available YouTube thumbnail URL for a video ID."""
    if not video_id:
        return ""
    # hqdefault is universally available; mqdefault/sddefault may 404 on older vids
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def get_youtube_recommendations(query: str) -> List[Dict[str, str]]:
    """
    Search Tavily for YouTube tutorial videos related to *query* and return
    up to 3 structured video objects ready for card rendering.

    IMPORTANT — Returns STRUCTURED DICTS, never raw HTML strings.
    The caller (app.py render_youtube_cards) is responsible for all HTML.

    Args:
        query: The user's original question.

    Returns:
        List of dicts with keys:
            "title"         – video title (plain text, HTML-safe)
            "channel"       – channel name extracted from title/url or "YouTube"
            "video_url"     – full https://www.youtube.com/watch?v=... URL
            "thumbnail_url" – https://img.youtube.com/vi/<id>/hqdefault.jpg
            "video_id"      – 11-char YouTube video ID

        Returns [] on any error so the caller is never affected.

    Example:
        >>> get_youtube_recommendations("dynamic programming")
        [
            {
                "title": "Dynamic Programming - Learn to Solve ...",
                "channel": "NeetCode",
                "video_url": "https://www.youtube.com/watch?v=...",
                "thumbnail_url": "https://img.youtube.com/vi/.../hqdefault.jpg",
                "video_id": "oBt53YbR9Kk",
            },
            ...
        ]
    """
    tavily_key = _get_tavily_key().strip()
    if not tavily_key:
        logger.warning("TAVILY_API_KEY not set — skipping YouTube recommendations")
        return []

    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=tavily_key)

        enriched_query = f"{query} tutorial explained site:youtube.com"
        logger.info("YouTube Tavily search | query='%s'", enriched_query)

        response = client.search(
            query=enriched_query,
            search_depth="basic",
            max_results=8,
            include_domains=["youtube.com"],
        )

        raw_results = response.get("results", [])
        logger.info("YouTube Tavily returned %d raw results", len(raw_results))

        videos: List[Dict[str, str]] = []
        seen_ids: set = set()

        for item in raw_results:
            raw_title = (item.get("title") or "").strip()
            url       = (item.get("url")   or "").strip()

            if not raw_title or not url:
                logger.debug("Skipping result with missing title or URL")
                continue

            video_id = _extract_video_id(url)
            if not video_id:
                logger.debug("Could not extract video ID from URL: %s", url)
                continue

            if video_id in seen_ids:
                logger.debug("Duplicate video ID skipped: %s", video_id)
                continue
            seen_ids.add(video_id)

            # Normalise URL to canonical watch?v= form
            canonical_url = f"https://www.youtube.com/watch?v={video_id}"

            # Best-effort channel extraction: YouTube titles often end with " - ChannelName"
            # e.g. "Dynamic Programming Explained - NeetCode"
            if " - " in raw_title:
                parts   = raw_title.rsplit(" - ", 1)
                title   = parts[0].strip()
                channel = parts[1].strip()
            else:
                title   = raw_title
                channel = "YouTube"

            # Defensive: strip any HTML tags that might appear in Tavily titles
            title   = re.sub(r"<[^>]+>", "", title).strip()
            channel = re.sub(r"<[^>]+>", "", channel).strip()

            video = {
                "title":         title   or raw_title,
                "channel":       channel or "YouTube",
                "video_url":     canonical_url,
                "thumbnail_url": _thumbnail_url(video_id),
                "video_id":      video_id,
            }

            logger.debug("Video data: %s", video)
            videos.append(video)

            if len(videos) == 3:
                break

        logger.info("Returning %d YouTube video(s)", len(videos))
        return videos

    except ImportError:
        logger.error("tavily-python not installed. Run: pip install tavily-python")
        return []
    except Exception as exc:
        logger.error("YouTube search failed: %s", exc)
        return []
