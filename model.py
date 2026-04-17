import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "emails.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

model = None  # FIX: cache model


SAMPLE_DATA = """label,text
spam,Win money now click here free prize
ham,Hey how are you doing today
spam,Limited offer buy now exclusive deal
ham,Let's meet tomorrow for lunch
spam,You won a lottery claim your prize now
ham,Can you send me the report by Friday
spam,Urgent your account has been compromised click
ham,Happy birthday hope you have a great day
spam,Free gift card claim it now limited time
ham,Are you coming to the meeting this afternoon
spam,Make money fast work from home guaranteed
ham,Just wanted to check in how are things
spam,Congratulations you are selected for cash reward
ham,Did you see the game last night amazing
spam,Buy cheap medications no prescription needed
ham,I will be a bit late to the office
spam,You have been chosen for exclusive membership
ham,Thanks for your help yesterday really appreciate it
spam,Click here to claim your free vacation package
ham,The project deadline has been moved to next week
spam,Earn 5000 dollars daily from home no experience
ham,Can we reschedule our call to Thursday morning
spam,Your bank account needs immediate verification click here
ham,Looking forward to seeing you at the conference
spam,Hot singles in your area click to meet them
ham,Please review the attached document and give feedback
spam,You owe taxes pay immediately to avoid arrest
ham,Great weather today perfect for a walk outside
spam,Investment opportunity double your money guaranteed returns
ham,Mom asked if you are coming for dinner Sunday
""".strip()


def ensure_data_file():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            f.write(SAMPLE_DATA)


def train_model():
    ensure_data_file()
    df = pd.read_csv(DATA_PATH)
    df.dropna(inplace=True)

    X = df["text"]
    y = df["label"]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2))),
        ("nb", MultinomialNB(alpha=0.1)),
    ])

    pipeline.fit(X, y)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    return pipeline


def load_model():
    global model
    if model is not None:
        return model

    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
    else:
        model = train_model()

    return model


def predict(text):
    model = load_model()

    proba = model.predict_proba([text])[0]
    classes = model.classes_

    label = classes[proba.argmax()]
    label = "spam" if label == "spam" else "ham"  # FIX: consistency

    confidence = round(float(proba.max()) * 100, 2)

    return label, confidence