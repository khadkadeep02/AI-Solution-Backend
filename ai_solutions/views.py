import json
from urllib import error, parse, request

from django.conf import settings
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import os
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


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if not user.is_staff and not user.is_superuser:
            raise serializers.ValidationError('Admin credentials are required to obtain a token.')
        return data


class AdminTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AdminTokenObtainPairSerializer


class AdminLoginSerializer(AdminTokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["refresh_token"] = data.pop("refresh")
        return data


class AdminLoginView(AdminTokenObtainPairView):
    serializer_class = AdminLoginSerializer


class AiAssistantRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=2000, trim_whitespace=True)
    max_words = serializers.IntegerField(
        min_value=20,
        max_value=300,
        required=False,
        default=settings.AI_ASSISTANT_MAX_WORDS,
    )


def _format_value(value):
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _join_fields(fields):
    parts = []
    for label, value in fields:
        formatted = _format_value(value)
        if formatted:
            parts.append(f"{label}: {formatted}")
    return "; ".join(parts)


def _format_section(title, rows):
    if not rows:
        return f"{title}: No records available."
    return f"{title}:\n" + "\n".join(f"- {row}" for row in rows)


def _build_company_context():
    services = [
        _join_fields([
            ("Title", service.title),
            ("Short description", service.short_description),
            ("Full description", service.full_description),
        ])
        for service in Service.objects.all()
    ]
    projects = [
        _join_fields([
            ("Title", project.title),
            ("Short description", project.short_description),
            ("Full description", project.full_description),
            ("Technologies", project.technologies),
            ("Client", project.client_name),
            ("Project URL", project.project_url),
        ])
        for project in Project.objects.all()
    ]
    team_members = [
        _join_fields([
            ("Name", member.name),
            ("Designation", member.designation),
            ("Bio", member.bio),
            ("LinkedIn", member.linkedin_url),
            ("GitHub", member.github_url),
        ])
        for member in TeamMember.objects.all()
    ]
    timeline = [
        _join_fields([
            ("Year", item.year),
            ("Title", item.title),
            ("Description", item.description),
        ])
        for item in CompanyTimeline.objects.all()
    ]
    events = [
        _join_fields([
            ("Title", event.title),
            ("Type", event.get_event_type_display()),
            ("Description", event.description),
            ("Location", event.location),
            ("Start", event.start_date),
            ("End", event.end_date),
            ("Registration URL", event.registration_url),
        ])
        for event in Event.objects.all()
    ]
    gallery = [
        _join_fields([
            ("Title", image.title),
            ("Category", image.category),
        ])
        for image in GalleryImage.objects.all()
    ]
    testimonials = [
        _join_fields([
            ("Client", testimonial.client_name),
            ("Company", testimonial.company),
            ("Designation", testimonial.designation),
            ("Rating", testimonial.rating),
            ("Review", testimonial.review),
        ])
        for testimonial in Testimonial.objects.all()
    ]
    metrics = [
        _join_fields([
            ("Name", metric.metric_name),
            ("Value", metric.metric_value),
            ("Percentage change", metric.percentage_change),
            ("Type", metric.get_metric_type_display()),
        ])
        for metric in DashboardMetric.objects.all()
    ]

    return "\n\n".join([
        _format_section("Services", services),
        _format_section("Projects", projects),
        _format_section("Team Members", team_members),
        _format_section("Company Timeline", timeline),
        _format_section("Events", events),
        _format_section("Gallery", gallery),
        _format_section("Testimonials", testimonials),
        _format_section("Dashboard Metrics", metrics),
    ])


def _build_system_prompt():
    company_context = _build_company_context()
    return (
        f"{settings.AI_ASSISTANT_SYSTEM_PROMPT}\n\n"
        "Company database context:\n"
        f"{company_context}"
    )


def _build_user_prompt(prompt, max_words):
    return (
        f"User question:\n{prompt}\n\n"
        "Answer concisely.\n"
        "Use at most 2-5 short sentences.\n"
        "Use bullet points when appropriate.\n"
        "Do not repeat information.\n"
        "If the answer is unknown, say so clearly."
    )


def _extract_gemini_text(payload):
    for candidate in payload.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        text_parts = [
            part.get("text", "").strip()
            for part in parts
            if part.get("text", "").strip()
        ]
        if text_parts:
            return "\n".join(text_parts)
    return ""


def _call_gemini(prompt, max_words):
    model = settings.GEMINI_MODEL
    model_path = model if model.startswith("models/") else f"models/{model}"
    encoded_model_path = parse.quote(model_path, safe="/")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"{encoded_model_path}:generateContent"
    )
    payload = {
        "systemInstruction": {
            "parts": [{"text": _build_system_prompt()}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": _build_user_prompt(prompt, max_words)}],
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": max(128, max_words * 2),
            "responseMimeType": "text/plain",
        },
    }
    body = json.dumps(payload).encode("utf-8")
    gemini_request = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": settings.GEMINI_API_KEY,
        },
        method="POST",
    )
    print(body)

    with request.urlopen(gemini_request, timeout=30) as response:
        response_payload = json.loads(response.read().decode("utf-8"))
    print(response_payload)
    return _extract_gemini_text(response_payload), response_payload


class AiAssistantView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AiAssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not settings.GEMINI_API_KEY:
            return Response(
                {"detail": "GEMINI_API_KEY is not configured on the server."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        prompt = serializer.validated_data["prompt"]
        max_words = serializer.validated_data["max_words"]

        try:
            answer, raw_payload = _call_gemini(prompt, max_words)
            print(answer)
        except error.HTTPError as exc:
            error_message = "Gemini API request failed."
            try:
                body = json.loads(exc.read().decode("utf-8"))
                error_message = body.get("error", {}).get("message", error_message)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
            return Response(
                {"detail": error_message},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except (TimeoutError, error.URLError):
            return Response(
                {"detail": "Gemini API is unavailable. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {"detail": "Gemini API returned an invalid response."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if not answer:
            finish_reason = ""
            candidates = raw_payload.get("candidates", [])
            if candidates:
                finish_reason = candidates[0].get("finishReason", "")
            return Response(
                {
                    "detail": "Gemini API returned no text response.",
                    "finish_reason": finish_reason,
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )


        return Response({
            "response": answer,
            "model": settings.GEMINI_MODEL,
            "max_words": max_words,
        })

from .serializers import (
    ServiceSerializer,
    ProjectSerializer,
    TeamMemberSerializer,
    CompanyTimelineSerializer,
    EventSerializer,
    GalleryImageSerializer,
    TestimonialSerializer,
    ContactInquirySerializer,
    DashboardMetricSerializer
)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer


class CompanyTimelineViewSet(viewsets.ModelViewSet):
    queryset = CompanyTimeline.objects.all()
    serializer_class = CompanyTimelineSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class GalleryImageViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer


class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer


class DashboardMetricViewSet(viewsets.ModelViewSet):
    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer
