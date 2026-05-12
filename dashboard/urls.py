from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.index, name='home'),
    path('admin-login/', views.login_view, name='login'),
    path('super-admin-login/', views.login_view, name='super_admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('super-admin-dashboard/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('cas/', views.cas_dashboard, name='cas_dashboard'),
    path('cit/', views.cit_dashboard, name='cit_dashboard'),
    path('caf/', views.caf_dashboard, name='caf_dashboard'),
    path('cted/', views.cted_dashboard, name='cted_dashboard'),
    path('ccje/', views.ccje_dashboard, name='ccje_dashboard'),
    path('cba/', views.cba_dashboard, name='cba_dashboard'),
    path('news/', views.news, name='news'),
    path('news/preview/', views.news_preview, name='news_preview'),
    path('news/static/<slug:news_key>/', views.static_news_detail, name='static_news_detail'),
    path('news/<int:post_id>/', views.news_detail, name='news_detail'),
    path('achievement/<int:achievement_id>/', views.achievement_detail, name='achievement_detail'),
    path('news1/', views.news1, name='news1'),
    path('programs/', views.programs, name='programs'),
    path('contacts/', views.contacts, name='contacts'),
    path('alumni/', views.alumni, name='alumni'),
    path('alumni/about/', views.alumni_about, name='alumni_about'),
    path('alumni/achievements/', views.alumni_achievements, name='achievements'),
    path('alumni/stories/<int:story_id>/', views.alumni_success_story_public_detail, name='alumni_success_story_detail'),
    path('alumni/careers/', views.alumni_careers, name='careers'),
    path('alumni/contact/', views.alumni_contact, name='contact'),
    path('directory/', views.alumni_directory, name='directory'),
    path('alumni/directory/', views.alumni_directory, name='directory_alumni'),
    path('alumni/events/', views.alumni_events, name='events'),
    path('alumni/gallery/', views.alumni_gallery, name='gallery'),
    path('alumni/programs/', views.alumni_programs, name='programs_alumni'),
    path('alumni/news/', views.alumni_news, name='news_alumni'),
    path('alumni/upload-media/', views.alumni_upload_media, name='upload_media'),
    path('alumnidasbord/', views.alumni_dashboard, name='alumni_dashboard'),
    # Post Management API endpoints
    path('api/posts/get/', views.get_posts, name='get_posts'),
    path('api/posts/get/<int:post_id>/', views.get_post_detail, name='get_post_detail'),
    path('api/posts/create/', views.create_post, name='create_post'),
    path('api/posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    # Announcement and News API endpoints
    path('api/announcements/', views.get_announcements, name='get_announcements'),
    path('api/news/', views.get_news, name='get_news'),
    # Program Management API endpoints
    path('api/programs/', views.program_list_create, name='program_list_create'),
    path('api/programs/<int:pk>/', views.program_detail, name='program_detail'),
    # Faculty Management API endpoints
    path('api/faculty/', views.faculty_list_create, name='faculty_list_create'),
    path('api/faculty/<int:pk>/', views.faculty_delete, name='faculty_delete'),
    # Facility Management API endpoints
    path('api/facilities/', views.facility_list_create, name='facility_list_create'),
    path('api/facilities/<int:pk>/', views.facility_delete, name='facility_delete'),
    path('api/university-info/', views.api_university_info_list_create, name='api_university_info_list_create'),
    path('api/university-info/<int:pk>/', views.api_university_info_detail, name='api_university_info_detail'),
    path('api/site-contact-info/', views.api_site_contact_info, name='api_site_contact_info'),
    path('api/president-profile/', views.api_president_profile, name='api_president_profile'),
    path('api/norsu-history/', views.api_norsu_history, name='api_norsu_history'),
    path('about/', views.aboutnorsu, name='about'),
    path('aboutnorsu-dashboard/', views.aboutnorsu_dashboard, name='aboutnorsu_dashboard'),
    path('academic-calendar/', views.academic_calendar, name='academic_calendar'),
    # Academic Calendar API endpoints
    path('api/calendar/', views.api_calendar_list_create, name='api_calendar_list_create'),
    path('api/calendar/<int:pk>/', views.api_calendar_detail, name='api_calendar_detail'),
    # Alumni API
    path('api/alumni/', views.alumni_api, name='alumni_api'),
    path('api/alumni/<int:pk>/', views.alumni_api, name='alumni_api_detail'),
    
    # Achievement API endpoints
    path('api/achievements/', views.achievement_list_create, name='achievement_list_create'),
    path('api/achievements/<int:pk>/', views.api_achievement_detail, name='api_achievement_detail'),
    # Alumni Success Story API endpoints
    path('api/success-stories/', views.success_story_list_create, name='success_story_list_create'),
    path('api/success-stories/<int:pk>/', views.success_story_detail, name='success_story_detail'),
    # Media Upload Management API endpoints
    path('api/media-uploads/', views.get_media_uploads, name='get_media_uploads'),
    path('api/media-uploads/<int:upload_id>/approve/', views.approve_media_upload, name='approve_media_upload'),
    path('api/media-uploads/<int:upload_id>/reject/', views.reject_media_upload, name='reject_media_upload'),
    path('api/media-uploads/<int:upload_id>/delete/', views.delete_media_upload, name='delete_media_upload'),
    
    # College Management API endpoints
    path('api/colleges/', views.college_list_create, name='college_list_create'),
    path('api/colleges/<int:pk>/', views.college_detail, name='college_detail'),
    
    # Contact Message API endpoints
    path('api/contact-messages/', views.api_contact_message, name='api_contact_message'),
    path('api/contact-messages/<int:pk>/read/', views.api_mark_message_read, name='api_mark_message_read'),
    path('api/contact-messages/<int:pk>/reply/', views.api_reply_inquiry, name='api_reply_inquiry'),
    path('api/contact-messages/<int:pk>/delete/', views.api_delete_inquiry, name='api_delete_inquiry'),
    path('api/admin-accounts/', views.api_admin_accounts, name='api_admin_accounts'),
    path('api/system-analytics/', views.api_system_analytics, name='api_system_analytics'),
    path('api/admin-accounts/<str:account_key>/', views.api_admin_account_update, name='api_admin_account_update'),

    path('api/alumni/about/', views.api_alumni_about, name='api_alumni_about'),
    path('api/alumni/news/', views.api_alumni_news, name='api_alumni_news'),
    path('api/alumni/news/<int:pk>/delete/', views.api_alumni_news_delete, name='api_alumni_news_delete'),
    path('api/alumni/events/', views.api_alumni_events, name='api_alumni_events'),
    path('api/alumni/events/<int:pk>/delete/', views.api_alumni_events_delete, name='api_alumni_events_delete'),
    path('aboutnosu/', views.aboutnorsu_dashboard, name='aboutnorsu_dashboard'),
    # Keep the generic college route last so it does not shadow public single-segment pages.
    path('<str:abbr>/', views.college_dashboard_router, name='college_dashboard_router'),
]
