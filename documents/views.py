from rest_framework import viewsets, mixins, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from .models import Document, DocumentScan
from .serializers import (
    DocumentSerializer,
    DocumentWithScansSerializer,
    DocumentScanSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document operations.
    Requires authentication for all operations.
    Users can only access their own documents.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file_type', 'processed']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return documents for authenticated user only."""
        if self.request.user.is_anonymous:
            return Document.objects.none()
        return Document.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'retrieve':
            return DocumentWithScansSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['get'])
    def scans(self, request, pk=None):
        """
        Return all scans for a specific document
        """
        document = self.get_object()
        scans = document.scans.all()
        serializer = DocumentScanSerializer(scans, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Create a new document associated with the current user."""
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Ensure users can only delete their own documents."""
        document = self.get_object()
        if document.user != request.user:
            raise PermissionDenied("You cannot delete documents that don't belong to you.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def request_scan(self, request, pk=None):
        """Request a new scan for the document."""
        document = self.get_object()
        scan = DocumentScan.objects.create(
            document=document,
            status='pending'
        )
        serializer = DocumentScanSerializer(scan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentScanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document scan operations.
    Requires authentication for all operations.
    Users can only access scans of their own documents.
    """
    serializer_class = DocumentScanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['risk_level']
    ordering_fields = ['scan_date']
    ordering = ['-scan_date']
    
    def get_queryset(self):
        """Return scans for authenticated user's documents only."""
        if self.request.user.is_anonymous:
            return DocumentScan.objects.none()
        return DocumentScan.objects.filter(document__user=self.request.user)
    
    def perform_create(self, serializer):
        """Create a new scan after validating document ownership."""
        document = serializer.validated_data['document']
        if document.user != self.request.user:
            raise PermissionDenied("You can only scan documents that belong to you.")
        serializer.save()

    @action(detail=True, methods=['post'])
    def retry_scan(self, request, pk=None):
        """Retry a failed scan."""
        scan = self.get_object()
        if scan.status != 'failed':
            return Response(
                {"detail": "Only failed scans can be retried."},
                status=status.HTTP_400_BAD_REQUEST
            )
        scan.status = 'pending'
        scan.save()
        return Response(
            DocumentScanSerializer(scan).data,
            status=status.HTTP_200_OK
        ) 