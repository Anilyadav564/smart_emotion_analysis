# 🎯 Smart Emotion Analysis – YouTube Comment Intelligence Platform

A **Flask-based web application** that analyzes YouTube comments using **Natural Language Processing (NLP)** to understand audience sentiment, emotions, toxicity, comment quality, and content insights.

The project helps creators understand **what their audience feels, what they are talking about, and which comments need attention**.

---

## 🚀 Features

### 1. 😊 Sentiment Analysis

Analyzes comments and identifies:

* Positive
* Negative
* Neutral

The system also provides a sentiment score to understand the strength of the sentiment.

### 2. 💭 Emotion Analysis

Identifies emotions expressed in comments, including:

* Joy / Happiness
* Sadness
* Anger
* Fear / Anxiety
* Surprise
* Disgust
* Neutral

### 3. 🛡️ Toxicity Detection

Detects potentially harmful content such as:

* Threats
* Insults
* Harassment
* Profanity
* Hate-related content

The system helps identify comments that may require moderation.

### 4. 📊 Comment Quality Analysis

Comments can be evaluated based on factors such as:

* Substance
* Specificity
* Constructiveness
* Sentiment alignment
* Engagement value

A quality score is generated to help identify useful and meaningful comments.

### 5. 🔍 Topic Intelligence

The application analyzes frequently discussed topics and keywords.

It provides:

* Important keywords
* Unigrams
* Bigrams
* Mention counts
* Sentiment distribution
* Dominant sentiment
* Supporting comments

### 6. 💡 Creator Insights

The system provides actionable insights for content creators, such as:

* Comments requiring attention
* Content opportunities
* Positive audience signals
* Moderation suggestions
* Content recommendations

### 7. 📈 Dashboard

The dashboard provides an overall view of the analyzed comments, including:

* Total comments
* Sentiment distribution
* Emotion distribution
* Toxicity information
* Comment quality
* Important topics

### 8. 📁 Comment Management

The application supports analyzing and viewing comments through the web interface.

Users can explore comments based on different analysis results.

### 9. 📄 Creator Report

The application provides a structured report containing the main findings from the comment analysis.

---

## 🏗️ Project Architecture

```text
smart_emotion_analysis/
│
├── app.py
├── .env.example
├── .gitignore
│
├── models/
│   ├── analysis_service.py
│   ├── comment_analyzer.py
│   ├── sentiment_analyzer.py
│   ├── emotion_analyzer.py
│   ├── toxicity_analyzer.py
│   ├── quality_scorer.py
│   └── youtube_service.py
│
├── utils/
│   ├── text_preprocessing.py
│   ├── comment_parser.py
│   ├── data_manager.py
│   └── demo_data.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   ├── youtube_comments.html
│   ├── comments.html
│   ├── top_comments.html
│   ├── negative_comments.html
│   ├── emotions.html
│   ├── insights.html
│   ├── history.html
│   └── creator_report.html
│
├── static/
│   ├── style.css
│   └── app.js
│
├── data/
│   └── sessions/
│
└── analysis_history.json
```

---

## 🔄 How the Project Works

```text
YouTube Comments / Input
          ↓
    Comment Collection
          ↓
   Text Preprocessing
          ↓
      NLP Analysis
          ↓
 ┌────────┬────────┬────────┐
 ↓        ↓        ↓        ↓
Sentiment Emotion Toxicity Quality
 └────────┴────────┴────────┘
          ↓
    Topic Analysis
          ↓
   Insights & Dashboard
          ↓
      Creator Report
```

---

## 🧠 Technologies Used

| Technology    | Purpose                    |
| ------------- | -------------------------- |
| Python        | Main programming language  |
| Flask         | Web application framework  |
| NLP           | Text and comment analysis  |
| VADER         | Sentiment analysis         |
| HTML          | Web page structure         |
| CSS           | Web page styling           |
| JavaScript    | Frontend interaction       |
| SQLite / JSON | Data storage               |
| YouTube API   | YouTube comment collection |

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Anilyadav564/smart_emotion_analysis.git
```

### 2. Open the project folder

```bash
cd smart_emotion_analysis
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file if your project requires API configuration.

Example:

```text
YOUTUBE_API_KEY=your_api_key_here
```

**Do not upload your real API key to GitHub.**

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

## 🧪 Testing

The project contains test files for checking different parts of the application.

Run the available tests using:

```bash
python -m unittest discover
```

---

## 📊 Example Analysis

For a comment such as:

```text
"This video is amazing! I really enjoyed it."
```

The system can identify:

```text
Sentiment: Positive
Emotion: Joy
Toxicity: Safe
Quality: High
```

For a negative or harmful comment, the system can identify the negative sentiment and flag potentially toxic content for moderation.

---

## 🎯 Project Objective

The main objective of **Smart Emotion Analysis** is to convert large amounts of YouTube comment data into meaningful information.

Instead of manually reading thousands of comments, the system automatically analyzes them and presents useful information through a simple web interface.

---

## 🌟 Benefits

* Saves time when analyzing large numbers of comments
* Helps understand audience feelings
* Identifies common emotions
* Detects potentially harmful comments
* Finds important discussion topics
* Helps creators understand audience feedback
* Provides data-driven content insights

---

## ⚠️ Limitations

The analysis may not always correctly understand:

* Sarcasm
* Irony
* New slang
* Context-dependent expressions
* Mixed emotions
* Very short comments

Therefore, the results should be treated as **decision-support information**, not as perfect human-level interpretation.

---

## 🔮 Future Enhancements

Possible future improvements include:

* Advanced transformer-based NLP models
* Better sarcasm detection
* Multilingual comment analysis
* Real-time YouTube analysis
* Advanced visualization
* User authentication
* Cloud deployment
* More detailed creator analytics

---

## 👨‍💻 Project

**Project Name:** Smart Emotion Analysis

**Repository:** `smart_emotion_analysis`

**Technology:** Python + Flask + NLP

---

## 📜 License

This project is developed for educational and project demonstration purposes.
