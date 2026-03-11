import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from detections.models import Survey, Detection


# =========================
# WORKER DASHBOARD APIS
# =========================

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


# =========================
# EDGE DEVICE APIs
# =========================

@csrf_exempt
def start_survey(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body or "{}")

    survey = Survey.objects.create(
        location_description=data.get("location", "Highway Survey"),
        description=data.get("description", "")
    )

    return JsonResponse({
        "survey_id": survey.id
    })


@csrf_exempt
def ingest_detection(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    survey = Survey.objects.get(id=data["survey_id"])

    Detection.objects.create(
        survey=survey,
        frame_id=data["frame_id"],
        latitude=data["gps"]["lat"],
        longitude=data["gps"]["lon"],
        confidence=data["confidence"],
    )

    return JsonResponse({"status": "saved"})