"""
Curated realistic sample comments for testing and instant demonstration.
Covers diverse sentiment, emotional expressions, constructive criticism,
spam, questions, and toxic edge cases across a popular tutorial video.
"""

SAMPLE_COMMENTS = [
    {
        "author": "CodeCrafter_99",
        "comment_text": "Your explanation of the project was incredibly clear and well paced! I finally understood how the state pipeline works after struggling with it for days. Thank you so much!",
        "likes": 342,
        "reply_count": 14,
        "published_at": "2026-09-02 10:15"
    },
    {
        "author": "DevJourney",
        "comment_text": "The video was really useful overall, but the explanation of step 3 at 08:45 was a bit too fast. Could you consider doing a separate deep dive on authentication next time?",
        "likes": 189,
        "reply_count": 8,
        "published_at": "2026-09-02 11:30"
    },
    {
        "author": "TechEnthusiast_Pro",
        "comment_text": "Best tutorial on this topic on YouTube hands down! The visual architecture diagrams and practical code examples made all the difference.",
        "likes": 275,
        "reply_count": 6,
        "published_at": "2026-09-02 12:05"
    },
    {
        "author": "ElenaR_Dev",
        "comment_text": "At minute 14:20 the microphone volume suddenly dropped. Great content as always, but please check the audio levels in post-production!",
        "likes": 98,
        "reply_count": 3,
        "published_at": "2026-09-02 13:40"
    },
    {
        "author": "RandomUser123",
        "comment_text": "This video is completely useless and a waste of time.",
        "likes": 4,
        "reply_count": 7,
        "published_at": "2026-09-02 14:10"
    },
    {
        "author": "AngryViewer99",
        "comment_text": "You are an idiot who knows nothing about programming. Delete your channel and get lost.",
        "likes": 1,
        "reply_count": 12,
        "published_at": "2026-09-02 14:55"
    },
    {
        "author": "FrontendNinja",
        "comment_text": "Love the clean design and dark mode! Can we get the GitHub repository link for the starter templates mentioned in the video?",
        "likes": 156,
        "reply_count": 5,
        "published_at": "2026-09-02 15:20"
    },
    {
        "author": "CuriousCoder",
        "comment_text": "How do I deploy this to AWS or Docker? What would be the performance impact if we have over 10,000 requests per second?",
        "likes": 64,
        "reply_count": 2,
        "published_at": "2026-09-02 16:00"
    },
    {
        "author": "PythonistaAlex",
        "comment_text": "I was afraid this was going to be overwhelming, but your step-by-step breakdown made it feel effortless. So happy I found your channel!",
        "likes": 112,
        "reply_count": 4,
        "published_at": "2026-09-02 16:45"
    },
    {
        "author": "AudioCritic",
        "comment_text": "The background music was slightly distracting between 04:00 and 07:00, but the coding walkthrough itself was top notch.",
        "likes": 47,
        "reply_count": 1,
        "published_at": "2026-09-02 17:10"
    },
    {
        "author": "TrollAccount",
        "comment_text": "What a piece of garbage trash video. Stupid presenter.",
        "likes": 0,
        "reply_count": 9,
        "published_at": "2026-09-02 18:00"
    },
    {
        "author": "StudentScholar",
        "comment_text": "This literally saved my final year project submission! My professor was amazed by the sentiment analytics demo. Thank you a thousand times!",
        "likes": 210,
        "reply_count": 9,
        "published_at": "2026-09-02 19:15"
    },
    {
        "author": "Sam_V",
        "comment_text": "Timestamp 12:40 was mind-blowing! I had no idea Python could handle batch data processing so cleanly without external heavy dependencies.",
        "likes": 88,
        "reply_count": 2,
        "published_at": "2026-09-02 20:00"
    },
    {
        "author": "FrustratedNewbie",
        "comment_text": "I am so frustrated because I keep getting ModuleNotFoundError on line 12. Could someone please tell me which pip package I need to install?",
        "likes": 35,
        "reply_count": 11,
        "published_at": "2026-09-02 20:30"
    },
    {
        "author": "DataGeek",
        "comment_text": "Would be better if you added a comparison between rule-based VADER and transformer models like RoBERTa in a future episode.",
        "likes": 125,
        "reply_count": 4,
        "published_at": "2026-09-02 21:10"
    },
    {
        "author": "QuickCommenter",
        "comment_text": "Great video!",
        "likes": 18,
        "reply_count": 0,
        "published_at": "2026-09-02 21:40"
    },
    {
        "author": "SpamBot99",
        "comment_text": "first",
        "likes": 2,
        "reply_count": 1,
        "published_at": "2026-09-02 22:00"
    },
    {
        "author": "MayaL",
        "comment_text": "I was surprised how fast the analysis ran on 5,000 comments. Super responsive UI and smooth experience!",
        "likes": 94,
        "reply_count": 3,
        "published_at": "2026-09-02 22:45"
    },
    {
        "author": "Jordan_K",
        "comment_text": "Honestly one of the rare videos where no time is wasted on self-promotion. Straight to the practical knowledge.",
        "likes": 178,
        "reply_count": 5,
        "published_at": "2026-09-03 00:15"
    },
    {
        "author": "BugHunter",
        "comment_text": "Notice a small bug at 22:15 when parsing CSV with comma inside quotes, but you fixed it right away. Excellent debugging demo!",
        "likes": 73,
        "reply_count": 1,
        "published_at": "2026-09-03 01:20"
    },
    {
        "author": "HateSpammer",
        "comment_text": "shut up and stop posting forever you pathetic loser",
        "likes": 0,
        "reply_count": 15,
        "published_at": "2026-09-03 02:00"
    },
    {
        "author": "Sarah_T",
        "comment_text": "Could you provide subtitles or transcripts in Spanish? We have a large student study group following your series from Latin America.",
        "likes": 84,
        "reply_count": 6,
        "published_at": "2026-09-03 03:10"
    },
    {
        "author": "Marcus_Dev",
        "comment_text": "The emotion scoring breakdown gave me an exact picture of how my viewers felt. Absolutely fantastic tool.",
        "likes": 62,
        "reply_count": 2,
        "published_at": "2026-09-03 04:30"
    },
    {
        "author": "ZenithCoder",
        "comment_text": "Watching this in 2026, still the most relevant tutorial on YouTube. Thank you creator!",
        "likes": 140,
        "reply_count": 3,
        "published_at": "2026-09-03 05:00"
    },
    {
        "author": "CriticalThinker",
        "comment_text": "The video was informative, but 35 minutes is too long for this concept. A concise 15-minute summary would be much more accessible for beginners.",
        "likes": 115,
        "reply_count": 8,
        "published_at": "2026-09-03 06:15"
    }
]


def get_demo_comments():
    """Returns a fresh deepcopy list of demo comments."""
    import copy
    return copy.deepcopy(SAMPLE_COMMENTS)
