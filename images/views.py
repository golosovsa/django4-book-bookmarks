from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import redis
from django.conf import settings

from .forms import ImageCreateForm
from .models import Image
from actions.utils import create_action

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarklet image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(request.GET)

    return render(request, 'images/image/create.html', {
        'section': 'images',
        'form': form,
    })


def image_detail(request, pk, slug):
    image = get_object_or_404(Image, pk=pk, slug=slug)
    total_views = r.incr(f'image:{image.pk}:views')
    r.zincrby('image_ranking', 1, image.pk)
    return render(request, 'images/image/detail.html',
                  {'section': 'images', 'image': image, 'total_views': total_views})


@login_required
@require_POST
def image_like(request):
    image_pk = request.POST.get('pk')
    action = request.POST.get('action')
    if image_pk and action:
        try:
            image = Image.objects.get(pk=image_pk)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request, 'images/image/list_images.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    image_ranking_ = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_pks = [int(pk) for pk in image_ranking_]
    most_viewed = list(Image.objects.filter(id__in=image_ranking_pks))
    most_viewed.sort(key=lambda x: image_ranking_pks.index(x.id))
    return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})
