from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from detections.models import Survey


@login_required
def surveys_api(request):
    surveys = Survey.objects.order_by("-uploaded_at")

    data = [
        {
            "id": s.id,
            "location": s.location_description,
            "uploaded_at": s.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        }
        for s in surveys
    ]

    return JsonResponse(data, safe=False)


@login_required
def survey_detail_api(request, survey_id):
    survey = Survey.objects.get(id=survey_id)

    detections = [
        {
            "lat": d.latitude,
            "lon": d.longitude,
            "confidence": d.confidence,
        }
        for d in survey.detections.all()
    ]

    return JsonResponse({
        "id": survey.id,
        "location": survey.location_description,
        "uploaded_at": survey.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        "detections": detections,
    })
