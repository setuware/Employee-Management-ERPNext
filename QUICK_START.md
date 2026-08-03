# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install App
```bash
cd frappe-bench
git clone https://github.com/setuware/Employee-Management-ERPNext.git apps/lms
bench --site your-site.local install-app lms
bench --site your-site.local migrate
```

### Step 2: Start Server
```bash
bench start
```

### Step 3: Access Application
Open browser: `http://localhost:8000/employee-list`

## First Steps

### 1. Create Department
- Go to: HR > Department
- Create: HR, IT, Sales, Accounting

### 2. Add Employee
- Click "+ Add Employee"
- Fill form:
  - Employee ID: EMP001
  - Full Name: John Doe
  - Email: john@example.com
  - Department: HR
  - Joining Date: 2024-01-01
- Click "Save"

### 3. Create Leave Request
- Switch to "Leave Requests" tab
- Use API or form to create:
  - Employee: EMP001
  - Leave Type: Casual
  - From Date: 2024-01-15
  - To Date: 2024-01-17
  - Status: Pending

### 4. View Summary
- Switch to "Summary Report" tab
- View statistics
- Click "Download CSV" to export

## Test API

### Get Employees
```bash
curl "http://localhost:8000/api/method/lms.api.employee.get_employees?page=1&page_size=10"
```

### Create Employee
```bash
curl -X POST "http://localhost:8000/api/method/lms.api.employee.create_employee" \
  -H "Content-Type: application/json" \
  -d '{"data": {"employee_id": "EMP002", "full_name": "Jane Smith", "email": "jane@example.com", "department": "IT", "joining_date": "2024-01-15"}}'
```

### Get Summary
```bash
curl "http://localhost:8000/api/method/lms.api.leave_request.get_summary"
```

## Troubleshooting

**App not showing:**
```bash
bench clear-cache
bench restart
```

**Permission errors:**
- Ensure user has System Manager or HR Manager role

**Database errors:**
```bash
bench migrate
```

## Next Steps

- Read `INSTALLATION.md` for detailed setup
- Read `API_DOCUMENTATION.md` for API reference
- Read `TESTING.md` for test scenarios
