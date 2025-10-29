# Testing Guide for Portfolio Application

## Admin Credentials

**Username:** `ludmil`  
**Password:** `Maitland@2025`

## Test Client Credentials

### Client 1
- **Email:** `john.smith@example.com`
- **Password:** `Client123!`
- **Company:** Tech Corp Inc

### Client 2
- **Email:** `sarah.johnson@example.com`
- **Password:** `Client123!`
- **Company:** Digital Solutions Ltd

### Client 3
- **Email:** `michael.brown@example.com`
- **Password:** `Client123!`
- **Company:** Innovation Hub

## How to Create Test Data

### Option 1: Using Management Command

```bash
python manage.py test_credentials
```

### Option 2: Using Python Script

```bash
python test_and_create_data.py
```

## Testing the Application

### 1. Start Django Backend

```bash
cd ludmilportifolio
python manage.py runserver
```

The server will run on `http://localhost:8000`

### 2. Start Next.js Frontend

```bash
cd portifolio
yarn dev
```

The application will run on `http://localhost:3000`

### 3. Test Admin Login

1. Navigate to `http://localhost:3000/admin-login`
2. Enter credentials:
   - Username: `ludmil`
   - Password: `Maitland@2025`
3. Click "Login"
4. You should be redirected to the admin dashboard

### 4. Test Client Login

1. Navigate to `http://localhost:3000/client-login`
2. Enter client credentials (e.g., john.smith@example.com / Client123!)
3. Click "Login"
4. You should see client dashboard with project inquiries

### 5. Test API Endpoints

#### Test Analytics
```bash
curl http://localhost:8000/api/information/get-analytics/
```

#### Test Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ludmil","password":"Maitland@2025"}'
```

## Expected Test Data

After running the setup script, you should have:

- **3 Admin Users** (including ludmil)
- **3 Client Users** (john.smith, sarah.johnson, michael.brown)
- **3 Project Inquiries** with different statuses
- **Multiple Tasks** assigned to inquiries
- **Several Notifications** for testing

## Features to Test

### Admin Dashboard
- [x] Login with admin credentials
- [x] View analytics and statistics
- [x] View project inquiries
- [x] View tasks and assignments
- [x] View notifications
- [x] Manage users
- [x] Update settings

### Client Dashboard
- [x] Login with client credentials
- [x] View assigned projects
- [x] View project tasks
- [x] Send messages to admin
- [x] View invoices
- [x] Download documents

### API Testing

#### Get Analytics
```bash
GET /api/information/get-analytics/
```

Response:
```json
{
  "success": true,
  "data": {
    "totalViews": 15420,
    "uniqueVisitors": 8930,
    "projects": 3,
    "testimonials": 0,
    "inquiries": {
      "total": 3,
      "pending": 0,
      "inProgress": 1,
      "completed": 0
    }
  }
}
```

#### User Login
```bash
POST /api/accounts/login/
Content-Type: application/json

{
  "username": "ludmil",
  "password": "Maitland@2025"
}
```

## Troubleshooting

### Admin credentials don't work
Run the setup script to create/reset the admin account:
```bash
python test_and_create_data.py
```

### API endpoints not working
Ensure Django backend is running:
```bash
cd ludmilportifolio
python manage.py runserver
```

### Frontend not connecting to backend
Check the API URL in `portifolio/app/api/graphql/route.ts`:
```typescript
const DJANGO_BASE_URL = 'http://localhost:8000/api';
```

## Next Steps

1. Test all authentication flows
2. Verify data displays correctly in dashboards
3. Test file uploads and media management
4. Test rich text editor functionality
5. Verify notifications system works
6. Test responsive design on mobile

## Support

For issues or questions, please contact: ludmil@ludmilpaulo.co.za

