"""
Core views for app
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(["GET"])
def health_check(request):
    """returns successful rersponse"""
    return Response({"healthy": True}, status.HTTP_200_OK)