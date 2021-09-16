from database_classes import Payer
from databaseUtil import DatabaseUtil
import random
import csv

class InsuranceFiller:
    session = None
    types = ['HMO','PPO','FFS','MMC','SUP']

    def __init__(self):
        """
         setup and fetch the database session from the database utility.
        """
        dbUtil = DatabaseUtil()
        self.session = dbUtil.getSession()

    def doFill(self):
        global session
        global types
        with open('database-scripts/insurance.txt', newline='') as insurance_companies:
            insuranceReader = csv.reader(insurance_companies, delimiter='\t')
            headers = next(insuranceReader, None)
            for payer in insuranceReader:
                print(payer)
                dbRecord = Payer()
                dbRecord.Name = payer[0]
                dbRecord.plan_type = random.choice(self.types)
                dbRecord.address = payer[1]
                self.session.add(dbRecord)
                self.session.commit()
                print('name: %s, Addr: %s' % (dbRecord.Name, dbRecord.address))


insuranceFiller = InsuranceFiller()
insuranceFiller.doFill()
