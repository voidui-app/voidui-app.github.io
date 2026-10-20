"""
Zero-dependency RSS 2.0 and Atom Feed Parser with In-Memory Caching.
Standard library only (urllib + xml.etree.ElementTree).
"""

import re
import ssl
import time
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any


def strip_tags(html_str: str) -> str:
    """Removes HTML tags and unescapes entities for clean summary snippets."""
    if not html_str:
        return ""
    clean = re.sub(r"<[^>]+>", " ", html_str)
    clean = html.unescape(clean)
    return " ".join(clean.split())


class RSSFeedParser:
    """Parses RSS 2.0 and Atom feeds into a standardized dictionary format."""

    @staticmethod
    def fetch_xml(url: str, timeout: int = 8) -> str:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "VoidUI-RSS-Daemon/1.0 (+https://github.com/voidui)",
                "Accept": "application/rss+xml, application/atom+xml, text/xml, application/xml, */*"
            }
        )
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            raw_bytes = resp.read()
            # Try utf-8 first, fallback to latin-1
            try:
                return raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return raw_bytes.decode("latin-1", errors="replace")

    @classmethod
    def parse_feed(cls, feed_id: str, title: str, icon: str, url: str) -> Dict[str, Any]:
        """Fetches and parses a single feed into category structure."""
        items = []
        try:
            xml_text = cls.fetch_xml(url)
            root = ET.fromstring(xml_text)
            
            # Detect RSS 2.0 vs Atom
            if root.tag.endswith("feed"):
                items = cls._parse_atom(root, feed_id, title)
            else:
                items = cls._parse_rss(root, feed_id, title)
        except Exception as e:
            # Fallback mock items if network/parse fails
            items = cls._get_offline_items(feed_id, title, str(e))

        return {
            "id": feed_id,
            "title": title,
            "icon": icon,
            "badge": len(items),
            "items": items
        }

    @staticmethod
    def _parse_rss(root: ET.Element, feed_id: str, feed_title: str) -> List[Dict[str, Any]]:
        items = []
        channel = root.find("channel") or root
        
        for idx, item in enumerate(channel.findall("item")):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pubdate_el = item.find("pubDate")
            author_el = item.find("{http://purl.org/dc/elements/1.1/}creator") or item.find("author")

            title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled Article"
            link = link_el.text.strip() if link_el is not None and link_el.text else "#"
            desc = desc_el.text.strip() if desc_el is not None and desc_el.text else "No description provided."
            pubdate = pubdate_el.text.strip() if pubdate_el is not None and pubdate_el.text else "Recent"
            author = author_el.text.strip() if author_el is not None and author_el.text else feed_title

            clean_snippet = strip_tags(desc)[:160] + ("..." if len(strip_tags(desc)) > 160 else "")

            # Formatted readable HTML content for Reader pane
            content_html = f"""
            <div class="article-reader">
              <h2>{html.escape(title)}</h2>
              <div class="article-meta" style="color: #64748b; font-size: 13px; margin: 8px 0 16px 0;">
                <span>By <strong>{html.escape(author)}</strong></span> &bull; 
                <span>Published: {html.escape(pubdate)}</span> &bull;
                <span>Source: {html.escape(feed_title)}</span>
              </div>
              <div class="article-body" style="line-height: 1.6; font-size: 15px;">
                {desc}
              </div>
              <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0;">
                <a href="{link}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 13px;">Open Full Source Article &rarr;</a>
              </div>
            </div>
            """

            items.append({
                "id": f"{feed_id}-item-{idx}",
                "title": title,
                "subtitle": f"{feed_title} &bull; {pubdate}",
                "preview": clean_snippet,
                "content": content_html,
                "url": link,
                "meta": {
                    "author": author,
                    "published": pubdate,
                    "feed": feed_title
                }
            })
            if len(items) >= 25:
                break
        return items

    @staticmethod
    def _parse_atom(root: ET.Element, feed_id: str, feed_title: str) -> List[Dict[str, Any]]:
        items = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        entries = root.findall("atom:entry", ns) or root.findall("entry")
        for idx, entry in enumerate(entries):
            title_el = entry.find("atom:title", ns) or entry.find("title")
            link_el = entry.find("atom:link", ns) or entry.find("link")
            summary_el = entry.find("atom:summary", ns) or entry.find("atom:content", ns) or entry.find("summary") or entry.find("content")
            updated_el = entry.find("atom:updated", ns) or entry.find("updated")

            title = title_el.text.strip() if title_el is not None and title_el.text else "Untitled Entry"
            link = link_el.attrib.get("href", "#") if link_el is not None and "href" in link_el.attrib else (link_el.text if link_el is not None and link_el.text else "#")
            desc = summary_el.text.strip() if summary_el is not None and summary_el.text else "No content summary provided."
            pubdate = updated_el.text.strip() if updated_el is not None and updated_el.text else "Recent"

            clean_snippet = strip_tags(desc)[:160] + ("..." if len(strip_tags(desc)) > 160 else "")

            content_html = f"""
            <div class="article-reader">
              <h2>{html.escape(title)}</h2>
              <div class="article-meta" style="color: #64748b; font-size: 13px; margin: 8px 0 16px 0;">
                <span>Source: <strong>{html.escape(feed_title)}</strong></span> &bull; 
                <span>Updated: {html.escape(pubdate)}</span>
              </div>
              <div class="article-body" style="line-height: 1.6; font-size: 15px;">
                {desc}
              </div>
              <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0;">
                <a href="{link}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background: #2563eb; color: #ffffff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; font-size: 13px;">Open Full Source Article &rarr;</a>
              </div>
            </div>
            """

            items.append({
                "id": f"{feed_id}-item-{idx}",
                "title": title,
                "subtitle": f"{feed_title} &bull; {pubdate}",
                "preview": clean_snippet,
                "content": content_html,
                "url": link,
                "meta": {
                    "author": feed_title,
                    "published": pubdate,
                    "feed": feed_title
                }
            })
            if len(items) >= 25:
                break
        return items

    @staticmethod
    def _get_offline_items(feed_id: str, feed_title: str, reason: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": f"{feed_id}-offline-1",
                "title": f"Welcome to {feed_title} (Cached Overview)",
                "subtitle": f"{feed_title} &bull; Offline Mode",
                "preview": f"Feed data could not be reached ({reason}). Demonstrating offline resilience.",
                "content": f"""
                <div class="article-reader">
                  <h2>{feed_title} Offline Overview</h2>
                  <p style="color: #f59e0b; background: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 6px;">
                    ⚠️ Live feed network notice: {html.escape(reason)}
                  </p>
                  <p>VoidUI seamlessly preserves the 3-pane workstation layout even when offline.</p>
                </div>
                """,
                "url": "https://voidui.dev",
                "meta": {
                    "author": "System",
                    "published": "Now",
                    "feed": feed_title
                }
            }
        ]


