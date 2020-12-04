def dollars_to_dec(x):
    for i in range(len(x)):
        if x[i] != '' and isinstance(x[i], str):
            x[i] = float(x[i].strip('$').strip().replace(',', ''))
        elif x[i] == '':
            x[i] = 0
    return x

def dec_to_dollars(x):
    for i in range(len(x)):
        if x[i] != 0:
            x[i] = '$%.2f' % x[i]
        else:
            x[i] = ''
    return x

def dec_to_percents(x):
    for i in range(len(x)):
        if x[i] != 0:
            x[i] = "{:.2%}".format(x[i])
        else:
            x[i] = ''
    return x
