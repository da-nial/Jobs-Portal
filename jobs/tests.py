from django.test import TestCase

# Create your tests here.
from django.urls import reverse

from jobs.models import Company, JobOffer, TagsOfSkill


class CompanyModelTests(TestCase):
    def test_successful_company_with_logo_creation(self):
        company = Company(name='test_1', logo='images/test.jpg',
                          telephone_number='test_phone', link='test.com')
        self.assertTrue(company.logo.url, 'media/images/test.jpg')

    def test_successful_company_without_logo_creation(self):
        company = Company(name='test_2', telephone_number='test_phone', link='test.com')
        company.save()


def create_job_offer():
    company = Company(name='test_company', link='test.com', telephone_number=98)
    skill = TagsOfSkill(skill='test_skill')
    job_offer = JobOffer(title='test_title', description='test_description', company=company)
    company.save()
    skill.save()
    job_offer.save()
    job_offer.skills_required.set([skill])
    return job_offer


class JobOfferPageTests(TestCase):
    def test_not_found_skill(self):
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 404)

    def test_found_skill_link(self):
        job_offer = create_job_offer()
        response = self.client.get(reverse('jobs:job_offers', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['joboffer'], job_offer)
