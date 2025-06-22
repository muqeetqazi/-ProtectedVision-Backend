from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is None:
        # If there's an unhandled exception, create a custom response
        response = Response({
            'error': str(exc),
            'detail': 'An unexpected error occurred'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Add more information to the response
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            response.data = {
                'error': 'Validation Error',
                'detail': exc.detail
            }
        else:
            response.data = {
                'error': str(exc.detail),
                'detail': str(exc.detail)
            }

    # Add error code to response
    if response is not None:
        response.data['status_code'] = response.status_code

    return response 