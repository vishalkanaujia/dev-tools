There are following files in the source:

scheduler.py
The scheduler requires a list of talks title, type, start time
and end time of each event. It prepares a set of available
slots and allocate talks in each slot independently.
The strategy to pick a talk in a slot is configurable and extensible.
The code uses Greedy algorithm and a random selection.

client.py
It is client code that provides the input file and calls scheduler
APIs.

conference.py
It defines a conference time slot and helper routine.

config.py
The conference events timings are added here. It helps adding fixed
events such as lunch, tea etc. Number and type of events are extensible.

talks.json
This is the input file that has all talks defined in a JSON.

test.py
Test code that checks if the scheduler is picking all the talks.
