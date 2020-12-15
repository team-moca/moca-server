# MQTT API for communication with services (WhatsApp, Telegram etc.)

All payloads must be valid JSON.

## Variables

The topics or payloads may contain variables. You can find their meaning in the table below.

|Variable|Description|Example|
|-|-|-|
|`service_type`|Type of service. This value is defined by the service.|`telegram`, `whatsapp`|





## Connect MOCA to a service

`{service_type}/configure/{connector_id}`

MOCA will send an empty payload `{}` to this topic. The service should either return:

**A) A configuration step payload:**
```json
{
    "step": "{step_id}",
    "schema": "{schema}"
}
```

|Variable|Description|Example|
|-|-|-|
|`step_id`|Unique id of the step.|`phone`, `verification_code`|
|`schema`|A JSON schema describing the next required payload.|*See full example below*|



**B) The finishing step including the user's contact:**
```json
{
    "step": "finished",
    "contact": {
        "id": "{contact_id}",
        "name": "{name}",
        "username": "{username}",
        "phone": "{phone}",
    }
}
```

|Variable|Description|Example|
|-|-|-|
|`contact_id`|The contact id how the service references the contact. Must be an integer.|`12345`|

### Example configuration flow

MOCA sends `demo/configure/42`
```json
{}
```

Service responds `demo/configure/42/response`
```json
{
    "step": "phone",
    "schema": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "phone.schema.json",
        "title": "Phone",
        "description": "A phone number to start configuration of the moca demo service",
        "type": "object",
        "properties": {
            "phone": {
            "title": "Phone number",
            "description": "Phone number in international format",
            "type": "string",
            "examples": ["+491711234567", "+442071838750"]
            }
        },
        "required": ["phone"]
    }
}
```

MOCA sends `demo/configure/42`
```json
{"phone": "+491711234567"}
```

Service responds `demo/configure/42/response`
```json
{
    "step": "finished",
    "contact": {
        "id": 192168,
        "name": "Jon Doe",
        "username": "jon.doe",
        "phone": "+491711234567"
    }
}
```

## Request data

The service should answer to these requests with the same topic, but with `/response` appended to it.

### Old API

`{service_type}/users/{connector_id}/get_chats {}`

`{service_type}/users/{connector_id}/get_contacts {}`

`{service_type}/users/{connector_id}/send_message {...}`

`{service_type}/users/{connector_id}/delete {}`

`{service_type}/users/{connector_id}/get_messages/{message_id} {}`

`{service_type}/users/{connector_id}/get_contact/{contact_id} {}`

### New proposed API

`{service_type}/{connector_id}/{uuid}/get_contacts {}`
`{service_type}/{connector_id}/{uuid}/get_contact/{contact_id} {}`

`{service_type}/{connector_id}/{uuid}/get_chats {}`
`{service_type}/{connector_id}/{uuid}/get_chat/{chat_id} {}`

`{service_type}/{connector_id}/{uuid}/get_messages/{chat_id} {}`
`{service_type}/{connector_id}/{uuid}/send_message/{chat_id} {...}`

`{service_type}/{connector_id}/{uuid}/delete_connector {}`

## Push API

Use this to push data from the service to MOCA.

`moca/via/{service_type}/{connector_id}/contacts [...]`
`moca/via/{service_type}/{connector_id}/chats [...]`
`moca/via/{service_type}/{connector_id}/messages [...]`
