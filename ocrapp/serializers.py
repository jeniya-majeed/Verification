from rest_framework import serializers

class VerificationSerializer(serializers.Serializer):
    source_file = serializers.FileField()
    target_file = serializers.FileField()