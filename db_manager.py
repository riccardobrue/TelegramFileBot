from pymongo import MongoClient
import datetime

def initdb():
    client = MongoClient('mongodb://mongodb:mongodbpassword@mongodb/db')    #from OpenShift
    #client = MongoClient('mongodb://localhost:27017/db')                   #local

    db = client.db
    try:
        db.create_collection("countdowns")  # create a new collection called "countdowns"
    except:
        pass
    return db.countdowns #get the collection


def add(chatId, chatName, message, date, counter):
    collection=initdb()
    record = collection.find_one({'chatId': chatId, 'chatName': chatName, 'counter': counter})
    if (record == None):
        targetDate = datetime.datetime.strptime(date, '%d-%m-%Y')
        today = datetime.datetime.utcnow()

        if(today<targetDate):
            # Add a document in the collection
            if(message==None):
                countdown = {"chatId": chatId,
                             "chatName": chatName,
                             "message": "",
                             "date": date,
                             "counter": counter}
            else:
                countdown = {"chatId": chatId,
                             "chatName": chatName,
                             "message":message,
                             "date": date,
                             "counter": counter}

            insertedId=collection.insert_one(countdown).inserted_id
            #SET THE NEXT COUNTDOWN
            return "Date saved for the countdown! [code: "+str(counter)+"]"
        else:
            return "Cannot countdown to the past!"
    else:
        return add(chatId, chatName, message, date, counter+1)



def edit(chatId, chatName, newmessage, newdate, counter):
    collection = initdb()
    record = collection.find_one({'chatId': chatId, 'chatName': chatName, 'counter': counter})
    if (record == None):
        return "Cannot find the countdown!"
    else:
        targetDate = datetime.datetime.strptime(newdate, '%d-%m-%Y')
        today = datetime.datetime.utcnow()

        if(today<targetDate):
            countdown = {"chatId": chatId,
                         "chatName": chatName,
                         "message": newmessage,
                         "date": newdate,
                         "counter": counter}

            collection.update_one({'_id': record["_id"] }, {"$set": countdown})
            # SET THE NEXT COUNTDOWN
            return "Record updated!"
        else:
            return "Cannot countdown to the past!"


def getSingle(chatId,chatName,counter):
    collection=initdb()
    record=collection.find_one({'chatId': chatId, 'chatName': chatName, 'counter': counter})
    if(record==None):
        return "None object found"
    else:
        return record

def getAll(chatId,chatName):
    collection=initdb()
    record=collection.find({'chatId': chatId, 'chatName': chatName})
    if(record==None):
        return "None object found"
    else:
        return record

def removeAll(chatId,chatName):
    collection=initdb()
    result=collection.delete_many({'chatId': chatId, 'chatName': chatName})
    return "Deleted "+str(result.deleted_count)+" countdowns"


def removeOne(chatId,chatName,counter):
    collection=initdb()
    result=collection.delete_one({'chatId': chatId, 'chatName': chatName, 'counter': counter})
    return "Deleted " + str(result.deleted_count) + " countdown"