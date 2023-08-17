from aiodb import BotDB
import os.path

filepath = os.path.abspath('prod.sqlite3')
db = BotDB(filepath)