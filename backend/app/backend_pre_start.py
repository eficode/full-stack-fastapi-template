import logging
import socket
import sys
import time

import boto3
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from botocore.config import Config
from botocore.exceptions import ReadTimeoutError

from app.core.config import settings
from urllib.parse import urlparse

# Configure more detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

max_tries = 60 * 2  # 2 minutes
wait_seconds = 1


def check_network_connectivity(host: str, port: int) -> bool:
    """
    Check if a network connection can be established to the given host and port

    Args:
        host: The hostname to connect to
        port: The port to connect to

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Parse the URL using urlparse
        parsed_url = urlparse(host)
        hostname = parsed_url.hostname or host
        port = parsed_url.port or port

        logger.info(f"Testing connection to {hostname}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        if result == 0:
            logger.info(f"Successfully connected to {hostname}:{port}")
            return True
        else:
            logger.error(f"Failed to connect to {hostname}:{port} (error code: {result})")
            return False
    except Exception as e:
        logger.error(f"Error checking network connectivity: {e}")
        return False


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_dynamodb() -> None:
    """
    Try to connect to DynamoDB to verify it's available
    """
    try:
        # Create a specialized config for DynamoDB Local with more generous timeouts
        boto_config = Config(
            signature_version='v4',
            connect_timeout=2,    # Reduced from 5 to 2 seconds
            read_timeout=5,       # Added explicit read timeout
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )

        # For DynamoDB-local, we need specific configuration
        endpoint_url = settings.DYNAMODB_ENDPOINT
        region = settings.DYNAMODB_REGION

        # Log connection parameters for debugging (redacting sensitive info)
        connection_params = {
            'endpoint_url': endpoint_url,
            'region_name': region,
            'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': '***REDACTED***',
            'config': 'Config with signature_version=v4, read_timeout=5s, connect_timeout=2s'
        }
        logger.info(f"Attempting to connect to DynamoDB with params: {connection_params}")

        # Parse the endpoint URL to extract host and port
        parsed_url = urlparse(endpoint_url)
        host = parsed_url.hostname or "localhost"
        port = parsed_url.port or 8000  # Default DynamoDB port

        # Check if we can establish a TCP connection to the host:port
        if not check_network_connectivity(host, port):
            raise Exception(f"Cannot establish connection to {host}:{port}")

        logger.info("Network connectivity test passed, attempting API connection...")

        # Try a simpler operation first - just initialize the client without making calls
        dynamodb_client = boto3.client(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=boto_config
        )

        # Give DynamoDB a moment to be ready (sometimes it needs a bit of time)
        time.sleep(1)

        # Try to list tables with a retry mechanism for read timeouts
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to list tables (try {retry_count + 1}/{max_retries})...")
                tables = dynamodb_client.list_tables()
                logger.info(tables)
                logger.info(f"Successfully connected to DynamoDB. Available tables: {tables.get('TableNames', [])}")
                return  # Success, exit the function
            except ReadTimeoutError as timeout_error:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                    logger.warning(f"Read timeout, retrying in {wait_time} seconds: {timeout_error}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Exhausted retries for table listing: {timeout_error}")
                    raise Exception("Failed to list tables after multiple attempts - DynamoDB may be overloaded")

    except Exception as e:
        logger.error(f"Error connecting to DynamoDB: {str(e)}")
        raise e


def main() -> None:
    logger.info("Initializing service")
    init_dynamodb()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
