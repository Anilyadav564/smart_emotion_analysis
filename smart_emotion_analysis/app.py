import io
import json
import csv
from flask import Flask, render_template, request, jsonify, redirect, url_for, Response

from models.analysis_service import AnalysisService
from models.youtube_service import (
    YouTubeService,
    YouTubeAPIKeyMissingError,
    YouTubeCommentsDisabledError,
    YouTubeQuotaExceededError,
    YouTubeVideoNotFoundError,
    YouTubeNoCommentsError,
    YouTubeAPIError
)
from utils.data_manager import DataManager
from utils.comment_parser import CommentParser
from utils.demo_data import get_demo_comments


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload limit

# Initialize core services
analysis_service = AnalysisService()
data_manager = DataManager()
youtube_service = YouTubeService()


# -------------------------------------------------------------
# Helper: Get current session data
# -------------------------------------------------------------
def get_active_session_data(session_id=None):
    """
    Fetches session by ID if provided, otherwise loads most recent session.
    If no sessions exist, initializes and returns demo dataset automatically.
    """
    if session_id:
        sess = data_manager.get_session(session_id)
        if sess:
            return sess

    # Check for latest session in index
    sessions = data_manager.get_sessions()
    if sessions:
        latest_id = sessions[0].get("session_id")
        sess = data_manager.get_session(latest_id)
        if sess:
            return sess

    # Auto-initialize demo data only if absolutely no session exists yet
    demo_comments = get_demo_comments()
    demo_session = analysis_service.analyze_comments(
        demo_comments, video_title="Full-Stack AI Project Tutorial (Demo Data)"
    )
    data_manager.save_session(demo_session)
    return demo_session


# -------------------------------------------------------------
# Existing Single-Text Routes (Preserved & Modernized)
# -------------------------------------------------------------
@app.route("/")
def home():
    """Modern landing page with platform hero, quick text analyzer, and feature highlights."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Original single-text analysis endpoint preserved for 100% backward compatibility."""
    text = request.form.get("text")
    if not text or not text.strip():
        return render_template("index.html", error="Please enter some text to analyze.")

    result = analysis_service.analyze_text(text)
    data_manager.save_result(result)
    return render_template("result.html", result=result)


# -------------------------------------------------------------
# YouTube Comment Intelligence Dashboard Pages
# -------------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    """Main Analytics Dashboard with KPI metrics, charts, top comments, topics, and insights."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "dashboard.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="dashboard"
    )


@app.route("/youtube-comments")
def youtube_comments():
    """Ingestion page for entering YouTube URLs, uploading files, or pasting comments."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "youtube_comments.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="youtube-comments"
    )


@app.route("/comments")
def comments_explorer():
    """Full Comment Explorer table with live search, filters, sorting, and pagination."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "comments.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="comments"
    )


@app.route("/top-comments")
def top_comments():
    """Curated Top Comments: Best Comments, Constructive Feedback, Most Positive, Most Engaged."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "top_comments.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="top-comments"
    )


@app.route("/negative-comments")
def negative_comments():
    """Negative Feedback breakdown: Constructive Criticism vs Toxic vs Critical Complaints."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "negative_comments.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="negative-comments"
    )


@app.route("/emotions")
def emotions():
    """In-depth Emotion Analysis page with dominant emotion badge and dynamic interpretation."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "emotions.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="emotions"
    )


@app.route("/insights")
def insights():
    """AI Audience Insights, friction points, topics, and creator content recommendations."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    all_sessions = data_manager.get_sessions()
    return render_template(
        "insights.html",
        session_data=session_data,
        all_sessions=all_sessions,
        active_tab="insights"
    )


@app.route("/history")
def history():
    """History of YouTube intelligence sessions and individual text logs."""
    all_sessions = data_manager.get_sessions()
    single_text_history = data_manager.get_history()
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    return render_template(
        "history.html",
        sessions=all_sessions,
        single_text_history=list(reversed(single_text_history)),
        session_data=session_data,
        active_tab="history"
    )


@app.route("/report")
def creator_report():
    """Printable / Exportable Executive YouTube Creator Report."""
    session_id = request.args.get("session_id")
    session_data = get_active_session_data(session_id)
    return render_template(
        "creator_report.html",
        session_data=session_data,
        active_tab="report"
    )


