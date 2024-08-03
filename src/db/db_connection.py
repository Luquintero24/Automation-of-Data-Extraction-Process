from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
import src.app_config as config
from .bol import Base1
from .textract_response import Base


class Database:
    def __init__(self, table_name):
        db_url = f'postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}'
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.table_name = table_name
        self.create_tables()

    def create_tables(self):
        inspector = inspect(self.engine)
        if not inspector.has_table(self.table_name):
            if self.table_name is not 'BOL_test':
                Base.metadata.create_all(self.engine)
                print(f"{self.table_name} table was created!")
            else:
                Base1.metadata.create_all(self.engine)
                print(f"{self.table_name} table was created!")
                
    def close_session(self):
        self.session.close()
        