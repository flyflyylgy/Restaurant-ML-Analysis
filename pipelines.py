import json
import pymongo
from itemadapter import ItemAdapter


class TaobaoPipeline:
    def open_spider(self, spider):
        # 初始化MongoDB连接（可选）
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['taobao']
        self.collection = self.db['products']

    def process_item(self, item, spider):
        # 保存到JSON文件
        with open('taobao_products.json', 'a', encoding='utf-8') as f:
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            f.write(line)

        # 保存到MongoDB
        self.collection.insert_one(dict(item))

        return item

    def close_spider(self, spider):
        self.client.close()