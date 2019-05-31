import sys

import input
import conference as cf
import scheduler

if __name__ == "__main__":
    # print input.prepareInput()
    try:
        if len(sys.argv) != 4:
            print("Usage: $ python client.py <absolute path to input.json>\
                 <output file> <random order=True/False>")
            sys.exit(-1)

        inputFile = sys.argv[1]
        outputFile = sys.argv[2]
        random = sys.argv[3]
        # print sys.argv

        if inputFile is None:
            print("No input found")
            sys.exit(-1)

        input.prepareInput(inputFile)
        allTalksCategory = input.getTalkMeta()
        talkDetails = input.getTalkDetails()

        scheduler.scheduleEvents(allTalksCategory, talkDetails, 2, 1, outputFile, random)
    except Exception as error:
        print(error)
