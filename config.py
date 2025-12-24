import os
from dotenv import load_dotenv

load_dotenv()

settings={
    "FINANCIAL-PREP-API-KEY": os.getenv("FINANCIAL-PREP-API-KEY"),
    "CURRANCY-API-KEY ": os.getenv("CURRANCY-API-KEY "),
    "POLYGON-API-KEY": os.getenv("POLYGON_API_KEY"),
    "GEMINI-API-KEY": os.getenv("GEMINI-API-KEY"),

    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DB-NAME": os.getenv("DB-NAME"),
    "DB-USER": os.getenv("DB-USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    "DB_POOL_SIZE": os.getenv("DB_POOL_SIZE"),

    "REDIS-HOST": os.getenv("REDIS-HOST"),
    "REDIS-PORT": os.getenv("REDIS-PORT"),
    "REDIS-DB": os.getenv("REDIS-DB"),
    "REDIS-PASSWORD": os.getenv("REDIS-PASSWORD")
}