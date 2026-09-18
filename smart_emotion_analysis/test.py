from models.analysis_service import AnalysisService
from utils.data_manager import DataManager


service = AnalysisService()
data_manager = DataManager()

text = """
I am very happy today because I completed my project.
However, I am also nervous about my presentation tomorrow.
"""

# Analyze text
result = service.analyze_text(text)

# Save result to JSON
data_manager.save_result(result)

# Display result
print("\n----- SMART EMOTION ANALYSIS -----\n")

print("Original Text:\n")
print(text)

print("\nCleaned Text:")
print(result["cleaned_text"])

print("\nPrimary Emotion:")
print(result["primary_emotion"])

print("\nSentiment:")
print(result["sentiment"])

print("\nEmotion Scores:")

for emotion, score in result["emotion_scores"].items():
    print(f"{emotion} : {score}")

print("\nSentiment Scores:")

for sentiment, score in result["sentiment_scores"].items():
    print(f"{sentiment} : {score}")

print("\nResult saved successfully!")