def winddirection2string(winddirection,
                         sectors=8,
                         addunicodearrow=False):

    import numpy as np
    if type(winddirection) == str:
        if winddirection.isnumeric():
            winddirection = float(winddirection)
        else:
            return '*'

    if np.isnan(winddirection):
        return '*'
    winddirection = (winddirection + 360) % 360

    _sectors = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'n']

    # unicodes for arrow directions, dont follow a particular order
    # and thus are fixed here
    arrlist = ['129107', '129111', '129104', '129108', '129105',
               '129109', '129106', '129110', '129107']

    arrlist = ['8659', '8665', '8656', '8662', '8657',
               '8663', '8658', '8664', '8659']

    # adjust up, no actual fixing of anything in particular
    if sectors == 8:
        pass
    elif sectors == 16:
        _sectors = ['n', 'nne', 'ne', 'ene', 'e', 'ese', 'se', 'sse', 's',
                    'ssw', 'sw', 'wsw', 'w', 'wnw', 'nw', 'nnw', 'n']
        print('addunicodearrow only supported for 8 or 4 sectors')
        addunicodearrow = False
    elif sectors == 4:
        _sectors = _sectors
        arrlist = arrlist[::2]
    else:
        print('Not compatible (4,8,16) number of sectors, defaulting to 8')
        sectors = 8

    _sectors = [i.upper() for i in _sectors]

    halfsector = 360 / (len(_sectors)-1)/2
    winddirection += halfsector

    ix = (int(winddirection // (360 / (len(_sectors)-1)))) % len(_sectors)
    if addunicodearrow:
        return _sectors[ix] + ' &#'+arrlist[ix]+';'

    else:
        return _sectors[ix]


if __name__ == '__main__':
    print('*'*10, 'HELP for winddirection2string', '*'*10)
    print('Converts a winddirection to a string of direction')
