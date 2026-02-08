# Authentication Documentation

This API uses OAuth2 with Password Flow and Bearer Tokens for authentication.

## 1. Sign Up
To register a new user, send a POST request to `/auth/signup`.

**Endpoint:** `POST http://127.0.0.1:8000/auth/signup`
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword",
  "full_name": "Your Name"
}
```

**Response:**
```json
{
  "email": "user@example.com",
  "full_name": "Your Name",
  "id": 1,
  "is_active": true,
  "created_at": "2024-02-08T12:00:00.000000Z"
}
```

## 2. Login (Get Access Token)
To log in and obtain an access token, send a POST request to `/auth/token`. Note that this endpoint expects form-data, not JSON, as per the OAuth2 spec.

**Endpoint:** `POST http://127.0.0.1:8000/auth/token`
**Content-Type:** `application/x-www-form-urlencoded`

**Form Data:**
*   `username`: Your email address (e.g., `user@example.com`)
*   `password`: Your password

**Example using `curl`:**
```bash
curl -X POST "http://127.0.0.1:8000/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=yourpassword"
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

## 3. accessing Protected Endpoints
To access endpoints that require authentication (like `/users/me`), include the access token in the `Authorization` header.

**Header:** `Authorization: Bearer <your_access_token>`

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example using Python (requests):**
```python
import requests

token = "YOUR_ACCESS_TOKEN"
url = "http://127.0.0.1:8000/users/me"
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(url, headers=headers)
print(response.json())
```
