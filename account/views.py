from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from account.forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from account.models import Profile, Contact
from actions.utils import create_action
from actions.models import Action


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
    create_action(new_user, 'has created an account')

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


@login_required
def user_list(request):
    users = get_user_model().objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people', 'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(get_user_model(), username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})


@require_POST
@login_required
def user_follow(request):
    user_pk = request.POST.get('pk')
    action = request.POST.get('action')
    if user_pk and action:
        try:
            user = get_user_model().objects.get(pk=user_pk)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except get_user_model().DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_pks = request.user.following.values_list('pk', flat=True)
    if following_pks:
        actions = actions.filter(user_id__in=following_pks)
    actions = actions.select_related('user', 'user__profile')[:10].prefetch_related('target')[:10]
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})
