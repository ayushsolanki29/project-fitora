from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'role', 'content_preview', 'customer_id', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session_key')
    readonly_fields = ('created_at',)

    def content_preview(self, obj):
        return obj.content[:80]
    content_preview.short_description = 'Message'
