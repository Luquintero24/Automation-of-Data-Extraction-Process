from sqlalchemy import Column, Integer, Text, DateTime, desc, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import json
import requests
from io import BytesIO

Base = declarative_base()


class textract_responses(Base):

    def __init__(self, **kw:any):
        super().__init__(**kw)
        


    __tablename__ = 'TR_test'
    id = Column(String, primary_key=True)
    image_processing_status = Column(Boolean, default=False)
    error_message = Column(Text, default=None)
    textract_response = Column(Text)



    def from_textract_response(self, document_name, textract_response, error_message=None):
        self.id = document_name.replace('_bol_img.png', '')
        self.textract_response = json.dumps(textract_response)
        self.error_message = error_message
        if error_message is None:
            self.image_processing_status = True
        print(self.id)


    def save_textract_response_to_db(self, session, document_name):
        try:

            # Save to the database
            session.add(self)
            session.commit()
            print(f"Textract response for {document_name} saved to database with ID {self.id}")

        except Exception as e:
            session.rollback()
            print(f"An error occurred while saving to the database: {str(e)}")
