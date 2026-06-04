from rest_framework import serializers
from .models import (
    Service,
    Project,
    TeamMember,
    CompanyTimeline,
    Event,
    GalleryImage,
    Testimonial,
    ContactInquiry,
    DashboardMetric
)


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = "__all__"


class CompanyTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyTimeline
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = "__all__"


class TestimonialSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Testimonial
        fields = "__all__"
    
    def get_image(self, obj):
        """Return image URL or default image if not provided"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        # Return default image URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri('/media/testimonials/default-avatar.png')
        return '/media/testimonials/default-avatar.png'


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = "__all__"


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = "__all__"