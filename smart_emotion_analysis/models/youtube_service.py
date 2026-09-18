import os
import re
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class YouTubeAPIError(Exception):
    """Base exception for YouTube API errors."""
    pass


class YouTubeAPIKeyMissingError(YouTubeAPIError):
    """Raised when the YOUTUBE_API_KEY is not set or is still the placeholder."""
    pass


class YouTubeVideoNotFoundError(YouTubeAPIError):
    """Raised when a video is private, deleted, or does not exist."""
    pass


class YouTubeCommentsDisabledError(YouTubeAPIError):
    """Raised when the video creator has disabled comments."""
    pass


class YouTubeQuotaExceededError(YouTubeAPIError):
    """Raised when the YouTube Data API v3 quota is exhausted."""
    pass


class YouTubeNoCommentsError(YouTubeAPIError):
    """Raised when a video has zero public comments."""
    pass


class YouTubeService:
    """
    Dedicated service for YouTube Data API v3 integration:
    - URL parsing & 11-char video ID extraction
    - Video metadata retrieval (title, channel, views, likes, thumbnail)
    - Comment thread retrieval with pagination
    - Fine-grained API error handling
    - Video-ID-isolated caching
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        # Isolated cache keyed strictly by video_id: { video_id: { "video_info": ..., "comments": ..., "cached_at": ... } }
        self._cache = {}
        self.cache_ttl_seconds = 600  # 10 minutes cache per video_id

    def get_api_key(self) -> str:
        """
        Retrieves YOUTUBE_API_KEY from environment or .env file.
        Raises YouTubeAPIKeyMissingError if absent or placeholder.
        """
        # Reload dotenv in case .env was edited while app is running
        load_dotenv()
        key = os.getenv("YOUTUBE_API_KEY") or os.getenv("YOUTUBE_DATA_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key or not key.strip() or "your_api_key_here" in key:
            raise YouTubeAPIKeyMissingError(
                "YouTube API configuration is missing. Please configure YOUTUBE_API_KEY in your .env file."
            )
        return key.strip()

    @staticmethod
    def extract_video_id(url_or_id: str) -> str:
        """
        Extracts 11-character YouTube video ID from various URL formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/shorts/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/live/VIDEO_ID
        - Raw 11-char ID
        """
        if not url_or_id or not isinstance(url_or_id, str):
            return ""

        trimmed = url_or_id.strip()

        # Check for bare 11-character ID
        if re.match(r"^[0-9A-Za-z_-]{11}$", trimmed):
            return trimmed

        patterns = [
            r"(?:v=|\/v\/|youtu\.be\/|embed\/|shorts\/|live\/)([0-9A-Za-z_-]{11})",
            r"(?:[?&]v=)([0-9A-Za-z_-]{11})"
        ]

        for p in patterns:
            match = re.search(p, trimmed)
            if match:
                return match.group(1)

        return ""

    @staticmethod
    def validate_video_id(video_id: str) -> bool:
        """Validates that a video ID is 11 characters matching standard YouTube characters."""
        if not video_id:
            return False
        return bool(re.match(r"^[0-9A-Za-z_-]{11}$", video_id))

    def fetch_video_details(self, video_id: str, api_key: str = None) -> dict:
        """
        Retrieves video metadata (title, channel, views, likes, comments, thumbnail)
        via YouTube Data API v3 videos.list endpoint.
        """
        if not api_key:
            api_key = self.get_api_key()

        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "snippet,statistics",
            "id": video_id,
            "key": api_key
        }

        try:
            resp = requests.get(url, params=params, timeout=12)
        except requests.RequestException as e:
            raise YouTubeAPIError(f"Network error connecting to YouTube API: {str(e)}")

        if resp.status_code == 400:
            raise YouTubeVideoNotFoundError("Invalid video request or video ID format.")
        elif resp.status_code == 403:
            self._handle_forbidden_error(resp)
        elif resp.status_code == 404:
            raise YouTubeVideoNotFoundError("YouTube video not found. Please check the URL.")
        elif resp.status_code != 200:
            raise YouTubeAPIError(f"YouTube API returned HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        items = data.get("items", [])
        if not items:
            raise YouTubeVideoNotFoundError("Unable to find video. It may be private, deleted, or unlisted.")

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        thumbnails = snippet.get("thumbnails", {})

        # Select highest resolution available thumbnail
        thumb_url = ""
        for quality in ["maxres", "standard", "high", "medium", "default"]:
            if quality in thumbnails:
                thumb_url = thumbnails[quality].get("url", "")
                break
        if not thumb_url:
            thumb_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

        return {
            "video_id": video_id,
            "title": snippet.get("title", "YouTube Video"),
            "channel_title": snippet.get("channelTitle", "Unknown Channel"),
            "published_at": snippet.get("publishedAt", ""),
            "description": snippet.get("description", "")[:200],
            "thumbnail_url": thumb_url,
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0))
        }

    def fetch_video_comments(self, video_id: str, max_comments: int = 300, api_key: str = None) -> list:
        """
        Retrieves real comments for the exact video_id using commentThreads.list with pagination.
        Every returned comment is associated strictly with this video_id.
        """
        if not api_key:
            api_key = self.get_api_key()

        url = f"{self.BASE_URL}/commentThreads"
        comments = []
        next_page_token = None

        while len(comments) < max_comments:
            # Calculate fetch size for this page (max 100 per YouTube API limit)
            page_size = min(100, max_comments - len(comments))

            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": page_size,
                "textFormat": "plainText",
                "order": "relevance",
                "key": api_key
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            try:
                resp = requests.get(url, params=params, timeout=12)
            except requests.RequestException as e:
                raise YouTubeAPIError(f"Network error while retrieving comments: {str(e)}")

            if resp.status_code == 403:
                self._handle_forbidden_error(resp)
            elif resp.status_code == 404:
                raise YouTubeVideoNotFoundError("Video or comment thread not found.")
            elif resp.status_code != 200:
                raise YouTubeAPIError(f"YouTube API returned HTTP {resp.status_code}: {resp.text}")

            data = resp.json()
            items = data.get("items", [])
            if not items and len(comments) == 0:
                raise YouTubeNoCommentsError(
                    "No comments were found for this video. Comments may be disabled or none have been posted yet."
                )

            for item in items:
                top_comment = item.get("snippet", {}).get("topLevelComment", {})
                snippet = top_comment.get("snippet", {})
                raw_text = snippet.get("textDisplay", "").strip()
                if not raw_text:
                    continue

                comment_obj = {
                    "comment_id": top_comment.get("id") or item.get("id"),
                    "author": snippet.get("authorDisplayName") or "Anonymous Viewer",
                    "comment_text": raw_text,
                    "likes": int(snippet.get("likeCount", 0)),
                    "published_at": snippet.get("publishedAt", ""),
                    "updated_at": snippet.get("updatedAt", ""),
                    "reply_count": int(item.get("snippet", {}).get("totalReplyCount", 0)),
                    "video_id": video_id
                }
                comments.append(comment_obj)

            next_page_token = data.get("nextPageToken")
            if not next_page_token or not items:
                break

        if not comments:
            raise YouTubeNoCommentsError(
                "No public comments were found for this video. Comments may be disabled or empty."
            )

        return comments

    def get_video_and_comments(self, url_or_id: str, max_comments: int = 300, use_cache: bool = True) -> tuple[dict, list]:
        """
        End-to-end pipeline:
        1. Extract video ID
        2. Validate ID
        3. Check isolated cache for this video_id
        4. Fetch video metadata
        5. Fetch real comments
        6. Store in cache[video_id]
        Returns (video_info, comments)
        """
        video_id = self.extract_video_id(url_or_id)
        if not video_id or not self.validate_video_id(video_id):
            raise ValueError("Please enter a valid YouTube video URL.")

        # Check video-specific cache
        now = time.time()
        if use_cache and video_id in self._cache:
            entry = self._cache[video_id]
            if (now - entry.get("cached_at", 0)) < self.cache_ttl_seconds:
                return entry["video_info"], entry["comments"]

        api_key = self.get_api_key()

        # Step 1: Retrieve Video Info
        video_info = self.fetch_video_details(video_id, api_key)

        # Step 2: Retrieve Comments
        comments = self.fetch_video_comments(video_id, max_comments, api_key)

        # Cache strictly under this video_id
        self._cache[video_id] = {
            "video_info": video_info,
            "comments": comments,
            "cached_at": now
        }

        return video_info, comments

    def clear_cache_for_video(self, video_id: str):
        """Clears cached data for a specific video ID."""
        if video_id in self._cache:
            del self._cache[video_id]

    def _handle_forbidden_error(self, resp: requests.Response):
        """Parses 403 error details to provide exact, user-friendly messages."""
        try:
            err_data = resp.json().get("error", {})
            errors = err_data.get("errors", [])
            for e in errors:
                reason = e.get("reason", "")
                if reason == "commentsDisabled":
                    raise YouTubeCommentsDisabledError("Comments are disabled for this video.")
                elif reason in ["quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"]:
                    raise YouTubeQuotaExceededError(
                        "YouTube API quota has been exceeded. Please try again later or check your API configuration."
                    )
                elif reason in ["videoNotFound", "forbidden"]:
                    raise YouTubeVideoNotFoundError("This video is unavailable or private.")
            
            message = err_data.get("message", "Access denied by YouTube API.")
            raise YouTubeAPIError(f"YouTube API access error: {message}")
        except (ValueError, KeyError):
            raise YouTubeAPIError("Access denied by YouTube API (403 Forbidden).")
