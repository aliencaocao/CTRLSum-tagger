## Tagger
### `POST API_ENDPOINT/tagger`

Generate tags from text using CTRLSum

#### Input

```json
{
    "source": "text to tag"
}
```

#### Output

```json
{
    "success": "true",
    "tags": "tags separated by ;, tags are strictly single-word (may include hyphens)"
}
```

If error occurred, the `success` field will be `false` and the `tags` field will be replaced by `error` which contains the detailed error message.
```json
{
    "success": "false",
    "error": "error message"
}
```

### `GET API_ENDPOINT/health`

Obtain the health status of the service

### Input

```
N/A
```

### Output

healthy:
```json
{
    "health": "true"
}
```

unhealthy:
```json
{
    "health": "false"
}
```
