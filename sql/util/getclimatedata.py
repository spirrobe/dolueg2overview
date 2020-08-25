def getclimatedata(code, month, issuncode=False):
    import socket
    import numpy as np
    import pandas as pd
    import calendar

    from sql.util import getdata

    if type(code) == str:
        codes = code.split(',')
    else:
        codes = code


    # todel will contain codes that could not be found
    if type(month) != int:
        month = int(month)

    # ensure month is in range
    if month <= 0:
        month = 1

    month = (month % 13)

    vdt2npagg = {'average': np.mean,
         'total': np.sum,
         'sum': np.sum,
         'max': np.max,
         'min': np.min,
         'std': np.std,
         'wind':'wind',
         'direction':'direction',
         }

    values = {}
    crit = 'and month(date) = '+str(month)+' '
    crit += 'and not(month(date) = '+str(month)+' '
    crit += ' and day(date) = 1 and time <= "00:00:00") '
    crit += 'or (month(date) = '+str((month+1) % 12)+' '
    crit += 'and day(date) = 1 and time = "00:00:00")'

    for code in codes:
        code = ''.join(code.split('#'))
        code = code.lower()
               if code.endswith('su') or code.endswith('sun') or issuncode:
            sunhourcode = True
        else:
            sunhourcode = False

        data, meta = getdata(code, criteria=crit, fill=False,)

        if data is False:
            values[code] = np.nan
            continue

        data = data.dropna()
        # undo timezone shift for the climateagg!
        timezone = meta[code]['timezone']
        if isinstance(timezone, str):
            timezone = int(timezone)
        elif isinstance(timezone, datetime.timedelta):
            timezone = timezone / datetime.timedelta(hours=1)
        data = data.tshift(periods=int(timezone), freq='H',)
        # and move it back 40 microseconds (in case there will ever)
        # be sonic data) to take care of the now next month
        data = data.tshift(periods=-40, freq='L',)
        agghow = meta[code]['aggregation']
        how = {code: vdt2npagg[agghow]}
        if sunhourcode:
            data['sunhours'] = data[code].gt(120) * 1
            how['sunhours'] = 'sum'
            data['mhours'] = data[code]*0+1
            how['mhours'] = 'count'
            data['nhours'] = calendar.monthrange(2001, month)[1] * 24.0
            data['nhours'] += data[code].index.is_leap_year * int(month == 2)
            how['nhours'] = 'min'

        _ = data.groupby([data.index.year, data.index.month]).agg(how)
        if sunhourcode:
            # scale according to should be hours and how many we have
            # also takes care of the aggregation that we did with the sum
            # without needing the DT of the time series
            _['sunhours'] *=  _['nhours'] / _['mhours']
            _ = _.drop(columns=[i for i in _.columns if i != 'sunhours'])
        values[code] = _.mean().values[0]

    return values
