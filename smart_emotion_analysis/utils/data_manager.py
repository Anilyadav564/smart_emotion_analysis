import json
import os
from datetime import datetime


class DataManager:
    """
    Manages persistence for:
    1. Single-text sentiment/emotion results (backward-compatible with data/analysis_history.json)
    2. Batch YouTube comment intelligence sessions (data/sessions/)
    """

    def __init__(self):
        self.data_dir = "data"
        self.file_path = os.path.join(self.data_dir, "analysis_history.json")
        self.sessions_dir = os.path.join(self.data_dir, "sessions")
        self.sessions_index_path = os.path.join(self.data_dir, "sessions_index.json")

        # Create data folders if they do not exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.sessions_dir, exist_ok=True)

        # Create JSON history file if it does not exist or is empty
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump([], file)

        # Create sessions index if it does not exist
        if not os.path.exists(self.sessions_index_path) or os.path.getsize(self.sessions_index_path) == 0:
            with open(self.sessions_index_path, "w", encoding="utf-8") as file:
                json.dump([], file)

    # -------------------------------------------------------------
    # Single Text Analysis (Existing functionality preserved)
    # -------------------------------------------------------------
    def save_result(self, result):
        """Saves a single text analysis result."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = []

        if "timestamp" not in result:
            result["timestamp"] = str(datetime.now())

        data.append(result)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def get_history(self):
        """Retrieves history of single text analyses."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return []

    # -------------------------------------------------------------
    # YouTube Intelligence Sessions
    # -------------------------------------------------------------
    def save_session(self, session_data: dict):
        """Saves full session data and updates the sessions index."""
        session_id = session_data.get("session_id")
        if not session_id:
            return

        full_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)
        except OSError as e:
            print(f"Error saving session file: {e}")

        metrics = session_data.get("metrics", {})
        video_info = session_data.get("video_info", {})
        summary = {
            "session_id": session_id,
            "video_id": session_data.get("video_id") or video_info.get("video_id", ""),
            "video_title": session_data.get("video_title", "YouTube Video Analysis"),
            "channel_name": session_data.get("channel_name") or video_info.get("channel_title", "YouTube Channel"),
            "thumbnail_url": video_info.get("thumbnail_url", ""),
            "timestamp": session_data.get("timestamp", str(datetime.now())),
            "total_comments": session_data.get("total_comments", 0),
            "positive_percentage": metrics.get("positive_percentage", 0.0),
            "neutral_percentage": metrics.get("neutral_percentage", 0.0),
            "negative_percentage": metrics.get("negative_percentage", 0.0),
            "toxicity_percentage": metrics.get("toxicity_percentage", 0.0),
            "average_quality": metrics.get("average_quality", 0.0),
            "dominant_emotion": metrics.get("dominant_emotion", "neutral")
        }

        index = self.get_sessions()
        existing_idx = next((i for i, s in enumerate(index) if s.get("session_id") == session_id), None)
        if existing_idx is not None:
            index[existing_idx] = summary
        else:
            index.insert(0, summary)

        try:
            with open(self.sessions_index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=4)
        except OSError as e:
            print(f"Error saving sessions index: {e}")

    def get_sessions(self) -> list:
        """Returns list of session summaries sorted newest first."""
        try:
            with open(self.sessions_index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def get_session(self, session_id: str) -> dict:
        """Loads complete session data by session_id."""
        full_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading session {session_id}: {e}")
        return None

    def delete_session(self, session_id: str) -> bool:
        """Deletes a session file and its index record."""
        full_path = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except OSError:
                pass

        index = self.get_sessions()
        updated = [s for s in index if s.get("session_id") != session_id]
        try:
            with open(self.sessions_index_path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=4)
            return True
        except OSError:
            return False