# -------------------------------------------------------------
# Real YouTube URL Analysis REST API
# -------------------------------------------------------------
@app.route("/api/analyze-youtube", methods=["POST"])
def api_analyze_youtube():
    """
    Dedicated endpoint for real YouTube Video URL analysis.
    Retrieves real comments & video metadata via YouTube Data API v3.
    NEVER falls back to demo data.
    """
    # Accept URL from JSON payload or form-data
    data = request.get_json(silent=True) or {}
    url = data.get("url") or request.form.get("url") or request.form.get("youtube_url")

    if not url or not str(url).strip():
        return jsonify({"success": False, "error": "Please enter a valid YouTube video URL."}), 400

    try:
        # Step 1: Extract and validate Video ID
        video_id = YouTubeService.extract_video_id(url)
        if not video_id or not YouTubeService.validate_video_id(video_id):
            return jsonify({"success": False, "error": "Please enter a valid YouTube video URL."}), 400

        # Step 2: Retrieve real video metadata and real comments
        video_info, comments = youtube_service.get_video_and_comments(video_id, max_comments=300)

        # Step 3: Run full analysis pipeline on the retrieved comments
        session_data = analysis_service.analyze_comments(
            comments,
            video_title=video_info.get("title", f"YouTube Video ({video_id})"),
            video_info=video_info
        )

        # Step 4: Save session
        data_manager.save_session(session_data)

        return jsonify({
            "success": True,
            "session_id": session_data["session_id"],
            "redirect_url": url_for("dashboard", session_id=session_data["session_id"]),
            "video": video_info,
            "comments": session_data.get("comments"),
            "statistics": session_data.get("metrics"),
            "emotions": session_data.get("metrics", {}).get("emotion_totals"),
            "top_comments": session_data.get("best_comments"),
            "negative_comments": session_data.get("negative_comments"),
            "toxic_comments": session_data.get("toxic_comments"),
            "insights": session_data.get("insights"),
            "topics": session_data.get("topics")
        })

    except YouTubeAPIKeyMissingError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except YouTubeCommentsDisabledError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except YouTubeQuotaExceededError as e:
        return jsonify({"success": False, "error": str(e)}), 429
    except YouTubeVideoNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except YouTubeNoCommentsError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except YouTubeAPIError as e:
        return jsonify({"success": False, "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred during video analysis: {str(e)}"}), 500


