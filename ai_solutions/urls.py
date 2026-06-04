from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter

from .views import (
    ServiceViewSet,
    ProjectViewSet,
    TeamMemberViewSet,
    CompanyTimelineViewSet,
    EventViewSet,
    GalleryImageViewSet,
    TestimonialViewSet,
    ContactInquiryViewSet,
    DashboardMetricViewSet,
    AiAssistantView,
    AdminLoginView,
    AdminTokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

router.register(r"services", ServiceViewSet, basename="services")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"team-members", TeamMemberViewSet, basename="team-members")
router.register(r"timeline", CompanyTimelineViewSet, basename="timeline")
router.register(r"events", EventViewSet, basename="events")
router.register(r"gallery", GalleryImageViewSet, basename="gallery")
router.register(r"testimonials", TestimonialViewSet, basename="testimonials")
router.register(r"inquiries", ContactInquiryViewSet, basename="inquiries")
router.register(r"dashboard-metrics", DashboardMetricViewSet, basename="dashboard-metrics")

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API Endpoints
    path("api/", include(router.urls)),
    path("api/ai/ask/", AiAssistantView.as_view(), name="ai_assistant"),
    path("api/admin/login/", AdminLoginView.as_view(), name="admin_login"),
    path("api/token/", AdminTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# Media & Static Files
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
