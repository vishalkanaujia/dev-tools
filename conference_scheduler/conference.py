class ConfTime:
    def __init__(self, hour, minute):
        self.hour = int(hour)
        self.minute = int(minute)
        if self.hour > 23 or self.minute > 60 \
                or self.hour < 0 or self.minute < 0:
            raise ValueError("Improper value for hour and minute")

    def diffMinutes(self, obj):
        h1 = self.hour
        m1 = self.minute

        h2 = (obj.hour)
        m2 = (obj.minute)

        if h1 < h2:
            raise ValueError("Improper value passed for hour")

        # print h1,m1,h2,m2
        if m1 < m2:
            h1 -= 1
            m1 += 60

        totalHours = (h1 - h2)
        totalMinutes = (m1 - m2) + (60 * totalHours)

        return totalMinutes

    def addMinutes(self, slot):
        total = (self.minute + slot.minute)
        m = total % 60
        self.hour += (total / 60)
        self.minute = m
