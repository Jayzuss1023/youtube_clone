from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm

# Create your views here.
class RegisterView(CreateView):
    form_class = CustomUserCreationForm # db model and for fields
    success_url = reverse_lazy("accounts:login") # Where to send the user after saving

    # Check if user sending the request has an account that exist
    # If not, call super() to continue with original dispatch() method
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        #  call the parent class's original form_valid method
        # this step saves the new user/object to the database and sets self.object
        super().form_valid(form)
        # Login the user
        login(self.request, self.object)
        return redirect("/")