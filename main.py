import json
import logging
import bot

with open("config.json", "r") as f:
    raw_config_data = f.read()
    f.close()

with open("replics.json", "r") as f:
    raw_replics_data = f.read()
    f.close()

config = json.loads(raw_config_data)
replics = json.loads(raw_replics_data)

logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    bot.start_bot()