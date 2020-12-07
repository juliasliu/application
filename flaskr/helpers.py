import math
import datetime
import re

def numbers_with_commas_list(x):
    if not isinstance(x, list):
        x = list(x)
    for i in range(len(x)):
        x[i] = numbers_with_commas(x[i])
    return x

def numbers_with_commas(x):
    if x == '':
        return ''
    elif x == "N/A":
        return x
    return "{0:,.0f}".format(x)

def filter_to_dec_list(x):
    for i in range(len(x)):
        x[i] = filter_to_dec(x[i])
    return x

def filter_to_dec(x):
    new_x = x
    if isinstance(new_x, str) and new_x != 'N/A':
        new_x = new_x.strip().replace(',', '')
        if new_x != '' and new_x.strip('%').strip('$') != '-':
            if '%' in new_x:
                new_x = new_x.strip('%')
            if '$' in new_x:
                new_x = new_x.strip('$')
            if '(' in new_x and ')' in new_x:
                new_x = -float(new_x.strip('(').strip(')'))
            else:
                new_x = float(new_x)
        else:
            new_x = 0
    return new_x

def str_to_datetime(x):
    return datetime.datetime(int(x.split("/")[1]), int(x.split("/")[0]), 1)

def dec_to_dollars_list(x):
    for i in range(len(x)):
        x[i] = dec_to_dollars(x[i])
    return x

def dec_to_dollars(x):
    if x == '':
        return ''
    elif x == "N/A":
        return x
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
    elif x == "N/A":
        return x
    return "{0:.0%}".format(float(x))

def nan_to_blank_list(x):
    for i in range(len(x)):
        x[i] = nan_to_blank(x[i])
    return x

def nan_to_blank(x):
    if x != "N/A" and math.isnan(float(x)):
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

def to_negative_list(x):
    if not isinstance(x, list):
        x = list(x)
    for i in range(len(x)):
        x[i] = to_negative(x[i])
    return x

def to_negative(x):
    if x == '':
        return ''
    return -x

def dec_to_tenths_list(x):
    if not isinstance(x, list):
        x = list(x)
    for i in range(len(x)):
        x[i] = dec_to_tenths(x[i])
    return x

def dec_to_tenths(x):
    if x == '':
        return ''
    return "{0:.1f}".format(x)
