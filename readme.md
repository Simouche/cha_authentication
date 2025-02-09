### Custom User Validation

To add custom validation to the login process, follow these steps:

1. **Define the Custom Validation Function:**

   Create a custom validation function in a module. This function should accept a `user` object and perform the necessary validation.

   ```python
   # authentication/custom_validations.py
   from django.core.exceptions import PermissionDenied
   from django.utils.translation import gettext as _

   def custom_user_validation(user):
       if not user.is_active:
           raise PermissionDenied(_("User is not active."), 'inactive_user')
   ```

2. **Update the Settings:**

   In your `settings.py` file, add the `MORE_USER_VALIDATION` setting and set it to the path of your custom validation function.

   ```python
   # cha_auth/settings.py
   MORE_USER_VALIDATION = 'authentication.custom_validations.custom_user_validation'
   ```

By following these steps, you can add custom validation to the login process without modifying the URL configuration. Users can specify their custom validation function in the `MORE_USER_VALIDATION` setting, and it will be called during the login process.