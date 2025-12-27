from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from network.models import NetworkNode, Product


class NetworkNodeAPITest(APITestCase):
    def setUp(self):
        # Create different types of users
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='password',
            is_staff=True,
            is_active=True
        )
        
        self.non_staff_user = User.objects.create_user(
            username='regular',
            email='regular@example.com', 
            password='password',
            is_staff=False,
            is_active=True
        )
        
        self.inactive_staff_user = User.objects.create_user(
            username='inactive_staff',
            email='inactive@example.com',
            password='password',
            is_staff=True,
            is_active=False
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
        
        self.us_retail = NetworkNode.objects.create(
            name="US Electronics Store",
            node_type="retail",
            email="us_store@example.com",
            country="USA",
            city="New York",
            street="Main Street",
            house_number="789",
            supplier=self.factory,
            debt=Decimal("3000.00")
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name="Smartphone",
            model="iPhone 15",
            release_date=date(2023, 9, 15),
            network_node=self.factory
        )
        
        self.product2 = Product.objects.create(
            name="Laptop",
            model="MacBook Pro",
            release_date=date(2023, 10, 30),
            network_node=self.factory
        )
        
        self.list_url = reverse('networknode-list')
        self.detail_url = lambda pk: reverse('networknode-detail', kwargs={'pk': pk})

    def test_unauthenticated_user_cannot_access_api(self):
        """Test unauthenticated users get 403 Forbidden"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_user_cannot_access_api(self):
        """Test authenticated but non-staff users get 403 Forbidden"""
        self.client.force_authenticate(user=self.non_staff_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_staff_user_cannot_access_api(self):
        """Test inactive staff users get 403 Forbidden"""
        self.client.force_authenticate(user=self.inactive_staff_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_staff_user_can_access_api(self):
        """Test active staff users can access API"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_network_nodes_returns_all_nodes(self):
        """Test list endpoint returns all network nodes"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response has results key (paginated) or is direct list
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 3)  # factory, retail, us_retail
        
        # Check structure of first node
        first_node = data[0]
        self.assertIn('id', first_node)
        self.assertIn('name', first_node)
        self.assertIn('node_type', first_node)
        self.assertIn('email', first_node)
        self.assertIn('debt', first_node)
        self.assertIn('supplier', first_node)
        self.assertIn('products', first_node)

    def test_create_network_node_success(self):
        """Test creating network node works for active staff"""
        self.client.force_authenticate(user=self.staff_user)
        
        data = {
            'name': 'New Factory',
            'node_type': 'factory',
            'email': 'newfactory@example.com',
            'country': 'France',
            'city': 'Paris',
            'street': 'Factory Street',
            'house_number': '100',
            'debt': '999.99'  # This should be ignored
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify node was created
        new_node = NetworkNode.objects.get(name='New Factory')
        self.assertEqual(new_node.email, 'newfactory@example.com')
        self.assertEqual(new_node.debt, Decimal('0.00'))  # debt should be default, not from request

    def test_retrieve_network_node_returns_correct_data(self):
        """Test retrieve endpoint returns correct node data"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.detail_url(self.factory.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.factory.id)
        self.assertEqual(response.data['name'], self.factory.name)
        self.assertEqual(response.data['debt'], str(self.factory.debt))

    def test_update_network_node_success_but_debt_readonly(self):
        """Test update works but debt field cannot be changed"""
        self.client.force_authenticate(user=self.staff_user)
        
        original_debt = self.factory.debt
        data = {
            'name': 'Updated Factory Name',
            'node_type': 'factory',
            'email': 'updatedfactory@example.com',
            'country': 'Germany',
            'city': 'Berlin',
            'street': 'Industrial Street',
            'house_number': '123',
            'debt': '99999.99'  # This should be ignored
        }
        
        response = self.client.put(self.detail_url(self.factory.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.factory.refresh_from_db()
        self.assertEqual(self.factory.name, 'Updated Factory Name')
        self.assertEqual(self.factory.email, 'updatedfactory@example.com')
        self.assertEqual(self.factory.debt, original_debt)  # Debt should remain unchanged

    def test_partial_update_network_node_debt_ignored(self):
        """Test PATCH request ignores debt field"""
        self.client.force_authenticate(user=self.staff_user)
        
        original_debt = self.factory.debt
        data = {
            'name': 'Partially Updated Factory',
            'debt': '88888.88'  # This should be ignored
        }
        
        response = self.client.patch(self.detail_url(self.factory.id), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.factory.refresh_from_db()
        self.assertEqual(self.factory.name, 'Partially Updated Factory')
        self.assertEqual(self.factory.debt, original_debt)  # Debt should remain unchanged

    def test_delete_network_node_success(self):
        """Test delete removes node from database"""
        self.client.force_authenticate(user=self.staff_user)
        
        # Create a node to delete (don't delete test fixtures)
        node_to_delete = NetworkNode.objects.create(
            name="Temporary Node",
            node_type="entrepreneur",
            email="temp@example.com",
            country="Germany",
            city="Hamburg",
            street="Temp Street",
            house_number="999",
            debt=Decimal("100.00")
        )
        
        response = self.client.delete(self.detail_url(node_to_delete.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify node was deleted
        self.assertFalse(NetworkNode.objects.filter(id=node_to_delete.id).exists())

    def test_filter_by_country(self):
        """Test filtering nodes by country"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.list_url, {'country': 'Germany'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 2)  # factory and retail
        
        response = self.client.get(self.list_url, {'country': 'USA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)  # us_retail

    def test_filter_by_city(self):
        """Test filtering nodes by city"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.list_url, {'city': 'Berlin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response has results key (paginated) or is direct list
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)  # factory
        self.assertEqual(data[0]['name'], 'Electronics Factory')

    def test_filter_by_level(self):
        """Test filtering nodes by hierarchy level"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.list_url, {'level': '0'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)  # factory only
        
        response = self.client.get(self.list_url, {'level': '1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 2)  # both retail stores

    def test_search_by_name(self):
        """Test searching nodes by name"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.list_url, {'search': 'Factory'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Electronics Factory')

    def test_search_by_email(self):
        """Test searching nodes by email"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.list_url, {'search': 'factory@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'factory@example.com')

    def test_supplier_nested_representation(self):
        """Test supplier shows as nested object with id and name"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.detail_url(self.retail.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        supplier_data = response.data['supplier']
        self.assertIsNotNone(supplier_data)
        self.assertEqual(supplier_data['id'], self.factory.id)
        self.assertEqual(supplier_data['name'], self.factory.name)

    def test_products_nested_representation(self):
        """Test products show as nested list"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.detail_url(self.factory.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        products_data = response.data['products']
        self.assertEqual(len(products_data), 2)  # product1 and product2
        
        # Check product structure
        product = products_data[0]
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertIn('model', product)
        self.assertIn('release_date', product)

    def test_debt_field_is_read_only_in_serializer(self):
        """Test debt field cannot be updated even if included in request data"""
        self.client.force_authenticate(user=self.staff_user)
        
        original_debt = self.retail.debt
        
        # Try to update only the debt field
        response = self.client.patch(self.detail_url(self.retail.id), {
            'debt': '0.00'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify debt wasn't changed
        self.retail.refresh_from_db()
        self.assertEqual(self.retail.debt, original_debt)

    def test_create_with_supplier_relationship(self):
        """Test creating node with supplier relationship"""
        self.client.force_authenticate(user=self.staff_user)
        
        data = {
            'name': 'New Entrepreneur',
            'node_type': 'entrepreneur',
            'email': 'entrepreneur@example.com',
            'country': 'Germany',
            'city': 'Frankfurt',
            'street': 'Business Street',
            'house_number': '50',
            'supplier': self.retail.id
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify relationships
        new_node = NetworkNode.objects.get(name='New Entrepreneur')
        self.assertEqual(new_node.supplier, self.retail)
        self.assertEqual(new_node.level, 2)  # Should be level 2 since retail is level 1

    def test_invalid_data_returns_400(self):
        """Test invalid data returns 400 Bad Request"""
        self.client.force_authenticate(user=self.staff_user)
        
        # Missing required fields
        data = {
            'name': 'Incomplete Node'
            # Missing node_type, email, etc.
        }
        
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_node_returns_404(self):
        """Test accessing nonexistent node returns 404"""
        self.client.force_authenticate(user=self.staff_user)
        
        response = self.client.get(self.detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)