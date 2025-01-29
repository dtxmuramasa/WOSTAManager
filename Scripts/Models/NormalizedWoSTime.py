from datetime import datetime, timedelta
import re
import logging

class NormalizedWoSTime:
    ALLOW_FORMAT = '【(入力内容)->(解釈結果)】35->00:00:35 / 204->00:02:04 / 235959->23:59:59 / 23:59:59->23:59:59'
    
    TIME_FORMAT = {
        'S':        re.compile(r'^([0-9])$'),
        'SS':       re.compile(r'^([0-5][0-9])$'),
        'MSS':      re.compile(r'^([0-9])([0-5][0-9])$'),
        'MMSS':     re.compile(r'^([0-5][0-9])([0-5][0-9])$'),
        'McSS':     re.compile(r'^([0-9]):([0-5][0-9])$'),
        'MMcSS':    re.compile(r'^([0-5][0-9]):([0-5][0-9])$'),
        'HMMSS':    re.compile(r'^([0-9])([0-5][0-9])([0-5][0-9])$'),
        'HHMMSS':   re.compile(r'^([0-2][0-9])([0-5][0-9])([0-5][0-9])$'),
        'HcMMcSS':  re.compile(r'^([0-9]):([0-5][0-9]):([0-5][0-9])$'),
        'HHcMMcSS': re.compile(r'^([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$'),
    }
    
    TIME_FORMAT_MIN = {
        'minS':        re.compile(r'^(-)([0-9])$'),
        'minSS':       re.compile(r'^(-)([0-5][0-9])$'),
        'minMSS':      re.compile(r'^(-)([0-9])([0-5][0-9])$'),
        'minMMSS':     re.compile(r'^(-)([0-5][0-9])([0-5][0-9])$'),
        'minMcSS':     re.compile(r'^(-)([0-9]):([0-5][0-9])$'),
        'minMMcSS':    re.compile(r'^(-)([0-5][0-9]):([0-5][0-9])$'),
        'minHMMSS':    re.compile(r'^(-)([0-9])([0-5][0-9])([0-5][0-9])$'),
        'minHHMMSS':   re.compile(r'^(-)([0-2][0-9])([0-5][0-9])([0-5][0-9])$'),
        'minHcMMcSS':  re.compile(r'^(-)([0-9]):([0-5][0-9]):([0-5][0-9])$'),
        'minHHcMMcSS': re.compile(r'^(-)([0-2][0-9]):([0-5][0-9]):([0-5][0-9])$')
    }
    
    def __init__(self, time: str, logger: logging.Logger = None):
        self.srcTime = time
        self.logger = logger
        
        self.srcTimeFormat = NormalizedWoSTime.getTimeFormat(time)
        if self.srcTimeFormat is None:
            self.logError(f'Invalid time format: {time}')
            raise ValueError(f'Invalid time format: {time}')
        
        self.isMinus = NormalizedWoSTime.isMinusType(time)
        self.hour = self.getHourFromString()
        self.minutes = self.getMinutesFromString()
        self.seconds = self.getSecondsFromString()
        self.datetime = datetime.strptime(self.getFullUTCFormat(), '%H:%M:%S')
    
    def logInfo(self, message: str):
        if self.logger:
            self.logger.info(message)
            
    def logWarning(self, message: str):
        if self.logger:
            self.logger.warning(message)
    
    def logError(self, message: str):
        if self.logger:
            self.logger.error(message)
    
    @staticmethod
    def getTimeFormat(time: str):
        for formatType, formatPattern in NormalizedWoSTime.TIME_FORMAT.items():
            if formatPattern.match(time):
                return formatType
        for formatType, formatPattern in NormalizedWoSTime.TIME_FORMAT_MIN.items():
            if formatPattern.match(time):
                return formatType
        return None
    
    @staticmethod
    def isMinusType(time: str) -> bool:
        return time.startswith('-')
    
    def getHourFromString(self) -> int:
        hour = None
        if self.srcTimeFormat == 'S':
            hour = 0
        elif self.srcTimeFormat == 'SS':
            hour = 0
        elif self.srcTimeFormat == 'MSS':
            hour = 0
        elif self.srcTimeFormat == 'MMSS':
            hour = 0
        elif self.srcTimeFormat == 'McSS':
            hour = 0
        elif self.srcTimeFormat == 'MMcSS':
            hour = 0
        elif self.srcTimeFormat == 'HMMSS':
            hour = int(self.srcTime[0])
        elif self.srcTimeFormat == 'HHMMSS':
            hour = int(self.srcTime[0:2])
        elif self.srcTimeFormat == 'HcMMcSS':
            hour = int(self.srcTime[0])
        elif self.srcTimeFormat == 'HHcMMcSS':
            hour = int(self.srcTime[0:2])
        elif self.srcTimeFormat == 'minS':
            hour = 0
        elif self.srcTimeFormat == 'minSS':
            hour = 0
        elif self.srcTimeFormat == 'minMSS':
            hour = 0
        elif self.srcTimeFormat == 'minMMSS':
            hour = 0
        elif self.srcTimeFormat == 'minMcSS':
            hour = 0
        elif self.srcTimeFormat == 'minMMcSS':
            hour = 0
        elif self.srcTimeFormat == 'minHMMSS':
            hour = int(self.srcTime[1])
        elif self.srcTimeFormat == 'minHHMMSS':
            hour = int(self.srcTime[1:3])
        elif self.srcTimeFormat == 'minHcMMcSS':
            hour = int(self.srcTime[1])
        elif self.srcTimeFormat == 'minHHcMMcSS':
            hour = int(self.srcTime[1:3])
        return hour if hour != None and hour >= 0 and hour <= 23 else None
    
    def getMinutesFromString(self) -> int:
        min = None
        if self.srcTimeFormat == 'S':
            min = 0
        elif self.srcTimeFormat == 'SS':
            min = 0
        elif self.srcTimeFormat == 'MSS':
            min = int(self.srcTime[0])
        elif self.srcTimeFormat == 'MMSS':
            min = int(self.srcTime[0:2])
        elif self.srcTimeFormat == 'McSS':
            min = int(self.srcTime[0])
        elif self.srcTimeFormat == 'MMcSS':
            min = int(self.srcTime[0:2])
        elif self.srcTimeFormat == 'HMMSS':
            min = int(self.srcTime[1:3])
        elif self.srcTimeFormat == 'HHMMSS':
            min = int(self.srcTime[2:4])
        elif self.srcTimeFormat == 'HcMMcSS':
            min = int(self.srcTime[2:4])
        elif self.srcTimeFormat == 'HHcMMcSS':
            min = int(self.srcTime[3:5])
        elif self.srcTimeFormat == 'minS':
            min = 0
        elif self.srcTimeFormat == 'minSS':
            min = 0
        elif self.srcTimeFormat == 'minMSS':
            min = int(self.srcTime[2])
        elif self.srcTimeFormat == 'minMMSS':
            min = int(self.srcTime[2:4])
        elif self.srcTimeFormat == 'minMcSS':
            min = int(self.srcTime[2])
        elif self.srcTimeFormat == 'minMMcSS':
            min = int(self.srcTime[2:4])
        elif self.srcTimeFormat == 'minHMMSS':
            min = int(self.srcTime[1:3])
        elif self.srcTimeFormat == 'minHHMMSS':
            min = int(self.srcTime[3:5])
        elif self.srcTimeFormat == 'minHcMMcSS':
            min = int(self.srcTime[3:5])
        elif self.srcTimeFormat == 'minHHcMMcSS':
            min = int(self.srcTime[4:6])
        return min if min != None and min >= 0 and min <= 59 else None
    
    def getSecondsFromString(self) -> int:
        sec = None
        if self.srcTimeFormat == 'S':
            sec = int(self.srcTime)
        elif self.srcTimeFormat == 'SS':
            sec = int(self.srcTime)
        elif self.srcTimeFormat == 'MSS':
            sec = int(self.srcTime[1:])
        elif self.srcTimeFormat == 'MMSS':
            sec = int(self.srcTime[2:])
        elif self.srcTimeFormat == 'McSS':
            sec = int(self.srcTime[2:])
        elif self.srcTimeFormat == 'MMcSS':
            sec = int(self.srcTime[3:])
        elif self.srcTimeFormat == 'HMMSS':
            sec = int(self.srcTime[3:])
        elif self.srcTimeFormat == 'HHMMSS':
            sec = int(self.srcTime[4:])
        elif self.srcTimeFormat == 'HcMMcSS':
            sec = int(self.srcTime[5:])
        elif self.srcTimeFormat == 'HHcMMcSS':
            sec = int(self.srcTime[6:])
        elif self.srcTimeFormat == 'minS':
            sec = int(self.srcTime[2])
        elif self.srcTimeFormat == 'minSS':
            sec = int(self.srcTime[3])
        elif self.srcTimeFormat == 'minMSS':
            sec = int(self.srcTime[3:])
        elif self.srcTimeFormat == 'minMMSS':
            sec = int(self.srcTime[4:])
        elif self.srcTimeFormat == 'minMcSS':
            sec = int(self.srcTime[4:])
        elif self.srcTimeFormat == 'minMMcSS':
            sec = int(self.srcTime[5:])
        elif self.srcTimeFormat == 'minHMMSS':
            sec = int(self.srcTime[4:])
        elif self.srcTimeFormat == 'minHHMMSS':
            sec = int(self.srcTime[5:])
        elif self.srcTimeFormat == 'minHcMMcSS':
            sec = int(self.srcTime[6:])
        elif self.srcTimeFormat == 'minHHcMMcSS':
            sec = int(self.srcTime[7:])
        return sec if sec != None and sec >= 0 and sec <= 59 else None
    
    def convertToSeconds(self) -> int:
        totalSeconds = self.hour * 3600 + self.minutes * 60 + self.seconds
        return totalSeconds if not self.isMinus else -totalSeconds
    
    def getFullUTCFormat(self) -> str:
        utcFormat = f'{str(self.hour).zfill(2)}:{str(self.minutes).zfill(2)}:{str(self.seconds).zfill(2)}'
        return utcFormat if not self.isMinus else f'-{utcFormat}'

    def __add__(self, other):
        if not isinstance(other, NormalizedWoSTime):
            raise ValueError('Invalid operand type')
        timeStr = BuildTimeStringFromSeconds(self.convertToSeconds() + other.convertToSeconds())
        return CreateNormalizedWoSTime(timeStr, self.logger)

    def __sub__(self, other):
        if not isinstance(other, NormalizedWoSTime):
            raise ValueError('Invalid operand type')
        timeStr = BuildTimeStringFromSeconds(self.convertToSeconds() - other.convertToSeconds())
        return CreateNormalizedWoSTime(timeStr, self.logger)

def CreateNormalizedWoSTime(time: str, logger: logging.Logger = None):
    normalizedTime = NormalizedWoSTime(time, logger)
    return normalizedTime or None

def CreateNormalizedWoSTimeFromSeconds(seconds: int, logger: logging.Logger = None):
    timeStr = BuildTimeStringFromSeconds(seconds)
    return CreateNormalizedWoSTime(timeStr, logger)

def BuildTimeStringFromSeconds(seconds: int):
    abs_seconds = abs(seconds)
    abs_seconds_str = f'{str(abs_seconds // 3600).zfill(2)}:{str(abs_seconds // 60 % 60).zfill(2)}:{str(abs_seconds % 60).zfill(2)}'
    return abs_seconds_str if seconds >= 0 else f'-{abs_seconds_str}'
