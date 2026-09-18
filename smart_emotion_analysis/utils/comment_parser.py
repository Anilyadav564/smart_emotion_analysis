import csv
import io
import json
import re
import uuid
from datetime import datetime


class CommentParser:
    """
    Parses and standardizes YouTube comments from multiple sources:
    - Textarea pasted raw text
    - CSV files (smart column detection)
    - TXT files (line-by-line or paragraph-by-paragraph)
    - YouTube URL validation & metadata extraction placeholder
    """

    # Common aliases for comment text columns in CSV
    TEXT_COL_CANDIDATES = [
        "comment_text", "comment", "text", "body", "content", "comments",
        "message", "review", "statement", "feedback"
    ]
    # Aliases for author column
    AUTHOR_COL_CANDIDATES = [
        "author", "user", "username", "author_name", "channel", "name", "commenter"
    ]
    # Aliases for likes column
    LIKES_COL_CANDIDATES = [
        "likes", "like_count", "likes_count", "upvotes", "thumbs_up", "votes"
    ]
    # Aliases for published date
    DATE_COL_CANDIDATES = [
        "published_at", "date", "created_at", "timestamp", "time", "published"
    ]
    # Aliases for replies count
    REPLY_COL_CANDIDATES = [
        "reply_count", "replies", "total_replies", "responses"
    ]

    @staticmethod
    def parse_pasted_text(text: str) -> list:
        """
        Parses pasted text. Supports:
        1. JSON array of objects or strings
        2. Blank-line separated comments
        3. Line-by-line comments
        """
        if not text or not text.strip():
            return []

        cleaned = text.strip()

        # Check if user pasted a JSON string
        if cleaned.startswith("[") and cleaned.endswith("]"):
            try:
                parsed_json = json.loads(cleaned)
                comments = []
                for item in parsed_json:
                    if isinstance(item, str) and item.strip():
                        comments.append(CommentParser._standardize_comment(item))
                    elif isinstance(item, dict):
                        txt = item.get("comment_text") or item.get("text") or item.get("comment") or ""
                        if txt.strip():
                            comments.append(CommentParser._standardize_comment(
                                text=txt,
                                author=item.get("author"),
                                likes=item.get("likes", 0),
                                published_at=item.get("published_at"),
                                reply_count=item.get("reply_count", 0)
                            ))
                if comments:
                    return comments
            except Exception:
                pass  # Fall through to line/paragraph parsing

        # Check if separated by double newlines
        if "\n\n" in cleaned:
            blocks = [b.strip() for b in re.split(r"\n\s*\n", cleaned) if b.strip()]
            if len(blocks) > 1:
                return [CommentParser._standardize_comment(b) for b in blocks]

        # Line-by-line parsing
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        return [CommentParser._standardize_comment(line) for line in lines]

    @staticmethod
    def parse_csv_content(content_bytes: bytes) -> list:
        """
        Parses CSV data from bytes, trying UTF-8, Latin-1, CP1252 encodings.
        Intelligently discovers header names for comment text, author, likes, etc.
        """
        if not content_bytes:
            return []

        # Decode with fallback encodings
        text = None
        for enc in ["utf-8-sig", "utf-8", "latin-1", "cp1252"]:
            try:
                text = content_bytes.decode(enc)
                break
            except UnicodeDecodeError:
                continue

        if not text:
            raise ValueError("Could not decode CSV file. Please ensure it is saved with UTF-8 encoding.")

        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return []

        header = [col.strip().lower() for col in rows[0]]

        # Try to locate column indices
        text_idx = CommentParser._find_column_index(header, CommentParser.TEXT_COL_CANDIDATES)
        author_idx = CommentParser._find_column_index(header, CommentParser.AUTHOR_COL_CANDIDATES)
        likes_idx = CommentParser._find_column_index(header, CommentParser.LIKES_COL_CANDIDATES)
        date_idx = CommentParser._find_column_index(header, CommentParser.DATE_COL_CANDIDATES)
        reply_idx = CommentParser._find_column_index(header, CommentParser.REPLY_COL_CANDIDATES)

        start_row = 1
        # If no recognized header found, but first row has text, maybe there is no header
        if text_idx is None:
            # Check if first column has text strings
            if len(rows[0]) > 0:
                text_idx = 0
                start_row = 0
            else:
                raise ValueError("Could not find a comment text column in the CSV. Looked for: 'comment', 'text', 'body', etc.")

        comments = []
        for r_idx in range(start_row, len(rows)):
            row = rows[r_idx]
            if not row or text_idx >= len(row):
                continue
            comment_text = row[text_idx].strip()
            if not comment_text:
                continue

            author = row[author_idx].strip() if author_idx is not None and author_idx < len(row) else None
            likes_val = 0
            if likes_idx is not None and likes_idx < len(row):
                try:
                    likes_val = int(re.sub(r"[^\d]", "", row[likes_idx]) or 0)
                except Exception:
                    likes_val = 0

            date_val = row[date_idx].strip() if date_idx is not None and date_idx < len(row) else None
            reply_val = 0
            if reply_idx is not None and reply_idx < len(row):
                try:
                    reply_val = int(re.sub(r"[^\d]", "", row[reply_idx]) or 0)
                except Exception:
                    reply_val = 0

            comments.append(CommentParser._standardize_comment(
                text=comment_text,
                author=author,
                likes=likes_val,
                published_at=date_val,
                reply_count=reply_val
            ))

        return comments

    @staticmethod
    def parse_txt_content(content_bytes: bytes) -> list:
        """
        Parses plain text file.
        Supports UTF-8 / Latin-1 and splits by double newline or line-by-line.
        """
        text = None
        for enc in ["utf-8-sig", "utf-8", "latin-1"]:
            try:
                text = content_bytes.decode(enc)
                break
            except UnicodeDecodeError:
                continue

        if not text:
            raise ValueError("Unable to read TXT file encoding.")

        return CommentParser.parse_pasted_text(text)

    @staticmethod
    def extract_youtube_video_id(url_or_id: str) -> str:
        """
        Extracts YouTube video ID from various URL formats or returns raw ID.
        e.g. youtube.com/watch?v=dQw4w9WgXcQ -> dQw4w9WgXcQ
             youtu.be/dQw4w9WgXcQ -> dQw4w9WgXcQ
             youtube.com/shorts/dQw4w9WgXcQ -> dQw4w9WgXcQ
        """
        if not url_or_id:
            return ""
        trimmed = url_or_id.strip()

        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)",
            r"youtu\.be\/([0-9A-Za-z_-]{11})",
            r"youtube\.com\/embed\/([0-9A-Za-z_-]{11})",
            r"youtube\.com\/shorts\/([0-9A-Za-z_-]{11})"
        ]
        for p in patterns:
            match = re.search(p, trimmed)
            if match:
                return match.group(1)

        # If user directly provided an 11-char ID
        if re.match(r"^[0-9A-Za-z_-]{11}$", trimmed):
            return trimmed

        return ""

    @staticmethod
    def _find_column_index(header: list, candidates: list):
        for candidate in candidates:
            for idx, col in enumerate(header):
                if col == candidate or candidate in col:
                    return idx
        return None

    @staticmethod
    def _standardize_comment(text: str, author: str = None, likes: int = 0,
                              published_at: str = None, reply_count: int = 0) -> dict:
        """Standardizes comment dictionary structure."""
        return {
            "comment_id": "c_" + uuid.uuid4().hex[:8],
            "author": author if author and author.strip() else "Anonymous Viewer",
            "comment_text": text.strip(),
            "likes": int(likes) if likes else 0,
            "published_at": published_at if published_at else datetime.now().strftime("%Y-%m-%d %H:%M"),
            "reply_count": int(reply_count) if reply_count else 0
        }
