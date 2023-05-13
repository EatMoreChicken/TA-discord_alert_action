#!/usr/bin/env python3

"""
A Splunk Alert Action script to send alerts to a Discord channel using a webhook.
"""

import requests
import json
import datetime
import logging
import sys
import fnmatch

# Configure logging
log_format = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)
logger = logging.getLogger('discord_alert_action')
logger.setLevel(logging.INFO)

debug_logger = logging.getLogger('discord_alert_action_debug')
debug_logger.setLevel(logging.WARNING)  # Disable debug logging by default
# debug_logger.setLevel(logging.DEBUG)  # Enable debug logging
debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.setFormatter(logging.Formatter(log_format))
debug_logger.addHandler(debug_handler)

logger.info('event="Starting discord_alert_action.py"')

# Trims message to fit Discord's documentation
def trim_message(message):
    """
    Trims the message to fit Discord's 2000 character limit.

    Args:
        message (str): The message to be trimmed.

    Returns:
        str: The trimmed message.
    """
    max_length = 2000
    suffix = "\n...View the alert for more information"
    
    if len(message) <= max_length:
        return message
    else:
        debug_logger.debug(f'event="Message length is too long" length={len(message)}')
        trimmed_message = message[:max_length-len(suffix)] + suffix
        debug_logger.debug(f'event="New length." length={len(trimmed_message)}')
        return trimmed_message

def send_discord_message(webhook_url, json_data, field_names):
    """
    Sends a formatted Discord message using a webhook.

    Args:
        webhook_url (str): The Discord webhook URL.
        json_data (dict): The JSON data containing alert information.
        field_names (list[str]): The field names to include in the message.
    """
    search_name = json_data['search_name']
    results_link = json_data['results_link']
    results = json_data['result']
    server_host = json_data['server_host']

    # Logging parameters
    debug_logger.debug(f'event="Webhook URL" webhook_url="{webhook_url}"')
    debug_logger.debug(f'event="Search Name" search_name="{search_name}"')
    debug_logger.debug(f'event="Results Link" results_link="{results_link}"')
    debug_logger.debug(f'event="Server Host" server_host="{server_host}"')
    debug_logger.debug(f'event="Available Fields" results="{results}"')
    debug_logger.debug(f'event="Selected Fields" field_names="{field_names}"')

    # Format the message with timestamp
    message = f'# [{search_name}]({results_link}) from `{server_host}`\n'
    message += f'**Alert Fields**\n'

    # Format and append the result fields
    for key, value in results.items():
        for field_name in field_names:
            debug_logger.debug(f'event="Key and Field Name" key="{key}" field_name="{field_name}"')
            if fnmatch.fnmatch(key, field_name):
                message += f'- **{key}:** {value}\n'
                break
    message += f'---\n'

    # Trim the message if necessary to fit Discord's character limit
    message = trim_message(message)

    # Prepare the payload for the Discord webhook
    payload = {'content': message}

    debug_logger.debug(f'event="Payload to Discord" payload="{payload}"')

    try:
        # Send the POST request to the Discord webhook
        response = requests.post(
            webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}
        )

        # Check the response status
        if response.status_code == 204:
            logger.info('event="Message sent successfully."')
        else:
            logger.error(f'event="Failed to send message." status_code={response.status_code}')
    except requests.RequestException as e:
        logger.exception('event="An error occurred while sending the Discord message."', exc_info=e)

if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--execute':
            logger.info('event="Running as alert action"')

            # Read the payload from stdin
            payload_str = sys.stdin.read()
            debug_logger.debug(f'event="Payload" payload="{payload_str}"')

            # Parse the payload as JSON
            json_data = json.loads(payload_str)

            # Extract webhook URL and field names from configuration
            webhook_url = json_data['configuration']['webhook_url']
            field_names = json_data['configuration']['field_names']

            # Split field_names into a list
            try:
                field_names = field_names.split(",")
            except AttributeError as e:
                logger.error(f'event="Error splitting field names" error="{e}"')

            debug_logger.debug(f'event="Field Names" field_names="{field_names}"')
            debug_logger.debug(f'event="Alert action webhook URL" webhook_url="{webhook_url}"')
            debug_logger.debug(f'event="Chosen Fields" chosen_fields="{field_names}"')

            # Call the function to send the Discord message
            send_discord_message(webhook_url, json_data, field_names)
    except Exception as e:
        logger.error(f'event="An error occurred" error="{e}"')