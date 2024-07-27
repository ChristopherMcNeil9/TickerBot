from services import nasdaq, logger, tickerbot
from services.database import db_setup

tickerbot_log = logger.get_logger()
tickerbot_log.info('\n\n\n--------------Tickerbot Starting up--------------')

db_setup.setup_databases()
nasdaq.update_nasdaq_data()

tickerbot.run()