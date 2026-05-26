from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

class Alumni(models.Model):
    LATIN_HONORS_CHOICES = [
        ('', 'No Latin Honor'),
        ('Summa Cum Laude', 'Summa Cum Laude'),
        ('Magna Cum Laude', 'Magna Cum Laude'),
        ('Cum Laude', 'Cum Laude'),
    ]
    name = models.CharField(max_length=255)
    latin_honors = models.CharField(max_length=50, choices=LATIN_HONORS_CHOICES, blank=True, default='')
    batch = models.CharField(max_length=10)
    course = models.CharField(max_length=255)
    college = models.CharField(max_length=50, default='all')
    position = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='alumni/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Alumni'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.batch}"


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=255)
    department = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.full_name} - {self.subject}"


class AlumniNews(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='alumni/news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='published', choices=[('draft', 'Draft'), ('published', 'Published'), ('scheduled', 'Scheduled')])
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically publish (leave blank for immediate)")
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically hide/expire the news")

    class Meta:
        verbose_name_plural = 'Alumni News'

    def __str__(self):
        return self.title

    def is_live(self):
        """Return True if this news item should currently be visible."""
        from django.utils import timezone
        now = timezone.now()
        if self.status == 'draft':
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True


class AlumniEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='alumni/events/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='published', choices=[('draft', 'Draft'), ('published', 'Published')])
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically publish")
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically hide/expire")

    class Meta:
        verbose_name_plural = 'Alumni Events'

    def __str__(self):
        return self.title

    def is_live(self):
        from django.utils import timezone
        now = timezone.now()
        if self.status == 'draft':
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True


class AlumniAbout(models.Model):
    title = models.CharField(max_length=255, default='The NORSU-BSC Alumni Association')
    content = models.TextField()
    vision = models.TextField(default='A globally recognized state university.')
    mission = models.TextField()
    image = models.ImageField(upload_to='alumni/about/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Alumni About'

    def __str__(self):
        return self.title


class College(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=20)
    dean = models.CharField(max_length=255)
    total_students = models.IntegerField(default=0)
    programs_offered = models.IntegerField(default=0)
    qualified_instructors = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, help_text="List of colleges/departments under this college")
    hero_description = models.TextField(blank=True, help_text="Text for the hero section (ABOUT COLLEGE)")
    about = models.TextField(blank=True, help_text="About the college section (ABOUT CAF)")
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    goals = models.JSONField(default=list, blank=True, help_text="Mnemonic goals (e.g., C-A-F)")
    theme_color = models.CharField(max_length=20, default='#0078d4', help_text="Theme color for the college (e.g. #2c7f76)")
    image = models.ImageField(upload_to='colleges/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class AdminProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile',
    )
    college = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['college']
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        return f"{self.college.upper()} Admin ({self.user.username})"


class Faculty(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('onleave', 'On Leave'),
        ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    college = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    image = models.ImageField(upload_to='faculty/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Faculty'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.college}"


class Facility(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True)
    capacity = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='facilities/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Facilities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.college}"


class News(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('event', 'Event'),
        ('academic', 'Academic'),
        ('sports', 'Sports'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AcademicCalendar(models.Model):
    title = models.CharField(max_length=255, default='Academic Calendar')
    academic_year = models.CharField(max_length=50, default='2025-2026')
    description = models.TextField(blank=True)
    images = models.JSONField(default=list, blank=True)  # List of image URLs
    pdf_file = models.FileField(upload_to='calendar/pdf/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Academic Calendar'

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class UniversityInfo(models.Model):
    general_mandate = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision_image = models.ImageField(upload_to='university-info/', blank=True, null=True)
    mission_image = models.ImageField(upload_to='university-info/', blank=True, null=True)
    strategic_goals = models.TextField(blank=True)
    core_values = models.TextField(blank=True)
    quality_policy = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'University Information'

    def __str__(self):
        return f"University Information #{self.pk}"


class SiteContactInfo(models.Model):
    office_name = models.CharField(max_length=255, default='NORSU BSC')
    address_label = models.CharField(max_length=100, default='Address')
    address_text = models.TextField(default='Bayawan City Campus\nNegros Oriental, 6221')
    phone_label = models.CharField(max_length=100, default='Trunkline')
    phone_number = models.CharField(max_length=100, default='(035) 225-4247')
    email_label = models.CharField(max_length=100, default='Direct Email')
    email_address = models.EmailField(default='norsu_bsc@norsu.edu.ph')
    inquiry_title = models.CharField(max_length=255, default='Direct Inquiry')
    inquiry_description = models.TextField(
        default='Send a message directly to our campus administration. All inquiries are processed through our central communications portal.'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at', '-created_at']
        verbose_name = 'Site Contact Information'
        verbose_name_plural = 'Site Contact Information'

    def __str__(self):
        return f"Site Contact Information #{self.pk}"


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('news', 'News'),
        ('update', 'Update'),
        ('alumni', 'Alumni'),
        ('award', 'Award'),
        ('general', 'General Post'),
    ]

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('event', 'Event'),
        ('academic', 'Academic'),
        ('sports', 'Sports'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='general')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    college = models.CharField(max_length=50, default='all')
    target_audience = models.CharField(max_length=50, default='all')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically publish")
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically hide/expire")
    author = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.post_type})"

    def is_live(self):
        """Return True if this post should currently be visible."""
        now = timezone.now()
        if self.status in ['draft', 'archived']:
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        import re
        if self.content:
            img_match = re.search(r'<img[^>]+src="([^">]+)"', self.content)
            if img_match:
                return img_match.group(1)
        return ""


class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('sports', 'Sports'),
        ('research', 'Research'),
        ('community', 'Community Service'),
        ('arts', 'Arts & Culture'),
        ('leadership', 'Leadership'),
        ('international', 'International'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    college = models.CharField(max_length=50, default='all')
    recipient = models.CharField(max_length=255, blank=True, null=True)
    achievement_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_highlighted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_live(self):
        """Return True if this achievement should currently be visible."""
        now = timezone.now()
        if self.status in ['draft', 'archived']:
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        import re
        if self.description:
            img_match = re.search(r'<img[^>]+src="([^">]+)"', self.description)
            if img_match:
                return img_match.group(1)
        return ""

    def __str__(self):
        return self.title


class AlumniSuccessStory(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
        ('archived', 'Archived'),
    ]

    alumni_name = models.CharField(max_length=255)
    achievement = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='alumni/success_stories/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    scheduled_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically publish")
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When to automatically hide/expire")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Alumni Success Stories'
        ordering = ['-created_at']

    def is_live(self):
        """Return True if this success story should currently be visible."""
        now = timezone.now()
        if self.status in ['draft', 'archived']:
            return False
        if self.scheduled_at and now < self.scheduled_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        return True

    @property
    def display_image_url(self):
        if self.image:
            return self.image.url
        import re
        if self.description:
            img_match = re.search(r'<img[^>]+src="([^">]+)"', self.description)
            if img_match:
                return img_match.group(1)
        return ""

    def __str__(self):
        return f"{self.alumni_name} - {self.achievement}"


class MediaUpload(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='alumni_media/')
    year = models.IntegerField()
    college = models.CharField(max_length=255)
    uploaded_by = models.CharField(max_length=255, blank=True, null=True)  # Alumni name
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Media Uploads'

    def __str__(self):
        return f"{self.title} - {self.approval_status}"


class Program(models.Model):
    LEVEL_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('certificate', 'Certificate'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, default='undergraduate')
    college = models.CharField(max_length=50)
    college_ref = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='programs',
        blank=True,
        null=True,
    )
    duration = models.CharField(max_length=100, blank=True)
    objectives = models.TextField(blank=True, null=True)  # kept for backward compat
    dresscode_schedule = models.TextField(blank=True, null=True)
    dresscode_images = models.JSONField(blank=True, null=True, default=list)  # list of image paths
    vision = models.TextField(blank=True, null=True)
    mission = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='programs/', blank=True, null=True) # Primary image
    image2 = models.ImageField(upload_to='programs/', blank=True, null=True) # Secondary image
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def _sync_college_fields(self):
        if self.college_ref_id:
            self.college = (self.college_ref.abbreviation or '').strip().lower()
            return

        college_key = (self.college or '').strip().lower()
        if not college_key:
            return

        college_obj = College.objects.filter(abbreviation__iexact=college_key).first()
        if college_obj:
            self.college_ref = college_obj
            self.college = college_obj.abbreviation.lower()

    @staticmethod
    def _sync_program_counts(*college_ids):
        valid_ids = {college_id for college_id in college_ids if college_id}
        for college_id in valid_ids:
            College.objects.filter(pk=college_id).update(
                programs_offered=Program.objects.filter(college_ref_id=college_id).count()
            )

    def save(self, *args, **kwargs):
        previous_college_ref_id = None
        if self.pk:
            previous_college_ref_id = (
                Program.objects.filter(pk=self.pk)
                .values_list('college_ref_id', flat=True)
                .first()
            )

        self._sync_college_fields()
        super().save(*args, **kwargs)
        self._sync_program_counts(previous_college_ref_id, self.college_ref_id)

    def delete(self, *args, **kwargs):
        college_ref_id = self.college_ref_id
        super().delete(*args, **kwargs)
        self._sync_program_counts(college_ref_id)


class InquiryReply(models.Model):
    inquiry = models.ForeignKey(ContactMessage, on_delete=models.CASCADE, related_name='replies')
    sender = models.CharField(max_length=255) # or models.ForeignKey(User)
    message = models.TextField()
    is_sent_to_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to {self.inquiry.subject} by {self.sender}"


class PresidentProfile(models.Model):
    name = models.CharField(max_length=255, default='DR. NOEL MARJON E. YASI')
    role = models.CharField(max_length=255, default='University President')
    caption = models.TextField(blank=True, default='Information will be updated soon.')
    image = models.ImageField(upload_to='president/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'President Profile'
        verbose_name_plural = 'President Profiles'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.role}"


class NorsuHistory(models.Model):
    title = models.CharField(max_length=255, default='NORSU HISTORY')
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'NORSU History'
        verbose_name_plural = 'NORSU History'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
