import pytz
from datetime import datetime, timedelta, time
from .logging import utilsLogger
from .constants import CLASSES

### timezone = "Australia/Sydney"
def getTimeOffset(timezone):
    try:
        tz = pytz.timezone(timezone)
        current_offset = tz.localize(datetime.now()).utcoffset()
        return current_offset.seconds/3600
    except KeyError:
        utilsLogger.error ("getTimeOffset(%s) call failed" % timezone, exc_info=True)
        return None

### timezone = "Australia/Sydney"
def getCountryCode(timezone):
    for country_code, timezones in pytz.country_timezones.items():
        if timezone in timezones:
            return country_code
    return None

### timezone = "Australia/Sydney"
def getTimeRageInADay(timezone, dateStr=datetime.now().strftime("%Y-%m-%d")):
    try:
        offset = getTimeOffset (timezone)
        if offset is None: offset = 0
        # Get the current date in GMT
        gmt_timezone = pytz.timezone('GMT')
        current_date_gmt = gmt_timezone.localize (datetime.strptime(dateStr, "%Y-%m-%d"))

        # Create the start and end time for the time range
        start_time = datetime.combine(current_date_gmt, time.min)
        end_time = datetime.combine(current_date_gmt, time.max)

        # Convert the start and end time to GMT
        start_time_gmt = gmt_timezone.localize(start_time)
        end_time_gmt = gmt_timezone.localize(end_time)

        start_time_gmt -= timedelta(hours=offset)
        end_time_gmt -= timedelta(hours=offset)

        return [start_time_gmt, end_time_gmt]
    except Exception as e:
        utilsLogger.error ("getTimeRageInADay() call failed.", exc_info=True)
        return [None, None]

def getTimezonesInCountry(countryCode):
    return pytz.country_timezones.get(countryCode.upper(), [])

def getOffsetRangeOfCountry(countryCode):
    try:
        timezones = getTimezonesInCountry(countryCode)
        offsets = [getTimeOffset(timezone) for timezone in timezones]
        return [min(offsets), max(offsets)]
    except Exception as e:
        utilsLogger.error ("getTimeRangeOfCountry() call failed.", exc_info=True)
        return [0, 0]

def getTimeRangeOfCountry(dateStr, countryCode):
    [minOffset, maxOffset] = getOffsetRangeOfCountry(countryCode)
    
    gmt_timezone = pytz.timezone('GMT')
    current_date_gmt = gmt_timezone.localize (datetime.strptime(dateStr, "%Y-%m-%d"))

    # Create the start and end time for the time range
    start_time = datetime.combine(current_date_gmt, time.min)
    end_time = datetime.combine(current_date_gmt, time.max)

    # Convert the start and end time to GMT
    start_time_gmt = gmt_timezone.localize(start_time)
    end_time_gmt = gmt_timezone.localize(end_time)

    start_time_gmt -= timedelta(hours=maxOffset)
    end_time_gmt -= timedelta(hours=minOffset)

    return [start_time_gmt, end_time_gmt]

def getRegularClassStr(classStr):
    orgClassStr = classStr
    classStr = classStr.strip()
    classStr = classStr.upper()
    if len(classStr) == 0: return "Class 1"

    if classStr[-1] == "+":
        orgClassStr = orgClassStr[:-1]
    if classStr in list(CLASSES.keys()):
        return classStr
    if classStr.startswith ('BM'):
        orgClassStr = "Benchmark " + orgClassStr[2:]
    elif classStr.startswith ('CLS'):
        orgClassStr = "Class" + orgClassStr[3:]
    elif classStr.startswith ('OPEN'):
        orgClassStr = "Open Handicap"
    elif classStr.startswith ('MDN'):
        orgClassStr = "Maiden"
    elif classStr.startswith ('RESTRICTED'):
        orgClassStr = "RST" + orgClassStr[10:].strip()
    elif classStr.startswith ('RS0'):
        orgClassStr = "RS0" + orgClassStr[3:].strip()
    elif classStr.startswith ('RS1'):
        orgClassStr = "RS1" + orgClassStr[3:].strip()
    elif classStr.startswith ('JUMPER'):
        orgClassStr = "Jumper Flat"
    return orgClassStr

def getClassPoint(classStr):
    classStr = getRegularClassStr(classStr)
    if classStr in list(CLASSES.keys()):
        return CLASSES[classStr]
    else:
        return 0