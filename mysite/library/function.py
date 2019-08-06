from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime

from random import randrange
from django.utils.translation import get_language
from webs.messages import MESSAGE_DICTIONARY

import os
import re
from uuid import uuid4

from PIL import Image
import copy


def merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(merge_dicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def validate_image(fieldfile_obj):
    im = Image.open(fieldfile_obj.file)
    im.verify()

    width, height = im.size
    file_size = 1

    megabyte_limit = 2.0
    if file_size > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def today():
    return date.today()


def day_add(time, number):
    try:
        return time + timedelta(days=number)
    except (ValueError, TypeError):
        return None


def day_sub(time, number):
    try:
        return time - timedelta(days=number)
    except (ValueError, TypeError):
        return None


def now():
    return datetime.now()


# time is datetime
def time_slot(time, hour_from, hour_to):
    try:
        to_day = time.date().strftime("%d/%m/%Y")
    except AttributeError:
        return None, None

    time_slot_from = datetime.strptime(
        '{} {:02}:00:00'.format(to_day, hour_from), '%d/%m/%Y %H:%M:%S')
    time_slot_to = datetime.strptime(
        '{} {:02}:00:00'.format(to_day, hour_to), '%d/%m/%Y %H:%M:%S')

    return time_slot_from, time_slot_to


# time is datetime
def time_slot_from_string(time, time_from, time_to):
    try:
        to_day = time.date().strftime("%d/%m/%Y")
    except AttributeError:
        return None, None

    time_slot_from = datetime.strptime(
        '{} {}'.format(to_day, time_from), '%d/%m/%Y %H:%M:%S')
    time_slot_to = datetime.strptime(
        '{} {}'.format(to_day, time_to), '%d/%m/%Y %H:%M:%S')

    return time_slot_from, time_slot_to


# time is datetime
def time_from_string(time, time_string):
    try:
        to_day = time.date().strftime("%d/%m/%Y")
    except AttributeError:
        return None

    _time = datetime.strptime('{} {}'.format(
        to_day, time_string), '%d/%m/%Y %H:%M:%S')

    return _time


def start_a_day(_date):
    try:
        to_day = _date.strftime("%d/%m/%Y")
    except AttributeError:
        return None

    _time = datetime.strptime(
        '{} 00:00:00'.format(to_day), '%d/%m/%Y %H:%M:%S')

    return _time


def end_a_day(_date):
    try:
        to_day = _date.strftime("%d/%m/%Y")
    except AttributeError:
        return None

    _time = datetime.strptime(
        '{} 23:59:59'.format(to_day), '%d/%m/%Y %H:%M:%S')

    return _time


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


from django.utils.deconstruct import deconstructible


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        upload_to = self.path
        ext = filename.split('.')[-1]
        # get filename
        if instance.pk:
            filename = '{}.{}'.format(instance.pk, ext)
        else:
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(upload_to, filename)


def format_number(value):
    if value != 0:
        _value = int(value)
        return ("{:,d}".format(_value)).replace(",", "X").replace(".", ",").replace("X", ".") if _value > 0 else ''
    return 0


def string_to_time(_string, _format='%d/%m/%Y %H:%M:%S'):
    try:
        return datetime.strptime(_string, _format)
    except (ValueError, IndexError, AttributeError):
        return None


def time_to_string(_time, _format='%d/%m/%Y %H:%M:%S'):
    if _time:
        return _time.strftime(_format)
    return ''


def set_toastr_message(request, _type, _message):
    request.session['csrf_coop_type'] = _type
    request.session['csrf_coop_message'] = _message


def get_toastr_message(request):
    if request.session.get('csrf_coop_message') and request.session.get('csrf_coop_type'):
        type = request.session['csrf_coop_type']
        message = request.session['csrf_coop_message']
        del request.session['csrf_coop_message']

        return type, message

    return None, None


def get_message(code):
    try:
        _code = int(code)
        language = get_language()

        mess_dict = MESSAGE_DICTIONARY[_code]

        if mess_dict:
            return mess_dict[language]

        return ''
    except KeyError:
        return ''


def mobile_valid(mobile):
    if mobile:
        try:
            mobile = re.sub("[^\d+]", "", mobile.replace('\\', ''))
        except ValueError:
            mobile = None

    return mobile


def check_email_valid(email):
    pattern = r'^(([^<>()\[\]\\.,:\s@"]+(\.[^<>()\[\]\\.,:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))'

    regex = re.compile(pattern)

    if regex.search(email):
        return


def convert_none_to_empty(x):
    ret = copy.deepcopy(x)
    if isinstance(x, dict):
        for k, v in ret.items():
            ret[k] = convert_none_to_empty(v)
    if isinstance(x, (list, tuple)):
        for k, v in enumerate(ret):
            ret[k] = convert_none_to_empty(v)
    if x is None:
        ret = ''
    return ret
