import logging
import traceback

logger = logging.getLogger("employees")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        method = request.method
        path = request.get_full_path()
        ip = request.META.get("REMOTE_ADDR")

        logger.info(f"[REQUEST] {method} {path} from {ip}")

        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(f"[EXCEPTION] {method} {path} from {ip} → {e}")
            logger.debug(traceback.format_exc())
            raise

        return response
