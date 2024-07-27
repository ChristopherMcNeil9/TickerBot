from ..logger import get_logger
from psycopg2.extras import execute_values
from . import db_libs


def db_update_nasdaq(header, data_rows):
    connection = db_libs.get_connection()
    logger = get_logger()

    if connection:
        logger.debug('updating nasdaq tickers DB')
        cursor = connection.cursor()

        insert_query = f'''
            INSERT INTO nasdaq_tickers ({', '.join(header)}) 
            VALUES %s
            ON CONFLICT (symbol) DO UPDATE SET
                security_name = EXCLUDED.security_name,
                shortened_security_name = EXCLUDED.shortened_security_name,
                market_category = EXCLUDED.market_category,
                test_issue = EXCLUDED.test_issue,
                financial_status = EXCLUDED.financial_status,
                round_lot_size = EXCLUDED.round_lot_size,
                etf = EXCLUDED.etf
        '''

        execute_values(cursor, insert_query, data_rows)

        connection.commit()
        cursor.close()
        connection.close()
    else:
        logger.error('Update Nasdaq failed to retrieve connection.')


def db_update_others(header, data_rows):
    connection = db_libs.get_connection()
    logger = get_logger()

    if connection:
        logger.debug('updating other tickers from nasdaq DB')
        cursor = connection.cursor()

        insert_query = f'''
            INSERT INTO other_tickers ({', '.join(header)}) 
            VALUES %s
            ON CONFLICT (act_symbol) DO UPDATE SET
                security_name = EXCLUDED.security_name,
                exchange = EXCLUDED.exchange,
                cqs_symbol = EXCLUDED.cqs_symbol,
                etf = EXCLUDED.etf,
                round_lot_size = EXCLUDED.round_lot_size,
                test_issue = EXCLUDED.test_issue,
                nasdaq_symbol = EXCLUDED.nasdaq_symbol
        '''

        execute_values(cursor, insert_query, data_rows)

        connection.commit()
        cursor.close()
        connection.close()
    else:
        logger.error('Update Nasdaq failed to retrieve connection.')