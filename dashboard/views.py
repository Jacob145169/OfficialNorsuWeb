from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta
from dashboard.models import Post, Program, Faculty, Facility, AcademicCalendar, Announcement, Alumni, News, Achievement, College, MediaUpload, AlumniAbout, AlumniNews, AlumniEvent, AlumniSuccessStory, ContactMessage, InquiryReply


def _safe_int(value, default=0):
    if value is None:
        return default
    if isinstance(value, str) and value.strip() == '':
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def index(request):
    # Get latest published/scheduled posts, then filter by schedule window
    posts_raw = list(Post.objects.filter(
        status__in=['published', 'scheduled'], college='all'
    ).order_by('-created_at')[:20])
    posts = [p for p in posts_raw if p.is_live()][:6]
    
    # Get achievements for the homepage
    achievements_raw = list(Achievement.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')[:10])
    achievements = [a for a in achievements_raw if a.is_live()][:6]
    
    # Get alumni success stories for the homepage
    success_stories_raw = list(AlumniSuccessStory.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')[:10])
    success_stories = [s for s in success_stories_raw if s.is_live()][:3]
    
    # Add is_new flag to each post (posts created within last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    for post in posts:
        post.is_new = post.created_at >= seven_days_ago

    context = {
        'posts': posts,
        'achievements': achievements,
        'success_stories': success_stories,
    }
    
    return render(request, 'dashboard/index.html', context)
    
def admin_dashboard(request):
    # Total statistics for the dashboard
    total_posts = Post.objects.count()
    total_alumni = Alumni.objects.count()
    total_achievements = Achievement.objects.count()
    
    context = {
        'total_posts': total_posts,
        'total_alumni': total_alumni,
        'total_achievements': total_achievements,
    }
    return render(request, 'dashboard/admin-dashboard.html', context)

@csrf_exempt
def login_view(request):
    from dashboard.models import AdminProfile

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Superadmin check
            if user.is_superuser:
                return redirect('/super-admin-dashboard/')
            
            # College Admin check via AdminProfile
            try:
                profile = AdminProfile.objects.get(user=user)
                college_key = (profile.college or '').strip().lower()
                if college_key:
                    # Look up the college's full name
                    try:
                        college_obj = College.objects.get(abbreviation__iexact=college_key)
                        college_full = college_obj.name
                        college_color = college_obj.theme_color or '#2c7f76'
                    except College.DoesNotExist:
                        college_full = college_key.upper()
                        college_color = '#2c7f76'
                    
                    # Build session JSON to inject into template
                    import json
                    session_data = json.dumps({
                        'college': college_key,
                        'collegeFullName': college_full,
                        'collegeColor': college_color,
                        'name': f'{college_key.upper()} Administrator',
                        'username': user.username,
                        'loginTime': int(timezone.now().timestamp() * 1000),
                        'sessionTimeout': 3600000,
                    })
                    
                    context = {
                        'total_posts': Post.objects.count(),
                        'total_alumni': Alumni.objects.count(),
                        'total_achievements': Achievement.objects.count(),
                        'inject_session': session_data,
                    }
                    return render(request, 'dashboard/admin-dashboard.html', context)
            except AdminProfile.DoesNotExist:
                pass
            
            # Default fallback for regular staff/users
            return redirect('/admin-dashboard/')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'dashboard/super-admin-login.html')


def admin_logout(request):
    """Log out and redirect to the admin login page."""
    logout(request)
    return redirect('/super-admin-login/')

def get_system_analytics_context():
    from django.utils import timezone
    import datetime
    now = timezone.now()
    
    from dashboard.models import Post, Achievement, News, Announcement, MediaUpload, College, Alumni
    
    posts_count = Post.objects.count()
    achievements_count = Achievement.objects.count()
    news_count = News.objects.count()
    announcements_count = Announcement.objects.count()
    media_count = MediaUpload.objects.count()
    
    total_content = posts_count + achievements_count + news_count + announcements_count + media_count
    content_distribution = {
        'total': total_content,
        'items': []
    }
    if total_content > 0:
        raw_items = [
            {'label': 'Posts', 'count': posts_count, 'color': '#A51C30'},
            {'label': 'Achievements', 'count': achievements_count, 'color': '#2563EB'},
            {'label': 'News', 'count': news_count, 'color': '#10B981'},
            {'label': 'Announcements', 'count': announcements_count, 'color': '#F59E0B'},
            {'label': 'Media', 'count': media_count, 'color': '#8B5CF6'},
        ]
        for item in raw_items:
            if item['count'] > 0:
                item['percentage'] = round((item['count'] / total_content) * 100)
                content_distribution['items'].append(item)
                
    monthly_bars = []
    total_monthly = 0
    peak_value = -1
    peak_label = ""
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        start_date = now.replace(year=y, month=m, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        next_m = m + 1
        next_y = y
        if next_m > 12:
            next_m = 1
            next_y += 1
        end_date = now.replace(year=next_y, month=next_m, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        c_posts = Post.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        c_achievements = Achievement.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
        val = c_posts + c_achievements
        
        label = start_date.strftime('%b')
        monthly_bars.append({'label': label, 'value': val, 'height_percent': 0, 'is_peak': False, '_raw_val': val})
        total_monthly += val
        if val > peak_value:
            peak_value = val
            peak_label = label
            
    if peak_value > 0:
        for b in monthly_bars:
            b['height_percent'] = round((b['_raw_val']/peak_value)*100)
            if b['_raw_val'] == peak_value:
                b['is_peak'] = True

    colleges = College.objects.all()
    engagement_items = []
    total_engagement = 0
    for c in colleges:
        key = (c.abbreviation or '').strip().lower()
        c_posts = Post.objects.filter(college__iexact=key).count()
        val = c_posts
        total_engagement += val
        engagement_items.append({
            'label': c.abbreviation,
            'name': c.name,
            'total_records': val,
            'color': c.theme_color or '#17cada'
        })
        
    top_engagement = None
    if total_engagement > 0:
        engagement_items.sort(key=lambda x: x['total_records'], reverse=True)
        top_engagement = engagement_items[0]
        for e in engagement_items:
            e['percentage'] = round((e['total_records']/total_engagement)*100)
            e['meta'] = f"{e['total_records']} records"
            
    alumni_bars = []
    current_year = now.year
    total_alumni = Alumni.objects.count()
    additions_in_window = 0
    max_alumni_yr = 0
    
    for y in range(current_year-4, current_year+1):
        c_alumni = Alumni.objects.filter(batch=str(y)).count()
        additions_in_window += c_alumni
        if c_alumni > max_alumni_yr:
            max_alumni_yr = c_alumni
        alumni_bars.append({'label': str(y), 'value': c_alumni, 'height_percent': 0, 'is_latest': (y == current_year), '_raw_val': c_alumni})
        
    if max_alumni_yr > 0:
        for b in alumni_bars:
            b['height_percent'] = round((b['_raw_val']/max_alumni_yr)*100)

    system_analytics = {
        'generated_at_display': now.strftime('%b %d, %Y %I:%M %p'),
        'content_distribution': content_distribution,
        'monthly_activity': {
            'bars': monthly_bars,
            'window_label': 'Last 6 months',
            'total': total_monthly,
            'peak_label': peak_label,
            'peak_value': peak_value
        },
        'college_engagement': {
            'metric': 'Total posts per college.',
            'items': engagement_items,
            'top_item': top_engagement
        },
        'alumni_growth': {
            'bars': alumni_bars,
            'window_label': f'Since {current_year-4}',
            'additions_in_window': additions_in_window,
            'total': total_alumni
        }
    }
    return system_analytics

@login_required(login_url='/super-admin-login/')
def super_admin_dashboard(request):
    from dashboard.models import AdminProfile, SiteContactInfo
    from django.contrib.auth.models import User

    # Get college statistics for admin dashboard
    college_totals = College.objects.aggregate(
        total_students=Sum('total_students'),
        total_instructors=Sum('qualified_instructors'),
        total_programs=Sum('programs_offered'),
    )
    total_colleges = College.objects.count()
    
    # Content statistics
    total_posts = Post.objects.count()
    total_announcements = Announcement.objects.count()
    total_news = News.objects.count()
    total_alumni = Alumni.objects.count()
    total_achievements = Achievement.objects.count()

    # ── Build Admin Accounts for the Account Management tab ──
    superadmin_account = None
    if request.user.is_superuser:
        has_usable = request.user.has_usable_password()
        superadmin_account = {
            'key': 'superadmin',
            'label': 'Super Admin',
            'collegeName': 'University-wide access',
            'username': request.user.username,
            'exists': True,
            'statusTone': 'configured' if has_usable else 'setup',
        }

    college_admin_accounts = []
    for college in College.objects.all().order_by('abbreviation'):
        key = (college.abbreviation or '').strip().lower()
        profile = AdminProfile.objects.filter(college__iexact=key).select_related('user').first()

        # Auto-create admin profile if it doesn't exist
        if not profile:
            username = f'{key}_admin'
            counter = 2
            while User.objects.filter(username=username).exists():
                username = f'{key}_admin{counter}'
                counter += 1
            user = User.objects.create_user(username=username, is_staff=True)
            user.set_unusable_password()
            user.save(update_fields=['password'])
            profile = AdminProfile.objects.create(user=user, college=key)

        has_usable = profile.user.has_usable_password()
        college_admin_accounts.append({
            'key': key,
            'label': f'{college.abbreviation.upper()} Administrator',
            'collegeName': college.name,
            'username': profile.user.username,
            'exists': True,
            'statusTone': 'configured' if has_usable else 'setup',
        })

    # Site contact info
    site_contact_info = SiteContactInfo.objects.first()
    if not site_contact_info:
        site_contact_info = SiteContactInfo()

    context = {
        'total_colleges': total_colleges,
        'total_students': college_totals.get('total_students') or 0,
        'total_instructors': college_totals.get('total_instructors') or 0,
        'total_programs': college_totals.get('total_programs') or 0,
        
        # Content statistics
        'total_posts': total_posts,
        'total_announcements': total_announcements,
        'total_news': total_news,
        'total_alumni': total_alumni,
        'total_achievements': total_achievements,

        # Admin accounts
        'superadmin_account': superadmin_account,
        'college_admin_accounts': college_admin_accounts,

        # Site contacts
        'site_contact_info': site_contact_info,
        
        # System analytics
        'system_analytics': get_system_analytics_context(),
    }
    
    return render(request, 'dashboard/super-admin-dashboard.html', context)

def admin_logout(request):
    """Log out and redirect to the admin login page."""
    logout(request)
    return redirect('/super-admin-login/')

def contacts(request):
    """View for the Contacts Dashboard"""
    return render(request, 'dashboard/contacts.html')

def cas_dashboard(request):
    # Get CAS college information
    cas_college = College.objects.filter(abbreviation='CAS').first()
    
    context = {
        'college': cas_college,
    }
    
    return render(request, 'dashboard/dashbordcas.html', context)

def cit_dashboard(request):
    return render(request, 'dashboard/dashbordcit.html')

def caf_dashboard(request):
    return render(request, 'dashboard/dashbordcaf.html')

def cted_dashboard(request):
    return render(request, 'dashboard/dashbordcted.html')

def ccje_dashboard(request):
    return render(request, 'dashboard/dashbordccje.html')

def cba_dashboard(request):
    return render(request, 'dashboard/dashbordcba.html')

def aboutnorsu_dashboard(request):
    return render(request, 'dashboard/aboutnorsu/aboutnorsu-dashboard.html')

def aboutnorsu(request):
    return render(request, 'dashboard/aboutnorsu.html')
   

def news(request):
    # Get published posts by category for the news page
    # FILTER: Only show Superadmin posts (college='all') in "Latest News"
    # Include both 'general' and 'announcement' categories for main news section
    general_posts_raw = list(Post.objects.filter(
        status__in=['published', 'scheduled'],
        college='all'
    ).filter(
        Q(category='general') | Q(category='announcement')
    ).order_by('-created_at')[:30])
    general_posts = [p for p in general_posts_raw if p.is_live()]

    event_posts_raw = list(Post.objects.filter(status__in=['published', 'scheduled'], category='event', college='all').order_by('-created_at')[:20])
    event_posts = [p for p in event_posts_raw if p.is_live()]

    academic_posts_raw = list(Post.objects.filter(status__in=['published', 'scheduled'], category='academic', college='all').order_by('-created_at')[:20])
    academic_posts = [p for p in academic_posts_raw if p.is_live()]

    sports_posts_raw = list(Post.objects.filter(status__in=['published', 'scheduled'], category='sports', college='all').order_by('-created_at')[:20])
    sports_posts = [p for p in sports_posts_raw if p.is_live()]
    
    # Get latest achievements for the news page
    achievements_raw = list(Achievement.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')[:20])
    achievements = [a for a in achievements_raw if a.is_live()][:6]
    
    # Get college administrator posts for "COLLEGES ANNOUNCEMENT"
    colleges = ['cas', 'cted', 'caf', 'ccje', 'cba', 'cit']
    college_latest_posts = {}
    
    for code in colleges:
        candidates = list(Post.objects.filter(status__in=['published', 'scheduled'], college=code).order_by('-created_at')[:10])
        live = [p for p in candidates if p.is_live()]
        if live:
            college_latest_posts[code] = live[0]
    
    return render(request, 'dashboard/newsdashbord.html', {
        'general_posts': general_posts,
        'event_posts': event_posts,
        'academic_posts': academic_posts,
        'sports_posts': sports_posts,
        'achievements': achievements,
        'college_latest_posts': college_latest_posts,
    })

def news_detail(request, post_id):
    """Detail page for a single news post."""
    try:
        post = Post.objects.get(id=post_id, status__in=['published', 'scheduled'])
        if not post.is_live():
            from django.http import Http404
            raise Http404("Post not available")
    except Post.DoesNotExist:
        from django.http import Http404
        raise Http404("Post not found")

    # Get related posts (same category, same college, exclude current, up to 5)
    related_raw = list(Post.objects.filter(
        status__in=['published', 'scheduled'],
        category=post.category,
        college=post.college
    ).exclude(id=post.id).order_by('-created_at')[:10])
    related_posts = [p for p in related_raw if p.is_live()][:5]

    return render(request, 'dashboard/news_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })

def news1(request):
    return render(request, 'dashboard/news/news1.html')

def achievement_detail(request, achievement_id):
    """Detail page for a single achievement."""
    from django.http import Http404
    try:
        achievement = Achievement.objects.get(id=achievement_id, status__in=['published', 'scheduled'])
        if not achievement.is_live():
            raise Http404("Achievement not available")
    except Achievement.DoesNotExist:
        raise Http404("Achievement not found")

    # Get related achievements (same category, exclude current, up to 4)
    related_raw = list(Achievement.objects.filter(
        status__in=['published', 'scheduled']
    ).exclude(id=achievement.id).order_by('-created_at')[:10])
    related = [a for a in related_raw if a.is_live()][:4]

    return render(request, 'dashboard/achievement_detail.html', {
        'achievement': achievement,
        'related': related,
    })



def programs(request):
    return render(request, 'dashboard/news/programs.html')

def alumni(request):
    import re
    # Get latest alumni-specific news (fetch extra to allow for schedule filtering)
    latest_news_raw = list(AlumniNews.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')[:20])
    latest_news = [n for n in latest_news_raw if n.is_live()][:10]
    
    # Extract thumbnails for news without explicit cover images
    for news in latest_news:
        if not news.image:
            img_match = re.search(r'<img[^>]+src="([^">]+)"', news.content)
            if img_match:
                news.extracted_image_url = img_match.group(1)
    
    # Get upcoming alumni-specific events
    upcoming_events = AlumniEvent.objects.filter(status='published').order_by('-date')[:3]
    
    # Get featured alumni / success stories (using AlumniSuccessStory model)
    featured_achievements_raw = list(AlumniSuccessStory.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')[:10])
    featured_achievements = [s for s in featured_achievements_raw if s.is_live()][:3]
    
    # Get Alumni About data safely
    try:
        about_data = AlumniAbout.objects.first()
    except Exception:
        about_data = None
    
    return render(request, 'dashboard/alumni/home.html', {
        'latest_news': latest_news,
        'upcoming_events': upcoming_events,
        'featured_achievements': featured_achievements,
        'about_data': about_data
    })

def alumni_about(request):
    try:
        about_data = AlumniAbout.objects.first()
    except Exception:
        about_data = None
        
    return render(request, 'dashboard/alumni/about.html', {
        'about_data': about_data
    })

def alumni_achievements(request):
    achievements_qs = AlumniSuccessStory.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at')
    search = request.GET.get('search')
    
    if search:
        achievements_qs = achievements_qs.filter(Q(alumni_name__icontains=search) | Q(achievement__icontains=search) | Q(description__icontains=search))
        
    achievements = [a for a in achievements_qs if a.is_live()]
        
    context = {
        'notable_alumni': achievements,
    }
    return render(request, 'dashboard/alumni/achievements.html', context)

def alumni_careers(request):
    return render(request, 'dashboard/alumni/careers.html')

def alumni_contact(request):
    return render(request, 'dashboard/alumni/contact.html')

@csrf_exempt
def alumni_api(request, pk=None):
    """
    API endpoint for Alumni CRUD operations.
    GET requests are public (for viewing alumni on college dashboards)
    POST requests require authentication (for admin operations)
    """
    if request.method == 'GET':
        if pk:
            try:
                alumnus = Alumni.objects.get(pk=pk)
                return JsonResponse({
                    'success': True,
                    'alumni': {
                        'id': alumnus.id,
                        'full_name': alumnus.name,
                        'latin_honors': alumnus.latin_honors,
                        'graduation_year': alumnus.batch,
                        'course': alumnus.course,
                        'position': alumnus.position,
                        'company': alumnus.company,
                        'bio': alumnus.bio,
                        'profile_image': alumnus.image.url if alumnus.image else None,
                    }
                })
            except Alumni.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Alumni not found'}, status=404)
        else:
            alumni_list = Alumni.objects.all().order_by('-created_at')
            
            # Filtering
            year = request.GET.get('year')
            course = request.GET.get('course')
            if year:
                alumni_list = alumni_list.filter(batch=year)
            if course:
                alumni_list = alumni_list.filter(course__icontains=course)
                
            data = []
            for a in alumni_list:
                data.append({
                    'id': a.id,
                    'full_name': a.name,
                    'latin_honors': a.latin_honors,
                    'graduation_year': a.batch,
                    'course': a.course,
                    'position': a.position,
                    'company': a.company,
                    'bio': a.bio,
                    'profile_image': a.image.url if a.image else None,
                    # Add fields that CCJE dashboard expects
                    'name': a.name,
                    'batch': a.batch,
                    'image': a.image.url if a.image else None,
                })
            return JsonResponse({'success': True, 'alumni': data})

    elif request.method == 'POST':
        # POST requests require authentication
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            
        try:
            # Handle both create and update
            alumni_id = request.POST.get('id')
            name = request.POST.get('name')
            latin_honors = request.POST.get('latin_honors', '')
            batch = request.POST.get('batch')
            course = request.POST.get('course')
            position = request.POST.get('position', '')
            company = request.POST.get('company', '')
            bio = request.POST.get('bio', '')
            image = request.FILES.get('image')

            if alumni_id:
                alumnus = Alumni.objects.get(pk=alumni_id)
                alumnus.name = name
                alumnus.latin_honors = latin_honors
                alumnus.batch = batch
                alumnus.course = course
                alumnus.position = position
                alumnus.company = company
                alumnus.bio = bio
                if image:
                    alumnus.image = image
                alumnus.save()
                message = 'Alumni updated successfully'
            else:
                alumnus = Alumni.objects.create(
                    name=name,
                    latin_honors=latin_honors,
                    batch=batch,
                    course=course,
                    position=position,
                    company=company,
                    bio=bio,
                    image=image
                )
                message = 'Alumni added successfully'

            return JsonResponse({'success': True, 'message': message, 'id': alumnus.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            if not pk:
                return JsonResponse({'success': False, 'error': 'ID required'}, status=400)
            alumnus = Alumni.objects.get(pk=pk)
            alumnus.delete()
            return JsonResponse({'success': True, 'message': 'Alumni deleted successfully'})
        except Alumni.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Alumni not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

def alumni_directory(request):
    program = request.GET.get('program')
    year = request.GET.get('year')
    query = request.GET.get('q')
    
    # Get alumni from dedicated Alumni model
    alumni_list = list(Alumni.objects.all())
    
    # Also include alumni entries from the generic Post model
    # (some entries might have been added as 'alumni' type posts)
    alumni_posts = Post.objects.filter(post_type='alumni')
    
    # Map Post objects to a format similar to Alumni model
    for post in alumni_posts:
        alumni_list.append({
            'name': post.title,
            'course': post.content, # Post content often used as course for alumni types
            'batch': 'N/A', # Posts don't have batch
            'latin_honors': '',
            'image': post.image,
            'position': '',
            'company': '',
            'is_post': True
        })
    
    # Now filter the combined list
    filtered_alumni = []
    
    # Filtering logic for combined list
    core_name = ""
    if program:
        p_lower = program.lower()
        core_name = p_lower.replace('bachelor of science in ', '') \
                           .replace('bachelor of ', '') \
                           .replace('bs in ', '') \
                           .replace('bs ', '') \
                           .replace('college of ', '') \
                           .replace('&', 'and') \
                           .strip()
        core_alt = core_name.replace('and', '&')

    for a in alumni_list:
        # Normalize alumni object (handle both dict and model)
        a_name = a['name'] if isinstance(a, dict) else a.name
        a_course = a['course'] if isinstance(a, dict) else a.course
        a_batch = a['batch'] if isinstance(a, dict) else a.batch
        a_position = a['position'] if isinstance(a, dict) else a.position
        a_company = a['company'] if isinstance(a, dict) else a.company
        
        keep = True
        
        if program:
            c_lower = a_course.lower()
            if core_name not in c_lower and program.lower() not in c_lower and core_alt not in c_lower:
                keep = False
                
        if keep and year:
            if str(a_batch) != str(year):
                keep = False
                
        if keep and query:
            q_lower = query.lower()
            if q_lower not in a_name.lower() and \
               q_lower not in a_course.lower() and \
               q_lower not in a_position.lower() and \
               q_lower not in a_company.lower():
                keep = False
                
        if keep:
            filtered_alumni.append(a)
        
    return render(request, 'dashboard/alumni/directory.html', {
        'alumni': filtered_alumni,
        'selected_program': program,
        'selected_year': year,
        'query': query
    })

def alumni_events(request):
    events = AlumniEvent.objects.filter(status='published').order_by('-date')
    return render(request, 'dashboard/alumni/events.html', {'events': events})

def alumni_gallery(request):
    return render(request, 'dashboard/alumni/gallery.html')

def alumni_programs(request):
    return render(request, 'dashboard/alumni/programs.html')

def alumni_news(request):
    news_id = request.GET.get('id')
    if news_id:
        try:
            all_items = list(AlumniNews.objects.filter(id=news_id, status__in=['published', 'scheduled']))
            news_items = [n for n in all_items if n.is_live()]
        except (AlumniNews.DoesNotExist, ValueError):
            all_items = list(AlumniNews.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at'))
            news_items = [n for n in all_items if n.is_live()]
    else:
        all_items = list(AlumniNews.objects.filter(status__in=['published', 'scheduled']).order_by('-created_at'))
        news_items = [n for n in all_items if n.is_live()]
        
    return render(request, 'dashboard/alumni/news.html', {'news': news_items, 'single_view': bool(news_id)})

def alumni_upload_media(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            media_type = request.POST.get('media_type')
            year = request.POST.get('year')
            college = request.POST.get('college')
            file = request.FILES.get('file')
            
            if not all([title, media_type, year, college, file]):
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'dashboard/alumni/upload_media.html')
            
            # Create media upload with pending status
            media_upload = MediaUpload.objects.create(
                title=title,
                description=description,
                media_type=media_type,
                file=file,
                year=year,
                college=college,
                uploaded_by=request.user.username if request.user.is_authenticated else 'Anonymous Alumni',
                approval_status='pending'
            )
            
            messages.success(request, 'Your media has been uploaded successfully! It will be reviewed by the admin before being published.')
            return redirect('gallery')
            
        except Exception as e:
            messages.error(request, f'Error uploading media: {str(e)}')
            return render(request, 'dashboard/alumni/upload_media.html')
    
    return render(request, 'dashboard/alumni/upload_media.html')

def alumni_dashboard(request):
    return render(request, 'dashboard/alumnidasbord.html')


# Media Upload Management API Endpoints

def get_media_uploads(request):
    """Get all media uploads for admin approval"""
    uploads = MediaUpload.objects.all().order_by('-created_at')
    uploads_data = []
    for upload in uploads:
        uploads_data.append({
            'id': upload.id,
            'title': upload.title,
            'description': upload.description,
            'media_type': upload.media_type,
            'file_url': upload.file.url if upload.file else '',
            'file_name': upload.file.name.split('/')[-1] if upload.file else '',
            'year': upload.year,
            'college': upload.college,
            'uploaded_by': upload.uploaded_by,
            'approval_status': upload.approval_status,
            'rejection_reason': upload.rejection_reason,
            'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return JsonResponse({'uploads': uploads_data})

@csrf_exempt
def approve_media_upload(request, upload_id):
    """Approve a media upload"""
    if request.method == 'POST':
        try:
            upload = MediaUpload.objects.get(id=upload_id)
            upload.approval_status = 'approved'
            upload.save()
            return JsonResponse({'success': True, 'message': 'Media upload approved successfully'})
        except MediaUpload.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Media upload not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def reject_media_upload(request, upload_id):
    """Reject a media upload"""
    if request.method == 'POST':
        try:
            upload = MediaUpload.objects.get(id=upload_id)
            upload.approval_status = 'rejected'
            rejection_reason = request.POST.get('rejection_reason', '')
            upload.rejection_reason = rejection_reason
            upload.save()
            return JsonResponse({'success': True, 'message': 'Media upload rejected successfully'})
        except MediaUpload.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Media upload not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def delete_media_upload(request, upload_id):
    """Delete a media upload"""
    if request.method == 'POST':
        try:
            upload = MediaUpload.objects.get(id=upload_id)
            # Delete the file
            if upload.file:
                upload.file.delete()
            upload.delete()
            return JsonResponse({'success': True, 'message': 'Media upload deleted successfully'})
        except MediaUpload.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Media upload not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# Post Management API Endpoints

def get_posts(request):
    """
    API endpoint to retrieve all posts.
    Returns JSON response with success flag and posts array.
    """
    college = request.GET.get('college')
    post_type = request.GET.get('type')
    
    posts = Post.objects.all()
    
    if college and college != 'all':
        posts = posts.filter(college__iexact=college)
    if post_type:
        posts = posts.filter(post_type=post_type)
        
    posts_data = []
    for post in posts:
        post_dict = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'post_type': post.post_type,
            'category': post.category,
            'college': post.college,
            'target_audience': post.target_audience,
            'image': post.image.url if post.image else '',
            'status': post.status,
            'author': post.author,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
            'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else '',
            'expires_at': post.expires_at.isoformat() if post.expires_at else '',
            # Support legacy field names if any
            'date': post.created_at.isoformat(),
            'type': post.post_type,
        }
        posts_data.append(post_dict)
    
    return JsonResponse({
        'success': True,
        'posts': posts_data
    })


def get_post_detail(request, post_id):
    """
    API endpoint to retrieve a single post by ID.
    """
    try:
        post = Post.objects.get(id=post_id)
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'post_type': post.post_type,
                'category': post.category,
                'college': post.college,
                'target_audience': post.target_audience,
                'image': post.image.url if post.image else '',
                'status': post.status,
                'author': post.author,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat(),
                'scheduled_at': post.scheduled_at.isoformat() if post.scheduled_at else '',
                'expires_at': post.expires_at.isoformat() if post.expires_at else '',
            }
        })
    except Post.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Post not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
def create_post(request):
    """
    API endpoint to create a new post.
    Accepts POST requests with post data and returns success JSON.
    """
    if request.method == 'POST':
        try:
            # Extract data from POST request
            post_id = request.POST.get('id')
            title = request.POST.get('title')
            content = request.POST.get('content')
            post_type = request.POST.get('type', 'general')
            category = request.POST.get('category', 'general')
            college = request.POST.get('college', 'all').lower()
            target_audience = request.POST.get('target_audience', 'all')
            status = request.POST.get('status', 'published')
            author = request.POST.get('author')
            
            # Handle image upload if present
            image = request.FILES.get('image', None)
            
            # Schedule fields
            scheduled_at_raw = request.POST.get('scheduled_at', '').strip()
            expires_at_raw = request.POST.get('expires_at', '').strip()

            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as tz

            scheduled_at = None
            if scheduled_at_raw:
                parsed = parse_datetime(scheduled_at_raw)
                scheduled_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed

            expires_at = None
            if expires_at_raw:
                parsed = parse_datetime(expires_at_raw)
                expires_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed
            
            if post_id:
                # Update existing
                post = Post.objects.get(id=post_id)
                post.title = title
                post.content = content
                post.post_type = post_type
                post.category = category
                post.college = college
                post.target_audience = target_audience
                post.status = status
                post.scheduled_at = scheduled_at
                post.expires_at = expires_at
                if author:
                    post.author = author
                if image:
                    post.image = image
                post.save()
                message = 'Post updated successfully'
            else:
                # Create new Post instance
                post = Post.objects.create(
                    title=title,
                    content=content,
                    post_type=post_type,
                    category=category,
                    college=college,
                    target_audience=target_audience,
                    status=status,
                    scheduled_at=scheduled_at,
                    expires_at=expires_at,
                    author=author,
                    image=image
                )
                message = 'Post created successfully'
            
            # Return success response with created post data
            return JsonResponse({
                'success': True,
                'message': message,
                'post': {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'post_type': post.post_type,
                    'image': post.image.url if post.image else '',
                    'created_at': post.created_at.isoformat(),
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)


@csrf_exempt
def api_contact_message(request):
    """API endpoint to receive contact messages from the contact form."""
    print(f"DEBUG: api_contact_message called with method {request.method}")
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone', '')
            subject = request.POST.get('subject')
            department = request.POST.get('department', '')
            message = request.POST.get('message')
            
            print(f"DEBUG: Received message from {full_name} ({email})")

            if not all([full_name, email, subject, message]):
                print("DEBUG: Missing required fields")
                return JsonResponse({'success': False, 'error': 'All required fields must be filled.'}, status=400)

            msg = ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                subject=subject,
                department=department,
                message=message
            )
            print(f"DEBUG: Message created successfully with ID {msg.id}")
            return JsonResponse({'success': True, 'message': 'Message sent successfully!'})
        except Exception as e:
            print(f"DEBUG: Error creating message: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    # For admin to get messages
    elif request.method == 'GET':
        # Temporarily allow GET without authentication for testing
        # if not request.user.is_authenticated:
        #     print("DEBUG: GET failed - User not authenticated")
        #     return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            
        try:
            messages = ContactMessage.objects.all().order_by('-created_at')
            print(f"DEBUG: Found {messages.count()} messages")
            messages_data = []
            for m in messages:
                replies_data = [{
                    'id': r.id,
                    'sender': r.sender,
                    'message': r.message,
                    'created_at': r.created_at.isoformat()
                } for r in m.replies.all()]
                
                messages_data.append({
                    'id': m.id,
                    'full_name': m.full_name,
                    'email': m.email,
                    'phone': m.phone,
                    'subject': m.subject,
                    'department': m.department,
                    'message': m.message,
                    'is_read': m.is_read,
                    'created_at': m.created_at.isoformat(),
                    'replies': replies_data
                })
            return JsonResponse({'success': True, 'messages': messages_data})
        except Exception as e:
            print(f"DEBUG: Error fetching messages: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_mark_message_read(request, pk):
    """Mark a message as read."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        
    try:
        message = ContactMessage.objects.get(pk=pk)
        message.is_read = True
        message.save()
        return JsonResponse({'success': True})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)


@csrf_exempt
def api_delete_inquiry(request, pk):
    """Delete an inquiry."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    if request.method == 'POST' or request.method == 'DELETE':
        try:
            message = ContactMessage.objects.get(pk=pk)
            message.delete()
            return JsonResponse({'success': True, 'message': 'Inquiry deleted successfully'})
        except ContactMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# Academic Calendar Views

def academic_calendar(request):
    """
    Public view for the Academic Calendar.
    Displays images and description for the active academic calendar.
    """
    # Get the latest active academic calendar
    calendar = AcademicCalendar.objects.filter(is_active=True).order_by('-created_at').first()
    
    context = {
        'calendar': calendar,
    }
    
    return render(request, 'dashboard/academic_calendar.html', context)

@csrf_exempt
def api_calendar_list_create(request):
    """
    API endpoint to list (GET) or create (POST) calendar entries.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        
    if request.method == 'GET':
        calendars = AcademicCalendar.objects.all().order_by('-created_at')
        
        data = []
        for cal in calendars:
            data.append({
                'id': cal.id,
                'title': cal.title,
                'academic_year': cal.academic_year,
                'description': cal.description,
                'images': cal.images or [],
                'pdf_url': cal.pdf_file.url if cal.pdf_file else None,
                'is_active': cal.is_active,
                'created_at': cal.created_at.isoformat(),
            })
            
        return JsonResponse({
            'success': True,
            'calendars': data
        })
        
    elif request.method == 'POST':
        try:
            title = request.POST.get('title', 'Academic Calendar')
            academic_year = request.POST.get('academic_year', '2025-2026')
            description = request.POST.get('description', '')
            is_active = request.POST.get('is_active') == 'true'
            
            # Handle PDF upload
            pdf_file = request.FILES.get('pdf_file')
            
            # Handle multiple image uploads
            calendar_images = []
            files = request.FILES.getlist('images')
            if files:
                import os
                from django.core.files.storage import default_storage
                for f in files:
                    # Save to media/calendar/
                    path = default_storage.save(f'calendar/{f.name}', f)
                    calendar_images.append(default_storage.url(path))
            
            # If this is active, deactivate others
            if is_active:
                AcademicCalendar.objects.filter(is_active=True).update(is_active=False)
            
            calendar = AcademicCalendar.objects.create(
                title=title,
                academic_year=academic_year,
                description=description,
                images=calendar_images,
                pdf_file=pdf_file,
                is_active=is_active
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Calendar created successfully',
                'calendar': {
                    'id': calendar.id,
                    'title': calendar.title,
                    'academic_year': calendar.academic_year,
                    'images': calendar.images,
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_calendar_detail(request, pk):
    """
    API endpoint to retrieve (GET), update (POST/PUT), or delete (DELETE) a calendar entry.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        
    try:
        calendar = AcademicCalendar.objects.get(pk=pk)
    except AcademicCalendar.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Calendar not found'}, status=404)
        
    if request.method == 'GET':
        try:
            return JsonResponse({
                'success': True,
                'calendar': {
                    'id': calendar.id,
                    'title': calendar.title,
                    'academic_year': calendar.academic_year,
                    'description': calendar.description,
                    'images': calendar.images or [],
                    'pdf_url': calendar.pdf_file.url if calendar.pdf_file and hasattr(calendar.pdf_file, 'url') else None,
                    'is_active': calendar.is_active,
                    'created_at': calendar.created_at.isoformat(),
                }
            })
        except Exception as e:
            print(f"Error in GET api_calendar_detail: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Data processing error: {str(e)}"}, status=500)
        
    elif request.method in ['POST', 'PUT']:
        try:
            calendar.title = request.POST.get('title', calendar.title)
            calendar.academic_year = request.POST.get('academic_year', calendar.academic_year)
            calendar.description = request.POST.get('description', calendar.description)
            
            is_active_val = request.POST.get('is_active')
            if is_active_val is not None:
                new_is_active = is_active_val == 'true'
                if new_is_active and not calendar.is_active:
                    # Deactivate others if this one is becoming active
                    AcademicCalendar.objects.filter(is_active=True).update(is_active=False)
                calendar.is_active = new_is_active
            
            # Handle images (Selective removal + adding new ones)
            # 1. Start with the list of images to keep
            keep_images = request.POST.getlist('keep_images')
            updated_images = keep_images if keep_images else []
            
            # 2. Add new images if uploaded
            files = request.FILES.getlist('images')
            if files:
                from django.core.files.storage import default_storage
                for f in files:
                    path = default_storage.save(f'calendar/{f.name}', f)
                    updated_images.append(default_storage.url(path))
            
            calendar.images = updated_images
            
            # Handle new PDF
            pdf_file = request.FILES.get('pdf_file')
            if pdf_file:
                calendar.pdf_file = pdf_file
            
            calendar.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Calendar updated successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    elif request.method == 'DELETE':
        try:
            calendar.delete()
            return JsonResponse({
                'success': True,
                'message': 'Calendar deleted successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# Achievement Management API Endpoints

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def achievement_list_create(request):
    """
    API endpoint to list all achievements (GET) or create/update an achievement (POST).
    """
    if request.method == 'GET':
        achievements = Achievement.objects.all().order_by('-created_at')
        achievements_data = []
        for achievement in achievements:
            achievements_data.append({
                'id': achievement.id,
                'title': achievement.title,
                'description': achievement.description,
                'category': achievement.category,
                'recipient': achievement.recipient,
                'achievement_date': achievement.achievement_date.isoformat() if achievement.achievement_date else '',
                'image': achievement.display_image_url,
                'status': achievement.status,
                'scheduled_at': achievement.scheduled_at.isoformat() if achievement.scheduled_at else '',
                'expires_at': achievement.expires_at.isoformat() if achievement.expires_at else '',
            })
        return JsonResponse({'success': True, 'achievements': achievements_data})
    
    elif request.method == 'POST':
        try:
            achievement_id = request.POST.get('id')
            title = request.POST.get('title')
            description = request.POST.get('description')
            category = request.POST.get('category', 'other')
            recipient = request.POST.get('recipient')
            achievement_date_raw = request.POST.get('achievement_date')
            status = request.POST.get('status', 'published')
            scheduled_at_raw = request.POST.get('scheduled_at')
            expires_at_raw = request.POST.get('expires_at')
            image = request.FILES.get('image')

            from django.utils.dateparse import parse_date, parse_datetime
            from django.utils import timezone as tz

            achievement_date = parse_date(achievement_date_raw) if achievement_date_raw else None

            scheduled_at = None
            if scheduled_at_raw:
                parsed_s = parse_datetime(scheduled_at_raw)
                scheduled_at = tz.make_aware(parsed_s) if parsed_s and parsed_s.tzinfo is None else parsed_s

            expires_at = None
            if expires_at_raw:
                parsed_e = parse_datetime(expires_at_raw)
                expires_at = tz.make_aware(parsed_e) if parsed_e and parsed_e.tzinfo is None else parsed_e

            if achievement_id:
                achievement = Achievement.objects.get(id=achievement_id)
                achievement.title = title
                achievement.description = description
                achievement.category = category
                achievement.recipient = recipient
                if achievement_date:
                    achievement.achievement_date = achievement_date
                achievement.status = status
                if scheduled_at:
                    achievement.scheduled_at = scheduled_at
                else:
                    achievement.scheduled_at = None
                if expires_at:
                    achievement.expires_at = expires_at
                else:
                    achievement.expires_at = None
                if image:
                    achievement.image = image
                achievement.save()
            else:
                achievement = Achievement.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    recipient=recipient,
                    achievement_date=achievement_date,
                    image=image,
                    status=status,
                    scheduled_at=scheduled_at,
                    expires_at=expires_at
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'Achievement saved successfully',
                'achievement': {
                    'id': achievement.id,
                    'title': achievement.title,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@login_required(login_url='/super-admin-login/')
def success_story_list_create(request):
    """
    API endpoint to list all alumni success stories (GET) or create/update a success story (POST).
    """
    if request.method == 'GET':
        stories = AlumniSuccessStory.objects.all().order_by('-created_at')
        stories_data = []
        for story in stories:
            stories_data.append({
                'id': story.id,
                'alumni_name': story.alumni_name,
                'achievement': story.achievement,
                'description': story.description,
                'image': story.display_image_url,
                'status': story.status,
                'scheduled_at': story.scheduled_at.isoformat() if story.scheduled_at else '',
                'expires_at': story.expires_at.isoformat() if story.expires_at else '',
            })
        return JsonResponse({'success': True, 'stories': stories_data})
    
    elif request.method == 'POST':
        try:
            from django.utils.dateparse import parse_datetime
            story_id = request.POST.get('id')
            alumni_name = request.POST.get('alumni_name')
            achievement = request.POST.get('achievement')
            description = request.POST.get('description')
            status = request.POST.get('status', 'published')
            image = request.FILES.get('image')

            # Parse schedule fields
            scheduled_at = request.POST.get('scheduled_at')
            expires_at = request.POST.get('expires_at')
            parsed_scheduled_at = parse_datetime(scheduled_at) if scheduled_at else None
            parsed_expires_at = parse_datetime(expires_at) if expires_at else None

            if story_id:
                story = AlumniSuccessStory.objects.get(id=story_id)
                story.alumni_name = alumni_name
                story.achievement = achievement
                story.description = description
                story.status = status
                story.scheduled_at = parsed_scheduled_at
                story.expires_at = parsed_expires_at
                if image:
                    story.image = image
                story.save()
            else:
                story = AlumniSuccessStory.objects.create(
                    alumni_name=alumni_name,
                    achievement=achievement,
                    description=description,
                    status=status,
                    scheduled_at=parsed_scheduled_at,
                    expires_at=parsed_expires_at,
                    image=image
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'Success story saved successfully',
                'story': {
                    'id': story.id,
                    'alumni_name': story.alumni_name,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def success_story_detail(request, pk):
    """
    API endpoint to get or delete a success story.
    """
    try:
        story = AlumniSuccessStory.objects.get(pk=pk)
    except AlumniSuccessStory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Success story not found'}, status=404)
        
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'story': {
                'id': story.id,
                'alumni_name': story.alumni_name,
                'achievement': story.achievement,
                'description': story.description,
                'image': story.display_image_url,
                'status': story.status,
                'scheduled_at': story.scheduled_at.isoformat() if story.scheduled_at else '',
                'expires_at': story.expires_at.isoformat() if story.expires_at else '',
            }
        })
    elif request.method == 'DELETE' or request.method == 'POST':
        try:
            story.delete()
            return JsonResponse({'success': True, 'message': 'Success story deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_achievement_detail(request, pk):
    """
    API endpoint to get or delete an achievement.
    """
    try:
        achievement = Achievement.objects.get(pk=pk)
    except Achievement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Achievement not found'}, status=404)
        
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'achievement': {
                'id': achievement.id,
                'title': achievement.title,
                'description': achievement.description,
                'category': achievement.category,
                'recipient': achievement.recipient,
                'achievement_date': achievement.achievement_date.isoformat() if achievement.achievement_date else '',
                'image': achievement.display_image_url,
                'status': achievement.status,
                'scheduled_at': achievement.scheduled_at.isoformat() if achievement.scheduled_at else '',
                'expires_at': achievement.expires_at.isoformat() if achievement.expires_at else '',
            }
        })
    elif request.method == 'DELETE' or request.method == 'POST':
        try:
            achievement.delete()
            return JsonResponse({'success': True, 'message': 'Achievement deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


# College Management API Endpoints

@csrf_exempt
def college_list_create(request):
    """
    API endpoint to list all colleges (GET) or create/update a college (POST).
    GET requests are public (for viewing college information on dashboards)
    POST requests require authentication (for admin operations)
    """
    if request.method == 'GET':
        colleges = College.objects.all().order_by('name')
        colleges_data = []
        for college in colleges:
            colleges_data.append({
                'id': college.id,
                'name': college.name,
                'abbreviation': college.abbreviation,
                'dean': college.dean,
                'students': college.total_students,
                'programs': college.programs_offered,
                'instructors': college.qualified_instructors,
                'status': college.status,
                'description': college.description,
                'hero_description': college.hero_description,
                'about': college.about,
                'vision': college.vision,
                'mission': college.mission,
                'goals': college.goals or [],
                'image': college.image.url if college.image else '',
            })
        return JsonResponse({'success': True, 'colleges': colleges_data})
    
    elif request.method == 'POST':
        # POST requests require authentication
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
            
        try:
            college_id = request.POST.get('id')
            name = request.POST.get('name')
            abbreviation = request.POST.get('abbreviation')
            dean = request.POST.get('dean')
            students = request.POST.get('students', 0)
            programs = request.POST.get('programs', 0)
            instructors = request.POST.get('instructors', 0)
            status = request.POST.get('status', 'active')
            description = request.POST.get('description', '')
            hero_description = request.POST.get('hero_description', '')
            about = request.POST.get('about', '')
            vision = request.POST.get('vision', '')
            mission = request.POST.get('mission', '')
            
            import json as _json
            goals_json = request.POST.get('goals')
            goals = _json.loads(goals_json) if goals_json else []
            
            image = request.FILES.get('image')

            if college_id:
                college = College.objects.get(id=college_id)
                college.name = name
                college.abbreviation = abbreviation
                college.dean = dean
                college.total_students = _safe_int(students)
                college.programs_offered = _safe_int(programs)
                college.qualified_instructors = _safe_int(instructors)
                college.status = status
                college.description = description or about
                college.hero_description = hero_description
                college.about = about
                college.vision = vision
                college.mission = mission
                college.goals = goals
                if image:
                    college.image = image
                college.save()
            else:
                college = College.objects.create(
                    name=name,
                    abbreviation=abbreviation,
                    dean=dean,
                    total_students=_safe_int(students),
                    programs_offered=_safe_int(programs),
                    qualified_instructors=_safe_int(instructors),
                    status=status,
                    description=description or about,
                    hero_description=hero_description,
                    about=about,
                    vision=vision,
                    mission=mission,
                    goals=goals,
                    image=image
                )
            
            return JsonResponse({
                'success': True, 
                'message': 'College saved successfully',
                'college': {
                    'id': college.id,
                    'name': college.name,
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def college_detail(request, pk):
    """
    API endpoint to get or delete a college.
    """
    try:
        college = College.objects.get(pk=pk)
    except College.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'College not found'}, status=404)
        
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'college': {
                'id': college.id,
                'name': college.name,
                'abbreviation': college.abbreviation,
                'dean': college.dean,
                'students': college.total_students,
                'programs': college.programs_offered,
                'instructors': college.qualified_instructors,
                'status': college.status,
                'description': college.description,
                'hero_description': college.hero_description,
                'about': college.about,
                'vision': college.vision,
                'mission': college.mission,
                'goals': college.goals or [],
                'image': college.image.url if college.image else '',
            }
        })
    elif request.method == 'DELETE' or request.method == 'POST':
        try:
            college.delete()
            return JsonResponse({'success': True, 'message': 'College deleted successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)





@csrf_exempt
def delete_post(request, post_id):
    """
    API endpoint to delete a post.
    Accepts DELETE requests and returns success JSON.
    """
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
            post.delete()
            return JsonResponse({
                'success': True,
                'message': 'Post deleted successfully'
            })
        except Post.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Post not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_alumni_news(request):
    if request.method == 'GET':
        news = AlumniNews.objects.all().order_by('-created_at')
        news_data = []
        for n in news:
            news_data.append({
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'image': n.image.url if n.image else '',
                'created_at': n.created_at.isoformat(),
                'status': n.status,
                'scheduled_at': n.scheduled_at.isoformat() if n.scheduled_at else '',
                'expires_at': n.expires_at.isoformat() if n.expires_at else '',
            })
        return JsonResponse({'success': True, 'news': news_data})
    
    elif request.method == 'POST':
        try:
            news_id = request.POST.get('id')
            if news_id:
                news_item = AlumniNews.objects.get(id=news_id)
            else:
                news_item = AlumniNews()
            
            news_item.title = request.POST.get('title')
            news_item.content = request.POST.get('content')
            news_item.status = request.POST.get('status', 'published')

            # Schedule fields
            scheduled_at_raw = request.POST.get('scheduled_at', '').strip()
            expires_at_raw = request.POST.get('expires_at', '').strip()

            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as tz

            if scheduled_at_raw:
                parsed = parse_datetime(scheduled_at_raw)
                news_item.scheduled_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed
            else:
                news_item.scheduled_at = None

            if expires_at_raw:
                parsed = parse_datetime(expires_at_raw)
                news_item.expires_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed
            else:
                news_item.expires_at = None
            
            if request.FILES.get('image'):
                news_item.image = request.FILES.get('image')
            
            news_item.save()
            return JsonResponse({'success': True, 'message': 'Alumni news saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_alumni_events(request):
    if request.method == 'GET':
        events = AlumniEvent.objects.all().order_by('-date')
        events_data = []
        for e in events:
            events_data.append({
                'id': e.id,
                'title': e.title,
                'description': e.description,
                'date': e.date.isoformat(),
                'location': e.location,
                'image': e.image.url if e.image else '',
                'status': e.status,
                'scheduled_at': e.scheduled_at.isoformat() if e.scheduled_at else '',
                'expires_at': e.expires_at.isoformat() if e.expires_at else '',
            })
        return JsonResponse({'success': True, 'events': events_data})
    
    elif request.method == 'POST':
        try:
            event_id = request.POST.get('id')
            if event_id:
                event = AlumniEvent.objects.get(id=event_id)
            else:
                event = AlumniEvent()
            
            event.title = request.POST.get('title')
            event.description = request.POST.get('description')
            event.date = request.POST.get('date')
            event.location = request.POST.get('location')
            event.status = request.POST.get('status', 'published')
            
            # Schedule fields
            scheduled_at_raw = request.POST.get('scheduled_at', '').strip()
            expires_at_raw = request.POST.get('expires_at', '').strip()

            from django.utils.dateparse import parse_datetime
            from django.utils import timezone as tz

            if scheduled_at_raw:
                parsed = parse_datetime(scheduled_at_raw)
                event.scheduled_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed
            else:
                event.scheduled_at = None

            if expires_at_raw:
                parsed = parse_datetime(expires_at_raw)
                event.expires_at = tz.make_aware(parsed) if parsed and parsed.tzinfo is None else parsed
            else:
                event.expires_at = None
            
            if request.FILES.get('image'):
                event.image = request.FILES.get('image')
            
            event.save()
            return JsonResponse({'success': True, 'message': 'Alumni event saved successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_alumni_news_delete(request, pk):
    if request.method == 'POST':
        try:
            item = AlumniNews.objects.get(id=pk)
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_alumni_events_delete(request, pk):
    if request.method == 'POST':
        try:
            item = AlumniEvent.objects.get(id=pk)
            item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_alumni_about(request):
    """
    API endpoint to get (GET) or update (POST) the Alumni About information.
    """
    if request.method == 'GET':
        about = AlumniAbout.objects.first()
        if not about:
            # Create a default one if none exists
            about = AlumniAbout.objects.create(
                title='The NORSU-BSC Alumni Association',
                content="We are a vibrant community of graduates dedicated to fostering lifelong relationships between Negros Oriental State University and its alumni. Through networking, mentorship, and support, we empower our members to achieve excellence in their respective fields.",
                vision="A globally recognized state university.",
                mission="To build a strong, supportive network that champions the success of NORSUnians and contributes to the institution's enduring legacy of academic excellence."
            )
        
        return JsonResponse({
            'success': True,
            'about': {
                'id': about.id,
                'title': about.title,
                'content': about.content,
                'vision': about.vision,
                'mission': about.mission,
                'image': about.image.url if about.image else ''
            }
        })
    
    elif request.method == 'POST':
        try:
            about = AlumniAbout.objects.first()
            if not about:
                about = AlumniAbout()
            
            about.title = request.POST.get('title', about.title)
            about.content = request.POST.get('content', about.content)
            about.vision = request.POST.get('vision', about.vision)
            about.mission = request.POST.get('mission', about.mission)
            
            image = request.FILES.get('image')
            if image:
                about.image = image
            
            about.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Alumni About information updated successfully'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# Faculty Management API Endpoints

@csrf_exempt
def faculty_list_create(request):
    """
    API endpoint to list all faculty members (GET) or create a new faculty member (POST).
    """
    if request.method == 'GET':
        college = request.GET.get('college')
        if college:
            faculty = Faculty.objects.filter(college__iexact=college)
        else:
            faculty = Faculty.objects.all()
            
        faculty_data = []
        for member in faculty:
            faculty_data.append({
                'id': member.id,
                'name': member.name,
                'position': member.position,
                'college': member.college,
                'status': member.status,
                'image': member.image.url if member.image else '',
                'created_at': member.created_at.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'faculty': faculty_data
        })
    
    elif request.method == 'POST':
        try:
            name = request.POST.get('name')
            position = request.POST.get('position')
            college = request.POST.get('college').lower() if request.POST.get('college') else None
            status = request.POST.get('status', 'active')
            image = request.FILES.get('image')
            
            faculty_id = request.POST.get('id')
            if faculty_id:
                # Update existing
                member = Faculty.objects.get(id=faculty_id)
                member.name = name
                member.position = position
                member.college = college
                member.status = status
                if image:
                    member.image = image
                member.save()
            else:
                # Create new
                member = Faculty.objects.create(
                    name=name,
                    position=position,
                    college=college,
                    status=status,
                    image=image
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Faculty member saved successfully',
                'faculty': {
                    'id': member.id,
                    'name': member.name,
                    'position': member.position,
                    'college': member.college,
                    'status': member.status,
                    'image': member.image.url if member.image else '',
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def faculty_delete(request, pk):
    """
    API endpoint to delete a faculty member.
    """
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            member = Faculty.objects.get(pk=pk)
            member.delete()
            return JsonResponse({'success': True, 'message': 'Faculty member deleted successfully'})
        except Faculty.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Faculty member not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


# Facility Management API Endpoints

@csrf_exempt
def facility_list_create(request):
    """
    API endpoint to list all facilities (GET) or create a new facility (POST).
    """
    if request.method == 'GET':
        college = request.GET.get('college')
        if college:
            facilities = Facility.objects.filter(college__iexact=college)
        else:
            facilities = Facility.objects.all()
            
        facilities_data = []
        for facility in facilities:
            facilities_data.append({
                'id': facility.id,
                'name': facility.name,
                'type': facility.type,
                'capacity': facility.capacity,
                'college': facility.college,
                'status': facility.status,
                'image': facility.image.url if facility.image else '',
            })
        
        return JsonResponse({
            'success': True,
            'facilities': facilities_data
        })
    
    elif request.method == 'POST':
        try:
            name = request.POST.get('name')
            facility_type = request.POST.get('type')
            capacity = request.POST.get('capacity')
            college = request.POST.get('college').lower() if request.POST.get('college') else None
            status = request.POST.get('status', 'available')
            image = request.FILES.get('image')
            
            facility_id = request.POST.get('id')
            if facility_id:
                # Update
                facility = Facility.objects.get(id=facility_id)
                facility.name = name
                facility.type = facility_type
                facility.capacity = capacity
                facility.college = college
                facility.status = status
                if image:
                    facility.image = image
                facility.save()
            else:
                # Create
                facility = Facility.objects.create(
                    name=name,
                    type=facility_type,
                    capacity=capacity,
                    college=college,
                    status=status,
                    image=image
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Facility saved successfully',
                'facility': {
                    'id': facility.id,
                    'name': facility.name,
                    'image': facility.image.url if facility.image else '',
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def facility_delete(request, pk):
    """
    API endpoint to delete a facility.
    """
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            facility = Facility.objects.get(pk=pk)
            facility.delete()
            return JsonResponse({'success': True, 'message': 'Facility deleted successfully'})
        except Facility.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Facility not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
def delete_post(request, post_id):
    """
    API endpoint to delete a post by ID.
    Accepts POST requests with post ID and returns success JSON.
    """
    if request.method == 'POST':
        try:
            # Retrieve and delete the post
            post = Post.objects.get(id=post_id)
            post.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Post deleted successfully'
            })
        except Post.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Post not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)


# Program Management API Endpoints

@csrf_exempt
def program_list_create(request):
    """
    API endpoint to list all programs (GET) or create a new program (POST).
    GET: Returns JSON response with all programs.
    POST: Creates a new program and returns the created program data.
    """
    if request.method == 'GET':
        college = request.GET.get('college')
        if college:
            programs = Program.objects.filter(college__iexact=college)
        else:
            programs = Program.objects.all()
        programs_data = []
        
        for program in programs:
            program_dict = {
                'id': program.id,
                'title': program.title,
                'description': program.description,
                'level': program.level,
                'college': program.college,
                'duration': program.duration,
                'objectives': program.objectives,
                'dresscode_schedule': program.dresscode_schedule,
                'dresscode_images': program.dresscode_images or [],
                'vision': program.vision,
                'mission': program.mission,
                'image': program.image.url if program.image else '',
                'image2': program.image2.url if program.image2 else '',
                'status': program.status,
                'created_at': program.created_at.isoformat(),
                'updated_at': program.updated_at.isoformat(),
            }
            programs_data.append(program_dict)
        
        return JsonResponse({
            'success': True,
            'programs': programs_data
        })
    
    elif request.method == 'POST':
        try:
            # Extract data from POST request
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            level = request.POST.get('level', 'undergraduate')
            college = request.POST.get('college').lower() if request.POST.get('college') else None
            duration = request.POST.get('duration', '')
            objectives = request.POST.get('objectives', '')
            dresscode_schedule = request.POST.get('dresscode_schedule', '')
            vision = request.POST.get('vision', '')
            mission = request.POST.get('mission', '')
            status = request.POST.get('status', 'published')
            
            # Validate required fields
            if not title:
                return JsonResponse({
                    'success': False,
                    'error': 'Title is required'
                }, status=400)
            
            if not college:
                return JsonResponse({
                    'success': False,
                    'error': 'College is required'
                }, status=400)
            
            # Handle image upload if present
            image = request.FILES.get('image', None)
            image2 = request.FILES.get('image2', None)
            
            # Handle multiple dresscode images
            import json as _json
            dresscode_images = []
            new_dresscode_days = request.POST.get('new_dresscode_days')
            new_days_list = _json.loads(new_dresscode_days) if new_dresscode_days else []
            
            for idx, f in enumerate(request.FILES.getlist('dresscode_images')):
                from django.core.files.storage import default_storage
                path = default_storage.save(f'programs/dresscode/{f.name}', f)
                day = new_days_list[idx] if idx < len(new_days_list) else 'Monday'
                dresscode_images.append({
                    'url': default_storage.url(path),
                    'day': day
                })
            
            # Create new Program instance
            program = Program.objects.create(
                title=title,
                description=description,
                level=level,
                college=college,
                duration=duration,
                objectives=objectives,
                dresscode_schedule=dresscode_schedule,
                dresscode_images=dresscode_images,
                vision=vision,
                mission=mission,
                status=status,
                image=image,
                image2=image2
            )
            
            # Return success response with created program data
            return JsonResponse({
                'success': True,
                'message': 'Program created successfully',
                'program': {
                    'id': program.id,
                    'title': program.title,
                    'description': program.description,
                    'level': program.level,
                    'college': program.college,
                    'duration': program.duration,
                    'objectives': program.objectives,
                    'dresscode_schedule': program.dresscode_schedule,
                    'dresscode_images': program.dresscode_images or [],
                    'vision': program.vision,
                    'mission': program.mission,
                    'image': program.image.url if program.image else '',
                    'image2': program.image2.url if program.image2 else '',
                    'status': program.status,
                    'created_at': program.created_at.isoformat(),
                    'updated_at': program.updated_at.isoformat(),
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)


@csrf_exempt
def program_detail(request, pk):
    """
    API endpoint to retrieve (GET), update (PUT), or delete (DELETE) a specific program.
    GET: Returns the program data.
    PUT: Updates the program and returns updated data.
    DELETE: Deletes the program and returns success message.
    """
    try:
        program = Program.objects.get(pk=pk)
    except Program.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Program not found'
        }, status=404)
    
    if request.method == 'GET':
        # Retrieve program details
        program_dict = {
            'id': program.id,
            'title': program.title,
            'description': program.description,
            'level': program.level,
            'college': program.college,
            'duration': program.duration,
            'objectives': program.objectives,
            'dresscode_schedule': program.dresscode_schedule,
            'dresscode_images': program.dresscode_images or [],
            'vision': program.vision,
            'mission': program.mission,
            'image': program.image.url if program.image else '',
            'image2': program.image2.url if program.image2 else '',
            'status': program.status,
            'created_at': program.created_at.isoformat(),
            'updated_at': program.updated_at.isoformat(),
        }
        
        return JsonResponse({
            'success': True,
            'program': program_dict
        })
    
    elif request.method == 'PUT' or request.method == 'POST':
        # Handle both PUT and POST for update (some clients use POST for updates)
        try:
            # Extract data from request
            title = request.POST.get('title')
            description = request.POST.get('description')
            level = request.POST.get('level')
            college = request.POST.get('college')
            duration = request.POST.get('duration')
            objectives = request.POST.get('objectives')
            dresscode_schedule = request.POST.get('dresscode_schedule')
            vision = request.POST.get('vision')
            mission = request.POST.get('mission')
            status = request.POST.get('status')
            
            # Update fields if provided
            if title:
                program.title = title
            if description is not None:
                program.description = description
            if level:
                program.level = level
            if college:
                program.college = college
            if duration is not None:
                program.duration = duration
            if objectives is not None:
                program.objectives = objectives
            if dresscode_schedule is not None:
                program.dresscode_schedule = dresscode_schedule
            if vision is not None:
                program.vision = vision
            if mission is not None:
                program.mission = mission
            if status:
                program.status = status
            
            # Handle dresscode images (update list)
            import json as _json
            kept_existing = request.POST.get('kept_dresscode_images')
            if kept_existing:
                try:
                    # Update to only keep specified existing images
                    program.dresscode_images = _json.loads(kept_existing)
                except:
                    pass
            
            # Handle new dresscode images (append)
            new_dresscode_files = request.FILES.getlist('dresscode_images')
            new_dresscode_days = request.POST.get('new_dresscode_days')
            if new_dresscode_files:
                from django.core.files.storage import default_storage
                import json as _json
                new_days_list = _json.loads(new_dresscode_days) if new_dresscode_days else []
                
                existing = program.dresscode_images or []
                for idx, f in enumerate(new_dresscode_files):
                    path = default_storage.save(f'programs/dresscode/{f.name}', f)
                    day = new_days_list[idx] if idx < len(new_days_list) else 'Monday'
                    existing.append({
                        'url': default_storage.url(path),
                        'day': day
                    })
                program.dresscode_images = existing
            
            # Handle image upload if present
            if 'image' in request.FILES:
                program.image = request.FILES['image']
            if 'image2' in request.FILES:
                program.image2 = request.FILES['image2']
            
            program.save()
            
            # Return success response with updated program data
            return JsonResponse({
                'success': True,
                'message': 'Program updated successfully',
                'program': {
                    'id': program.id,
                    'title': program.title,
                    'description': program.description,
                    'level': program.level,
                    'college': program.college,
                    'duration': program.duration,
                    'objectives': program.objectives,
                    'dresscode_schedule': program.dresscode_schedule,
                    'dresscode_images': program.dresscode_images or [],
                    'vision': program.vision,
                    'mission': program.mission,
                    'image': program.image.url if program.image else '',
                    'image2': program.image2.url if program.image2 else '',
                    'status': program.status,
                    'created_at': program.created_at.isoformat(),
                    'updated_at': program.updated_at.isoformat(),
                }
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            program.delete()
            return JsonResponse({
                'success': True,
                'message': 'Program deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)
@csrf_exempt
@login_required(login_url='/super-admin-login/')
def get_announcements(request):
    """API endpoint to get all announcements"""
    try:
        announcements = Announcement.objects.all().order_by('-created_at')
        data = []
        for a in announcements:
            data.append({
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'priority': a.priority,
                'date': a.created_at.isoformat() if a.created_at else '',
                'status': 'active', # Placeholder
                'image': a.image.url if a.image else '',
                'target_audience': 'all' # Placeholder
            })
        return JsonResponse({'success': True, 'announcements': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def get_news(request):
    """API endpoint to get all news articles"""
    try:
        news = News.objects.all().order_by('-created_at')
        data = []
        for n in news:
            data.append({
                'id': n.id,
                'title': n.title,
                'content': n.content,
                'category': n.category,
                'date': n.created_at.isoformat() if n.created_at else '',
                'status': 'published', # Placeholder
                'image': n.image.url if n.image else '',
                'author': 'Super Admin' # Placeholder
            })
        return JsonResponse({'success': True, 'news': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_reply_inquiry(request, pk):
    """API endpoint to reply to an inquiry (Direct Message)"""
    if request.method == 'POST':
        try:
            inquiry = ContactMessage.objects.get(id=pk)
            message_text = request.POST.get('message')
            
            if not message_text:
                return JsonResponse({'success': False, 'error': 'Message is required'}, status=400)
            
            # Create the reply
            reply = InquiryReply.objects.create(
                inquiry=inquiry,
                sender="Super Admin", # Hardcoded for now
                message=message_text,
                is_sent_to_user=True
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Reply sent successfully',
                'reply': {
                    'id': reply.id,
                    'sender': reply.sender,
                    'message': reply.message,
                    'created_at': reply.created_at.isoformat()
                }
            })
        except ContactMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Inquiry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


# ─── Missing view functions (restored after accidental revert) ───

from django.http import Http404
from dashboard.models import AdminProfile, UniversityInfo, SiteContactInfo, PresidentProfile, NorsuHistory
from django.contrib.auth.models import User
import json


def news_preview(request):
    """Preview a news post before publishing."""
    return render(request, 'dashboard/news_detail.html', {'post': None, 'preview': True})


def static_news_detail(request, news_key):
    """Display a static news detail page by slug key."""
    return render(request, 'dashboard/news_detail.html', {'news_key': news_key})


def alumni_success_story_public_detail(request, story_id):
    """Public detail page for an alumni success story."""
    try:
        story = AlumniSuccessStory.objects.get(pk=story_id)
    except AlumniSuccessStory.DoesNotExist:
        raise Http404("Success story not found")
    return render(request, 'dashboard/alumni/home.html', {'story': story})


def college_dashboard_router(request, abbr):
    """Dynamic router for college pages by abbreviation."""
    college = College.objects.filter(abbreviation__iexact=abbr).first()
    if not college:
        raise Http404(f"College '{abbr}' not found")
    return render(request, 'dashboard/dashbordgeneric.html', {'college': college})


def _normalize_college_key(value):
    return (value or '').strip().lower()


def _get_admin_profile(user):
    try:
        return AdminProfile.objects.select_related('user').get(user=user)
    except AdminProfile.DoesNotExist:
        return None


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_university_info_list_create(request):
    """List or create university info entries."""
    if request.method == 'GET':
        entries = UniversityInfo.objects.all().order_by('-updated_at' if hasattr(UniversityInfo, 'updated_at') else '-id')
        return JsonResponse({'success': True, 'entries': [
            {'id': e.id, 'key': e.key, 'title': getattr(e, 'title', ''), 'content': e.content,
             'image': e.image.url if e.image else ''}
            for e in entries
        ]})
    elif request.method == 'POST':
        try:
            key = request.POST.get('key', '')
            content = request.POST.get('content', '')
            title = request.POST.get('title', '')
            image = request.FILES.get('image')
            entry_id = request.POST.get('id')

            if entry_id:
                entry = UniversityInfo.objects.get(pk=entry_id)
            else:
                entry = UniversityInfo(key=key)

            entry.content = content
            if hasattr(entry, 'title'):
                entry.title = title
            if image:
                entry.image = image
            entry.save()
            return JsonResponse({'success': True, 'id': entry.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_university_info_detail(request, pk):
    """Get or delete a university info entry."""
    try:
        entry = UniversityInfo.objects.get(pk=pk)
    except UniversityInfo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'success': True, 'entry': {
            'id': entry.id, 'key': entry.key, 'content': entry.content,
            'title': getattr(entry, 'title', ''), 'image': entry.image.url if entry.image else ''
        }})
    elif request.method == 'DELETE':
        entry.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_site_contact_info(request):
    """Get or update site contact info."""
    info = SiteContactInfo.objects.first()
    if request.method == 'GET':
        if not info:
            return JsonResponse({'success': True, 'data': {}})
        data = {}
        for field in info._meta.get_fields():
            if hasattr(field, 'attname'):
                val = getattr(info, field.attname, '')
                data[field.attname] = val
        return JsonResponse({'success': True, 'data': data})
    elif request.method == 'POST':
        try:
            body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            if not info:
                info = SiteContactInfo()
            for key, value in body.items():
                if hasattr(info, key) and key != 'id':
                    setattr(info, key, value)
            info.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_president_profile(request):
    """Get or update president profile."""
    profile = PresidentProfile.objects.first()
    if request.method == 'GET':
        if not profile:
            return JsonResponse({'success': True, 'data': {}})
        data = {
            'id': profile.id,
            'name': getattr(profile, 'name', ''),
            'title': getattr(profile, 'title', ''),
            'message': getattr(profile, 'message', ''),
            'image': profile.image.url if hasattr(profile, 'image') and profile.image else '',
        }
        return JsonResponse({'success': True, 'data': data})
    elif request.method == 'POST':
        try:
            if not profile:
                profile = PresidentProfile()
            profile.name = request.POST.get('name', getattr(profile, 'name', ''))
            profile.title = request.POST.get('title', getattr(profile, 'title', ''))
            profile.message = request.POST.get('message', getattr(profile, 'message', ''))
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_norsu_history(request):
    """Get or update NORSU history."""
    history = NorsuHistory.objects.first()
    if request.method == 'GET':
        if not history:
            return JsonResponse({'success': True, 'data': {}})
        data = {
            'id': history.id,
            'content': getattr(history, 'content', ''),
            'image': history.image.url if hasattr(history, 'image') and history.image else '',
        }
        return JsonResponse({'success': True, 'data': data})
    elif request.method == 'POST':
        try:
            if not history:
                history = NorsuHistory()
            history.content = request.POST.get('content', getattr(history, 'content', ''))
            if 'image' in request.FILES:
                history.image = request.FILES['image']
            history.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


def _superadmin_json_guard(request):
    """Return a JsonResponse if user is not a superadmin, else None."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Superadmin access required'}, status=403)
    return None


def get_dynamic_college_admin_config():
    """Build admin config from College model."""
    config = {}
    for c in College.objects.all():
        key = _normalize_college_key(c.abbreviation)
        config[key] = {
            'college_name': c.name,
            'label': f'{c.abbreviation.upper()} Administrator',
            'color': c.theme_color or '#2c7f76',
        }
    return config


def _build_admin_session(profile):
    college_key = _normalize_college_key(profile.college)
    config = get_dynamic_college_admin_config().get(college_key, {})
    college_color = config.get('color', '#2c7f76')
    try:
        college_obj = College.objects.get(abbreviation__iexact=college_key)
        if college_obj.theme_color:
            college_color = college_obj.theme_color
    except College.DoesNotExist:
        pass
    return {
        'college': college_key,
        'collegeFullName': config.get('college_name', college_key.upper()),
        'collegeColor': college_color,
        'name': config.get('label', f'{college_key.upper()} Administrator'),
        'username': profile.user.username,
        'loginTime': int(timezone.now().timestamp() * 1000),
        'sessionTimeout': 60 * 60 * 1000,
    }


def _generate_available_username(base_username):
    username = base_username
    counter = 2
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{counter}'
        counter += 1
    return username


def _ensure_college_admin_profiles():
    profiles_by_college = {
        _normalize_college_key(profile.college): profile
        for profile in AdminProfile.objects.select_related('user')
    }
    for college_key in get_dynamic_college_admin_config():
        if college_key in profiles_by_college:
            continue
        user = User.objects.create_user(
            username=_generate_available_username(f'{college_key}_admin'),
            is_staff=True,
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])
        profiles_by_college[college_key] = AdminProfile.objects.create(
            user=user, college=college_key,
        )
    return profiles_by_college


def _build_admin_account_snapshot(current_superadmin):
    profiles_by_college = _ensure_college_admin_profiles()
    accounts = [{
        'key': 'superadmin', 'role': 'superadmin', 'label': 'Super Admin',
        'college': '', 'collegeName': 'University-wide access',
        'exists': bool(current_superadmin),
        'username': current_superadmin.username if current_superadmin else '',
    }]
    for college_key, profile in sorted(profiles_by_college.items()):
        config = get_dynamic_college_admin_config().get(college_key, {})
        accounts.append({
            'key': college_key, 'role': 'college_admin',
            'label': config.get('label', f'{college_key.upper()} Admin'),
            'college': college_key,
            'collegeName': config.get('college_name', college_key.upper()),
            'exists': True, 'username': profile.user.username,
        })
    return accounts


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_admin_accounts(request):
    """List admin accounts (GET)."""
    guard = _superadmin_json_guard(request)
    if guard:
        return guard
    accounts = _build_admin_account_snapshot(request.user)
    return JsonResponse({'success': True, 'accounts': accounts})


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_admin_account_update(request, account_key):
    """Update username and/or password for an admin account (POST)."""
    guard = _superadmin_json_guard(request)
    if guard:
        return guard

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        body = json.loads(request.body) if request.content_type and 'json' in request.content_type else request.POST
        new_username = body.get('username', '').strip()
        new_password = body.get('password', '').strip()

        if not new_username and not new_password:
            return JsonResponse({'success': False, 'error': 'Please provide a username or password to update'}, status=400)

        if new_password and len(new_password) < 4:
            return JsonResponse({'success': False, 'error': 'Password must be at least 4 characters'}, status=400)

        if account_key == 'superadmin':
            # Update superadmin
            if new_username and new_username != request.user.username:
                if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
                    return JsonResponse({'success': False, 'error': 'Username already taken'}, status=400)
                request.user.username = new_username

            if new_password:
                request.user.set_password(new_password)

            request.user.save()

            if new_password:
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)

            return JsonResponse({'success': True, 'message': 'Super Admin credentials updated'})

        # College admin
        profile = AdminProfile.objects.filter(college__iexact=account_key).select_related('user').first()
        if not profile:
            return JsonResponse({'success': False, 'error': f'Admin for {account_key} not found'}, status=404)

        if new_username and new_username != profile.user.username:
            if User.objects.filter(username=new_username).exclude(pk=profile.user.pk).exists():
                return JsonResponse({'success': False, 'error': 'Username already taken'}, status=400)
            profile.user.username = new_username

        if new_password:
            profile.user.set_password(new_password)

        profile.user.save()
        return JsonResponse({'success': True, 'message': f'{account_key.upper()} admin credentials updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@login_required(login_url='/super-admin-login/')
def api_system_analytics(request):
    """Return system-wide analytics for the super admin dashboard."""
    guard = _superadmin_json_guard(request)
    if guard:
        return guard

    total_posts = Post.objects.count()
    total_alumni = Alumni.objects.count()
    total_colleges = College.objects.count()
    total_inquiries = ContactMessage.objects.count()
    total_programs = Program.objects.count()
    total_faculty = Faculty.objects.count()
    total_facilities = Facility.objects.count()
    total_achievements = Achievement.objects.count()

    # Per-college breakdown
    college_stats = []
    for college in College.objects.all():
        key = _normalize_college_key(college.abbreviation)
        college_stats.append({
            'abbreviation': college.abbreviation,
            'name': college.name,
            'posts': Post.objects.filter(college__iexact=key).count(),
            'alumni': Alumni.objects.filter(college__iexact=key).count(),
            'programs': Program.objects.filter(college__iexact=key).count(),
            'faculty': Faculty.objects.filter(college__iexact=key).count(),
            'facilities': Facility.objects.filter(college__iexact=key).count(),
            'achievements': Achievement.objects.filter(college__iexact=key).count(),
        })

    return JsonResponse({
        'success': True,
        'analytics': {
            'total_posts': total_posts,
            'total_alumni': total_alumni,
            'total_colleges': total_colleges,
            'total_inquiries': total_inquiries,
            'total_programs': total_programs,
            'total_faculty': total_faculty,
            'total_facilities': total_facilities,
            'total_achievements': total_achievements,
            'college_stats': college_stats,
        }
    })
