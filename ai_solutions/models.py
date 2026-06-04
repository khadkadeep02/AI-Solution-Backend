from django.db import models
from django.db import models
from django.utils.text import slugify
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Service(TimeStampedModel):
    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )
    image = models.ImageField(
                upload_to="services/",
                blank=True,
                null=True
            )
    short_description = models.TextField()

    full_description = models.TextField()

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

class Project(TimeStampedModel):

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    image = models.ImageField(
        upload_to="projects/"
    )

    short_description = models.TextField()

    full_description = models.TextField()

    technologies = models.JSONField(
        default=list,
        blank=True
    )

    client_name = models.CharField(
        max_length=255,
        blank=True
    )

    project_url = models.URLField(
        blank=True,
        null=True
    )
    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TeamMember(models.Model):

    name = models.CharField(max_length=255)

    designation = models.CharField(
        max_length=255
    )

    bio = models.TextField()

    image = models.ImageField(
        upload_to="team/"
    )

    linkedin_url = models.URLField(
        blank=True,
        null=True
    )

    github_url = models.URLField(
        blank=True,
        null=True
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.name


class CompanyTimeline(models.Model):

    year = models.PositiveIntegerField()

    title = models.CharField(max_length=255)

    description = models.TextField()

    display_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.year} - {self.title}"


class Event(TimeStampedModel):

    EVENT_TYPES = (
        ("WEBINAR", "Webinar"),
        ("WORKSHOP", "Workshop"),
        ("CONFERENCE", "Conference"),
        ("MEETUP", "Meetup"),
        ("TRAINING", "Training"),
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField()

    location = models.CharField(max_length=255)

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    image = models.ImageField(
        upload_to="events/"
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES
    )

    registration_url = models.URLField(
        blank=True,
        null=True
    )
    class Meta:
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):

    title = models.CharField(max_length=255)

    image = models.ImageField(
        upload_to="gallery/"
    )

    category = models.CharField(
        max_length=100
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title



class Testimonial(models.Model):

    client_name = models.CharField(
        max_length=255
    )

    company = models.CharField(
        max_length=255
    )

    designation = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to="testimonials/",
        blank=True,
        null=True,
        default="testimonials/default-avatar.png"
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    review = models.TextField()

    def __str__(self):
        return self.client_name


class ContactInquiry(TimeStampedModel):

    STATUS_CHOICES = (
        ("NEW", "New"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    )

    full_name = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=50
    )

    company = models.CharField(
        max_length=255,
        blank=True
    )

    country = models.CharField(
        max_length=100
    )

    designation = models.CharField(
        max_length=255,
        blank=True
    )

    project_description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NEW"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"



class DashboardMetric(models.Model):

    METRIC_TYPES = (
        ("COUNTER", "Counter"),
        ("PERCENTAGE", "Percentage"),
        ("REVENUE", "Revenue"),
        ("TRAFFIC", "Traffic"),
    )

    metric_name = models.CharField(
        max_length=255
    )

    metric_value = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    percentage_change = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    metric_type = models.CharField(
        max_length=50,
        choices=METRIC_TYPES
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.metric_name