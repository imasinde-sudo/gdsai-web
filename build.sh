#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python core/manage.py collectstatic --no-input
python core/manage.py migrate

# Create or reset the admin superuser (one-time setup)
python core/manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@gdsai.com', 'is_staff': True, 'is_superuser': True});
user.set_password('admin');
user.is_staff = True;
user.is_superuser = True;
user.save();
print('Superuser admin ' + ('created' if created else 'password reset'))
"
