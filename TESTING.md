# Testing Guide

## Test Scenarios

### 1. Employee Management

#### Create Employee
1. Navigate to Employee List page
2. Click "+ Add Employee"
3. Fill in form:
   - Employee ID: EMP001
   - Full Name: John Doe
   - Email: john@example.com
   - Department: HR
   - Joining Date: 2024-01-01
4. Upload profile picture (optional)
5. Click "Save"
6. Verify employee appears in list

#### Edit Employee
1. Click edit icon next to employee
2. Modify fields
3. Click "Save"
4. Verify changes reflected in list

#### Search Employees
1. Enter search term in search box
2. Verify filtered results
3. Test search by: ID, Name, Email, Department

#### Pagination
1. Add more than 10 employees
2. Verify pagination controls appear
3. Navigate between pages
4. Verify correct data displayed

### 2. Leave Request Management

#### Create Leave Request
1. Navigate to Leave Requests tab
2. Create leave request via API or form:
   - Employee: Select from dropdown
   - Leave Type: Casual/Sick/Annual/Emergency
   - From Date: 2024-01-15
   - To Date: 2024-01-17
   - Status: Pending (default)
3. Verify leave request appears in list

#### Update Leave Status
1. As HR Manager, view pending leave requests
2. Click "Approve" or "Reject"
3. Verify status updated
4. Verify status badge color changes

#### Filter Leave Requests
1. Select status filter dropdown
2. Verify filtered results
3. Test all statuses: Pending, Approved, Rejected, Canceled

#### Search Leave Requests
1. Enter search term
2. Verify filtered results by:
   - Leave ID
   - Employee name
   - Leave type

### 3. Summary Report

#### View Summary
1. Navigate to Summary Report tab
2. Verify statistics displayed:
   - Total Leaves
   - Approved Leaves
   - Pending Leaves
   - Canceled Leaves

#### Export CSV
1. Click "Download CSV" button
2. Verify CSV file downloads
3. Open CSV and verify:
   - All columns present
   - Data matches database
   - Proper formatting

### 4. Validation Tests

#### Employee Validation
- Test duplicate Employee ID (should fail)
- Test invalid email format (should fail)
- Test missing required fields (should fail)
- Test invalid date format (should fail)

#### Leave Request Validation
- Test To Date before From Date (should fail)
- Test invalid employee (should fail)
- Test invalid status (should fail)
- Test missing required fields (should fail)

### 5. Permission Tests

#### System Manager
- Can create/edit/delete employees
- Can approve/reject leave requests
- Can view all data
- Can export CSV

#### HR Manager
- Can create/edit employees
- Can approve/reject leave requests
- Can view all data
- Cannot delete employees (if restricted)

#### Employee Role
- Can view own employee record
- Can create own leave requests
- Can cancel own pending leave requests
- Cannot approve/reject leave requests
- Cannot edit other employees

### 6. API Tests

Use Postman or curl to test:

#### Get Employees API
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.employee.get_employees?page=1&page_size=10" \
  -H "Cookie: sid=your_session_id"
```

#### Create Employee API
```bash
curl -X POST "http://localhost:8000/api/method/lms.api.employee.create_employee" \
  -H "Content-Type: application/json" \
  -H "Cookie: sid=your_session_id" \
  -d '{
    "data": {
      "employee_id": "EMP002",
      "full_name": "Jane Smith",
      "email": "jane@example.com",
      "department": "IT",
      "joining_date": "2024-01-15"
    }
  }'
```

#### Get Leave Requests API
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.leave_request.get_leave_requests?page=1&page_size=10&status=Pending" \
  -H "Cookie: sid=your_session_id"
```

#### Get Summary API
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.leave_request.get_summary" \
  -H "Cookie: sid=your_session_id"
```

#### Export CSV API
```bash
curl -X GET "http://localhost:8000/api/method/lms.api.leave_request.export_csv" \
  -H "Cookie: sid=your_session_id"
```

### 7. UI/UX Tests

#### Responsive Design
- Test on desktop (1920x1080)
- Test on tablet (768x1024)
- Test on mobile (375x667)
- Verify layout adapts correctly

#### Navigation
- Test tab switching
- Verify active tab highlighted
- Verify content loads correctly on tab switch

#### Forms
- Test form validation messages
- Test required field indicators
- Test date picker functionality
- Test file upload functionality

### 8. Performance Tests

#### Large Dataset
- Create 100+ employees
- Create 200+ leave requests
- Test pagination performance
- Test search performance
- Test CSV export with large dataset

#### Concurrent Users
- Test multiple users accessing simultaneously
- Test concurrent create/update operations
- Verify no data corruption

## Test Data

### Sample Employees
```
EMP001, John Doe, john@example.com, HR, 2024-01-01
EMP002, Jane Smith, jane@example.com, IT, 2024-01-15
EMP003, Bob Johnson, bob@example.com, Sales, 2024-02-01
```

### Sample Leave Requests
```
LR001, EMP001, Casual, 2024-01-15, 2024-01-17, Pending
LR002, EMP002, Sick, 2024-01-20, 2024-01-21, Approved
LR003, EMP003, Annual, 2024-02-01, 2024-02-05, Pending
```

## Expected Results

All tests should pass with:
- No errors in browser console
- No errors in server logs
- Proper validation messages
- Correct data persistence
- Proper permission enforcement
- Responsive UI on all devices
