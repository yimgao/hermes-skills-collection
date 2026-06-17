---
name: api-doc-generator
description: "Use when generating API documentation from code — scans FastAPI/Express/Gin routes and schemas, produces OpenAPI spec or Markdown docs."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [api, documentation, openapi, swagger, fastapi, express]
    related_skills: [project-scaffolder]
---

# API Doc Generator

> Auto-generate API documentation from your codebase. Scans route definitions and schemas, produces OpenAPI specs or structured Markdown docs.

---

## When to Use

- *"Generate API docs for my FastAPI project"*
- *"Create an OpenAPI spec from my Express routes"*
- *"Document all endpoints in this project"*
- *"What APIs does this project expose?"*

---

## Core Workflow

### Step 1: Scan Project

Identify the framework and find route files:

```bash
# Python / FastAPI
grep -rn "router\|@app\.\(get\|post\|put\|delete\|patch\)" src/ --include="*.py"

# TypeScript / Express
grep -rn "router\.\(get\|post\|put\|delete\)\|app\.\(get\|post\)" src/ --include="*.ts"

# Go / Gin
grep -rn "router\.\(GET\|POST\|PUT\|DELETE\)\|gin\.\(Default\|New\)" . --include="*.go"
```

### Step 2: Extract Endpoints

For each route, extract:
- **Method** (GET/POST/PUT/DELETE/PATCH)
- **Path** (`/api/v1/users/{id}`)
- **Parameters** (path, query, body)
- **Response schema** (return type)
- **Description** (docstring/comment)
- **Auth requirements**

### Step 3: Generate Documentation

**Markdown format:**
```markdown
# API Documentation

## Overview
Base URL: `http://localhost:8000`
Version: v1

## Endpoints

### GET /api/v1/users
- **Description:** List all users
- **Auth:** Required (Bearer token)
- **Query params:**
  | Name | Type | Required | Description |
  |------|------|----------|-------------|
  | page | int | No | Page number (default: 1) |
  | limit | int | No | Items per page (default: 20) |
- **Response:** `200` — Array of User objects

### POST /api/v1/users
- **Description:** Create a new user
- **Auth:** Required (Admin)
- **Body:**
  ```json
  {
    "name": "string (required)",
    "email": "string (required)",
    "role": "string (optional, default: 'user')"
  }
  ```
- **Response:** `201` — Created User object
```

**OpenAPI 3.0 format:** Output as `openapi.yaml`

### Step 4: Save

Save to `docs/api.md` or `docs/openapi.yaml` in the project root.

---

## Framework Support

| Framework | Detection | Pydantic Schemas |
|-----------|-----------|-----------------|
| FastAPI | ✅ Route decorators | ✅ auto |
| Express (TS/JS) | ✅ Router patterns | ⚠️ Manual |
| Gin (Go) | ✅ Router methods | ⚠️ Manual |
| Flask | ✅ Route decorators | ⚠️ Manual |
