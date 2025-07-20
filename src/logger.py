import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
    datefmt="%m-%d-%Y %I:%M:%S %p %Z",
)
logger = logging.getLogger("fitbot")
