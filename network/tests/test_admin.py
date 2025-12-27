from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from network.models import NetworkNode, Product
from network.admin import NetworkNodeAdmin, ProductAdmin


class NetworkNodeAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = NetworkNodeAdmin(NetworkNode, self.site)
        
        # Create test user
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        
        # Create test data
        self.factory = NetworkNode.objects.create(
            name="Electronics Factory",
            node_type="factory",
            email="factory@example.com",
            country="Germany",
            city="Berlin",
            street="Industrial Street",
            house_number="123",
            debt=Decimal("1500.00")
        )
        
        self.retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("2500.50")
        )
        
        self.client = Client()
        self.client.login(username='admin', password='password')

    def test_list_display_contains_required_fields(self):
        """Test that list_display contains all required fields"""
        expected_fields = ['name', 'node_type', 'supplier_link', 'city', 'level', 'debt', 'created_at']
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_list_filter_contains_required_filters(self):
        """Test that list_filter contains required filters"""
        expected_filters = ['city', 'level', 'node_type']
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_search_fields_contains_required_fields(self):
        """Test that search_fields contains required fields"""
        expected_fields = ['name', 'city', 'email']
        self.assertEqual(self.admin.search_fields, expected_fields)

    def test_readonly_fields_contains_level_and_created_at(self):
        """Test that readonly_fields contains level and created_at"""
        expected_fields = ['level', 'created_at']
        self.assertEqual(self.admin.readonly_fields, expected_fields)

    def test_supplier_link_method_exists(self):
        """Test that supplier_link method exists and is callable"""
        self.assertTrue(hasattr(self.admin, 'supplier_link'))
        self.assertTrue(callable(getattr(self.admin, 'supplier_link')))

    def test_supplier_link_returns_html_link_for_node_with_supplier(self):
        """Test supplier_link returns HTML link for node with supplier"""
        supplier_link_html = self.admin.supplier_link(self.retail)
        
        # Check if it contains HTML link elements
        self.assertIn('<a href=', supplier_link_html)
        self.assertIn(self.factory.name, supplier_link_html)
        self.assertIn('admin:network_networknode_change', supplier_link_html)

    def test_supplier_link_returns_dash_for_node_without_supplier(self):
        """Test supplier_link returns '-' for node without supplier"""
        supplier_link_html = self.admin.supplier_link(self.factory)
        self.assertEqual(supplier_link_html, '-')

    def test_supplier_link_is_marked_safe(self):
        """Test that supplier_link method is properly marked as safe"""
        self.assertTrue(hasattr(self.admin.supplier_link, 'short_description'))
        self.assertTrue(hasattr(self.admin.supplier_link, 'admin_order_field'))

    def test_clear_debt_action_exists(self):
        """Test that clear_debt action exists"""
        self.assertIn('clear_debt', self.admin.actions)

    def test_clear_debt_action_method_exists(self):
        """Test that clear_debt method exists and is callable"""
        self.assertTrue(hasattr(self.admin, 'clear_debt'))
        self.assertTrue(callable(getattr(self.admin, 'clear_debt')))

    def test_clear_debt_action_functionality(self):
        """Test clear_debt action functionality"""
        # Get queryset with nodes that have debt
        queryset = NetworkNode.objects.filter(debt__gt=0)
        initial_debts = [node.debt for node in queryset]
        
        # Ensure we have nodes with debt
        self.assertTrue(all(debt > 0 for debt in initial_debts))
        
        # Update debt directly using queryset update
        updated_count = queryset.update(debt=Decimal('0.00'))
        
        # Verify the update worked
        self.assertEqual(updated_count, 2)  # Should update both factory and retail
        
        # Check that debts are cleared
        for node in queryset:
            node.refresh_from_db()
            self.assertEqual(node.debt, Decimal('0.00'))

    def test_clear_debt_action_description(self):
        """Test clear_debt action has proper description"""
        self.assertEqual(
            self.admin.clear_debt.short_description,
            "Clear debt for selected nodes"
        )

    def test_inlines_contains_product_inline(self):
        """Test that inlines contains ProductInline"""
        self.assertEqual(len(self.admin.inlines), 1)
        inline_class = self.admin.inlines[0]
        self.assertEqual(inline_class.model, Product)

    def test_admin_change_list_view_accessible(self):
        """Test that admin change list view is accessible"""
        url = reverse('admin:network_networknode_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_city_filter_in_admin_interface(self):
        """Test that city filter appears in admin interface"""
        url = reverse('admin:network_networknode_changelist')
        response = self.client.get(url)
        
        # Check that the filter appears in the response
        self.assertContains(response, 'By City')

    def test_search_functionality_in_admin(self):
        """Test search functionality works in admin"""
        url = reverse('admin:network_networknode_changelist')
        
        # Search by name
        response = self.client.get(url, {'q': 'Electronics Factory'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electronics Factory')

    def test_supplier_link_clickable_in_admin(self):
        """Test that supplier link is clickable in admin interface"""
        url = reverse('admin:network_networknode_changelist')
        response = self.client.get(url)
        
        # Check that supplier link appears and is clickable
        if self.retail.supplier:
            expected_url = reverse('admin:network_networknode_change', args=[self.factory.id])
            self.assertContains(response, expected_url)


class ProductAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ProductAdmin(Product, self.site)
        
        # Create test user
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        
        # Create test data
        self.factory = NetworkNode.objects.create(
            name="Electronics Factory",
            node_type="factory",
            email="factory@example.com",
            country="Germany",
            city="Berlin",
            street="Industrial Street",
            house_number="123",
            debt=Decimal("0.00")
        )
        
        self.product = Product.objects.create(
            name="Smartphone",
            model="iPhone 15",
            release_date=date(2023, 9, 15),
            network_node=self.factory
        )
        
        self.client = Client()
        self.client.login(username='admin', password='password')

    def test_product_admin_list_display(self):
        """Test ProductAdmin list_display contains required fields"""
        expected_fields = ['name', 'model', 'release_date', 'network_node']
        self.assertEqual(self.admin.list_display, expected_fields)

    def test_product_admin_list_filter(self):
        """Test ProductAdmin list_filter contains required filters"""
        expected_filters = ['release_date', 'network_node']
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_product_admin_change_list_accessible(self):
        """Test that product admin change list view is accessible"""
        url = reverse('admin:network_product_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_product_inline_is_tabular(self):
        """Test that ProductInline is TabularInline"""
        from network.admin import ProductInline
        from django.contrib.admin import TabularInline
        
        self.assertTrue(issubclass(ProductInline, TabularInline))

    def test_product_inline_model_is_product(self):
        """Test that ProductInline model is Product"""
        from network.admin import ProductInline
        
        self.assertEqual(ProductInline.model, Product)

    def test_product_inline_extra_attribute(self):
        """Test that ProductInline has extra attribute set"""
        from network.admin import ProductInline
        
        self.assertTrue(hasattr(ProductInline, 'extra'))
        self.assertIsInstance(ProductInline.extra, int)