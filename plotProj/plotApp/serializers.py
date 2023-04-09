from rest_framework import serializers

class CSVInputSerializer(serializers.Serializer):
    file = serializers.FileField()