# -------------------------------------------------------------
# General Batch Analysis API (Files, Paste, or Demo)
# -------------------------------------------------------------
@app.route("/api/analyze-comments", methods=["POST"])
def api_analyze_comments():
    """
    Ingests and analyzes comments from:
    1. YouTube URL (delegates to YouTube Data API v3, NO fake fallback)
    2. Uploaded CSV file
    3. Uploaded TXT file
    4. Pasted raw text
    5. Explicit demo request
    """
    try:
        video_title = request.form.get("video_title", "").strip() or "Uploaded YouTube Comments"
        raw_comments = []
        video_info = None

        # 1. Check for YouTube URL input -> REAL RETRIEVAL ONLY
        if "youtube_url" in request.form and request.form.get("youtube_url", "").strip():
            url = request.form.get("youtube_url")
            video_id = YouTubeService.extract_video_id(url)
            if not video_id or not YouTubeService.validate_video_id(video_id):
                return jsonify({"error": "Please enter a valid YouTube video URL."}), 400

            # Real API call
            video_info, raw_comments = youtube_service.get_video_and_comments(video_id, max_comments=300)
            video_title = video_info.get("title", video_title)

        # 2. Check for explicit demo request
        elif request.form.get("is_demo") == "true":
            raw_comments = get_demo_comments()
            video_title = "Full-Stack AI Project Tutorial (Demo Data)"
            video_info = {
                "video_id": "demo_video",
                "title": video_title,
                "channel_title": "AI Masterclass",
                "thumbnail_url": "",
                "view_count": 48200,
                "like_count": 3120,
                "comment_count": 25
            }

        # 3. Check for file upload
        elif "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            filename = file.filename.lower()
            file_bytes = file.read()

            if filename.endswith(".csv"):
                raw_comments = CommentParser.parse_csv_content(file_bytes)
            elif filename.endswith(".txt"):
                raw_comments = CommentParser.parse_txt_content(file_bytes)
            elif filename.endswith(".json"):
                try:
                    json_data = json.loads(file_bytes.decode("utf-8"))
                    raw_comments = CommentParser.parse_pasted_text(json.dumps(json_data))
                except Exception as e:
                    return jsonify({"error": f"Invalid JSON file format: {str(e)}"}), 400
            else:
                return jsonify({"error": "Unsupported file type. Please upload a .csv, .txt, or .json file."}), 400

            if not video_title or video_title == "Uploaded YouTube Comments":
                video_title = file.filename.rsplit(".", 1)[0].replace("_", " ").title()

        # 4. Check for pasted text
        elif "pasted_text" in request.form and request.form.get("pasted_text", "").strip():
            pasted_text = request.form.get("pasted_text")
            raw_comments = CommentParser.parse_pasted_text(pasted_text)

        if not raw_comments:
            return jsonify({
                "error": "No comments found. Please provide valid comments or a valid YouTube URL."
            }), 400

        # Execute full analysis pipeline
        session_data = analysis_service.analyze_comments(
            raw_comments,
            video_title=video_title,
            video_info=video_info
        )

        data_manager.save_session(session_data)

        return jsonify({
            "success": True,
            "session_id": session_data["session_id"],
            "total_comments": session_data["total_comments"],
            "redirect_url": url_for("dashboard", session_id=session_data["session_id"]),
            "video": video_info,
            "statistics": session_data.get("metrics"),
            "topics": session_data.get("topics")
        })

    except YouTubeAPIKeyMissingError as e:
        return jsonify({"error": str(e)}), 400
    except YouTubeCommentsDisabledError as e:
        return jsonify({"error": str(e)}), 400
    except YouTubeQuotaExceededError as e:
        return jsonify({"error": str(e)}), 429
    except YouTubeVideoNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except YouTubeNoCommentsError as e:
        return jsonify({"error": str(e)}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except YouTubeAPIError as ye:
        return jsonify({"error": str(ye)}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred during analysis: {str(e)}"}), 500


@app.route("/api/demo-data", methods=["POST", "GET"])
def api_demo_data():
    """Generates and saves a fresh demo analysis session ONLY when explicitly triggered."""
    demo_comments = get_demo_comments()
    session_data = analysis_service.analyze_comments(
        demo_comments, video_title="Full-Stack AI Project Tutorial (Demo Data)"
    )
    data_manager.save_session(session_data)

    if request.method == "POST":
        return jsonify({
            "success": True,
            "session_id": session_data["session_id"],
            "redirect_url": url_for("dashboard", session_id=session_data["session_id"])
        })
    return redirect(url_for("dashboard", session_id=session_data["session_id"]))


@app.route("/api/session/<session_id>")
def api_get_session(session_id):
    """Fetches full session JSON."""
    session = data_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


@app.route("/api/history")
def api_get_history():
    """Lists all saved sessions."""
    return jsonify(data_manager.get_sessions())


@app.route("/api/history/<session_id>", methods=["DELETE"])
def api_delete_history(session_id):
    """Deletes a session."""
    success = data_manager.delete_session(session_id)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Failed to delete session or session not found"}), 404


@app.route("/api/export/<session_id>")
def api_export_session(session_id):
    """Exports session comments as CSV or JSON."""
    fmt = request.args.get("format", "csv").lower()
    session = data_manager.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    filename = f"youtube_comments_{session_id}"

    if fmt == "json":
        json_str = json.dumps(session, indent=2)
        return Response(
            json_str,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename={filename}.json"}
        )
    else:  # CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Comment ID", "Video ID", "Author", "Comment Text", "Likes", "Published At",
            "Sentiment", "Compound Score", "Primary Emotion", "Quality Score",
            "Quality Grade", "Feedback Type", "Toxicity Status", "Toxicity Score",
            "Analysis Explanation"
        ])

        for c in session.get("comments", []):
            writer.writerow([
                c.get("comment_id", ""),
                c.get("video_id", ""),
                c.get("author", ""),
                c.get("comment_text", ""),
                c.get("likes", 0),
                c.get("published_at", ""),
                c.get("sentiment", ""),
                c.get("sentiment_scores", {}).get("compound", 0.0),
                c.get("primary_emotion", ""),
                c.get("quality", {}).get("quality_score", 0),
                c.get("quality", {}).get("quality_grade", ""),
                c.get("quality", {}).get("feedback_type", ""),
                c.get("toxicity", {}).get("status", ""),
                c.get("toxicity", {}).get("toxicity_score", 0.0),
                c.get("quality", {}).get("explanation", "")
            ])

        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}.csv"}
        )


if __name__ == "__main__":
    app.run(debug=True)