import logging
from app import db
from app.models.log import Log

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_message(level, message, username=None, log_type=None):
    new_log = Log(level=level, message=message, username=username, log_type=log_type)
    db.session.add(new_log)
    db.session.commit()
    
    if level == "ERROR":
        logger.error(f"{message} (User: {username})")
    else:
        logger.info(f"{message} (User: {username})") 