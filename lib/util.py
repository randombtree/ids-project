def month_range(start, stop):
    """
    Generator for ISO-style (YYYY-MM-dd) dates in inclusive range start,stop
    """
    intify = lambda l: list(map(lambda s: int(s), l))
    [year, month, day] = intify(start.split('-'))
    [stop_year, stop_month, stop_day] = intify(stop.split('-'))
    while year < stop_year or (year == stop_year and month <= stop_month):
        yield f'{year}-{month:02d}-{day:02d}'
        month += 1
        if month > 12:
            month = 1
            year += 1


