import requests
import json
import datetime
import logging
import sys
import fnmatch

# Configure logging
logging.basicConfig(filename='/opt/splunk/var/log/splunk/discord_alert_action.log',
    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('discord_alert_action')
logger.setLevel(logging.INFO)

debug_logger = logging.getLogger('discord_alert_action_debug')
# debug_logger.setLevel(logging.WARNING)  # Disable debug logging by default
debug_logger.setLevel(logging.DEBUG)  # Enable debug logging
debug_handler = logging.FileHandler('/opt/splunk/var/log/splunk/discord_alert_action_debug.log')
debug_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
debug_logger.addHandler(debug_handler)

logger.info('Starting discord_alert_action.py')

# Trims message to fit Discord's documentation
def trim_message(message):
    max_length = 2000
    suffix = "\n...View the alert for more information"
    
    if len(message) <= max_length:
        return message
    else:
        debug_logger.debug(f"Message length is too long. Current length: {len(message)}")
        trimmed_message = message[:max_length-len(suffix)] + suffix
        debug_logger.debug(f"New length: {len(trimmed_message)}")
        return trimmed_message

def send_discord_message(webhook_url, json_data, field_names):
    webhook_url = webhook_url
    search_name = json_data['search_name']
    results_link = json_data['results_link']
    results = json_data['result']
    server_host = json_data['server_host']

    # Logging parameters
    debug_logger.debug(f'Webhook URL: {webhook_url}')
    debug_logger.debug(f'Search Name: {search_name}')
    debug_logger.debug(f'Results Link: {results_link}')
    debug_logger.debug(f'Server Host: {server_host}')
    debug_logger.debug(f'Available Fields: {results}')
    debug_logger.debug(f'Selected Fields: {field_names}')
    
    # Format the message with timestamp
    message = f'# [{search_name}]({results_link}) from `{server_host}`\n'
    message += f'**Alert Fields**\n'

    # Format and append the result fields
    for key, value in results.items():
        for field_name in field_names:
            debug_logger.debug(f"Key: {key}, Field Name: {field_name}")
            if fnmatch.fnmatch(key, field_name):
                message += f'- **{key}:** {value}\n'
                break
    message += f'---\n'

    message = trim_message(message)

    # Prepare the payload for the Discord webhook
    payload = {'content': message}

    debug_logger.debug(f'Payload to Discord: {payload}')

    try:
        # Send the POST request to the Discord webhook
        response = requests.post(
            webhook_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'}
        )

        # Check the response status
        if response.status_code == 204:
            logger.info('Message sent successfully.')
        else:
            logger.error(f'Failed to send message. Status code: {response.status_code}')
    except requests.RequestException as e:
        logger.exception('An error occurred while sending the Discord message.', exc_info=e)


if __name__ == '__main__':
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--execute':
            logger.info('Running as alert action')
            payload_str = sys.stdin.read()
            debug_logger.debug(f'Payload: {payload_str}')
            json_data = json.loads(payload_str)
            webhook_url = json_data['configuration']['webhook_url']
            field_names = json_data['configuration']['field_names']
            try:
                field_names = field_names.split(",")
            except AttributeError as e:
                logger.error(f"Error splitting field names: {e}")
            debug_logger.debug(f'Field Names: {field_names}')
            debug_logger.debug(f'Alert action webhook URL: {webhook_url}')
            debug_logger.debug(f'Chosen Fields: {field_names}')
            send_discord_message(webhook_url, json_data, field_names)
    except Exception as e:
        logger.error(f"An error occurred: {e}")