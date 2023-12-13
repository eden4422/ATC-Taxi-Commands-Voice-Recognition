#!/usr/bin/env python3

import pymongo
import json



def Write_to_Mongo():
    # connection details for mongoDB
    mongo_uri = "mongodb://localhost:27017/"
    database_name = "BoeingTaxiCommands"
    collection_name = "commands"

    #  MongoDB connector, will only work for the localhost since it has to be offline
    client = pymongo.MongoClient(mongo_uri)
    database = client[database_name]
    collection = database[collection_name]
    # reads the data from the json file
    with open("JSON_Taxi_Commands.json", "r") as file:
        data = json.load(file)

    # uses collection insert from mongo
    result = collection.insert_one(data)

    # closes the mongoDB connection
    client.close()
