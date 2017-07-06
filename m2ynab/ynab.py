from pynYNAB.Client import nYnabClient
from pynYNAB.connection import nYnabConnection

import settings

connection = nYnabConnection(settings.ynab_user, settings.ynab_password)
client = nYnabClient(nynabconnection=connection, budgetname='isa+jo')
client.sync()
