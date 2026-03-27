from aiogram.types import ErrorEvent
from core import errors

from bot import tools

from logging import getLogger
logger = getLogger(__name__)

async def not_found_handler(event: ErrorEvent):
    await event.update.message.delete()
    await tools.show_register(event.update.message)
    logger.warning(f"User {event.update.message.from_user.full_name} not registred")


EXCEPTION_HANDLERS = {
    errors.UserNotFoundError: not_found_handler
}