from datetime import datetime, timedelta
from .logger import get_logger
from .database.db_update import db_update_nasdaq, db_update_others
import requests

# TODO: consider getting other info from nasdaqtrader FTP
# https://www.nasdaqtrader.com/Trader.aspx?id=Help


def parse_nasdaq_data(data):
    # KEY DATA FROM https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs
    # Symbol:           The one to four or five character identifier for each NASDAQ-listed security.
    # Security Name:    Company issuing the security.
    # Market Category:  (Q = NASDAQ Global Select MarketSM, G = NASDAQ Global MarketSM, S = NASDAQ Capital Market)
    # Test Issue:       Indicates whether or not the security is a test security.
    #                   Values: Y = yes, it is a test issue. N = no, it is not a test issue.
    # Financial Status: Indicates when an issuer has failed to submit its regulatory filings on a timely basis, has
    #                   failed to meet NASDAQ's continuing listing standards, and/or has filed for bankruptcy.
    #           Values include: D = Deficient: Issuer Failed to Meet NASDAQ Continued Listing Requirements
    #                           E = Delinquent: Issuer Missed Regulatory Filing Deadline
    #                           Q = Bankrupt: Issuer Has Filed for Bankruptcy
    #                           N = Normal (Default): Issuer Is NOT Deficient, Delinquent, or Bankrupt.
    #                           G = Deficient and Bankrupt
    #                           H = Deficient and Delinquent
    #                           J = Delinquent and Bankrupt
    #                           K = Deficient, Delinquent, and Bankrupt
    # Round Lot:        Indicates the number of shares that make up a round lot for the given security.
    # ETF:      Not listed on site but assumes Y/N for if it is an ETF
    # NextShares, Don't know, doesn't seem used, everything is N

    # normalize the data for processing
    data = data.split('File Creation Time')[0]
    data = data.rstrip()
    data_rows = data.split('\r\n')

    # extract header and normalize to db column values
    header = data_rows[0]
    header = header.replace(' ', '_')
    header = header.lower()
    header_row = header.split('|')[:-1]
    header_row.insert(2, 'shortened_security_name')

    # extract rows and convert to psycopg2 list of tuples
    data_rows = data_rows[1:]
    return_rows = []
    for row in data_rows:
        cells = row.split('|')[:-1]
        cells[3] = cells[3] == 'Y'
        cells[5] = int(cells[5])
        cells[6] = cells[6] == 'Y'
        cells.insert(2, cells[1].split(' - ')[0])

        return_rows.append(tuple(cells))

    return header_row, return_rows


def parse_other_data(data):
    # KEY DATA FROM https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs
    # ACT Symbol:       Identifier for each security used in ACT and CTCI connectivity protocol. Typical identifiers
    #                       have 1-5 character root symbol and then 1-3 characters for suffixes.
    #                       Allow up to 14 characters.
    # Security Name:    The name of the security including additional information, if applicable. Examples are security
    #                       type (common stock, preferred stock, etc.) or class (class A or B, etc.).
    #                       Allow up to 255 characters.
    # Exchange:         The listing stock exchange or market of a security.
    #                       A = NYSE MKT
    #                       N = New York Stock Exchange (NYSE)
    #                       P = NYSE ARCA
    #                       Z = BATS Global Markets (BATS)
    #                       V = Investors' Exchange, LLC (IEXG)
    # CQS Symbol:       Identifier of the security used to disseminate data via the SIAC Consolidated Quotation System
    #                       (CQS) and Consolidated Tape System (CTS) data feeds. Typical identifiers have 1-5 character
    #                       root symbol and then 1-3 characters for suffixes. Allow up to 14 characters.
    # ETF:              Identifies whether the security is an exchange traded fund (ETF)
    # Round Lot Size:   Indicates the number of shares that make up a round lot for the given security.
    #                       Allow up to 6 digits.
    # Test Issue:       Indicates whether the security is a test security.
    # NASDAQ Symbol:    Identifier of the security used to in various NASDAQ connectivity protocols and NASDAQ market
    #                       data feeds. Typical identifiers have 1-5 character root symbol and then 1-3 characters for
    #                       suffixes. Allow up to 14 characters.

    # normalize the data for processing
    data = data.split('File Creation Time')[0]
    data = data.rstrip()
    data_rows = data.split('\r\n')

    # extract header and normalize to db column values
    header = data_rows[0]
    header = header.replace(' ', '_')
    header = header.lower()
    header_row = header.split('|')

    # extract rows and convert to psycopg2 list of tuples
    data_rows = data_rows[1:]
    return_rows = []
    for row in data_rows:
        cells = row.split('|')
        cells[4] = cells[4] == 'Y'
        cells[5] = int(cells[5])
        cells[6] = cells[6] == 'Y'

        return_rows.append(tuple(cells))

    return header_row, return_rows


def get_nasdaq_tickers():
    url = 'http://ftp.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
    header = None
    data_rows = None
    try:
        data = requests.get(url).text
    except:
        data = None

    if data:
        header, data_rows = parse_nasdaq_data(data)
        db_update_nasdaq(header, data_rows)


def get_other_tickers():
    url = 'http://ftp.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'
    try:

        data = requests.get(url).text
    except:
        data = None

    if data:
        header, data_rows = parse_other_data(data)
        db_update_others(header, data_rows)


def update_nasdaq_data():
    logger = get_logger()
    logger.debug('running full nasdaq setup')

    get_nasdaq_tickers()
    get_other_tickers()


def main():
    dt = datetime.now() + timedelta(hours=24)


if __name__ == "__main__":
    main()
