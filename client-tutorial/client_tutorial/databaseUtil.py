import logging
from sqlalchemy import BigInteger, Column, DECIMAL, Date, DateTime, Integer, JSON, String, text
from sqlalchemy.dialects.mysql import MEDIUMINT, TEXT, TINYINT, VARCHAR
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

session=None
engine=None



class DatabaseUtil():
    """
    This class is the place where the database SqlAlchemy connection/session is created. This is where you acn alter the url for
    towards the MySQL (or whatever dbms you are using).
    """

    def __init__(self):
        self.createConnectionPool()

    def createConnectionPool(self) -> None:
        """
        tells SqlAlchemy to actually build the engine (which automatically creates the connection pool (allowing connection reuse,
        which for some DBMSs such as Oracle are very expensive to create)
        :return:
        :rtype:
        """
        global engine
        Base = declarative_base()
        metadata = Base.metadata

        settings = get_settings()
        logging.basicConfig()
        # print('DATABASEUTIL FROM CONFIG: ' + settings.tutorial_mysql_url)
        # turn this off in production as it will drive us crazy
        #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        # note I added the pool_pre_ping to prevent flask from timing out server connections via a stale pool state.
        # the ping is the "pessimistic" view from SqlAlchemy that assumes that it will always happen so this ping happens
        # as overhead on every querry. For more info: https://docs.sqlalchemy.org/en/13/core/pooling.html#pool-disconnects
        # fixed in project in commit 90978fd
        engine = create_engine(settings.tutorial_mysql_url, pool_pre_ping=True)



    def getSession(self):
        """
        Is used for external classes to fetch the SqlAlchemy session object from the engine object
        :return:
        :rtype:
        """
        global session
        global engine
        if (engine==None):
            self.createConnectionPool()
        if session == None:
            Session = sessionmaker(bind=engine)
            session = Session()
        return session
