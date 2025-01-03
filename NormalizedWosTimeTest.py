import NormalizedWoSTime

## Logging
import logging
import logging.handlers
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

logHandler = logging.handlers.RotatingFileHandler(
        filename='test.log',
        encoding='utf-8',
        mode='w',
        maxBytes=32 * 1024 * 1024, # 32MB
        backupCount=5
    )
dt_fmt = '%Y-%m-%d %H:%M:%S'
logFormatter = logging.Formatter(
    '[{asctime}] [{levelname:<8}] {name}: {message}',
    style='{',
    datefmt=dt_fmt
)
logHandler.setFormatter(logFormatter)
logger.addHandler(logHandler)

testCases = [
    '1', '12', '123', '1:23', '1234', '12:34', '12345', '1:23:45', '123456', '12:34:56',
    '9', '60', '960', '9:60', '6060', '60:60', '96060', '9:60:60', '246060', '24:60:60'
]

import NormalizedWoSTime

before = NormalizedWoSTime.CreateNormalizedWoSTime('0', logger)
for testCase in testCases:
    try:
        normalizedTime = NormalizedWoSTime.CreateNormalizedWoSTime(testCase, logger)
        logger.info(f'Base FullUTC: {normalizedTime.getFullUTCFormat()} FullSeconds: {normalizedTime.convertToSeconds()} Hour: {normalizedTime.hour}, Minutes: {normalizedTime.minutes}, Seconds: {normalizedTime.seconds}')
        logger.info(f'before FullUTC: {before.getFullUTCFormat()} FullSeconds: {before.convertToSeconds()} Hour: {before.hour}, Minutes: {before.minutes}, Seconds: {before.seconds}')
        added = normalizedTime + before
        logger.info(f'Added FullUTC: {added.getFullUTCFormat()} FullSeconds: {added.convertToSeconds()} Hour: {added.hour}, Minutes: {added.minutes}, Seconds: {added.seconds}')
        subbed = normalizedTime - before
        logger.info(f'Subbed FullUTC: {subbed.getFullUTCFormat()} FullSeconds: {subbed.convertToSeconds()} Hour: {subbed.hour}, Minutes: {subbed.minutes}, Seconds: {subbed.seconds}')
        logger.info('----------------------------------------')
    except Exception as e:
        continue
    finally:
        before = normalizedTime
        pass
