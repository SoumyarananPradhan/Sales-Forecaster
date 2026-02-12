import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client['sales_db']
sales_collection = db['sales_analysis']

def get_db_handle():
    return db, sales_collection