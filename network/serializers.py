from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """Simple serializer for nested product representation"""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'model', 'release_date']


class SupplierSerializer(serializers.ModelSerializer):
    """Simple serializer for nested supplier representation"""
    
    class Meta:
        model = NetworkNode
        fields = ['id', 'name']


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Serializer for NetworkNode with nested relationships and read-only debt"""
    
    supplier = SupplierSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    debt = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'email', 'country', 'city', 
            'street', 'house_number', 'supplier', 'level', 'debt', 
            'created_at', 'products'
        ]
        read_only_fields = ['level', 'created_at']
    
    def create(self, validated_data):
        """Create a new NetworkNode instance"""
        # Ensure debt is never set from validated_data (extra safety)
        validated_data.pop('debt', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update NetworkNode instance, ensuring debt cannot be modified"""
        # Remove debt from validated_data if present (extra safety)
        validated_data.pop('debt', None)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """Customize the representation to handle supplier field"""
        data = super().to_representation(instance)
        
        # Handle supplier field for create/update requests
        request = self.context.get('request')
        if request and hasattr(request, 'data') and 'supplier' in request.data:
            # For write operations, we need to handle supplier as ID
            supplier_id = request.data.get('supplier')
            if supplier_id:
                try:
                    supplier = NetworkNode.objects.get(id=supplier_id)
                    data['supplier'] = SupplierSerializer(supplier).data
                except NetworkNode.DoesNotExist:
                    data['supplier'] = None
        
        return data
    
    def to_internal_value(self, data):
        """Handle supplier field as ID in input data"""
        # Create a copy of data to avoid modifying the original
        data_copy = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Handle supplier as ID
        if 'supplier' in data_copy:
            supplier_id = data_copy.get('supplier')
            if supplier_id:
                try:
                    supplier = NetworkNode.objects.get(id=supplier_id)
                    data_copy['supplier'] = supplier
                except (NetworkNode.DoesNotExist, ValueError, TypeError):
                    raise serializers.ValidationError({
                        'supplier': 'Invalid supplier ID'
                    })
            else:
                data_copy['supplier'] = None
        
        # Remove supplier from data_copy for parent processing
        if 'supplier' in data_copy:
            supplier_value = data_copy.pop('supplier')
        else:
            supplier_value = None
        
        # Get validated data from parent
        validated_data = super().to_internal_value(data_copy)
        
        # Add supplier back to validated data
        if supplier_value is not None:
            validated_data['supplier'] = supplier_value
        
        return validated_data