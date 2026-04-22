### this file is for loading environment variables and any other configuration settings...

import os
from dotenv import load_dotenv

load_dotenv()

MODEL_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL")