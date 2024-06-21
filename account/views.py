from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from .forms import RegistrationForm, UserAddressForm, UserEditForm,ProfilePictureForm
from .models import Address, Customer
from .tokens import account_activation_token
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import user_passes_test

from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy




from account.models import AudioModel


from django.shortcuts import redirect
from django.contrib.auth import logout

def custom_logout(request):
    # Log out the user
    logout(request)
    # Redirect to a different page after logout, such as the login page
    return redirect('/account/login/')
  






@login_required
def dashboard(request):   
    audio_files = AudioModel.objects.all()
 
    return render(request, "account/dashboard/dashboard.html", {"section": "profile", 'audio_files':audio_files})

def unauthorised_access(request):
    return render(request, 'account/admin/restricted_message.html')



@login_required
def edit_details(request):
    if request.method == "POST":
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request, "account/dashboard/edit_details.html", {"user_form": user_form})


@login_required
def delete_user(request):
    user = Customer.objects.get(user_name=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect("account:delete_confirmation")


from django.views.decorators.http import require_POST
from account.models import AudioModel

# initial version code
def account_register(request):
    audio_files= AudioModel.objects.all()

    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        registerForm = RegistrationForm(request.POST)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = True
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('account/registration/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return render(request, 'account/registration/register_email_confirm.html', {'form': registerForm,'audio_files':audio_files})
    else:
        registerForm = RegistrationForm()
    return render(request, 'account/registration/register.html', {'form': registerForm})


def account_activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Customer.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('account:dashboard')
    else:
        return render(request, 'account/registration/activation_invalid.html')



  

class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.GET.get("next"):
            return self.request.GET.get("next")
        else:
            return super().get_success_url()
    


@login_required
def view_address(request):
    addresses = Address.objects.filter(customer=request.user)
    return render(request, "account/dashboard/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("account:dashboard"))
    else:
        address_form = UserAddressForm()
    return render(request, "account/dashboard/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("account:addresses"))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "account/dashboard/edit_addresses.html", {"form": address_form})


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("account:addresses")


@login_required
def set_default(request, id):
    Address.objects.filter(customer=request.user, default=True).update(default=False)
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    return redirect("account:addresses")




def update_profile_picture(request, user_id):
    user = get_object_or_404(Customer, pk=user_id)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('tickets:dash_board')  

    else:
        form = ProfilePictureForm(instance=user)

    return render(request, 'account/change_profile_picture.html', {'form': form})




@user_passes_test(lambda u: u.is_staff)
def admin_view(request):
    user_id = request.user.id
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    user_name = user.name
   
    if not request.user.is_staff:     
        messages.error(request, "You are not authorized to view this page.")  
        return HttpResponseRedirect(reverse("login"))
     
    return render(request, 'account/admin/admin_page.html', {'user': user_name,})

   