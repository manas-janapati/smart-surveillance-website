import json
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Survey, Detection


class DetectionInline(admin.TabularInline):
    model = Detection
    extra = 0
    can_delete = False
    show_change_link = False

    readonly_fields = (
        "frame_id",
        "confidence",
        "latitude",
        "longitude",
    )

    classes = ["collapse"]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("id", "location_description", "uploaded_at")
    ordering = ("-uploaded_at",)

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []  # NO detections
        return [DetectionInline]

    def get_fields(self, request, obj=None):
        if obj is None:  # ADD page
            return (
                "location_description",
                "description",
                "jsonl_file",
            )
        return (
            "location_description",
            "description",
            "uploaded_at",
            "map_preview",
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("uploaded_at", "map_preview")
        return ()

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new and obj.jsonl_file:
            with obj.jsonl_file.open("r") as f:
                for line in f:
                    record = json.loads(line)

                    Detection.objects.create(
                        survey=obj,
                        frame_id=record["frame_id"],
                        latitude=record["gps"]["lat"],
                        longitude=record["gps"]["lon"],
                        confidence=record["confidence"],
                    )

            obj.jsonl_file.delete(save=False)
            obj.jsonl_file = None
            obj.save(update_fields=["jsonl_file"])

    def map_preview(self, obj):
        detections = obj.detections.all()
        if not detections.exists():
            return "No detections available."

        points = [
            {"lat": d.latitude, "lon": d.longitude, "conf": d.confidence}
            for d in detections
        ]

        map_id = f"map_survey_{obj.id}"

        return mark_safe(f"""
            <div style="margin-top:12px;">
                <div id="{map_id}"
                    style="
                        height:380px;
                        width:700px;
                        border:1px solid #d1d5db;
                        border-radius:6px;
                        background:#f9fafb;
                    ">
                </div>
            </div>

            <!-- Leaflet -->
            <link rel="stylesheet"
                href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

            <!-- Leaflet Fullscreen -->
            <link rel="stylesheet"
                href="https://unpkg.com/leaflet.fullscreen@1.6.0/Control.FullScreen.css" />
            <script src="https://unpkg.com/leaflet.fullscreen@1.6.0/Control.FullScreen.js"></script>

            <script>
                (function() {{
                    const points = {json.dumps(points)};
                    const mapId = "{map_id}";

                    function initMap() {{
                        const el = document.getElementById(mapId);
                        if (!el || el.dataset.loaded) return;

                        el.dataset.loaded = "true";

                        const street = L.tileLayer(
                            "https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",
                            {{ maxZoom: 19 }}
                        );

                        const satellite = L.tileLayer(
                            "https://server.arcgisonline.com/ArcGIS/rest/services/" +
                            "World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}",
                            {{ maxZoom: 19 }}
                        );

                        const map = L.map(mapId, {{
                            layers: [street],
                            fullscreenControl: true,
                            fullscreenControlOptions: {{
                                position: 'topright'
                            }}
                        }});

                        const bounds = [];

                        points.forEach(p => {{
                            const marker = L.marker([p.lat, p.lon]).addTo(map);
                            marker.bindPopup("Confidence: " + p.conf.toFixed(3));
                            bounds.push([p.lat, p.lon]);
                        }});

                        if (bounds.length) {{
                            map.fitBounds(bounds, {{ padding: [40, 40] }});
                        }}

                        L.control.layers(
                            {{
                                "Street": street,
                                "Satellite": satellite
                            }},
                            null,
                            {{ collapsed: false }}
                        ).addTo(map);

                        // Fix rendering after fullscreen toggle
                        map.on('fullscreenchange', function () {{
                            setTimeout(() => map.invalidateSize(), 300);
                        }});

                        setTimeout(() => map.invalidateSize(), 300);
                    }}

                    // Wait for Django admin layout
                    setTimeout(initMap, 500);
                }})();
            </script>
        """)
