# API Documentation

Base URL: `http://your-site/api/method/`

All APIs require authentication. Include session cookie or API key in requests.

## Employee APIs

### Get Employees
**Endpoint:** `lms.api.employee.get_employees`

**Method:** GET

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 10)
- `search_term` (string, optional): Search in employee_id, full_name, email, department

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "EMP001",
      "employee_id": "EMP001",
      "profile_picture": "/files/image.jpg",
      "full_name": "John Doe",
      "email": "john@example.com",
      "department": "HR",
      "joining_date": "2024-01-01"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### Create Employee
**Endpoint:** `lms.api.employee.create_employee`

**Method:** POST

**Body:**
```json
{
  "data": {
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": "HR",
    "joining_date": "2024-01-01",
    "profile_picture": "/files/image.jpg"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Employee created successfully",
  "data": { ... }
}
```

### Update Employee
**Endpoint:** `lms.api.employee.update_employee`

**Method:** PUT

**Parameters:**
- `name` (string, required): Employee document name

**Body:**
```json
{
  "data": {
    "full_name": "John Doe Updated",
    "email": "john.updated@example.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Employee updated successfully",
  "data": { ... }
}
```

### Get Employee
**Endpoint:** `lms.api.employee.get_employee`

**Method:** GET

**Parameters:**
- `name` (string, required): Employee document name

**Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

### Delete Employee
**Endpoint:** `lms.api.employee.delete_employee`

**Method:** DELETE

**Parameters:**
- `name` (string, required): Employee document name

**Response:**
```json
{
  "success": true,
  "message": "Employee deleted successfully"
}
```

## Leave Request APIs

### Get Leave Requests
**Endpoint:** `lms.api.leave_request.get_leave_requests`

**Method:** GET

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 10)
- `search_term` (string, optional): Search in leave_id, employee, leave_type
- `status` (string, optional): Filter by status (Pending, Approved, Rejected, Canceled)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "LR20240101120000",
      "leave_id": "LR20240101120000",
      "employee": "EMP001",
      "employee_name": "John Doe",
      "employee_profile": "/files/image.jpg",
      "employee_email": "john@example.com",
      "leave_type": "Casual",
      "from_date": "2024-01-15",
      "to_date": "2024-01-17",
      "status": "Pending"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

### Create Leave Request
**Endpoint:** `lms.api.leave_request.create_leave_request`

**Method:** POST

**Body:**
```json
{
  "data": {
    "employee": "EMP001",
    "leave_type": "Casual",
    "from_date": "2024-01-15",
    "to_date": "2024-01-17",
    "status": "Pending"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Leave request created successfully",
  "data": { ... }
}
```

### Update Leave Request
**Endpoint:** `lms.api.leave_request.update_leave_request`

**Method:** PUT

**Parameters:**
- `name` (string, required): Leave Request document name

**Body:**
```json
{
  "data": {
    "status": "Approved"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Leave request updated successfully",
  "data": { ... }
}
```

### Get Leave Request
**Endpoint:** `lms.api.leave_request.get_leave_request`

**Method:** GET

**Parameters:**
- `name` (string, required): Leave Request document name

**Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

### Get Summary
**Endpoint:** `lms.api.leave_request.get_summary`

**Method:** GET

**Response:**
```json
{
  "success": true,
  "data": {
    "total_leaves": 100,
    "approved_leaves": 60,
    "pending_leaves": 25,
    "canceled_leaves": 10,
    "rejected_leaves": 5
  }
}
```

### Export CSV
**Endpoint:** `lms.api.leave_request.export_csv`

**Method:** GET

**Response:**
```json
{
  "success": true,
  "message": "CSV exported successfully",
  "file_url": "/private/files/leave_summary.csv",
  "file_name": "leave_summary.csv"
}
```

## Error Responses

All APIs return error responses in this format:

```json
{
  "success": false,
  "message": "Error message description"
}
```

## Authentication

### Using Session Cookie
Include the session cookie from ERPNext login in your requests.

### Using API Key
1. Generate API key in ERPNext: User > API Keys
2. Include in header: `Authorization: token api_key:api_secret`

## Rate Limiting

Default rate limit: 100 requests per minute per user.

## Status Codes

- 200: Success
- 400: Bad Request (validation error)
- 401: Unauthorized
- 403: Forbidden (permission denied)
- 404: Not Found
- 500: Internal Server Error
