from rest_framework import serializers
from .models import MLModel, MLPrediction


class MLModelSerializer(serializers.ModelSerializer):
    """Serializer for ML model registry entries."""
    type_display = serializers.CharField(source='get_model_type_display', read_only=True)

    class Meta:
        model = MLModel
        fields = '__all__'


class MLPredictionSerializer(serializers.ModelSerializer):
    """Serializer for ML prediction records."""
    type_display = serializers.CharField(source='get_prediction_type_display', read_only=True)
    drone_name = serializers.CharField(source='drone.name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True, default=None)

    class Meta:
        model = MLPrediction
        fields = '__all__'
