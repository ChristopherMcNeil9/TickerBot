from .db_libs import get_connection


# Symbol, Security_Name, Shortened_Security_Name, Market_Category, Test_Issue, Financial_Status, Round_Lot_Size, ETF
def create_nasdaq_market_categories(connection):
    cursor = connection.cursor()
    nasdaq_market_category_query = '''
        CREATE TABLE IF NOT EXISTS nasdaq_market_category (
            letter_code varchar(1) UNIQUE,
            full_name varchar(64)
        )
    '''

    nasdaq_market_category_insert = '''
        INSERT INTO nasdaq_market_category (letter_code, full_name)
        VALUES (%(letter_code)s, %(full_name)s)
        ON CONFLICT (letter_code) DO NOTHING
    '''

    nasdaq_market_category_data = [
        {'letter_code': 'Q', 'full_name': 'NASDAQ Global Select MarketSM'},
        {'letter_code': 'G', 'full_name': 'NASDAQ Global MarketSM'},
        {'letter_code': 'S', 'full_name': 'NASDAQ Capital Market'}
    ]

    cursor.execute(nasdaq_market_category_query)
    for category in nasdaq_market_category_data:
        cursor.execute(nasdaq_market_category_insert, category)

    connection.commit()
    cursor.close()


def create_nasdaq_financial_statuses(connection):
    cursor = connection.cursor()

    nasdaq_financial_status = '''
            CREATE TABLE IF NOT EXISTS nasdaq_financial_status (
                letter_code varchar(1) UNIQUE,
                full_name varchar(128)
            )
        '''

    nasdaq_financial_status_insert = '''
            INSERT INTO nasdaq_financial_status (letter_code, full_name)
            VALUES (%(letter_code)s, %(full_name)s)
            ON CONFLICT (letter_code) DO NOTHING
        '''

    nasdaq_financial_status_data = [
        {'letter_code': 'D', 'full_name': 'Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements'},
        {'letter_code': 'E', 'full_name': 'Delinquent: Issuer Missed Regulatory Filing Deadline'},
        {'letter_code': 'Q', 'full_name': 'Bankrupt: Issuer Has Filed for Bankruptcy'},
        {'letter_code': 'N', 'full_name': 'Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.'},
        {'letter_code': 'G', 'full_name': 'Deficient and Bankrupt'},
        {'letter_code': 'H', 'full_name': 'Deficient and Delinquent'},
        {'letter_code': 'J', 'full_name': 'Delinquent and Bankrupt'},
        {'letter_code': 'K', 'full_name': 'Deficient, Delinquent, and Bankrupt'}
    ]

    cursor.execute(nasdaq_financial_status)
    for category in nasdaq_financial_status_data:
        cursor.execute(nasdaq_financial_status_insert, category)

    connection.commit()
    cursor.close()


def create_nasdaq_ticker_table(connection):
    cursor = connection.cursor()

    nasdaq_tickers_query = '''
        CREATE TABLE IF NOT EXISTS nasdaq_tickers (
            symbol varchar(14) UNIQUE,
            security_name varchar(256),
            shortened_security_name varchar(256),
            market_category varchar(1) REFERENCES nasdaq_market_category(letter_code),
            test_issue boolean,
            financial_status varchar(1) REFERENCES nasdaq_financial_status(letter_code),
            round_lot_size integer,
            etf boolean
        )
    '''

    cursor.execute(nasdaq_tickers_query)

    connection.commit()
    cursor.close()


def create_other_exchange_names(connection):
    cursor = connection.cursor()
    other_exchanges_query = '''
        CREATE TABLE IF NOT EXISTS other_exchanges_names (
            letter_code varchar(1) UNIQUE,
            full_name varchar(64)
        )
    '''

    other_exchanges_insert = '''
        INSERT INTO other_exchanges_names (letter_code, full_name)
        VALUES (%(letter_code)s, %(full_name)s)
        ON CONFLICT (letter_code) DO NOTHING
    '''

    other_exchanges_data = [
        {'letter_code': 'A', 'full_name': 'NYSE MKT'},
        {'letter_code': 'N', 'full_name': 'New York Stock Exchange (NYSE)'},
        {'letter_code': 'P', 'full_name': 'NYSE ARCA'},
        {'letter_code': 'Z', 'full_name': 'BATS Global Markets (BATS)'},
        {'letter_code': 'V', 'full_name': 'Investors\' Exchange, LLC (IEXG)'}
    ]

    cursor.execute(other_exchanges_query)
    for category in other_exchanges_data:
        cursor.execute(other_exchanges_insert, category)

    connection.commit()
    cursor.close()


def create_other_table(connection):
    cursor = connection.cursor()
    other_tickers_query = '''
            CREATE TABLE IF NOT EXISTS other_tickers (
                act_symbol varchar(14) UNIQUE,
                security_name varchar(256),
                exchange varchar(1) REFERENCES other_exchanges_names(letter_code),
                cqs_symbol varchar(14),
                etf boolean,
                round_lot_size integer,
                test_issue boolean,
                nasdaq_symbol varchar(14)
            )
        '''
    cursor.execute(other_tickers_query)
    connection.commit()
    cursor.close()


def setup_databases():
    connection = get_connection()

    if connection:
        # create nasdaq specific data
        create_nasdaq_market_categories(connection)
        create_nasdaq_financial_statuses(connection)
        create_nasdaq_ticker_table(connection)

        # create other data
        create_other_exchange_names(connection)
        create_other_table(connection)

        connection.close()


def main():
    setup_databases()


if __name__ == "__main__":
    main()