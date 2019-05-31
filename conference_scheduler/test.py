import sys

import input
import conference
import scheduler

# Test if all talks are scheduled.
#
def testAllTalksScheduled():
    # print input.prepareInput()
    try:
        if len(sys.argv) != 4:
            print "Usage: $ python client.py <absolute path to input.json> <output file> <random order=True/False>"
            sys.exit(-1)

        inputFile = sys.argv[1]
        outputFile = sys.argv[2]
        random = sys.argv[3]

        if inputFile is None:
            print "No input found"
            sys.exit(-1)

        input.prepareInput(inputFile)
        allTalksCategory = input.getTalkMeta()
        talkDetails = input.getTalkDetails()

        scheduler.scheduleEvents(allTalksCategory, talkDetails, 2, 1, outputFile, random)
    except Exception as error:
        print error
    
    inputFreq = []
    outputFreq = []
    with open(inputFile, 'r') as f:
        for l in enumerate(f):
            if 'KEYNOTE' in l:
                inputFreq[0] += 1
            if 'CLOSING' in l:
                inputFreq[1] += 1
            if 'LUNCH' in l:
                inputFreq[2] += 1
            if 'TEA' in l:
                inputFreq[3] += 1
            if 'REGULAR_TALK' in l:
                inputFreq[4] += 1
            if 'LIGHTNING' in l:
                inputFreq[5] += 1
            if 'WORKSHOP' in l:
                inputFreq[6] += 1
            # print(l)

    with open(outputFile, 'r') as f:
        for l in enumerate(f):
            if 'KEYNOTE' in l:
                outputFreq[0] += 1
            if 'CLOSING' in l:
                outputFreq[1] += 1
            if 'LUNCH' in l:
                outputFreq[2] += 1
            if 'TEA' in l:
                outputFreq[3] += 1
            if 'REGULAR_TALK' in l:
                outputFreq[4] += 1
            if 'LIGHTNING' in l:
                outputFreq[5] += 1
            if 'WORKSHOP' in l:
                outputFreq[6] += 1
            # print(l)

    for i,j  in zip(inputFreq, outputFreq):
        assert(i == j)

if __name__ == "__main__":
    testAllTalksScheduled()
