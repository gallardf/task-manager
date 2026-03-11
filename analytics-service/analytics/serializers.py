from rest_framework import serializers


class StatusSummarySerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class UserSummarySerializer(serializers.Serializer):
    username = serializers.CharField(allow_null=True)
    count = serializers.IntegerField()
