from django.test import TestCase

# Create your tests here.
from jobs.models import Company


class CompanyModelTests(TestCase):
    def test_successful_company_with_logo_creation(self):
        company = Company(name='test_1', logo='images/test.jpg',
                          telephone_number='test_phone', link='test.com')
        self.assertTrue(company.logo.url, 'media/images/test.jpg')

    def test_successful_company_without_logo_creation(self):
        company = Company(name='test_2', telephone_number='test_phone', link='test.com')
        company.save()
