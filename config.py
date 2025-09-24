import os
from dotenv import load_dotenv

load_dotenv()

settings={
    "FINANCIAL-PREP-API-KEY": os.getenv("FINANCIAL-PREP-API-KEY"),
    "GEMINI-API-KEY": os.getenv("GEMINI-API-KEY"),
    "DB-USER": os.getenv("DB-USER"),
    "DB-PATH": os.getenv("DB-PATH"),
    "API-KEY": os.getenv("API-KEY"),
    "REDIS-HOST": os.getenv("REDIS-HOST"),
    "REDIS-PORT": os.getenv("REDIS-PORT"),
    "REDIS-DB": os.getenv("REDIS-DB"),
    "REDIS-PASSWORD": os.getenv("REDIS-PASSWORD")
}