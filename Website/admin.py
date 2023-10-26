from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    fields = (
        'user',
        'spoonacular_username',
        'spoonacular_password',
        'spoonacular_hash',
    )
    list_display = ('user', 'spoonacular_hash')
    list_display_links = ('user',)
    search_fields = ('user',)


admin.site.register(UserProfile, UserProfileAdmin)
