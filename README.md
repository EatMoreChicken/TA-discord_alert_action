# Discord Alert Action for Splunk

## Overview
This app enables you to send alerts from your Splunk instance to Discord channels using Discord webhooks. It provides an easy way to configure the alert action with the fields you want to send, allowing you to keep track of your alerts in Discord.

## How it works
When the app is installed and configured in your Splunk instance, you can create an alert action that sends specified fields to a Discord channel using a webhook URL. The alert action takes the result of a search and formats it as a message in Markdown format, which is then sent to the specified Discord channel (The Markdown is fairly basic and some elements, like headings, are pending Discord updates).

## Prerequisites
To use this app, you need a Discord webhook URL. To create a webhook URL for your Discord channel, follow the instructions provided in the [Discord documentation](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

## Installation and Configuration
1. Download the app package and install it in your Splunk instance.
2. Follow Discord's documentation to generate a webhook for a channel ([Discord documentation](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)).
3. Create or edit an alert to add the Discord Alert action. Be sure to populate the `Discord Webhook URL` and `Fields to Send` (Note: _Supports wildcards and should be comma-separated_) with fields you would like sent to Discord from your search.

> Note: The maximum message length currently supported is "2000" characters.
> Note: Please consider using the `For each result` trigger option for your alert.

## To-Do
- [ ] Update script to use Splunk's built-in logging.
- [ ] Fine tune max message length. It should be higher than 2000 characters.
- [ ] Look into getting trigger option `Once` to include all results instead of just the first.

## Support
This is an open-source project, no support provided, public repository available. Please feel free to contribute to this project by creating pull requests, filing bug reports, or providing feedback. Thank you!
- Public Repo: https://github.com/EatMoreChicken/TA-discord_alert_action
