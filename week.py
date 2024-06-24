import datetime
def cur_week():
    thisWeek:int = None;
    date = datetime.datetime.now()

    if date.month >= 8:
        start_year = date.year
    else:
        start_year = date.year - 1
  
    firstday = datetime.datetime(start_year, 8, 1)

    if firstday.weekday() == 6:
        if date.month == 8 and date.day == 1:
            thisWeek = 1
        else:
            endWeek = firstday.replace(day=1) + datetime.timedelta(days=5)
            startWeek = firstday.replace(day=1) - datetime.timedelta(days=2)
    else:
        weekday = firstday.weekday()
        startWeek = firstday - datetime.timedelta(days=weekday)
        endWeek = firstday.replace(day=1) + datetime.timedelta(days=6-weekday)
        endWeek = endWeek.replace(hour=23, minute=59, second=59, microsecond=999)

    if thisWeek == None:
        thisWeek = 1
        if startWeek < date and endWeek > date:
           pass
        else:
            while not (startWeek < date and endWeek > date):
                startWeek = startWeek + datetime.timedelta(weeks=1)
                endWeek = endWeek + datetime.timedelta(weeks=1)
                endWeek = endWeek.replace(hour=23, minute=59, second=59, microsecond=999)
                if thisWeek != 4:
                    thisWeek += 1
                else:
                    thisWeek = 1
    return(thisWeek)
