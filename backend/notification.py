import json

from urllib import response
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


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

            print("Response Status:", response.status, flush=True )
            print("Response Body:", body)

            return {
                    "success": True,
                    "status": response.status,
                    "response": body
                }
            

    except HTTPError as e:

        print(f"n8n HTTP Error {e.code}: {e.reason}")

        return {
            "success": False,
            "status": e.code,
            "error": str(e.reason)
        }

    except URLError as e:

        print(f"n8n URL Error: {e.reason}")

        return {
            "success": False,
            "status": None,
            "error": str(e.reason)
        }

    except Exception as ex:

        print(f"n8n Error: {ex}")

        return {
            "success": False,
            "status": None,
            "error": str(ex)
        }