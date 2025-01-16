import logging
import json

from app.core.config import settings

class StructuredLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if extra is None:
            extra = {}
        extra['app_name'] = settings.app_name
        super()._log(level, json.dumps(msg) if isinstance(msg, dict) else msg, args, exc_info, extra, stack_info)
