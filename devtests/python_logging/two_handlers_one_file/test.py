import logging.config
logging.config.fileConfig('log.conf')

normal_log = logging.getLogger('normal')
short_log = logging.getLogger('short')


normal_log.info("A message to file and console")
short_log.info("A short message to file and console")



