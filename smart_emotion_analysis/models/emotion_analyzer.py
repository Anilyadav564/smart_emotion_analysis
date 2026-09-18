class EmotionAnalyzer:

    def __init__(self):

        self.emotion_keywords = {

            "happiness": [
                "happy",
                "joy",
                "excited",
                "great",
                "wonderful",
                "love",
                "amazing",
                "fantastic",
                "good",
                "awesome",
                "brilliant",
                "helpful",
                "clear",
                "masterclass",
                "perfect",
                "excellent",
                "thank",
                "thanks",
                "appreciate",
                "appreciated",
                "loved",
                "best",
                "inspiring",
                "enjoyed",
                "cool",
                "nice"
            ],

            "sadness": [
                "sad",
                "cry",
                "lonely",
                "unhappy",
                "depressed",
                "heartbroken",
                "upset",
                "bad",
                "disappointed",
                "disappointing",
                "missed",
                "regret",
                "sorry",
                "hopeless",
                "struggled",
                "failed"
            ],

            "anger": [
                "angry",
                "furious",
                "hate",
                "annoyed",
                "frustrated",
                "mad",
                "irritated",
                "garbage",
                "trash",
                "waste",
                "stupid",
                "disaster",
                "horrible",
                "ridiculous",
                "pissed"
            ],

            "fear": [
                "afraid",
                "scared",
                "worried",
                "anxious",
                "terrified",
                "nervous",
                "fear",
                "stress",
                "stressed",
                "panic",
                "overwhelmed",
                "confused",
                "doubt",
                "doubtful",
                "intimidated"
            ],

            "surprise": [
                "surprised",
                "shocked",
                "unexpected",
                "wow",
                "unbelievable",
                "mind-blowing",
                "insane",
                "amazed",
                "astonishing",
                "sudden",
                "remarkable"
            ]
        }


    def analyze(self, text):

        scores = {
            "happiness": 0,
            "sadness": 0,
            "anger": 0,
            "fear": 0,
            "surprise": 0,
            "neutral": 0
        }

        if not text:
            scores["neutral"] = 1
            return "neutral", scores

        words = text.lower().split()

        for emotion, keywords in self.emotion_keywords.items():

            for word in words:
                # Strip simple punctuation from word
                cleaned_w = word.strip(".,!?\"'():;")
                if cleaned_w in keywords:
                    scores[emotion] += 1

        # If no emotion is found
        if max(scores.values()) == 0:
            scores["neutral"] = 1

        # Find emotion with highest score
        detected_emotion = max(scores, key=scores.get)

        return detected_emotion, scores