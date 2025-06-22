from rest_framework import serializers
from .models import Document, DocumentScan, SensitiveInformation


class SensitiveInformationSerializer(serializers.ModelSerializer):
    """
    Serializer for sensitive information detected in documents
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = SensitiveInformation
        fields = [
            'id', 
            'type', 
            'type_display', 
            'confidence', 
            'location', 
            'count', 
            'redacted'
        ]


class DocumentScanSerializer(serializers.ModelSerializer):
    """
    Serializer for document scan results
    """
    sensitive_information = SensitiveInformationSerializer(many=True, read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    document = serializers.PrimaryKeyRelatedField(queryset=Document.objects.all())
    
    class Meta:
        model = DocumentScan
        fields = [
            'id', 
            'document', 
            'risk_level', 
            'risk_level_display', 
            'processed_file', 
            'processing_time',
            'scan_date', 
            'sensitive_information',
            'status',
            'results',
            'confidence_score'
        ]
        read_only_fields = ['document', 'scan_date', 'status', 'results', 'confidence_score']

    def validate_document(self, value):
        """Ensure the document belongs to the current user."""
        request = self.context.get('request')
        if request and request.user and value.user != request.user:
            raise serializers.ValidationError(
                "You can only scan documents that belong to you."
            )
        return value


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for document uploads and metadata
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 
            'user', 
            'title', 
            'file', 
            'file_type', 
            'file_type_display', 
            'processed',
            'created_at', 
            'updated_at',
            'file_size',
            'upload_date',
            'description'
        ]
        read_only_fields = ['processed', 'created_at', 'updated_at', 'file_size', 'upload_date']

    def get_file_size(self, obj):
        """Return file size in bytes."""
        try:
            return obj.file.size
        except:
            return 0

    def validate_file(self, value):
        """Validate file size and type."""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF, JPEG, and PNG files are allowed."
            )
        return value

    def create(self, validated_data):
        # Set the user to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocumentWithScansSerializer(DocumentSerializer):
    """
    Detailed document serializer that includes scan results
    """
    scans = DocumentScanSerializer(many=True, read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['scans'] 