class MultiFeedAggregator:
    """Manages cooking 3 configured RSS feeds with in-memory caching."""

    FEEDS_CONFIG = [
        {
            "id": "bbc_world",
            "title": "BBC World News",
            "icon": "🌍",
            "url": "https://feeds.bbci.co.uk/news/world/rss.xml"
        },
        {
            "id": "ars_technica",
            "title": "Ars Technica",
            "icon": "💻",
            "url": "https://feeds.arstechnica.com/arstechnica/index"
        },
        {
            "id": "python_insider",
            "title": "Python Developer Blog",
            "icon": "🐍",
            "url": "https://blog.python.org/feeds/posts/default?alt=rss"
        }
    ]

    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cached_payload = None
        self._last_fetched_at = 0

    def get_cooked_feeds(self, force_refresh: bool = False) -> Dict[str, Any]:
        now = time.time()
        if not force_refresh and self._cached_payload and (now - self._last_fetched_at < self.ttl):
            return self._cached_payload

        categories = []
        for conf in self.FEEDS_CONFIG:
            cat = RSSFeedParser.parse_feed(
                feed_id=conf["id"],
                title=conf["title"],
                icon=conf["icon"],
                url=conf["url"]
            )
            categories.append(cat)

        payload = {
            "type": "json",
            "layout": "3pane",
            "title": "VoidUI RSS Multi-Feed Reader",
            "updated_at": datetime.now().isoformat(),
            "ttl_seconds": self.ttl,
            "categories": categories
        }

        self._cached_payload = payload
        self._last_fetched_at = now
        return payload
