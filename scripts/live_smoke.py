import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from bin.rw.get_session import get_session
from bin.control.parser import parser
from env_loader import session, logger

arg = 'Малмыж - Инфо_kultura'
logger.info('Starting live smoke for: %s', arg)
try:
    get_session(arg)
    logger.info('Session keys: %s', {k: session.get(k) for k in ('region_name','name_session','name_base','_regional_name_base','work')})
    res = parser(stat_mode=True)
    logger.info('Parser result: %s', res)
except Exception as e:
    logger.exception('Live smoke failed: %s', e)
    raise
