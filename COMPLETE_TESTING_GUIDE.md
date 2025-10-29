# Complete Testing Guide - Ludmil Paulo Portfolio

## 🎯 Overview

This guide provides complete instructions to test the full-stack portfolio application with authentication, admin dashboard, and client portal.

---

## 🔧 Setup Instructions

### 1. Backend Setup (Django)

Navigate to the backend directory:
```bash
cd C:\Users\ludmi\OneDrive\Desktop\Codes\ludmilportifolio
```

**Create Virtual Environment (if not exists):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Create Database Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Create Users:**
```bash
python setup_users.py
```

### 2. Frontend Setup (Next.js)

Navigate to the frontend directory:
```bash
cd C:\Users\ludmi\OneDrive\Desktop\Codes\portifolio
```

**Install Dependencies:**
```bash
yarn install
```

---

## 🔐 Credentials

### Admin User
- **Username:** `ludmil`
- **Password:** `Maitland@2026`
- **Email:** `ludmil@ludmilpaulo.co.za`
- **Access:** Admin Dashboard with full permissions

### Test Client Users

#### Client 1
- **Username:** `client_test1`
- **Email:** `client1@example.com`
- **Password:** `Client123!`
- **Name:** John Smith
- **Company:** Tech Corp

#### Client 2
- **Username:** `client_test2`
- **Email:** `client2@example.com`
- **Password:** `Client123!`
- **Name:** Jane Doe
- **Company:** Design Studio

---

## 🚀 Running the Application

### Start Backend Server

```bash
cd C:\Users\ludmi\OneDrive\Desktop\Codes\ludmilportifolio
python manage.py runserver
```

Backend runs on: `http://localhost:8000`

### Start Frontend Server

```bash
cd C:\Users\ludmi\OneDrive\Desktop\Codes\portifolio
yarn dev
```

Frontend runs on: `http://localhost:3000`

---

## 🧪 Testing Scenarios

### Test 1: Admin Login and Dashboard

1. **Navigate to Admin Login:**
   - Go to: `http://localhost:3000/admin-login`

2. **Login:**
   - Username: `ludmil`
   - Password: `Maitland@2026`

3. **Verify Access:**
   - ✓ Should redirect to `/dashboard`
   - ✓ Should see analytics dashboard
   - ✓ Should see project management options

4. **Test Features:**
   - View analytics and statistics
   - Manage projects
   - View testimonials
   - Access settings

### Test 2: Client Login and Portal

1. **Navigate to Client Login:**
   - Go to: `http://localhost:3000/client-login`

2. **Login:**
   - Email: `client1@example.com`
   - Password: `Client123!`

3. **Verify Access:**
   - ✓ Should redirect to `/dashboard/client`
   - ✓ Should see client project dashboard
   - ✓ Should see assigned projects

4. **Test Features:**
   - View project status
   - Check progress
   - View tasks
   - Review invoices

### Test 3: Public Portfolio Features

1. **Navigate to Home:**
   - Go to: `http://localhost:3000`

2. **Test Features:**
   - View projects gallery
   - View testimonials section
   - Leave a testimonial
   - Submit project inquiry

### Test 4: API Integration

Test the GraphQL API endpoints:

1. **Test Login Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/accounts/login/ \
   -H "Content-Type: application/json" \
   -d '{"username": "ludmil", "password": "Maitland@2026"}'
   ```

2. **Expected Response:**
   ```json
   {
     "success": true,
     "token": "xxx",
     "user": {...}
   }
   ```

---

## 📋 Checklist

### Backend Checklist
- [ ] Django server running on port 8000
- [ ] Admin user created successfully
- [ ] Client users created successfully
- [ ] All migrations applied
- [ ] API endpoints responding

### Frontend Checklist
- [ ] Next.js server running on port 3000
- [ ] Admin login page accessible
- [ ] Client login page accessible
- [ ] API integration working
- [ ] No console errors

### Authentication Checklist
- [ ] Admin can login successfully
- [ ] Client can login successfully
- [ ] Token is stored in localStorage
- [ ] User data persists across page refreshes
- [ ] Logout works correctly

### Dashboard Checklist
- [ ] Admin dashboard loads all sections
- [ ] Analytics data displays correctly
- [ ] Projects can be managed
- [ ] Client dashboard shows projects
- [ ] All navigation links work

---

## 🐛 Troubleshooting

### Issue: Python not found
**Solution:** Install Python 3.10+ from python.org

### Issue: Django not installed
**Solution:** Run `pip install -r requirements.txt`

### Issue: Port already in use
**Solution:** Change port in `manage.py` or kill the process using the port

### Issue: CORS errors
**Solution:** Check that CORS_ORIGIN_ALLOW_ALL is True in settings.py

### Issue: Authentication fails
**Solution:** 
1. Run `python setup_users.py` to create users
2. Verify database connection
3. Check that Token is in INSTALLED_APPS

---

## 📝 Files Modified

### Frontend Changes
1. **app/admin-login/page.tsx** - Updated password display
2. **app/client-login/page.tsx** - Fixed login flow
3. **app/api/graphql/route.ts** - Fixed API endpoints
4. **contexts/AuthContext.tsx** - Authentication logic

### Backend Changes
1. **setup_users.py** - User creation script
2. **accounts/models.py** - User models
3. **accounts/views.py** - Login views
4. **accounts/urls.py** - URL routing

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Can login as admin with credentials: ludmil / Maitland@2026
2. ✅ Can login as client with credentials: client1@example.com / Client123!
3. ✅ Admin dashboard displays analytics and projects
4. ✅ Client dashboard shows assigned projects
5. ✅ API calls return data without errors
6. ✅ No console errors in browser
7. ✅ Token persists across page refreshes

---

## 📞 Support

If you encounter any issues:

1. Check browser console for errors
2. Check Django server logs
3. Verify user exists in database
4. Confirm all dependencies installed
5. Review this guide for setup steps

---

## 🚀 Next Steps

After successful testing:

1. Deploy backend to PythonAnywhere
2. Deploy frontend to Vercel
3. Update environment variables
4. Test production deployment
5. Monitor for errors

---

**Good luck with testing! 🎯**

