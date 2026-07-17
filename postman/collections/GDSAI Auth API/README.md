# GDSAI Auth API

A JWT-based authentication API for the GDSAI web platform, built with Django REST Framework and `djangorestframework-simplejwt`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (recommended), or a local PostgreSQL/SQLite setup
- Postman (with the **GDSAI Local** environment selected)

### Running the Server

**With Docker:**
```bash
docker-compose up --build
```

**Without Docker:**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at: `http://localhost:8000`

---

## 🌍 Environment Setup

Select the **GDSAI Local** environment in Postman before running any requests. It includes:

| Variable | Default Value | Description |
|---|---|---|
| `base_url` | `http://localhost:8000` | API base URL |
| `test_email` | `testuser@example.com` | Email used in test requests |
| `test_password` | `TestPass123!` | Password used in test requests |
| `access_token` | *(auto-set)* | JWT access token — populated automatically |
| `refresh_token` | *(auto-set)* | JWT refresh token — populated automatically |

> **Tip:** Run **Register User** or **Login** first — the test scripts will automatically populate `access_token` and `refresh_token` for subsequent requests.

---

## 📋 API Reference

**Base URL:** `{{base_url}}/api/v1/`

All endpoints are prefixed with `/api/v1/auth/`.

---

### 1. Register User

**`POST /api/v1/auth/register/`**

Creates a new user account and returns the user profile along with JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "YourPassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Success Response — `201 Created`:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-07-14T20:00:00Z"
  },
  "tokens": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
  }
}
```

**Error Responses:**
| Status | Reason |
|---|---|
| `400 Bad Request` | Missing required fields or email already registered |

---

### 2. Login

**`POST /api/v1/auth/login/`**

Authenticates an existing user and returns JWT tokens.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "YourPassword123!"
}
```

> **Note:** The field is named `username` but expects an **email address**.

**Success Response — `200 OK`:**
```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>"
}
```

**Error Responses:**
| Status | Reason |
|---|---|
| `401 Unauthorized` | Invalid email or password |
| `400 Bad Request` | Missing required fields |

---

### 3. Refresh Token

**`POST /api/v1/auth/refresh/`**

Issues a new access token using a valid refresh token. Use this when the access token has expired.

**Request Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```

**Success Response — `200 OK`:**
```json
{
  "access": "<new_jwt_access_token>"
}
```

**Error Responses:**
| Status | Reason |
|---|---|
| `401 Unauthorized` | Refresh token is expired, invalid, or blacklisted |

---

### 4. Logout

**`POST /api/v1/auth/logout/`**

Logs out the user by blacklisting the refresh token. Requires a valid Bearer access token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "<jwt_refresh_token>"
}
```

**Success Response — `205 Reset Content`:**
```json
{
  "detail": "Successfully logged out."
}
```

**Error Responses:**
| Status | Reason |
|---|---|
| `401 Unauthorized` | Missing or invalid access token |
| `400 Bad Request` | Refresh token already blacklisted or invalid |

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** via the `Authorization: Bearer <token>` header.

| Token | Lifetime | Purpose |
|---|---|---|
| Access Token | 60 minutes | Authenticate protected requests |
| Refresh Token | 1 day | Obtain a new access token after expiry |

**Typical flow:**
1. **Register** or **Login** → receive `access` + `refresh` tokens
2. Use `access` token in the `Authorization` header for protected endpoints
3. When the access token expires, call **Refresh Token** to get a new one
4. Call **Logout** to invalidate the refresh token when done

---

## ✅ Automated Tests

Each request includes automated Postman test scripts that run after every response:

| Request | Tests |
|---|---|
| Register User | Status 201 · User object fields · Tokens returned · Email matches · Response < 2s |
| Login | Status 200 · Access + refresh fields · Non-empty access token · Response < 2s |
| Refresh Token | Status 200 · Access field present · Non-empty access token · Response < 2s |
| Logout | Status 205 · Success message · Response < 2s |

### Running All Tests

1. Open the **GDSAI Auth API** collection in Postman
2. Select the **GDSAI Local** environment
3. Click **Run collection** (▶ button)
4. All 4 requests will run in order with results shown in the Collection Runner

---

## 🗂️ Project Structure

```
postman/
├── collections/
│   └── GDSAI Auth API/
│       ├── README.md               ← This file
│       └── Auth/
│           ├── Register User.request.yaml
│           ├── Login.request.yaml
│           ├── Refresh Token.request.yaml
│           └── Logout.request.yaml
└── environments/
    └── GDSAI Local.environment.yaml
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Framework | Django 6.0.6 + Django REST Framework 3.15.2 |
| Auth | djangorestframework-simplejwt 5.3.1 |
| Database | PostgreSQL (Docker) / SQLite (local dev) |
| Containerization | Docker + Docker Compose |
