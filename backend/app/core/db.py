import boto3
import logging
import time
import uuid
from boto3.resources.base import ServiceResource
from boto3.dynamodb.table import TableResource
from botocore.config import Config
from botocore.exceptions import ReadTimeoutError
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.constants import BOOK_TABLE, USER_TABLE
from app.core.config import settings
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

# Create DynamoDB resource
@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
def get_dynamodb_resource() -> ServiceResource:
    """
    Create and return a boto3 DynamoDB resource with proper credentials and configuration
    with retry logic for better reliability

    Returns:
        ServiceResource: Configured DynamoDB resource
    """
    try:
        # Create a specialized config for DynamoDB Local with shorter timeouts
        boto_config = Config(
            signature_version='v4',
            connect_timeout=2,
            read_timeout=5,
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            }
        )

        # Log the connection attempt
        endpoint_url = settings.DYNAMODB_ENDPOINT
        region = settings.DYNAMODB_REGION
        logger.info(f"Connecting to DynamoDB at {endpoint_url}")

        # Create the resource with explicit credentials
        resource = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=boto_config
        )

        # Test the connection with a simple operation
        try:
            resource.meta.client.list_tables()
        except ReadTimeoutError:
            # If we get a timeout, wait a bit and try once more directly
            logger.warning("Initial timeout connecting to DynamoDB, retrying after short delay")
            time.sleep(2)
            resource.meta.client.list_tables(Limit=1)

        return resource
    except Exception as e:
        logger.error(f"Failed to connect to DynamoDB: {str(e)}")
        raise

# Initialize the DynamoDB resource with retry logic
try:
    dynamodb_resource = get_dynamodb_resource()
except Exception as e:
    logger.error(f"Failed to initialize DynamoDB resource after multiple attempts: {str(e)}")
    # We'll still define the resource variable, but operations will fail until the service is available
    # This allows the application to start and retry connections later
    dynamodb_resource = None

def create_tables_if_not_exist():
    """Create DynamoDB tables if they don't exist"""
    # If initial connection failed, try again
    global dynamodb_resource
    if dynamodb_resource is None:
        try:
            dynamodb_resource = get_dynamodb_resource()
        except Exception as e:
            logger.error(f"Still unable to connect to DynamoDB: {str(e)}")
            raise

    try:
        existing_tables = dynamodb_resource.meta.client.list_tables()['TableNames']
        logger.info(f"Existing tables: {existing_tables}")

        # Create User table if it doesn't exist
        if USER_TABLE not in existing_tables:
            logger.info(f"Creating {USER_TABLE} table")
            dynamodb_resource.create_table(
                TableName=USER_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'email', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'email_index',
                        'KeySchema': [
                            {'AttributeName': 'email', 'KeyType': 'HASH'},
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            # Wait briefly for table creation to complete
            time.sleep(2)

        # Create Book table if it doesn't exist
        if BOOK_TABLE not in existing_tables:
            logger.info(f"Creating {BOOK_TABLE} table")
            dynamodb_resource.create_table(
                TableName=BOOK_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'owner_id', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'owner_index',
                        'KeySchema': [
                            {'AttributeName': 'owner_id', 'KeyType': 'HASH'},
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            # Wait briefly for table creation to complete
            time.sleep(2)
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        raise

def get_table(table_name: str) -> TableResource:
    """
    Get a DynamoDB table by name, with retry logic if connection was lost

    Args:
        table_name: Name of the DynamoDB table

    Returns:
        TableResource: DynamoDB table resource
    """
    global dynamodb_resource
    # If the resource is None or we encounter an error, try to reconnect
    if dynamodb_resource is None:
        dynamodb_resource = get_dynamodb_resource()

    return dynamodb_resource.Table(table_name)


def _create_superuser(email: str, password: str) -> None:
    """
    Create a superuser directly without using crud functions

    Args:
        email: Email for the superuser
        password: Password for the superuser
    """
    user_id = str(uuid.uuid4())

    user_data = {
        "id": user_id,
        "email": email,
        "hashed_password": get_password_hash(password),
        "full_name": "Initial Superuser",
        "is_active": True,
        "is_superuser": True
    }

    user_table = get_table(USER_TABLE)
    user_table.put_item(Item=user_data)
    logger.info(f"Superuser {email} created with ID {user_id}")


def init_db() -> None:
    """Initialize the database with the first superuser if it doesn't exist"""
    try:
        # First, make sure tables exist
        create_tables_if_not_exist()

        # Get the user table
        user_table = get_table(USER_TABLE)

        # Check if superuser exists by email using GSI
        response = user_table.query(
            IndexName='email_index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(settings.FIRST_SUPERUSER)
        )

        # If superuser doesn't exist, create it
        if not response['Items']:
            logger.info(f"Creating superuser {settings.FIRST_SUPERUSER}")
            _create_superuser(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD
            )
    except Exception as e:
        logger.error(f"Error initializing DB: {str(e)}")
        raise
