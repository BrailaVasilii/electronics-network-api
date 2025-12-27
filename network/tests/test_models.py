from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from network.models import NetworkNode, Product


class NetworkNodeModelTest(TestCase):
    def setUp(self):
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

    def test_network_node_creation(self):
        """Test basic NetworkNode creation"""
        self.assertEqual(self.factory.name, "Electronics Factory")
        self.assertEqual(self.factory.node_type, "factory")
        self.assertEqual(self.factory.email, "factory@example.com")
        self.assertEqual(self.factory.level, 0)
        self.assertEqual(self.factory.debt, Decimal("0.00"))
        self.assertIsNotNone(self.factory.created_at)

    def test_factory_level_is_zero(self):
        """Test that factory (root node) has level 0"""
        self.assertEqual(self.factory.level, 0)

    def test_retail_with_supplier_level_calculation(self):
        """Test level calculation for retail with factory supplier"""
        retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("1500.50")
        )
        self.assertEqual(retail.level, 1)
        self.assertEqual(retail.supplier, self.factory)

    def test_entrepreneur_level_calculation(self):
        """Test level calculation for entrepreneur with retail supplier"""
        retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("1500.50")
        )
        
        entrepreneur = NetworkNode.objects.create(
            name="Individual Entrepreneur",
            node_type="entrepreneur",
            email="entrepreneur@example.com",
            country="Germany",
            city="Hamburg",
            street="Business Street",
            house_number="789",
            supplier=retail,
            debt=Decimal("500.25")
        )
        self.assertEqual(entrepreneur.level, 2)

    def test_maximum_three_levels_validation(self):
        """Test that creating a 4th level raises ValidationError"""
        retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("1500.50")
        )
        
        entrepreneur = NetworkNode.objects.create(
            name="Individual Entrepreneur",
            node_type="entrepreneur",
            email="entrepreneur@example.com",
            country="Germany",
            city="Hamburg",
            street="Business Street",
            house_number="789",
            supplier=retail,
            debt=Decimal("500.25")
        )

        with self.assertRaises(ValidationError) as context:
            invalid_node = NetworkNode(
                name="Invalid Fourth Level",
                node_type="retail",
                email="invalid@example.com",
                country="Germany",
                city="Frankfurt",
                street="Invalid Street",
                house_number="999",
                supplier=entrepreneur,
                debt=Decimal("100.00")
            )
            invalid_node.full_clean()

        self.assertIn("Maximum network depth of 3 levels exceeded", str(context.exception))

    def test_prevent_circular_reference(self):
        """Test that circular references are prevented"""
        retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("1500.50")
        )

        with self.assertRaises(ValidationError) as context:
            self.factory.supplier = retail
            self.factory.full_clean()

        self.assertIn("Circular reference detected", str(context.exception))

    def test_self_reference_prevention(self):
        """Test that a node cannot be supplier to itself"""
        with self.assertRaises(ValidationError) as context:
            self.factory.supplier = self.factory
            self.factory.full_clean()

        self.assertIn("Node cannot be supplier to itself", str(context.exception))

    def test_debt_field_precision(self):
        """Test debt field precision (12 digits, 2 decimal places)"""
        node = NetworkNode.objects.create(
            name="Precision Test",
            node_type="retail",
            email="precision@example.com",
            country="Germany",
            city="Dresden",
            street="Precision Street",
            house_number="111",
            supplier=self.factory,
            debt=Decimal("9999999999.99")
        )
        self.assertEqual(node.debt, Decimal("9999999999.99"))

    def test_str_method(self):
        """Test __str__ method returns node name"""
        self.assertEqual(str(self.factory), "Electronics Factory")

    def test_node_type_choices(self):
        """Test that only valid node_type choices are accepted"""
        valid_types = ["factory", "retail", "entrepreneur"]
        for node_type in valid_types:
            node = NetworkNode(
                name=f"Test {node_type}",
                node_type=node_type,
                email=f"{node_type}@example.com",
                country="Germany",
                city="Test City",
                street="Test Street",
                house_number="1",
                debt=Decimal("0.00")
            )
            node.full_clean()  # Should not raise ValidationError

    def test_level_read_only_behavior(self):
        """Test that level is automatically calculated and read-only"""
        retail = NetworkNode.objects.create(
            name="Electronics Store",
            node_type="retail",
            email="store@example.com",
            country="Germany",
            city="Munich",
            street="Shop Street",
            house_number="456",
            supplier=self.factory,
            debt=Decimal("1500.50")
        )
        
        # Level should be calculated automatically
        self.assertEqual(retail.level, 1)
        
        # Changing supplier should update level
        new_factory = NetworkNode.objects.create(
            name="New Factory",
            node_type="factory",
            email="newfactory@example.com",
            country="Germany",
            city="Berlin",
            street="New Industrial Street",
            house_number="321",
            debt=Decimal("0.00")
        )
        
        retail.supplier = new_factory
        retail.save()
        retail.refresh_from_db()
        self.assertEqual(retail.level, 1)


class ProductModelTest(TestCase):
    def setUp(self):
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

    def test_product_creation(self):
        """Test basic Product creation"""
        product = Product.objects.create(
            name="Smartphone",
            model="iPhone 15",
            release_date=date(2023, 9, 15),
            network_node=self.factory
        )
        
        self.assertEqual(product.name, "Smartphone")
        self.assertEqual(product.model, "iPhone 15")
        self.assertEqual(product.release_date, date(2023, 9, 15))
        self.assertEqual(product.network_node, self.factory)

    def test_product_str_method(self):
        """Test Product __str__ method"""
        product = Product.objects.create(
            name="Laptop",
            model="MacBook Pro",
            release_date=date(2023, 10, 30),
            network_node=self.factory
        )
        
        self.assertEqual(str(product), "Laptop - MacBook Pro")

    def test_product_network_node_relationship(self):
        """Test Product relationship to NetworkNode"""
        product1 = Product.objects.create(
            name="Tablet",
            model="iPad Air",
            release_date=date(2023, 5, 10),
            network_node=self.factory
        )
        
        product2 = Product.objects.create(
            name="Watch",
            model="Apple Watch",
            release_date=date(2023, 3, 8),
            network_node=self.factory
        )
        
        # Test that factory can have multiple products
        factory_products = self.factory.products.all()
        self.assertIn(product1, factory_products)
        self.assertIn(product2, factory_products)
        self.assertEqual(factory_products.count(), 2)

    def test_product_required_fields(self):
        """Test that all required fields are enforced"""
        with self.assertRaises(ValidationError):
            product = Product(
                model="Test Model",
                release_date=date(2023, 1, 1),
                network_node=self.factory
                # Missing required 'name' field
            )
            product.full_clean()