# API Documentation

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## Authentication

All API endpoints except authentication routes require a Bearer token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Authentication Endpoints

### Initiate Google Login

Redirects user to Google OAuth consent screen.

```http
GET /auth/google/login
```

**Response**: Redirect to Google OAuth

---

### Google OAuth Callback

Handles OAuth callback and issues JWT token.

```http
GET /auth/google/callback
```

**Query Parameters**:
- `code`: OAuth authorization code (provided by Google)
- `state`: OAuth state parameter (provided by Google)

**Response**: Redirect to frontend with token

```
https://yourdomain.com/auth/callback?token=<jwt_token>
```

---

### Logout

Logout endpoint (stateless, for API completeness).

```http
POST /auth/logout
```

**Headers**:
```
Authorization: Bearer <token>
```

**Response**:
```json
{
  "message": "Logged out successfully"
}
```

---

## Recording Endpoints

### Create Recording

Create a new recording session.

```http
POST /recordings/
```

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Response**: `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "active",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "audio_file_path": null,
  "transcription_text": null,
  "notes": null
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

---

### List Recordings

Get all recordings for the authenticated user.

```http
GET /recordings/
```

**Headers**:
```
Authorization: Bearer <token>
```

**Response**: `200 OK`
```json
{
  "recordings": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "ended",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:45:00",
      "audio_file_path": "/path/to/audio.webm",
      "transcription_text": "Patient presents with...",
      "notes": "Follow-up needed"
    }
  ]
}
```

---

### Get Recording

Get details of a specific recording.

```http
GET /recordings/{recording_id}
```

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "ended",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:45:00",
  "audio_file_path": "/path/to/audio.webm",
  "transcription_text": "Patient presents with...",
  "notes": "Follow-up needed"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: User doesn't own this recording
- `404 Not Found`: Recording doesn't exist

---

### Upload Audio Chunk

Upload an audio chunk for a recording.

```http
POST /recordings/{recording_id}/chunks
```

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Form Data**:
- `chunk_index` (integer, required): Sequential index of the chunk (0, 1, 2, ...)
- `audio_chunk` (file, required): Audio file chunk (webm format)
- `duration_seconds` (float, optional): Duration of the chunk in seconds

**Example using curl**:
```bash
curl -X POST \
  http://localhost:8000/recordings/550e8400-e29b-41d4-a716-446655440000/chunks \
  -H "Authorization: Bearer <token>" \
  -F "chunk_index=0" \
  -F "audio_chunk=@chunk_0.webm" \
  -F "duration_seconds=10.5"
```

**Response**: `201 Created`
```json
{
  "message": "Chunk uploaded successfully",
  "chunk_id": "660f9511-f39c-52e5-b827-557766551111",
  "chunk_index": 0
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: User doesn't own this recording
- `404 Not Found`: Recording doesn't exist

---

### Pause Recording

Mark a recording as paused.

```http
PATCH /recordings/{recording_id}/pause
```

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "paused",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:35:00",
  "audio_file_path": null,
  "transcription_text": null,
  "notes": null
}
```

---

### Finish Recording

Mark recording as ended, assemble chunks, and trigger transcription.

```http
POST /recordings/{recording_id}/finish
```

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "ended",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:45:00",
  "audio_file_path": "/app/audio_storage/550e8400/recording.webm",
  "transcription_text": "Patient presents with acute abdominal pain...",
  "notes": null
}
```

**Notes**:
- This endpoint assembles all uploaded chunks into a single audio file
- Triggers LLM transcription (may take several seconds/minutes)
- Transcription appears in the `transcription_text` field

---

### Add/Update Notes

Add or update notes for a recording.

```http
PATCH /recordings/{recording_id}/notes
```

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Request Body**:
```json
{
  "notes": "Patient requires follow-up in 2 weeks. Blood pressure elevated."
}
```

**Response**: `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "ended",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:50:00",
  "audio_file_path": "/app/audio_storage/550e8400/recording.webm",
  "transcription_text": "Patient presents with...",
  "notes": "Patient requires follow-up in 2 weeks. Blood pressure elevated."
}
```

---

### Delete Recording

Delete a recording and all associated files.

```http
DELETE /recordings/{recording_id}
```

**Headers**:
```
Authorization: Bearer <token>
```

**Path Parameters**:
- `recording_id` (string, required): UUID of the recording

**Response**: `204 No Content`

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `403 Forbidden`: User doesn't own this recording
- `404 Not Found`: Recording doesn't exist

---

## Health Check Endpoints

### Root

Basic API information.

```http
GET /
```

**Response**: `200 OK`
```json
{
  "name": "Audio Transcription Service",
  "version": "1.0.0",
  "status": "operational"
}
```

---

### Health Check

Service health status.

```http
GET /health
```

**Response**: `200 OK`
```json
{
  "status": "healthy"
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful request with no response body
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

*Note: Rate limiting should be implemented in production*

Recommended limits:
- Authentication endpoints: 5 requests per minute
- Upload endpoints: 100 requests per minute
- Other endpoints: 60 requests per minute

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints
- See request/response schemas
- Try out API calls directly in the browser
- Generate code examples

---

## Example Workflows

### Complete Recording Flow

```javascript
// 1. Create a recording session
const recording = await fetch('http://localhost:8000/recordings/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}).then(r => r.json());

// 2. Upload chunks as they're recorded
for (let i = 0; i < chunks.length; i++) {
  const formData = new FormData();
  formData.append('chunk_index', i);
  formData.append('audio_chunk', chunks[i]);

  await fetch(`http://localhost:8000/recordings/${recording.id}/chunks`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
}

// 3. Finish the recording
const finished = await fetch(
  `http://localhost:8000/recordings/${recording.id}/finish`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
).then(r => r.json());

console.log('Transcription:', finished.transcription_text);

// 4. Add notes
await fetch(`http://localhost:8000/recordings/${recording.id}/notes`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    notes: 'Important follow-up needed'
  })
});
```

---

## WebSocket Support

*Future Enhancement*

Real-time transcription streaming via WebSocket will be added in a future version:

```
WS /recordings/{recording_id}/stream
```

---

## Versioning

Current API version: **v1**

Future versions will be accessible via:
```
http://api.yourdomain.com/v2/...
```

---

For more information, see the [Setup Guide](SETUP_GUIDE.md) and [README](README.md).
