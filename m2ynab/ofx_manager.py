import glob
import json
import os

import sys

import requests
from settings import Settings
from ofxtools.Parser import OFXTree

sys.path.append('/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjC')
import applescript
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("Rotating Log")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


def create_rotating_log(path):
    """
    Creates a rotating log
    """
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

    logger.setLevel(logging.INFO)

    if Settings.print_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    # add a rotating handler
    file_handler = RotatingFileHandler(path, maxBytes=1000000,
                                       backupCount=5)
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)


def get_plain_script():
    return """
set appName to "MoneyMoney"
set fromDate to (current date) - ({} * days)
set accounts to {{"{}"}}
set export to {{}}

if application "MoneyMoney" is running then
	try
		repeat with a from 1 to length of accounts
			tell application "MoneyMoney"
				set account to item a of accounts
				# copy newItem to the end of export
				set export to export transactions from account account from fromDate as "ofx"
			end tell
		end repeat
		return export
	on error errStr number errNumber
		if errNumber is equal to -2720 then
			return "Error: " & errStr
		end if
	end try
end if  
return "app not running"
    """.format(Settings.days_to_export, '", "'.join(Settings.accounts.keys()))


def try_export():
    plain = get_plain_script()

    script = applescript.AppleScript(plain)
    logger.debug('Apple Script: \n\n{}\n\n'.format(plain))
    logger.info('Trying export from MoneyMoney...')
    ret = script.run()
    logger.info('AppleScript return value: {}'.format(ret))
    return ret


def main():
    logger.info('*' * 80)

    export_result = try_export()
    if 'app not running' in export_result or 'Locked database.' in export_result:
        exit_with_code(2)

    source_path = os.path.dirname(export_result)

    statements = dict()
    objects = dict()
    parsers = dict()

    files = [f for f in glob.glob('{}/{}'.format(source_path, Settings.pattern))]
    logger.info('Found {} ofx files in {}'.format(len(files), source_path))

    if not os.path.exists(Settings.destination_path):
        logging.info('Creating destination folder {}'.format(Settings.destination_path))
        os.makedirs(Settings.destination_path)

    # collect dates by unique_transactions
    for export in files:
        try:
            parser = OFXTree()
            parser.parse(export)
            o = parser.convert()

            # check if any statements exist
            if len(o.statements) is 0:
                continue

            # find account type
            if hasattr(o.statements[0], 'ccacctfrom'):
                key = o.statements[0].ccacctfrom.acctid
            elif hasattr(o.statements[0], 'account'):
                key = o.statements[0].account.acctid
            else:
                logging.warn('Found strange account type: {}'.format(o.statements[0]))

            if key not in statements:
                statements[key] = list()

            statements[key].append(o.statements[0])
            objects[key] = o
            parsers[key] = parser
        except (KeyError, AttributeError, TypeError, IndexError) as exc:
            logger.error('An error occurred during parsing the exports: {}'.format(exc))
            logger.error('Context: {}'.format(export))
            exit_with_code(1)

    logger.info('-' * 80)
    for account in statements:
        try:
            logger.info('Got {} statements for account {}'.format(len(statements[account]), account))

            # get all transactions
            transactions = [transaction for transaction_list in statements[account] for transaction in
                            transaction_list.banktranlist]
            logger.info('Got {} transactions for account {}'.format(len(transactions), account))

            # keep unique transactions only
            unique = dict()
            for t in transactions:
                unique[t.__repr__()] = t
            logger.info('Got {} unique transactions for account {}'.format(len(unique), account))
            #
            # logger.info('Sending transactions into the cloud'.format(len(unique)))
            # try:
            #     account_name = 'test'
            #     for t in transactions:
            #         data = {"transactions": [
            #             {"account": account_name, "payee": t.name, "amount": t.trnamt, "memo": t.memo,
            #              "created": t.dtposted}]}
            #
            #         # send to server
            #         response = requests.post(url='http://localhost:5000/transactions', json=data)
            #
            #         logger.debug(response.text)
            # except Exception as exc:
            #     logger.error(exc)

            objects[account].statements[0].banktranlist[:] = []
            objects[account].statements[0].banktranlist.extend(unique.values())
        except (KeyError, AttributeError, TypeError, IndexError) as exc:
            logger.error('An error occurred during parsing the statements: {}'.format(exc))
            exit_with_code(1)

        logger.info('-' * 80)

    for account in parsers:
        try:
            destination = '{}/{}.ofx'.format(Settings.destination_path, account)
            logger.info(
                'Writing {} transactions to {}'.format(len(objects[account].statements[0].banktranlist), destination))
            parsers[account].write(destination)
        except (KeyError, AttributeError, TypeError, IndexError) as exc:
            logger.error('An error occurred during writing the files: {}'.format(exc))
            exit_with_code(1)

    if Settings.delete_exports:
        logger.info('Deleting {} files from {}'.format(len(files), source_path))
        for export in files:
            os.remove(export)

    exit_with_code(0)


def exit_with_code(code):
    logger.info('*' * 80)
    sys.exit(code)


if __name__ == '__main__':
    log_file = "{}/log/ofx_manager.log".format(Settings.cwd)
    create_rotating_log(log_file)

    main()
