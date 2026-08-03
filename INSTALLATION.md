# Installation Guide

## Prerequisites

- ERPNext installed and running
- Bench CLI installed
- Python 3.6+ 
- Node.js 14+

## Installation Steps

### 1. Install ERPNext (if not already installed)

Follow the official ERPNext installation guide:
https://github.com/frappe/frappe_docker

Or use Bench:
```bash
bench init frappe-bench
cd frappe-bench
bench get-app erpnext
bench new-site your-site.local
bench install-app erpnext
```

### 2. Install LMS App

> Note: The app folder inside `apps/` **must** be named `lms` (the app name in `hooks.py`). If your repo is not named `lms`, clone it manually with the correct folder name — `bench get-app` cannot install an app whose repo name differs from the app name.

```bash
cd frappe-bench
git clone https://github.com/setuware/Employee-Management-ERPNext.git apps/lms
bench --site your-site.local install-app lms
bench --site your-site.local migrate
```

If you use a private repository, authenticate git first (personal access token or SSH key).

### 3. Create Site (if needed)

```bash
bench new-site your-site.local
bench --site your-site.local install-app lms
bench --site your-site.local migrate
```

### 4. Access the Application

1. Start the bench:
```bash
bench start
```

2. Access ERPNext:
   - URL: http://localhost:8000
   - Login with administrator credentials

3. Navigate to the application pages:
   - `/` - Company website (Home)
   - `/services` - Services
   - `/process` - How we work
   - `/contact` - Contact
   - `/employee-portal` - Employee self-service (check-in/out, attendance history, tasks & timers)
   - `/attendance-log` - Admin attendance log
   - `/tasks` - Admin task management
   - `/employee-list` - Employee & leave management dashboard

## Setup Department

Before adding employees, create departments:

1. Go to: HR > Department
2. Create departments like: HR, Accounting, IT, Sales, etc.

## Test Credentials

Default ERPNext installation creates:
- Username: `administrator`
- Password: (set during site creation)

## Creating Test Users

### System Manager
- Username: `administrator`
- Role: System Manager
- Full access to all features

### HR Manager
1. Go to: Users and Permissions > User
2. Create new user
3. Assign role: HR Manager
4. Can manage employees and approve/reject leave requests

### Employee
1. Go to: Users and Permissions > User  
2. Create new user
3. Assign role: Employee
4. Can view own data and create leave requests

> **Important for the portal:** open the employee's record (LMS Employee) and set the **User** field to their login — the portal (`/employee-portal`) uses this link for check-in/check-out and shows only that employee's data.

## API Testing

Use Postman or curl to test APIs:

### Get Employees
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.employee.get_employees?page=1&page_size=10"
```

### Create Employee
```bash
curl -X POST "http://localhost:8000/api/method/lms.api.employee.create_employee" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "employee_id": "EMP001",
      "full_name": "John Doe",
      "email": "john@example.com",
      "department": "HR",
      "joining_date": "2024-01-01"
    }
  }'
```

### Get Leave Requests
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.leave_request.get_leave_requests?page=1&page_size=10"
```

### Get Summary
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.leave_request.get_summary"
```

## Troubleshooting

### App not showing in desktop
```bash
bench clear-cache
bench restart
```

### Permission errors
- Ensure user has appropriate roles assigned
- Check DocType permissions in Employee and Leave Request

### Database errors
```bash
bench migrate
bench clear-cache
```

### Port conflicts
- Change port in site_config.json
- Or use: `bench --site your-site.local serve --port 8080`

## Development Mode

```bash
bench --site your-site.local set-config developer_mode 1
bench clear-cache
bench restart
```

## Production Deployment

1. Build assets:
```bash
bench build --app lms
```

2. Set production mode:
```bash
bench --site your-site.local set-config developer_mode 0
bench clear-cache
```

3. Use production server (gunicorn):
```bash
bench start --no-dev
```
