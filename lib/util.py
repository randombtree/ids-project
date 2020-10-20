def month_range(start, stop):
    """
    Generator for ISO-style (YYYY-MM-dd) dates in inclusive range start,stop
    stop: Iso data or month count, eg. 7 will generate 7 months
    """
    intify = lambda l: list(map(lambda s: int(s), l))
    [year, month, day] = intify(start.split('-'))
    if type(stop) == str:
        [stop_year, stop_month, stop_day] = intify(stop.split('-'))
    elif type(stop) == int:
        stop_dat = day
        stop_year = year
        stop_month = month + stop
        if stop_month > 12:
            stop_year += (stop_month // 12)
            stop_month = (stop_month -1) % 12 + 1 # Months start from 1
    else:
        raise TypeError(f'stop paremeter of unsupported type {type(stop)}')
    while year < stop_year or (year == stop_year and month <= stop_month):
        yield f'{year}-{month:02d}-{day:02d}'
        month += 1
        if month > 12:
            month = 1
            year += 1


