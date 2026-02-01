# auth-jwt

A small FastAPI project that implements JWT-based authentication (register, login, token issuance, and a protected `me` endpoint) backed by MongoDB.

Date: 2026-02-01

## Quick summary

- Purpose: Provide a minimal JWT authentication service for FastAPI applications.
- Main features: user registration with password strength validation, password hashing (argon2), JWT access & refresh tokens, token decoding/validation, a dependency to get the current user from the `Authorization: Bearer <token>` header, and MongoDB user storage.

## Project layout (important files)

- `main.py` — FastAPI app entrypoint, mounts the auth router and manages MongoDB connection lifecycle.
- `src/auth/routes/auth.py` — Auth router exposing endpoints: `/auth/register`, `/auth/login`, `/auth/me`.
- `src/auth/models/user.py` — Pydantic models for user creation, login and responses; password strength checks live here.
- `src/auth/services/user_service.py` — User CRUD and auth logic: create user, authenticate user, create tokens, store refresh tokens.
- `src/auth/security.py` — Password hashing (PassLib Argon2), JWT creation and decoding helpers.
- `src/auth/dependecies.py` — `get_current_user` dependency that validates the access token and retrieves the user from DB.
- `src/data/database.py` — MongoDB connection helpers (connect/close) using an async client.
- `src/utils/object_id.py` — Helper to validate MongoDB ObjectId strings.

## Prerequisites

- Python 3.10+ recommended
- A running MongoDB instance (local or cloud)
- Recommended packages (example):

```
fastapi
uvicorn
python-dotenv
pymongo
motor
python-jose
passlib[argon2]
python-bson
```

Note: The project imports an async Mongo client. If using Motor, ensure `motor` is installed; if you prefer `pymongo` ensure the async client class used in the code is compatible with your driver. Adjust dependencies as necessary.

## Environment variables

Create a `.env` file in the project root (the project uses `python-dotenv`):

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=auth_db
JWT_SECRET_KEY=replace_with_a_strong_secret
```

- `MONGO_URI` — MongoDB connection URI (use `mongodb+srv://...` for Atlas with DNS support)
- `MONGO_DB_NAME` — database name for the users collection
- `JWT_SECRET_KEY` — secret used to sign JWT tokens; keep this safe and do not commit it

Optional settings (currently set in code):
- `ACCESS_TOKEN_EXPIRE_MINUTES` — default: 15
- `REFRESH_TOKEN_EXPIRE_DAYS` — default: 7

## Installation

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Install dependencies (example):

```powershell
pip install fastapi uvicorn python-dotenv motor python-jose passlib[argon2] pymongo
```

Or pin them in `requirements.txt` and run `pip install -r requirements.txt`.

## Running the app

Run the app with Uvicorn from the project root (the project `main.py` runs uvicorn when executed directly on port 5000):

```powershell
uvicorn main:app --reload --port 5000
```

The app exposes endpoints on `http://127.0.0.1:5000` (or `localhost:5000`).

## API endpoints and examples

1) Register
- POST `/auth/register`
- Request JSON body: `{ "email": "you@example.com", "password": "StrongP@ssw0rd" }`
- Response: `{ "user_id": "<id>", "access_token": "<jwt>", "refresh_token": "<jwt>" }`

Example using `curl`:

```bash
curl -X POST "http://localhost:5000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyS3cret@1"}'
```

2) Login
- POST `/auth/login`
- Request JSON body: `{ "email": "you@example.com", "password": "yourpassword" }`
- Response: same shape as register: `user_id`, `access_token`, `refresh_token`.

Example:

```bash
curl -X POST "http://localhost:5000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "MyS3cret@1"}'
```

3) Current user (protected)
- GET `/auth/me`
- Requires header: `Authorization: Bearer <access_token>`
- Response: `{ "id": "<id>", "email": "you@example.com", "created_at": "..." }`

Example:

```bash
curl -X GET "http://localhost:5000/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

## Token behavior

- Access tokens are short lived (configured by `ACCESS_TOKEN_EXPIRE_MINUTES` in the code; default 15 minutes).
- Refresh tokens are longer lived (default 7 days) and are stored in the user's `refresh_tokens` array in the DB on create/login.
- The code distinguishes token types via the `type` claim (`access` vs `refresh`).

## Passwords and security

- Passwords are validated for strength in `UserCreate` model and hashed using Argon2 (via PassLib) before storing.
- JWT tokens are signed with `JWT_SECRET_KEY` and the `HS256` algorithm.
- The `get_current_user` dependency decodes and validates the token, checks `type == 'access'`, and fetches the user from the DB.

Security notes / suggestions:
- Use a strong `JWT_SECRET_KEY` (e.g., 32+ random bytes) and do not commit it.
- Consider storing refresh tokens with additional metadata (creation IP, user agent) and provide a revocation/logout endpoint.
- Consider rotating refresh tokens and maintain a blacklist for revoked access tokens if necessary.

## Troubleshooting

- If the app fails to connect to MongoDB, check `MONGO_URI` and network/Atlas firewall rules.
- If you see import errors about `AsyncMongoClient`, confirm you have installed and are using an async-compatible Mongo driver (e.g., `motor`) or change the import to your preferred client.

## Next steps / Improvements

- Add endpoints for refresh token exchange and logout (invalidate refresh tokens).
- Add unit and integration tests for auth flows.
- Add CORS configuration, rate limiting, and logging middleware for production readiness.

## License

