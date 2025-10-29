# PythonAnywhere Migration Fix Guide

## Problem

When Django admin migrations are applied before custom user model migrations, you get:
```
InconsistentMigrationHistory: Migration admin.0001_initial is applied before 
its dependency accounts.0001_initial on database 'default'.
```

This happens because Django admin depends on the AUTH_USER_MODEL, but the migration was applied before the custom user model existed.

## Solution

### Step 1: Check Migration Status

Run the diagnostic command:
```bash
python manage.py fix_migrations
```

This will tell you exactly what's wrong and what commands to run.

### Step 2: Fix Migration Order

**Option A: If CustomUser table doesn't exist yet**

```bash
# 1. Reset admin migrations (fake)
python manage.py migrate admin zero --fake

# 2. Apply accounts migration first
python manage.py migrate accounts 0001

# 3. Apply all remaining migrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser --username ludmil --email ludmil@ludmilpaulo.co.za
# Then set password: Maitland@2026
```

**Option B: If CustomUser table already exists**

```bash
# 1. Reset admin migrations (fake)
python manage.py migrate admin zero --fake

# 2. Fake the accounts migration (table exists)
python manage.py migrate accounts 0001 --fake

# 3. Apply all remaining migrations with fake-initial
python manage.py migrate --fake-initial

# 4. Update/create admin user via shell
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
user, created = User.objects.get_or_create(
    username='ludmil',
    defaults={
        'email': 'ludmil@ludmilpaulo.co.za',
        'user_type': 'admin',
        'is_staff': True,
        'is_superuser': True,
        'is_verified': True
    }
)
if not created:
    user.is_staff = True
    user.is_superuser = True
    user.user_type = 'admin'
    user.is_verified = True
user.set_password('Maitland@2026')
user.save()
print('✓ Admin user created/updated!')
exit()
```

### Step 3: Handle Existing Tables

If you get errors like "Table 'django_admin_log' already exists":

```bash
# Fake all initial migrations since tables exist
python manage.py migrate admin 0001 --fake-initial
python manage.py migrate accounts 0001 --fake-initial
python manage.py migrate information --fake-initial
python manage.py migrate testimonials --fake-initial
python manage.py migrate authtoken --fake-initial

# Then run normal migrate
python manage.py migrate
```

### Step 4: Verify

```bash
# Check migration status
python manage.py showmigrations

# Test admin login
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('CustomUser exists:', User.objects.filter(username='ludmil').exists())"
```

### Step 5: Reload Web App

In PythonAnywhere dashboard:
1. Go to Web tab
2. Click "Reload" button
3. Test at: https://ludmil.pythonanywhere.com/admin/

## Quick One-Liner Fix

If tables exist but migrations are inconsistent:

```bash
python manage.py migrate admin zero --fake && \
python manage.py migrate accounts 0001 --fake-initial && \
python manage.py migrate --fake-initial
```

## Troubleshooting

### Error: "Table already exists"
- Use `--fake-initial` flag
- Checks if table exists, marks migration as applied if it does

### Error: "InconsistentMigrationHistory"
- Admin must depend on accounts
- Reset admin first, then apply accounts, then migrate everything

### Error: "No such table"
- Run `python manage.py migrate` normally (without --fake flags)
- Creates missing tables

## After Fix

Once migrations are fixed:
1. Admin panel should load: https://ludmil.pythonanywhere.com/admin/
2. Frontend login should work: https://www.ludmilpaulo.co.za/admin-login
3. API endpoints should respond correctly

## Prevention

For future deployments:
1. Always migrate in order: accounts → admin → others
2. Use `--fake-initial` only when tables already exist
3. Test migrations locally before deploying

