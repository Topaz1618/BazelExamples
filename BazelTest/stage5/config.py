"""
Author: Hang Yan
Date created: 2023/8/13
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""
import os
from dotenv import load_dotenv


ENV = 'DEV'

if ENV == 'DEV':
    from config_dev import *
    env_file = '.env_dev'

elif ENV == 'PROD':
    from config_prod import *
    env_file = '.env_prod'

print(env_file)
load_dotenv(env_file)
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
