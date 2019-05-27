import conference as cf

# The end time for any slot is numerically higher than
# start time. Assuming all talks happen on the same day.
#

keyNoteStart = cf.ConfTime("09", "00")
keyNoteEnd = cf.ConfTime("09", "30")

breakLunchStart = cf.ConfTime("12", "30")
breakLunchEnd = cf.ConfTime("13", "30")

breakTeaStart = cf.ConfTime("15", "00")
breakTeaEnd = cf.ConfTime("15", "15")

closingStart = cf.ConfTime("17", "00")
closingEnd = cf.ConfTime("17", "30")

