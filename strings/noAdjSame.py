from queue import PriorityQueue

freq = {}


def GetFrequency(str):
    for i in range(len(str)):
        c = str[i]
        if c not in freq:
            freq[str[i]] = -1
        else:
            freq[str[i]] -= 1

    print(freq)

    pq = PriorityQueue()

    prevKey = None
    prevFreq = 1

    for k in freq:
        pq.put((freq[k], k))

    while not pq.empty():
        next = pq.get()
        c = next[1]

        print(c, end="")

        if prevFreq < 0:
            # print("Adding back {} {}".format(prevFreq, prevKey), end="\n")
            pq.put((prevFreq, prevKey))

        freq[c] += 1

        prevFreq = freq[c]
        prevKey = c

        # print("prev freq={} val={}".format(prevFreq, prevKey))
    print("")
    return 0


str = "ababbbbbbb"
# print(str)
x = GetFrequency(str)
