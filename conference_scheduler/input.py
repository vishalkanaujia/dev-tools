import json


talkMeta = {}
talkDetails = {}


def addTalkDetails(type, title):
    if type in talkDetails:
        talkDetails[type].append(title)
    else:
        talkDetails[type] = [title]


def prepareInput(fname):
    scheduleStr = ""
    try:
        with open(fname, "r") as readFile:
            scheduleStr = json.load(readFile)
    except ValueError:
        raise Exception("Failed reading input file")

    # print type(scheduleStr)  # [talks]

    listOfValues = []
    for k in scheduleStr:
        listOfValues = scheduleStr[k]


    # Iterate over all talks and prepare a meta data
    # of talk type and their count.
    for t in listOfValues:
        type = t['type']
        if type in talkMeta:
            talkMeta[type] = talkMeta[type] + 1
        else:
            talkMeta[type] = 1
        addTalkDetails(type, t['title'])


def getTalkMeta():
    return talkMeta

def getTalkDetails():
    return talkDetails
