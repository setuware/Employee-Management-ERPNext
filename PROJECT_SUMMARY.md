# Project Summary

## Employee Management & Leave Tracking Module

Built for Bits and Volts Pvt. Ltd. using ERPNext (Frappe Framework + Python)

## Project Structure

```
Assingment/
├── lms/
│   ├── doctype/
│   │   ├── employee/
│   │   │   ├── employee.json
│   │   │   ├── employee.py
│   │   │   └── employee.js
│   │   └── leave_request/
│   │       ├── leave_request.json
│   │       ├── leave_request.py
│   │       └── leave_request.js
│   ├── api/
│   │   ├── employee.py
│   │   └── leave_request.py
│   ├── utils/
│   │   ├── employee.py
│   │   └── leave_request.py
│   ├── www/
│   │   ├── employee_list.html
│   │   ├── employee_list.js
│   │   └── employee_list.py
│   ├── public/
│   │   ├── css/
│   │   │   └── lms.css
│   │   └── js/
│   │       ├── employee.js
│   │       └── leave_request.js
│   ├── boot/
│   │   └── boot_session.py
│   └── config/
│       ├── desktop.py
│       └── docs.py
├── hooks.py
├── setup.py
├── requirements.txt
├── README.md
├── INSTALLATION.md
├── API_DOCUMENTATION.md
├── TESTING.md
└── LICENSE
```

## Features Implemented

### 1. Employee Management
-  Employee DocType with fields: Employee ID, Profile Picture, Full Name, Email, Department, Joining Date
-  Employee list with edit option
-  Add/Edit employee form with validation
-  Search functionality
-  Pagination support

### 2. Leave Requests
-  Leave Request DocType with fields: ID, Employee, Leave Type, From Date, To Date, Status
-  Leave listing screen
-  Status handling (Pending, Approved, Rejected, Canceled)
-  Filter by status
-  Search functionality
-  Pagination support

### 3. Summary Report
-  Display total, approved, pending, canceled leaves
-  Download CSV option
-  Real-time statistics

### 4. Backend Features
-  Proper DocTypes using Frappe
-  CRUD operations with pagination
-  Search functionality
-  CSV export
-  Role-based permissions
-  Validation & error handling

## DocTypes

### Employee
- **Fields:**
  - Employee ID (Data, Unique, Required)
  - Profile Picture (Attach Image)
  - Full Name (Data, Required)
  - Email (Data, Required, Email validation)
  - Department (Link to Department, Required)
  - Joining Date (Date, Required)

### Leave Request
- **Fields:**
  - Leave ID (Data, Unique, Auto-generated)
  - Employee (Link to Employee, Required)
  - Leave Type (Select: Casual/Sick/Annual/Emergency, Required)
  - From Date (Date, Required)
  - To Date (Date, Required)
  - Status (Select: Pending/Approved/Rejected/Canceled, Default: Pending)

## API Endpoints

### Employee APIs
- `GET /api/method/lms.api.employee.get_employees` - List with pagination & search
- `POST /api/method/lms.api.employee.create_employee` - Create employee
- `PUT /api/method/lms.api.employee.update_employee` - Update employee
- `GET /api/method/lms.api.employee.get_employee` - Get single employee
- `DELETE /api/method/lms.api.employee.delete_employee` - Delete employee

### Leave Request APIs
- `GET /api/method/lms.api.leave_request.get_leave_requests` - List with pagination, search & filter
- `POST /api/method/lms.api.leave_request.create_leave_request` - Create leave request
- `PUT /api/method/lms.api.leave_request.update_leave_request` - Update leave request
- `GET /api/method/lms.api.leave_request.get_leave_request` - Get single leave request
- `GET /api/method/lms.api.leave_request.get_summary` - Get summary statistics
- `GET /api/method/lms.api.leave_request.export_csv` - Export CSV

## Permissions

### System Manager
- Full access to all features
- Can create/edit/delete employees
- Can approve/reject leave requests

### HR Manager
- Can create/edit employees
- Can approve/reject leave requests
- Can view all data

### Employee
- Can view own employee record
- Can create own leave requests
- Can cancel own pending leave requests

## Validations

### Employee Validations
- Employee ID must be unique
- Email format validation
- Date format validation
- Required fields validation

### Leave Request Validations
- To Date cannot be before From Date
- Employee must exist
- Status must be valid
- Required fields validation

## UI Features

- Modern, responsive design
- Tab-based navigation
- Search and filter functionality
- Pagination controls
- Status badges with color coding
- Form validation with error messages
- Profile picture upload
- CSV export functionality

## Technology Stack

- **Backend:** Python, Frappe Framework
- **Frontend:** JavaScript, HTML, CSS
- **Database:** MariaDB (via Frappe)
- **Framework:** ERPNext

## Installation

See `INSTALLATION.md` for detailed setup instructions.

## Testing

See `TESTING.md` for comprehensive test scenarios.

## Documentation

- `README.md` - Overview and quick start
- `INSTALLATION.md` - Installation guide
- `API_DOCUMENTATION.md` - Complete API reference
- `TESTING.md` - Testing guide

## Notes

- No comments included in code as per requirements
- All code follows Frappe/ERPNext conventions
- Proper error handling implemented
- Role-based access control configured
- Responsive UI design
