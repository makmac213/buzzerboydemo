

def user_profiles(request):
    if request.user.is_authenticated:
        my_profiles = request.user.profiles.filter()
        active_profile_id = request.session.get("active_profile")
        return {
            "my_profiles": my_profiles,
            "active_profile": my_profiles.filter(id=active_profile_id).first()
        }
    return {}
