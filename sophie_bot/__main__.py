import sys
import asyncio
import signal

from importlib import import_module

from sophie_bot import CONFIG, bot, redis, logger
from sophie_bot.modules import ALL_MODULES

LOAD_COMPONENTS = CONFIG["advanced"]["load_components"]


# Import modules
for module_name in ALL_MODULES:
    logger.debug("Importing " + module_name)
    imported_module = import_module("sophie_bot.modules." + module_name)

logger.info("Modules loaded!")

if LOAD_COMPONENTS is True:
    from sophie_bot.modules.components import ALL_COMPONENTS

    for module_name in ALL_COMPONENTS:
        logger.debug("Importing " + module_name)
        imported_module = import_module("sophie_bot.modules.components." + module_name)

    logger.info("Components loaded!")
else:
    logger.info("Components disabled!")


# Catch up missed updates
if CONFIG["advanced"]["catch_up"] is True:
    logger.info("Catch up missed updates..")

    try:
        asyncio.ensure_future(bot.catch_up())
    except Exception as err:
        logger.error(err)


def exit_gracefully(signum, frame):
    logger.info("Bye!")
    try:
        redis.bgsave()
    except Exception as err:
        logger.info("Redis error, exiting immediately!")
        logger.error(err)
        exit(1)
    logger.info("----------------------")
    sys.exit(1)


# Run loop
logger.info("Running loop..")
logger.info("Bot is alive!")
signal.signal(signal.SIGINT, exit_gracefully)

asyncio.get_event_loop().run_forever()
