"""
Tavily web-search helper for Placement Prep Assistant.

Provides get_useful_links(query) which returns up to 3 curated,
clickable resources from trusted educational domains
(GeeksforGeeks, W3Schools, Programiz, JavaTPoint).

Design decisions:
  - Completely decoupled from RAG pipeline — imported independently.
  - Fails silently: any Tavily error returns [] so the app never crashes.
  - Query is enriched with "explained tutorial for beginners" to bias
    Tavily toward introductory, beginner-friendly pages.
  - Domain whitelist is applied client-side as a post-filter on top of
    Tavily's own include_domains parameter for maximum reliability.
"""

import os
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
