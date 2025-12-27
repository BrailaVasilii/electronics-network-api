from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from decimal import Decimal
from .models import NetworkNode, Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'model', 'release_date']


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'node_type', 'supplier_link', 'city', 'level', 'debt', 'created_at']
    list_filter = ['city', 'level', 'node_type']
    search_fields = ['name', 'city', 'email']
    readonly_fields = ['level', 'created_at']
    actions = ['clear_debt']
    inlines = [ProductInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'node_type', 'email')
        }),
        ('Address', {
            'fields': ('country', 'city', 'street', 'house_number')
        }),
        ('Network Structure', {
            'fields': ('supplier', 'level')
        }),
        ('Financial', {
            'fields': ('debt',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def supplier_link(self, obj):
        """Return HTML link to supplier admin page"""
        if obj.supplier:
            url = reverse('admin:network_networknode_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return '-'
    
    supplier_link.short_description = 'Supplier'
    supplier_link.admin_order_field = 'supplier__name'
    
    def clear_debt(self, request, queryset):
        """Clear debt for selected nodes"""
        updated_count = queryset.update(debt=Decimal('0.00'))
        self.message_user(
            request,
            f'Successfully cleared debt for {updated_count} nodes.'
        )
    
    clear_debt.short_description = "Clear debt for selected nodes"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'release_date', 'network_node']
    list_filter = ['release_date', 'network_node']
    search_fields = ['name', 'model']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'model', 'release_date')
        }),
        ('Network Assignment', {
            'fields': ('network_node',)
        }),
    )
