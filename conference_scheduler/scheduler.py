import copy
from random import shuffle
import operator

import conference as cf
import config

talkInfo = {
    'KEYNOTE': 30,
    'CLOSING': 30,
    'WORKSHOP': 60,
    'REGULAR_TALK': 30,
    'LIGHTNING': 10
}

# {u'KEYNOTE': 2, u'WORKSHOP': 6, u'CLOSING': 2,
# u'REGULAR_TALK': 11, u'LIGHTNING': 5}

finalSchedule = {}

# The end time for any slot is numerically higher than
# start time. Assuming all talks happen on the same day.
#

keyNoteStart = config.keyNoteStart
keyNoteEnd = config.keyNoteEnd

breakLunchStart = config.breakLunchStart
breakLunchEnd = config.breakLunchEnd

breakTeaStart = config.breakTeaStart
breakTeaEnd = config.breakTeaEnd

closingStart = config.closingStart
closingEnd = config.closingEnd


def getSlotLength(start, end):
    return end.diffMinutes(start)


def canFit(limit, input):
    if input == 0:
        return False

    if limit >= input:
        # print "CanFit: current limit={} input={}".format(limit, input)
        return True
    # print "CannotFit: current limit={} input={}".format(limit, input)
    return False


def getTalkOrder(talkInfo, randomOrder=False):
    order = []
    #print "sorting the talk types ordertype={}".format(randomOrder)

    if randomOrder == 'True':
        # print "random order ------------"
        for k in talkInfo:
            order.append(k)
        shuffle(order)
    else:
        # print "increasing order ------------"
        sortedList = sorted(talkInfo.items(), key=lambda kv: kv[1], reverse=True)
        # print sortedList
        for k in range(len(sortedList)):
            # print sortedList[k]
            # print "appending {}".format(sortedList[k][0])
            order.append(sortedList[k][0])

    # print "Processing talk order={} all={}".format(order, talkInfo)
    return order


def updateTalksList(talksList, talkDetails, start, end, day, randomOrder=False):
    # print talksList

    startTime = copy.copy(start)
    #print "Processing a slot h={} m={} slot={}".format(startTime.hour, startTime.minute, slotTime)

    current = getSlotLength(start, end)

    # How we pick a talk type defines the schedule.
    # The following iteration picks the largest
    # talk type.
    # We can choose largest first or random order.
    for t in getTalkOrder(talkInfo, randomOrder):
        if t in ['KEYNOTE', 'CLOSING', 'LUNCH', 'TEA']:
            continue

        # print "Processing current={} talksList={} talkType={}".format(current, talksList[t], t)
        while canFit(current, talkInfo[t]):
            # If there are enough stances of a talk type
            if talksList[t] > 0:
                title = talkDetails[t].pop()
                # print "{:02d}:{:02d} {} {}".format(startTime.hour, startTime.minute, title, t)
                key = "{:02d}{:02d}".format(startTime.hour, startTime.minute)
                value = "{} {}".format(title, t)
                # print "update: key for finalSchedule is " + key
                # finalSchedule[int(key)] = value
                addToSchedule(day, key, value)
                current = current - talkInfo[t]
                talksList[t] = talksList[t] - 1
                startTime.addMinutes(cf.ConfTime("0", talkInfo[t]))
                # print talksList
            else:
                break
        if current == 0:
            break
    # print "The current slot residue={}".format(current)


def verifyPostSchedule(talksList, talkDetails):
    for k in talksList:
        if k == 'KEYNOTE' or k == 'CLOSING':
            assert(talksList[k] == 0)


def preVerifySchedule(talksList, days):
    for k in talksList:
        if k == 'KEYNOTE' or k == 'CLOSING':
            assert(talksList[k] == days)

def addToSchedule(day, key, value):
        if day not in finalSchedule:
            finalSchedule[day] = {}
        if key not in finalSchedule[day]:
            finalSchedule[day][key] = {}

        finalSchedule[day][key] = value
        # print finalSchedule

