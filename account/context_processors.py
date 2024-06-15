def user_info(request):
    user = request.user
    profile_picture_url = None
    if user.is_authenticated:
        profile_picture_url = user.profile_picture.url if user.profile_picture else None
    return {
        'user_info': user.name if user.is_authenticated else None,
        'profile_picture_url': profile_picture_url
    }
