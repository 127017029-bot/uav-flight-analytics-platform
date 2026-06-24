from django.contrib import admin
from .models import MLModel, MLPrediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    """Admin configuration for ML model registry."""
    list_display = [
        'name', 'version', 'model_type', 'is_active',
        'accuracy', 'f1_score', 'trained_at', 'created_at',
    ]
    list_filter = ['model_type', 'is_active']
    search_fields = ['name', 'description']


@admin.register(MLPrediction)
class MLPredictionAdmin(admin.ModelAdmin):
    """Admin configuration for ML prediction records."""
    list_display = [
        'drone', 'prediction_type', 'prediction_value',
        'prediction_label', 'confidence_score', 'created_at',
    ]
    list_filter = ['prediction_type']
    search_fields = ['prediction_label']
    date_hierarchy = 'created_at'
