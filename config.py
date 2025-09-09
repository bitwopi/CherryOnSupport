import os

import dotenv

dotenv.load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

BOT_TOKEN=os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_LIST=os.getenv('ADMIN_LIST')
DB_HOST=os.getenv('DB_HOST')
DB_PORT=os.getenv('DB_PORT')
DB_NAME=os.getenv('DB_NAME')
DB_USERNAME=os.getenv('DB_USERNAME')
DB_PASSWORD=os.getenv('DB_PASSWORD')
WEBHOOK_HOST=os.getenv('WEBHOOK_HOST')
WEBHOOK_PORT=os.getenv('WEBHOOK_PORT')
WEBHOOK_DOMAIN=os.getenv('WEBHOOK_DOMAIN')