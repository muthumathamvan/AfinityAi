# Afinity Luxury Redesign — Integration Notes

## 1. Repo scope
All UI changes are in two places only (Django-safe, backend untouched):

- `Client_app/templates/*.html` (rewritten / polished)
- `Client_app/static/afinity-theme.css` (new)

## 2. CSS load order (already set in base.html)
```html
<link rel="stylesheet" href="{% static 'style.css' %}">          <!-- legacy first -->
<link rel="stylesheet" href="{% static 'afinity-theme.css' %}"> <!-- theme wins -->
```

## 3. Avatar wiring — zero extra work when you add a profile image field
The dashboard (`index.html`) and CRM (`crm_dashboard.html`) user cards use:

```django
{% if request.user.is_authenticated and request.user.profile_image %}
  <img src="{{ request.user.profile_image.url }}" ... />
{% else %}
  <!-- gold initial-letter fallback -->
{% endif %}
```

When you're ready to support uploaded avatars, add **one line** to
`Client_app/models.py` on `CustomUser`:

```python
class CustomUser(AbstractUser):
    ROLE_CHOICES = (('superadmin','Super Admin'),('admin','Admin'),('user','Normal User'),)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    user_under = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='avatars/', blank=True, null=True)  # <-- add
```

Then:
```bash
python manage.py makemigrations Client_app
python manage.py migrate
```
That's it — the dashboard + CRM header will automatically swap to the real
image. No template edits needed.

## 4. Role badge
The user card shows `{{ request.user.get_role_display }}` in gold caps. The
mapping (from the existing `ROLE_CHOICES`) becomes `SUPER ADMIN / ADMIN /
NORMAL USER` automatically.

## 5. Middleware redirects (`/crm/`, `/hubspot_config`)
During my preview these redirected to `/home` for the seeded `admin` user —
that's your `RoleBasedAccessMiddleware` doing its job. The templates for
those pages are already redesigned and will render luxuriously when an
authorised role hits them.

## 6. Seeded preview user (DO NOT PUSH TO PROD DB)
I created `admin / admin123` locally to take screenshots. Delete/override it
in your own DB before going live:

```python
from Client_app.models import CustomUser
CustomUser.objects.filter(username='admin', is_superuser=True).delete()
```

## 7. Production follow-ups (optional)
- Replace `<script src="https://cdn.tailwindcss.com">` with a compiled build
  (`tailwindcss -i in.css -o static/tailwind.css --minify`) — trims ~150KB JS.
- Swap legacy `style.css` out entirely once QA confirms no page relies on it.
