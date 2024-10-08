import os
import io
import base64
import imghdr
import mimetypes
from insightscapehub.utils.settings import DOCUMENT_EXTENSIONS, AUDIO_EXTENSIONS, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from insightscapehub.utils.helpers import get_extensions_from_env
import os


def get_file_type(file_path, file_ext: str = "*"):
    """
    Determine the file type based on file extension.

    Parameters:
    - file_path (str): The path to the file.
    - file_ext (str): The desired file extension for the returned MIME type.

    Returns:
    - tuple: A tuple containing the file type (image, video, audio, document, or unknown) and the MIME type.
    """
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    image_extensions = get_extensions_from_env(IMAGE_EXTENSIONS)
    video_extensions = get_extensions_from_env(VIDEO_EXTENSIONS)
    audio_extensions = get_extensions_from_env(AUDIO_EXTENSIONS)
    document_extensions = get_extensions_from_env(DOCUMENT_EXTENSIONS)

    if file_extension in image_extensions:
        return 'image', f'image/{file_ext}'
    elif file_extension in video_extensions:
        return 'video', f'video/{file_ext}'
    elif file_extension in audio_extensions:
        return 'audio', f'audio/{file_ext}'
    elif file_extension in document_extensions:
        document_mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
            '.odp': 'application/vnd.oasis.opendocument.presentation',
            '.epub': 'application/epub+zip'
        }
        mime_type = document_mime_types.get(
            file_extension, 'application/octet-stream')
        return 'document', mime_type
    else:
        return 'unknown', 'application/octet-stream'


def get_image_info_from_base64(base64_string):
    """
    Get information about an image encoded in base64.

    Args:
        base64_string (str): The base64-encoded string representing an image.

    Returns:
        tuple: A tuple containing image type, MIME type, and file extension.
               If an error occurs during decoding or determining the image information,
               returns (None, None, None).
    """
    try:
        image_bytes = base64.b64decode(base64_string)
        file_type = imghdr.what(io.BytesIO(image_bytes))
        mime_type, _ = mimetypes.guess_type(f"image.{file_type}")
        image_type, _, file_ext = mime_type.partition('/')
        return image_type, mime_type, file_ext
    except Exception as e:
        return None, None, None


def is_base64_image(data):
    """
    Check if the given base64-encoded data represents an image.

    Args:
        data (str): The base64-encoded string.

    Returns:
        bool: True if the decoded data has a recognized image header,
              False otherwise.
    """
    try:
        decoded_data = base64.b64decode(data)
    except:
        return False
    image_headers = [b'\xFF\xD8\xFF',  # JPEG
                     b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A',  # PNG
                     b'GIF',  # GIF
                     b'\x42\x4D']  # BMP
    for header in image_headers:
        if decoded_data.startswith(header):
            return True
    return False


def extract_base64_from_data_uri(data_uri):
    """
    Extracts the Base64 value from a Data URI.

    Args:
        data_uri (str): The Data URI containing the image data.

    Returns:
        str: The plain Base64 value extracted from the Data URI.
             Returns None if an error occurs during extraction.
    """
    try:
        header, base64_data = data_uri.split(",", 1)
        if "base64" not in header:
            raise ValueError("Not a valid Data URI with base64 encoding")
        return base64_data
    except Exception as e:
        return None
