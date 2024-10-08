import httpx
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Union, List, Tuple

# Configure logging
logging.basicConfig(
    filename='request_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RequestError(Exception):
    """Custom exception class to encapsulate all request-related errors."""

    def __init__(self, message: str, original_error: Exception, response: Optional[httpx.Response] = None):
        self.message = message
        self.original_error = original_error
        self.response = response
        super().__init__(self.message)


async def make_request_async(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    files: Optional[Union[Tuple[str, Tuple[str, bytes, Optional[str]]],
                          List[Tuple[str, Tuple[str, bytes, Optional[str]]]]]] = None,
    timeout: Optional[int] = None
) -> Union[httpx.Response, RequestError]:
    """
    Make an asynchronous HTTP request using HTTPX and handle all types of errors.

    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
        url (str): The URL to send the request to
        headers (dict, optional): Request headers
        params (dict, optional): URL parameters
        data (dict, optional): Form data to send
        json_data (dict, optional): JSON data to send
        files (Union[Tuple, List], optional): Single or multiple file(s) to send
        timeout (int, optional): Request timeout in seconds

    Returns:
        Union[httpx.Response, RequestError]: The response object if successful, or a RequestError if an error occurred

    Raises:
        RequestError: If any request-related error occurs
    """
    try:
        if files and isinstance(files, tuple):
            files = [files]

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                files=files,
                timeout=timeout
            )

            if response.status_code >= 400:
                error = httpx.HTTPStatusError(
                    f"{response.status_code} {response.reason_phrase} for url {response.url}",
                    request=response.request,
                    response=response
                )
                log_error(error, method, url, headers, params,
                          data, json_data, files, timeout, response)
                return RequestError(str(error), error, response)

            return response

    except httpx.RequestError as e:
        log_error(e, method, url, headers, params,
                  data, json_data, files, timeout)
        return RequestError(str(e), e)
    except Exception as e:
        log_error(e, method, url, headers, params,
                  data, json_data, files, timeout)
        return RequestError(f"Unexpected error: {str(e)}", e)


def log_error(e: Exception, method: str, url: str, headers: Optional[Dict[str, str]],
              params: Optional[Dict[str, Any]], data: Optional[Dict[str, Any]],
              json_data: Optional[Dict[str, Any]], files: Optional[List[Tuple[str, Tuple[str, bytes, Optional[str]]]]],
              timeout: Optional[int], response: Optional[httpx.Response] = None):
    """
    Log error details to file.
    """
    error_data = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(e).__name__,
        "error_message": str(e),
        "request_info": {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "data": data,
            "json_data": json_data,
            "files": [{"field_name": f[0], "filename": f[1][0]} for f in files] if files else None,
            "timeout": timeout
        }
    }

    if response:
        error_data["response_info"] = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text
        }

    logger.error(json.dumps(error_data, indent=2))
