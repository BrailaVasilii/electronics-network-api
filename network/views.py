from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkNode
from .serializers import NetworkNodeSerializer
from .permissions import IsActiveStaff


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for NetworkNode with full CRUD operations.
    
    Provides:
    - List, Create, Retrieve, Update, Delete operations
    - Filtering by country, city, level
    - Search by name, email
    - Permission restricted to active staff users
    - Debt field protection (cannot be updated via API)
    """
    
    queryset = NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country', 'city', 'level']
    search_fields = ['name', 'email']
    
    def perform_update(self, serializer):
        """
        Override perform_update to ensure debt is never updated via API.
        This provides an additional layer of protection beyond the read-only serializer field.
        """
        # Get the current instance
        instance = self.get_object()
        
        # Store the current debt value
        current_debt = instance.debt
        
        # Save the instance with validated data
        serializer.save()
        
        # Ensure debt hasn't changed (extra safety measure)
        updated_instance = self.get_object()
        if updated_instance.debt != current_debt:
            # If debt somehow changed, revert it
            updated_instance.debt = current_debt
            updated_instance.save(update_fields=['debt'])
    
    def perform_create(self, serializer):
        """
        Override perform_create to ensure debt is set to default value.
        """
        # Remove debt from any potential validated data
        if hasattr(serializer, 'validated_data') and 'debt' in serializer.validated_data:
            serializer.validated_data.pop('debt')
        
        serializer.save()
