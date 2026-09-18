import re


class TextPreprocessor:

    def clean_text(self, text):

        # Convert text to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r"http\S+|www\S+", "", text)

        # Remove numbers and special characters
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        # Remove spaces from beginning and end
        text = text.strip()

        return text