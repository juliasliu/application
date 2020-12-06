import math
import datetime

def numbers_with_commas_list(x):
    if not isinstance(x, list):
        x = list(x)
    for i in range(len(x)):
        x[i] = numbers_with_commas(x[i])
    return x

def numbers_with_commas(x):
    if x == '':
        return ''
    return "{0:,.0f}".format(x)

def dollars_to_dec_list(x):
    for i in range(len(x)):
        x[i] = dollars_to_dec(x[i])
    return x

def dollars_to_dec(x):
    if x != '' and isinstance(x, str):
        return float(x.strip('$').strip().replace(',', ''))
    elif x == '':
        return 0

def str_to_datetime(x):
    return datetime.datetime(int(x.split("/")[1]), int(x.split("/")[0]), 1)

def dec_to_dollars_list(x):
    for i in range(len(x)):
        x[i] = dec_to_dollars(x[i])
    return x

def dec_to_dollars(x):
    if x == '':
        return ''
    return "$"+"{0:,.0f}".format(x)

def dec_to_percents_list(x):
    if not isinstance(x, list):
        x = list(x)
    for i in range(len(x)):
        x[i] = dec_to_percents(x[i])
    return x

def dec_to_percents(x):
    if x == '':
        return ''
    return "{0:.0%}".format(float(x))

def na_to_blank_list(x):
    for i in range(len(x)):
        x[i] = na_to_blank(x[i])
    return x

def na_to_blank(x):
    if math.isnan(float(x)):
        return ''
    return x

def zero_to_blank_list(x):
    for i in range(len(x)):
        x[i] = zero_to_blank(x[i])
    return x

def zero_to_blank(x):
    if x == 0:
        return ''
    return x
