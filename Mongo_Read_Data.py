import tkinter

import pymongo
import json

from bson import ObjectId

import myGUI

# connection details for mongoDB
mongo_uri = "mongodb://localhost:27017/"
database_name = "BoeingTaxiCommands"
collection_name = "commands"

#  MongoDB connector, will only work for the localhost since it has to be offline
client = pymongo.MongoClient(mongo_uri)
database = client[database_name]
collection = database[collection_name]

# This method handles ObjectId objects from the bson module in MongoDB to handle MongoDB OBjectID
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# This method will return the most recent timestamped item as a formatted string
def View_Most_Recent():
    most_recent_item = collection.find_one({}, sort=[("timestamp", -1)])
    if most_recent_item:
        return json.dumps(most_recent_item, indent=2, cls=CustomJSONEncoder)
    else:
        return "Empty collection."

# This method will return all collection items as a formatted string
def View_All():
    all_items = collection.find()
    items_list = [json.dumps(item, indent=2, cls=CustomJSONEncoder) for item in all_items]
    if items_list:
        return "\n".join(items_list)
    else:
        return "Empty collection."

View_Most_Recent()
View_All()