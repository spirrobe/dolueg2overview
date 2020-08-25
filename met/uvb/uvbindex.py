def uvbindex(value, adjust=True):
    import math
    if adjust:
        value *= 40

    if (value < -1 or value >= 20) or not math.isfinite(value):
        return 'No data'
    elif value <= 0.2:
        return 'None'
    elif value <= 2.5:
        return 'Low',
    elif value <= 5.5:
        return 'Moderate'
    elif value <= 7.5:
        return 'High'
    elif value <= 10.5:
        return 'Very high'
    else:
        return 'Extreme'


if __name__ == '__main__':
    print('*'*10, 'HELP for uvbindex', '*'*10)
    print('Calculates the UVB index from the proper data timeseries')
    print('Adjust (inherited from aml) by factor 40')
    print("1 MED/hr = 5.83E-6 Watts per square centimeter of biologically active radiation",
          "or 1 MED/hr = 0.0583 W/m^2 and 1 MED/10min = 0.349800",
          "calibration in davos showed that 1 MED/10min = 0.422160 W/m^2 for the",
          "instrument in Basel Binningen",
          "Levels after MeteoSchweiz",
          "(http://www.meteoschweiz.ch/de/Freizeit/Gesundheit/UV_Index/uv_protec.shtml)",
          "(outdated in June 2019)",
          "Levels adapted after WMO 2003 in communication with MeteoSchweiz",)
