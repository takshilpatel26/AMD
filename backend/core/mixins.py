"""
Custom Mixins - Reusable view mixins
"""
from rest_framework.response import Response
from rest_framework import status


class SuccessResponseMixin:
    """
    Mixin to provide consistent success responses
    """
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Return standardized success response
        """
        response_data = {
            'success': True,
            'message': message
        }
        
        if data is not None:
            response_data['data'] = data
        
        return Response(response_data, status=status_code)


class TimestampFilterMixin:
    """
    Mixin to add timestamp-based filtering to viewsets
    """
    def filter_by_date_range(self, queryset, start_date, end_date, field='created_at'):
        """
        Filter queryset by date range
        """
        if start_date:
            queryset = queryset.filter(**{f'{field}__gte': start_date})
        if end_date:
            queryset = queryset.filter(**{f'{field}__lte': end_date})
        return queryset


class UserFilterMixin:
    """
    Mixin to filter queryset by current user
    """
    def get_queryset(self):
        """
        Return queryset filtered by current user
        """
        queryset = super().get_queryset()
        if hasattr(self, 'filter_user_field'):
            return queryset.filter(**{self.filter_user_field: self.request.user})
        return queryset.filter(user=self.request.user)
