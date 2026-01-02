# Webhook Integration Template

This template creates an integration that receives data via webhooks from external services.

## Features

- Webhook endpoint registration
- Automatic sensor creation from JSON data
- Connectivity monitoring
- Event firing for automation triggers

## Usage

1. Copy this folder to `custom_components/my_webhook/`
2. Rename the domain in all files
3. Customize sensors based on your data structure
4. Configure via Home Assistant UI

## Webhook URL

After configuration, send POST requests to:

```
POST http://your-home-assistant:8123/api/webhook/{webhook_id}
Content-Type: application/json

{
  "value": 42,
  "status": "ok",
  "count": 100
}
```

## Automation Trigger

Listen for webhook events:

```yaml
automation:
  - alias: "Handle Webhook Data"
    trigger:
      - platform: event
        event_type: my_webhook_received
    action:
      - service: notify.notify
        data:
          message: "Received: {{ trigger.event.data.data.value }}"
```

## Customization

Edit `const.py` to define which keys from the JSON payload become sensors:

```python
DEFAULT_SENSORS = ["temperature", "humidity", "battery"]
```

## Security

- Each webhook gets a unique random ID
- Consider using HTTPS in production
- Validate incoming data in your implementation
