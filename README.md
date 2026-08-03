# Employee Management & Leave Tracking Module

Employee Management & Leave Tracking module built on ERPNext (Frappe Framework) for Bits and Volts Pvt. Ltd.

## Features

### Employee Management
- Employee CRUD operations with validation
- Employee list with search and pagination
- Add/Edit employee form
- Profile picture upload
- Department linking

### Leave Request Management
- Leave request creation and management
- Status handling (Pending, Approved, Rejected, Canceled)
- Filter by status
- Search functionality
- Pagination support

### Summary Report
- Real-time leave statistics
- Total, Approved, Pending, Canceled leaves count
- CSV export functionality

### Backend Features
- RESTful API endpoints
- Role-based permissions
- Data validation
- Error handling
- Search and pagination
- CSV export

### Attendance Tracking
- Employee check-in / check-out from the self-service portal
- Automatic work-hours calculation (based on a 10:00 AM – 5:00 PM workday)
- Auto status: Present, Late, Early Leave, Half Day
- Admin attendance log with filters and manual record entry
- Daily summary (checked-in, absent, total hours)

### Task Management
- Task assignment with priority, due date and estimated hours
- Status workflow: Not Started → In Progress → Completed / Cancelled
- Per-task timer (start / stop) with elapsed and total tracked time
- Employees time-track their own assigned tasks from the portal
- Admin task board with status updates and timer controls

### Company Website (Setuware)
- Public marketing pages: Home, Services, How We Work, Contact
- Employee & admin portals integrated into the same app

## Installation

### Prerequisites
- ERPNext installed and running
- Bench CLI installed
- Python 3.6+
- Node.js 14+

### Steps

1. **Get the app** (repo must be cloned as folder name `lms`):
```bash
cd frappe-bench
git clone https://github.com/setuware/Employee-Management-ERPNext.git apps/lms
```

2. **Install the app on your site:**
```bash
bench --site your-site.local install-app lms
bench --site your-site.local migrate
bench --site your-site.local clear-cache
```

3. **Start the server:**
```bash
bench start
```

4. **Access the application:**
   - Navigate to: `http://localhost:8000/employee-list`
   - Or use the desktop icon "Employee Management & Leave Tracking"

## Setup

1. **Create Departments:**
   - Go to: HR > Department
   - Create departments (HR, IT, Sales, etc.)

2. **Create Users:**
   - System Manager: Full access (default administrator)
   - HR Manager: Can manage employees and approve leaves
   - Employee: Can view own data and create leave requests

## Test Credentials

- **Username:** `administrator`
- **Password:** (set during ERPNext site creation)

## API Endpoints

### Employee APIs
- `GET /api/method/lms.api.employee.get_employees` - List employees (with pagination & search)
- `POST /api/method/lms.api.employee.create_employee` - Create employee
- `PUT /api/method/lms.api.employee.update_employee` - Update employee
- `GET /api/method/lms.api.employee.get_employee` - Get single employee
- `DELETE /api/method/lms.api.employee.delete_employee` - Delete employee

### Leave Request APIs
- `GET /api/method/lms.api.leave_request.get_leave_requests` - List leave requests (with pagination, search & filter)
- `POST /api/method/lms.api.leave_request.create_leave_request` - Create leave request
- `PUT /api/method/lms.api.leave_request.update_leave_request` - Update leave request
- `GET /api/method/lms.api.leave_request.get_leave_request` - Get single leave request
- `GET /api/method/lms.api.leave_request.get_summary` - Get summary statistics
- `GET /api/method/lms.api.leave_request.export_csv` - Export CSV

See `API_DOCUMENTATION.md` for detailed API documentation.

## DocTypes

### LMS Employee
- **Fields:** Employee ID, Profile Picture, Full Name, Email, Department, Joining Date
- **Validations:** Unique Employee ID, Email format, Date format

### LMS Leave Request
- **Fields:** Leave ID (auto-generated), Employee (link to LMS Employee), Leave Type, From Date, To Date, Status
- **Validations:** Date range validation, Employee existence, Status validation

## Documentation

- `README.md` - This file
- `INSTALLATION.md` - Detailed installation guide
- `API_DOCUMENTATION.md` - Complete API reference
- `TESTING.md` - Testing guide and scenarios
- `PROJECT_SUMMARY.md` - Project overview and structure

## Permissions

- **System Manager:** Full access to all features
- **HR Manager:** Can manage employees and approve/reject leave requests
- **Employee:** Can view own data and create leave requests

## Technology Stack

- **Backend:** Python, Frappe Framework
- **Frontend:** JavaScript, HTML, CSS
- **Database:** MariaDB (via Frappe)
- **Framework:** ERPNext

## Support

For issues or questions, refer to the documentation files or contact Bits and Volts Pvt. Ltd.
