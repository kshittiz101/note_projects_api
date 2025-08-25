from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "updated_at")
    search_fields = ("title", "content", "owner__username")
    list_filter = ("updated_at",)
