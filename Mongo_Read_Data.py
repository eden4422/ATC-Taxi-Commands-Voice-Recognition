import pymongo
import json

# connection details for mongoDB
mongo_uri = "mongodb://localhost:27017/"
database_name = "BoeingTaxiCommands"
collection_name = "commands"

#  MongoDB connector, will only work for the localhost since it has to be offline
client = pymongo.MongoClient(mongo_uri)
database = client[database_name]
collection = database[collection_name]

# this method will print the most recent timestamped item
def View_Most_Recent():
    most_recent_item = collection.find_one({}, sort=[("timestamp", -1)])
    print(most_recent_item)

# this method will print all collection items we can change to print it to the gui text box
def View_All():
    all_items = collection.find()
    for item in all_items:
        print(item)

View_Most_Recent()
View_All()