def scheduleFixedEvents(talksList, talkDetails, t, start, end, day):
    if t == 'KEYNOTE' or t == 'CLOSING':
        talksList[t] = talksList[t] - 1
        # startTime.addMinutes(cf.ConfTime("0", talkInfo[t]))
        title = talkDetails[t].pop()
        # print "{:02d}:{:02d} {} {}".format(start.hour, start.minute, title, t)
        key = "{:02d}{:02d}".format(start.hour, start.minute)
        value = "{} {}".format(title, t)
        # print "fixed: key for finalSchedule is " + key
        #print int(key), finalSchedule[day][key]
        addToSchedule(day, key, value)
        return

    if t == 'LUNCH' or t == 'TEA':
        # print "{:02d}:{:02d} {}".format(start.hour, start.minute, t)
        key = "{:02d}{:02d}".format(start.hour, start.minute)
        value = "{}".format(t)
        # print "fixed: key for finalSchedule is " + key
        #print int(key), finalSchedule[day][key]
        addToSchedule(day, key, value)
    else:
        # Just raise an exception otherwise
        raise ValueError("Incorrect talk type passed= {}".format(t))


def scheduleGreedy(talksList, talkDetails, day, track, order=False):
    # Slots
    # Each slot is independently scheduled, irrespective of their individual
    # oder, the schedule is consistent.
    scheduleFixedEvents(talksList, talkDetails, 'LUNCH', breakLunchStart, breakLunchEnd, day)
    updateTalksList(talksList, talkDetails, keyNoteEnd, breakLunchStart, day, order)
    scheduleFixedEvents(talksList, talkDetails, 'CLOSING', closingStart, closingEnd, day)
    scheduleFixedEvents(talksList, talkDetails, 'KEYNOTE', keyNoteStart, keyNoteEnd, day)
    updateTalksList(talksList, talkDetails, breakLunchEnd, breakTeaStart, day, order)
    scheduleFixedEvents(talksList, talkDetails, 'TEA', breakTeaStart, breakTeaEnd, day)
    updateTalksList(talksList, talkDetails, breakTeaEnd, closingStart, day, order)


def writeToOutput(f, str):
    f.write(str)
    f.write("\n")

def getFinalSchedule(talkDetails, outputFile):
    lastDay = None

    try:
        f = open(outputFile, 'w')
    except:
        print("Failed to open output file")

    # We iterate the final schedule in sorted order
    for d in sorted(finalSchedule.keys()):
        #print("Day {} Track 1".format(d))
        print "Day {} Track 1".format(d)
        out = "Day {} Track 1".format(d)

        writeToOutput(f, out)
        for k in sorted(finalSchedule[d].keys()):
            # print(k, finalSchedule[d][k])
            print k, finalSchedule[d][k]
            out = "{} {}".format(k, finalSchedule[d][k])
            writeToOutput(f, out)
        lastDay = d

    # Schedule remaining talks in track 2 on the last day.
    isTrackNeeded = False
    for k in talkDetails:
        if len(talkDetails[k]) > 0:
            if isTrackNeeded == False:
                #print("Day {} Track 2".format(lastDay))
                print "Day {} Track 2".format(lastDay)
                out = "Day {} Track 2".format(lastDay)
                writeToOutput(f, out)

                isTrackNeeded = True
                for item in talkDetails[k]:
                    print("{} {}".format(item, k))
                    out = "{} {}".format(item, k)
                    writeToOutput(f, out)
    f.close()

# Schedule events
def scheduleEvents(talksList, talkDetails, days, track, outFile, order=False):
    preVerifySchedule(talksList, days)

    # Iterate over all days
    for d in range(days):
        # print talkDetails
        scheduleGreedy(talksList, talkDetails, d + 1, track, order)

    # Verifies that all talks are scheduled. If there are still
    # talks remaining, we need to reschedule them on a new track.
    verifyPostSchedule(talksList, talkDetails)
    getFinalSchedule(talkDetails, outFile)