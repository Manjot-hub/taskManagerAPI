from rest_framework import viewsets, generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Task
from .serializers import TaskSerializer, RegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwner
from django.shortcuts import render
from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache

def index(request):
    return render(request, 'index.html')

class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        self._invalidate_cache()

    def perform_update(self, serializer):
        serializer.save()
        self._invalidate_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self._invalidate_cache()

    def list(self, request, *args, **kwargs):
        cache_key = f'tasks_user_{request.user.id}_page_{request.query_params.get("page", 1)}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 5)  # cache for 5 minutes
        return response

    def _invalidate_cache(self):
        # clear all cached pages for this user when data changes
        pattern = f'tasks_user_{self.request.user.id}_page_*'
        keys = cache.keys(pattern)
        cache.delete_many(keys)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset email sent.'})


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset successful.'})