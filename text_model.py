from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Demo training dataset
texts = [
    "Is this good for running?",
    "Can I use this for gym?",
    "Is this suitable for office?",
    "Is this durable?",
    "Is this expensive?",
    "Can I use this daily?",
    "Is this comfortable?"
]

labels = [
    "fitness",
    "fitness",
    "formal",
    "quality",
    "price",
    "daily_use",
    "comfort"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

classifier = LogisticRegression()
classifier.fit(X, labels)

def analyze_text(text):
    try:
        vec = vectorizer.transform([text])
        prediction = classifier.predict(vec)[0]
        return prediction
    except:
        return None