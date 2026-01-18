from django.db import models


class Survey(models.Model):
    location_description = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Used ONLY during creation
    jsonl_file = models.FileField(
        upload_to="uploads/",
        blank=True,
        null=True,
        help_text="Upload detection .jsonl file (only for new survey)"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey {self.id} - {self.location_description}"


class Detection(models.Model):
    survey = models.ForeignKey(
        Survey,
        related_name="detections",
        on_delete=models.CASCADE
    )

    frame_id = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    confidence = models.FloatField()

    def __str__(self):
        return f"Survey-{self.survey.id}"
