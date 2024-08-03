from sqlalchemy import Column, Integer, Text, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import json
import requests
from io import BytesIO

Base1 = declarative_base()


class BOL(Base1):
    __tablename__ = 'BOL_test'

    def __init__(self, **kw: any):
        super().__init__(**kw)
        self.tasks = None
        self.billing = None
        self.image_url = None
        self.image_upload_status = None
        self.response = None

    id = Column(Text, primary_key=True)
    ticket_num = Column(Text)
    purchase_order = Column(Text)
    weight = Column(Integer)
    sand_type = Column(Text)
    end_timestamp = Column(DateTime)
    db_insert_date = Column(DateTime)
    image_upload_status = Column(Text)
    response = Column(Text)

    def from_json(self, json_data):
        self.response = json.dumps(json_data)
        self.id = json_data.get('id')
        self.ticket_num = json_data.get('ticketNumber')
        self.purchase_order = json_data.get('purchaseOrderNumber')
        self.tasks = json_data.get('tasks')
        self.billing = json_data.get('billing')
        self.image_url = None
        self.image_upload_status = False
        self.weight = None
        self.sand_type = None
        self.end_timestamp = json_data.get('endTimestamp')
        self.extract_weight_sand()
        self.extract_image()

    def extract_weight_sand(self):
        if self.tasks:
            sub_tasks = self.tasks[0].get('subTasks') if self.tasks[0] else None
            if sub_tasks:
                payload = sub_tasks[0].get('payload') if sub_tasks[0] else None
                if payload:
                    self.weight = payload.get('actualAmount')
                    self.sand_type = payload.get('name')

    def extract_image(self):
        if self.billing:
            attachments = self.billing.get('attachments')
            if attachments:
                self.image_url = attachments[0].get('url', 'no image')

    @staticmethod
    def latest_entry(session):
        return session.query(BOL).order_by(desc(BOL.end_timestamp)).first()

    @staticmethod
    def latest_date(session):
        last_entry = BOL.latest_entry(session)
        if last_entry:
            return last_entry.end_timestamp.isoformat() + 'Z'
        else:
            dt = datetime(2024, 8, 1, 0, 0, 0)
            return dt.isoformat() + 'Z'

    def upload_image_to_bucket(self, s3_client):
        if self.image_url and self.image_url != 'no image':
            image = requests.get(self.image_url)
            image_data = BytesIO(image.content)
            bucket = 'sandi-bols'
            img_id = self.id + "_bol_img.png"
            self.image_upload_status = s3_client.upload_to_s3(image_data, bucket, img_id)
        else:
            self.image_upload_status = "False"

    def save(self, session):
        self.db_insert_date = datetime.now(timezone.utc)
        session.add(self)
