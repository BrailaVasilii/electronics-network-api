from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class NetworkNode(models.Model):
    NODE_TYPE_CHOICES = [
        ('factory', 'Factory'),
        ('retail', 'Retail Network'),
        ('entrepreneur', 'Individual Entrepreneur'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Name')
    node_type = models.CharField(
        max_length=12, 
        choices=NODE_TYPE_CHOICES, 
        verbose_name='Node Type'
    )
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Country')
    city = models.CharField(max_length=100, verbose_name='City')
    street = models.CharField(max_length=150, verbose_name='Street')
    house_number = models.CharField(max_length=10, verbose_name='House Number')
    supplier = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='supplied_nodes',
        verbose_name='Supplier'
    )
    level = models.IntegerField(
        default=0, 
        editable=False,
        verbose_name='Network Level'
    )
    debt = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Debt'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    
    class Meta:
        verbose_name = 'Network Node'
        verbose_name_plural = 'Network Nodes'
        ordering = ['level', 'name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate the model data"""
        super().clean()
        
        # Prevent self-reference
        if self.supplier == self:
            raise ValidationError("Node cannot be supplier to itself")
        
        # Check for circular references
        if self.supplier and self._check_circular_reference():
            raise ValidationError("Circular reference detected")
        
        # Calculate level and check maximum depth
        calculated_level = self._calculate_level()
        if calculated_level > 2:  # Maximum 3 levels (0, 1, 2)
            raise ValidationError("Maximum network depth of 3 levels exceeded")
    
    def _check_circular_reference(self):
        """Check if setting this supplier would create a circular reference"""
        current_supplier = self.supplier
        visited = set()
        
        while current_supplier:
            if current_supplier.id == self.id:
                return True
            if current_supplier.id in visited:
                break
            visited.add(current_supplier.id)
            current_supplier = current_supplier.supplier
        
        return False
    
    def _calculate_level(self):
        """Calculate the hierarchy level based on supplier chain"""
        if not self.supplier:
            return 0
        
        level = 0
        current_supplier = self.supplier
        visited = set()
        
        while current_supplier:
            level += 1
            if current_supplier.id in visited:
                # Circular reference detected
                break
            visited.add(current_supplier.id)
            current_supplier = current_supplier.supplier
        
        return level
    
    def save(self, *args, **kwargs):
        """Override save to auto-calculate level"""
        # Calculate level before saving
        self.level = self._calculate_level()
        
        # Call full_clean to trigger validation
        if not kwargs.get('skip_validation', False):
            self.full_clean()
        
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Product Name')
    model = models.CharField(max_length=100, verbose_name='Model')
    release_date = models.DateField(verbose_name='Release Date')
    network_node = models.ForeignKey(
        NetworkNode,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Network Node'
    )
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name', 'model']
    
    def __str__(self):
        return f"{self.name} - {self.model}"
