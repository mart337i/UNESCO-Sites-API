import logging

logging.basicConfig(filename='/home/sysadmin/code/unesco_world_heritage_sites/logs/application.log',  # log to a file named 'app.log'
                    filemode='a',  # append to the log file if it exists, otherwise create it
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
logging.captureWarnings(True)

logger = logging.getLogger(__name__)
