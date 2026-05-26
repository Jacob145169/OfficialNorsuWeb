from django.contrib import admin
from .models import AdminProfile, Alumni, Announcement, News, Post, Achievement, Program, ContactMessage, UniversityInfo

# Register your models here.

@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ('name', 'batch', 'course', 'position', 'company', 'created_at')
    list_filter = ('batch', 'course', 'created_at')
    search_fields = ('name', 'email', 'course', 'position', 'company')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'batch', 'course')
        }),
        ('Professional Information', {
            'fields': ('position', 'company', 'bio')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'created_at', 'updated_at')
    list_filter = ('priority', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'content', 'priority')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('News Details', {
            'fields': ('title', 'content', 'category')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'target_audience', 'status', 'created_at')
    list_filter = ('category', 'target_audience', 'status', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Post Details', {
            'fields': ('title', 'content', 'category', 'target_audience', 'status')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_highlighted', 'created_at')
    list_filter = ('category', 'status', 'is_highlighted', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Achievement Details', {
            'fields': ('title', 'description', 'category', 'status', 'is_highlighted')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'college', 'duration', 'status', 'created_at')
    list_filter = ('level', 'college', 'status', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Program Details', {
            'fields': ('title', 'description', 'level', 'college', 'duration', 'status')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'department', 'is_read', 'created_at')
    list_filter = ('is_read', 'department', 'created_at')
    search_fields = ('full_name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Sender Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Message Details', {
            'fields': ('subject', 'department', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )


@admin.register(UniversityInfo)
class UniversityInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'updated_at', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ('general_mandate', 'vision', 'mission', 'strategic_goals', 'core_values', 'quality_policy')
    fieldsets = (
        ('University Information', {
            'fields': (
                'general_mandate',
                'vision',
                'vision_image',
                'mission',
                'mission_image',
                'strategic_goals',
                'core_values',
                'quality_policy',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('college', 'user', 'updated_at')
    list_filter = ('college',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
