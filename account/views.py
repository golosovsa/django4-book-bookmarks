from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render

from account.forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from account.models import Profile


def user_login(request):
    template = 'account/login.html'

    if request.method != 'POST':
        return render(request, template, {'form': LoginForm()})

    form = LoginForm(request.POST)

    if not form.is_valid():
        return render(request, template, {'form': form})

    cleaned_data = form.cleaned_data
    user = authenticate(
        request,
        username=cleaned_data['username'],
        password=cleaned_data['password'],
    )

    if user is None:
        return HttpResponse('Invalid login')

    if not user.is_active:
        return HttpResponse('Disabled account')

    login(request, user)

    return HttpResponse('Authenticated successfully')


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


def register(request):
    template = 'account/register.html'

    if request.method != 'POST':
        return render(request, template, {'user_form': UserRegistrationForm()})

    user_form = UserRegistrationForm(request.POST)

    if not user_form.is_valid():
        return render(request, template, {'user_form': UserRegistrationForm()})

    new_user = user_form.save(commit=False)
    new_user.set_password(user_form.cleaned_data['password'])
    new_user.save()

    Profile.objects.create(user=new_user)

    return render(request, 'account/register_done.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully")
        else:
            messages.error(request, 'Error updating your profile')

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})
