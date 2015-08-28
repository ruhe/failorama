import datetime
import os
import re
import requests
import time

URL_REGEX = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.]'
                       ur'[a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()'
                       ur'<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'
                       ur'[^\s`!()\[\]{};:\'".,<>?\xab\xbb'
                       ur'\u201c\u201d\u2018\u2019]))')


def find_urls(text):
    return [mgroups[0] for mgroups in URL_REGEX.findall(text)]


def get_json(url):
    res = requests.get(url)
    if res.ok:
        return res.json()
    else:
        raise Exception("Couldn't read data from url {0}".format(url))


def ident(x):
    return x


def try_index(xs, index, default=None):
    try:
        x = xs[index]
    except IndexError:
        x = default
    return x


def try_int(x):
    if x:
        return int(x)
    else:
        return None


def try_read_timestamp(ts):
    try:
        return datetime.datetime.fromtimestamp(ts)
    except:
        return None


def has_key(d, key):
    return key in d.keys() and d[key]


def select_keys(d, keys):
    return {k: d.get(k, None) for k in keys}


def rename_key(d, old, new):
    d[new] = d.pop(old)


def remove_key(d, key):
    d.pop(key, None)


def memoize(f):
    """ Memoization decorator for a function taking one or more arguments. """
    class MemoDict(dict):
        def __getitem__(self, *key):
            return dict.__getitem__(self, key)

        def __missing__(self, key):
            ret = self[key] = f(*key)
            return ret

    return MemoDict().__getitem__


def file_abs_path(file_name, closes_file_path):
    dir_path = os.path.abspath(os.path.dirname(closes_file_path))
    return os.path.join(dir_path, file_name)


def days_ago_timestamp(days):
    now = datetime.date.today()
    week_ago = now - datetime.timedelta(days=days)

    ts = time.mktime(week_ago.timetuple())
    return int(ts)


def timestamp2str(ts):
    # round timestamp to seconds
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%Y-%m-%d')
