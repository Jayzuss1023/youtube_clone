from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Custom form inherits from User Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        # Specify the User object is being created
        model = User
        # Fields included to the form
        fields = ("username", "email", "password1", "password2")

        def save(self, commit=True):
            # super().save(...): This calls the original save() method of the parent class 
            # to convert the submitted, validated form data into a Python model 
            # instance.commit=False: This flag explicitly tells Django: "Create the User object in memory, 
            # but do not write it to the database yet. usually to modify the data if needed"
            user = super().save(commit=False)
            # This pulls the email address submitted by a user via a form, and
            #  the data has already passed security checks and format validation (e.g., verifying it contains an @ sign and a valid domain).
            user.email = self.clean_data["email"]
            if commit:
                user.save()
            return user