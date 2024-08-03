from src.db.bol import BOL
from src.app_config import final_count

class BOLProcessor:
    def __init__(self, db, s3_client, api_client):
        self.db = db
        self.s3_client = s3_client
        self.api_client = api_client
        self.latest_date = BOL.latest_date(self.db.session)
        self.page = 1
        self.counter = 0

    def process(self):
        status = True
        while status:
            params = {'endedSince': self.latest_date, 'pageLimit': '10', 'product': 'sandi', 'logisticsStatus': 'completed', 'page': self.page}
            data = self.api_client.fetch_data('/orders', params)

            if not data or self.counter >= int(final_count):
                status = False
                break

            for item in data:
                self.process_item(item)

            self.db.session.commit()
            self.counter += len(data)
            print(f"Data successfully inserted into BOL table, entries - {len(data)} | page - {self.page} | total - {self.counter}")
            self.page += 1

        print("Execution Complete")

    def process_item(self, item):
        bol = BOL()
        bol.from_json(item)

        if self.db.session.query(BOL).filter(BOL.id == bol.id).first():
            print(f"Skipping duplicate entry with id: {bol.id}")
            return

        bol.upload_image_to_bucket(self.s3_client)
        bol.save(self.db.session)
