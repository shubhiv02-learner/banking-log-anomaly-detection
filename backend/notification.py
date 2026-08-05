import json

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from backend.logging_config import get_logger

logger = get_logger(__name__)


def notify_n8n(webhook_url: str, payload: dict):
    """
    Generic function to invoke an n8n webhook.

    Returns:
    {
        "success": True/False,
        "status": HTTP status,
        "response": response body,
        "error": error message
    }
    """

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
            logger.info(
                "n8n webhook success status=%s url=%s",
                response.status,
                webhook_url,
            )
            logger.debug("n8n response body: %s", body)

            return {
                "success": True,
                "status": response.status,
                "response": body,
            }

    except HTTPError as e:
        logger.error(
            "n8n HTTP error code=%s reason=%s url=%s",
            e.code,
            e.reason,
            webhook_url,
        )

        return {
            "success": False,
            "status": e.code,
            "error": str(e.reason),
        }

    except URLError as e:
        logger.error(
            "n8n URL error reason=%s url=%s",
            e.reason,
            webhook_url,
        )

        return {
            "success": False,
            "status": None,
            "error": str(e.reason),
        }

    except Exception:
        logger.exception("n8n webhook failed url=%s", webhook_url)

        return {
            "success": False,
            "status": None,
            "error": "unexpected error",
        }
