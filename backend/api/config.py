import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
