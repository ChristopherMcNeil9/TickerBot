from ..logger import get_logger
import psycopg2
import json
import os


def get_connection():
    logger = get_logger()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '../../conf/db.conf')
    config_path = os.path.normpath(config_path)

    with open(config_path, 'r') as f:
        config = json.load(f)

    config = config['nasdaq_database']

    try:
        connection = psycopg2.connect(
            dbname=config['db_name'],
            password=config['password'],
            user=config['user'],
            host=config['host'],
            port=config['port']
        )
    except Exception as e:
        connection = None
        logger.error(e)

    return connection


def get_ticker(ticker):
    connection = get_connection()
    cursor = connection.cursor()

    nasdaq_query = '''
        SELECT shortened_security_name FROM nasdaq_tickers WHERE symbol = %s;
    '''
    cursor.execute(nasdaq_query, (ticker,))
    result = cursor.fetchone()

    if result:
        stock_name = result[0]
    else:
        nasdaq_query = '''
            SELECT security_name FROM other_tickers WHERE act_symbol = %s;
        '''
        cursor.execute(nasdaq_query, (ticker,))
        result = cursor.fetchone()
        if result:
            stock_name = result[0]
        else:
            stock_name = None

    connection.close()
    return stock_name
