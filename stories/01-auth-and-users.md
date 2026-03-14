# Story 1: Authentication & User Management

## Description
As a contractor, I need to register and log in so that my photos and projects are associated with my account.

## Acceptance Criteria
- POST /auth/register creates a new user with email, password, full_name, role
- POST /auth/login returns a JWT token
- GET /auth/me returns current user info from token
- Passwords are hashed with bcrypt
- JWT tokens expire after 24 hours
- Roles: contractor, admin, reviewer

## Technical Notes
- SQLAlchemy 1.4 style (session.query)
- python-jose for JWT, passlib for password hashing
- JWT_SECRET from .env
