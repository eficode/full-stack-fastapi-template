import logging

import boto3
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init_dynamodb() -> None:
    try:
        # Try to connect to DynamoDB to check if it's available
        dynamodb = boto3.resource('dynamodb', **settings.DYNAMODB_CONNECTION_CONFIG)
        dynamodb.meta.client.list_tables()
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init_dynamodb()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
