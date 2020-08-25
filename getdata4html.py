
def getdata4html(code,
                 timeoffset=0,
                 precision=1,
                 quiet=True,
                 ):

    import time
    import datetime
    import numpy as np

    # FIX THESE WITH YOUR IMPORTS TO WHERE YOU ARE RUNNING PYTHON
    import gettimezones
    import getclimatedata
    import getdata
    from met.util.winddirection2string import winddirection2string
    from met.uvb.uvbindex import uvbindex


    if type(code) == str:
        codes = [i.strip() for i in code.split(',')]
    else:
        codes = code.strip()

    if codes[0][0] == '[':
        codes[0] = codes[0][1:]

    if codes[-1][-1] == ']':
        codes[-1] = codes[-1][:-1]

    codes = [i.lower() for i in codes]

    if '%' in codes[0]:
        return codes[0]

    if len(codes) == 1:
        agg = 'ACT'.lower()
    else:
        agg = codes[1].lower()

    if len(codes) >= 4:
        valueprocessing = codes[3].split(':')

        if valueprocessing[0] == '1':
            valueprocessing = ['scale', valueprocessing[1]]

        # fill so it matches the rest
        if len(valueprocessing) == 2:
            valueprocessing = [valueprocessing[0], valueprocessing[1], '9999']

        # make all other things float
        valueprocessing = [valueprocessing[0]] + [float(i) for i in valueprocessing[1:]]

    else:
        valueprocessing = '*'

    if len(codes) >= 5:
        codes = codes[:4]

    # time period
    now = datetime.datetime.now() - datetime.timedelta(days=timeoffset)
    aday, anhour = datetime.timedelta(days=1), datetime.timedelta(hours=1)

    # cases where we dont get data from the DB since we can solve it without
    if codes[0].lower() in ['time', 'utctime', 'date', 'sdate',
                            'fullmonth', 'month', 'year','jsdate']:
        acode = False
        if codes[0].lower() == 'utctime':
            now = datetime.datetime.utcnow() - datetime.timedelta(days=timeoffset)
    elif '#' in codes[0]:
        acode = True
    elif 'UNIT' in codes[0]:
        acode = False
    else:
        acode = True


    if agg == 'v06':
        # round down to the last six hours of the day
        # this way we can also get the next day, otherwise we might run into
        # problems at midnight
        hh = datetime.timedelta(hours=now.hour // 6 * 6)
        now = datetime.datetime(now.year, now.month, now.day,
                                0, 0, 0)
        now += hh
    elif agg == 's06':
        # round down to first six hours of the day
        # this way we can also get the next day, otherwise we might run into
        # problems at midnight
        hh = datetime.timedelta(hours=now.hour // 6 * 6)
        now = datetime.datetime(now.year, now.month, now.day,
                                0, 0, 0)
        now += hh
    elif agg == 'v12':
        hh = datetime.timedelta(hours=now.hour // 12 * 12)
        now = datetime.datetime(now.year, now.month, now.day,
                                0, 0, 0)
        now += hh

    # no timespan has been given
    t1 = now


    if len(codes) <= 2:
        t0 = now - aday
        t0 = datetime.datetime(t0.year,
                               t0.month,
                               t0.day,
                               t0.hour,
                               (t0.minute//10)*10,
                               0)
        t1 = datetime.datetime(t1.year,
                               t1.month,
                               t1.day,
                               t1.hour,
                               (t1.minute//10)*10,
                               0)
    else:
        hour, day, mon = 0, 0, 0
        minute, second = 0, 0
        if 'm' in codes[2]:
            mon = now.month - int(codes[2].split('m')[-1])
            year = now.year
            if mon <= 0:
                year -= 1
                mon = 12
            day, hour = now.day, now.hour-24
            thismonth = datetime.datetime(year, now.month, 1, 0, 0)
            lastmonth = thismonth - datetime.timedelta(days=1)
            # ensure we take the maximum day possible for the actual month
            if lastmonth.day < day:
                now = now.replace(day=lastmonth.day)

            minute, second = (now.minute//10-1)*10, now.second
            t1 -= datetime.timedelta(days=now.day-1,
                                     hours=now.hour,
                                     minutes=now.minute,
                                     seconds=now.second,
                                     )
        elif 'f' in codes[2]:
            mon = codes[2].split('f')
            year, mon = now.year-int(mon[:2]), int(mon[2:])
            day = 1

        else:

            year, mon = now.year, now.month

            minute, second = now.minute, now.second

            if '.' in codes[2] or ':' in codes[2]:
                if '.' in codes[2]:
                    day, hour = [i for i in codes[2].split('.')]
                else:
                    day, hour = [i for i in codes[2].split(':')]
                day, hour = int(day), round(24*float('0.'+hour),2)
            elif codes[2][0] in ['d', 'h']:
                tcode = codes[2][0]
                if len(codes[2]) == 1:
                    codes[2] = codes[2]+'1'
                if tcode == 'd':
                    day = int(codes[2][1:])
                elif tcode == 'h':
                    hour = int(codes[2][1:])
                else:
                    print('Not a valid time code (D or H)')
            else:
                day, hour = int(codes[2]), 0
                minute, second = 0, 0

            t1 -= datetime.timedelta(minutes=now.minute,
                                     seconds=now.second,
                                     )
        # rounding to 10 minutes included to yield the same result
        # as the aml code that was used to derive this function
        # properly usage would be from now one hour back
        try:
            t0 = datetime.datetime(year, mon, now.day,
                                   now.hour, (now.minute//10)*10, now.second)
        except ValueError:
            print(year, mon, now.day, now.hour, codes)
            t0 = datetime.datetime(year, mon, now.day-1,
                                   now.hour, (now.minute//10)*10, now.second)

        t0 -= datetime.timedelta(days=day,
                                 hours=hour,
                                 minutes=(minute//10-1)*10,
                                 seconds=second)

    if acode:
       
        # adjust our t0 and t1 from our current timezone (local, system)
        # to the one of the timeseries that we are trying to get
        # i.e. when the timeseries is actually in MEZ but we are in MESZ
        # we still want valid data

        if '#' in codes[0]:

            codes[0] = ''.join(codes[0].split('#'))
            codes[0] = codes[0].lower()
            climatecode = True

        else:
            climatecode = False

        timezone = (gettimezones(codes[0]))[codes[0]]

        tzdt = timezone * anhour

        # account for difference between local and db time
        t0 -= tzdt
        t1 -= tzdt

        if climatecode:
            if codes[1] == 'sun':
                issuncode = True
            else:
                issuncode = False
            data = getclimatedata(codes[0], t1.month, issuncode)[codes[0]]
        else:
            data, meta = getdata(codes[0], t0=t0, t1=t1, )

        if data is None:
            return '*'

        if not quiet:
            print(data)

        # tendency profits from two digits after the point
        if agg == 'ten':
            precision += 1

        strformat = '{:.'+str(precision)+'f}'
        # just nan values
        if data is False:
            value = '*'
            strformat = '{}'
        elif climatecode:
            value = data
            if agg == 'sun':
                strformat = '{:.0f}'
        else:
            # we changed the time so we can match sevveral aggs with one elif
            if agg in ['act', 'v06', 's12']:
                value = data.tail(1).values[0][0]
                if np.isnan(value):
                    value = '*'
                    strformat = '{}'
            elif agg in ['s06', 'sum']:
                value = data.sum().values[0]
            elif agg == 'min':
                value = data.min().values[0]
            elif agg == 'max':
                value = data.max().values[0]
            elif agg == 'avg':
                value = data.mean().values[0]
            elif agg == 'sun':
                nhours = (data.index[-1] - data.index[0]) / anhour
                value = (data.gt(120).sum() / data.count() * nhours).values[0]
                strformat = '{:.0f}'
            elif agg == 'ten':
                data = data.dropna(how='all')
                value = (data.tail(1).values[0]-data.head(1).values[0])[0]
                dt = min(data.index[1:] - data.index[:-1])
                value /= (data.index[-1] - data.index[0]+dt) / anhour
                if value > 0:
                    strformat = '+'+strformat

    else:
        strformat = '{}'
        tzstring = ' '+ time.strftime("%Z", time.localtime())
        # its not a db code but something from the time
        if codes[0] == 'time':
            value = t1.strftime('%H:%M') + tzstring
        elif codes[0] == 'utctime':
            value = t1.strftime('%H:%M') + tzstring
        elif codes[0] == 'date':
            value = t1.strftime('%d-%m-%Y')
        elif codes[0] == 'jsdate':
            value = t1.strftime('%Y-%m-%d %H:%M')+':00' + tzstring
        elif codes[0] == 'sdate':
            value = t1.strftime('%d-%m')
        elif codes[0] == 'month':
            value = t0.strftime('%b')
        elif codes[0] == 'fullmonth':
            value = t0.strftime('%B')
        elif codes[0] == 'year':
            value = t0.strftime('%Y')
        else:
            value = '*'

    if valueprocessing[0] == 'hr':
        value = winddirection2string(value)
        strformat = '{}'
    elif valueprocessing[0] == 'hra':
        value = winddirection2string(value, addunicodearrow=True)
        strformat = '{}'
    elif valueprocessing[0] == 'uv':
        value = uvbindex(value)
        strformat = '{}'
    elif valueprocessing[0] == 'range':
        if value <= valueprocessing[1] or value >= valueprocessing[2]:
            value = '*'
            strformat = '{}'
    elif valueprocessing[0] == 'clip':
        value = np.clip(value, valueprocessing[1], valueprocessing[2])
    elif valueprocessing[0] == 'scale':
        value = value*valueprocessing[1]

    return strformat.format(value)
