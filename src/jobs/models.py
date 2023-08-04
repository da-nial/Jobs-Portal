from django.utils.translation import get_language
from jobs.templatetags.extra_tags import translate_numbers
from django.db import models, IntegrityError
from authentication.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from jobs.managers import EnabledManager, JobQuerySet
from django.core.files.storage import FileSystemStorage
from website.settings import MEDIA_URL, MEDIA_ROOT


class EducationalLevel(models.TextChoices):
    DIPLOMA = 'DI', _('High School Diploma')
    ASSOCIATE = 'A', _('Associate Degree')
    BACHELORS_DEGREE = 'B', _('Bachelors Degree')
    MASTERS_DEGREE = 'M', _('Masters Degree')
    DOCTORAL_DEGREE = 'DO', _('Doctoral Degree')
    POSTDOCTORAL_DEGREE = 'P', _('Post Doctoral Degree')
    OTHERS = 'O', _('Others')

    @staticmethod
    def _get_educational_levels_order_list():
        return [EducationalLevel.OTHERS,
                EducationalLevel.DIPLOMA,
                EducationalLevel.ASSOCIATE,
                EducationalLevel.BACHELORS_DEGREE,
                EducationalLevel.MASTERS_DEGREE,
                EducationalLevel.DOCTORAL_DEGREE,
                EducationalLevel.POSTDOCTORAL_DEGREE]

    def get_le_educational_levels(self):
        return EducationalLevel._get_educational_levels_order_list()[:self.order_index + 1]

    def get_ge_educational_levels(self):
        return EducationalLevel._get_educational_levels_order_list()[self.order_index:]

    @property
    def order_index(self):
        return EducationalLevel._get_educational_levels_order_list().index(self)


class CategoryJob(models.TextChoices):
    DataScience_and_Analytics = 'DA', _('Data')
    Design_and_UX = 'DU', _('Design and UX')
    Engineering = 'E', _('Engineering')
    Finance_and_Accounting = 'FA', _('Finance and Accounting')
    Human_Resources = 'HR', _('Human Resources')
    Marketing_and_Communications = 'MC', _('Marketing and Communications')
    Operation = 'O', _('Operation')
    Product = 'P', _('Product')
    Sales = 'S', _('Sales')
    Other = 'OT', _('Other')


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='images', blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(max_length=200)
    telephone_number = models.CharField(max_length=12)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Each skills consists of a title.
    UserProfile has ManyToMany relationship with fields.
    """
    title = models.CharField(max_length=80, primary_key=True)

    def __str__(self):
        return self.title


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    salary = models.IntegerField(blank=True, null=True)
    minimum_work_experience = models.IntegerField(default=0)
    CHOICES_TIME = [
        ('full_time', _('full time')),
        ('part_time', _('part time')),
    ]

    type_of_cooperation = models.CharField(choices=CHOICES_TIME, max_length=10)
    minimum_degree = models.CharField(max_length=2, choices=EducationalLevel.choices, null=True, blank=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="job_offers")
    city = models.CharField(max_length=100, null=True, blank=True)
    is_enabled = models.BooleanField(default=True, db_index=True)
    category = models.CharField(max_length=2, choices=CategoryJob.choices, null=True, blank=True)
    users_tagged_job = models.ManyToManyField(CustomUser, blank=True, related_name='tagged_jobs')

    objects = JobQuerySet.as_manager()
    enabled = EnabledManager()

    def __str__(self):
        return self.title

    def send_offer_suggestion_email_to_qualified_users(self, *exceptional_users):
        """
        Calling Situation:
        This Function Should be called after saving JobOffer and setting it's m2m and foreign key relations
        """
        for user in CustomUser.objects.qualified_users_for_offer(self, *exceptional_users):
            from jobs.tasks import send_offer_suggestion_email
            send_offer_suggestion_email.delay(user.pk, self.pk)

    def send_inform_email_to_tagged_users(self):
        from jobs.tasks import send_tagged_offer_email
        for user in self.users_tagged_job.all():
            send_tagged_offer_email.delay(user.pk, self.pk)
        self.clear_tagged_job_for_users()

    def clear_tagged_job_for_users(self):
        self.users_tagged_job.clear()

    class Meta:
        ordering = ['-is_enabled']


class UserProfile(models.Model):
    """
    UserProfile model, first_name & last_name of users are stored in CustomUser,
    other personal fields are stored here.
    """

    class MilitaryServiceStatus(models.TextChoices):
        CONSCRIPT = 'CO', _('Conscript')
        EDUCATIONAL_EXEMPTION = 'EE', _('Educational Exemption')
        EXEMPT = 'E', _('Exempt')
        DISCHARGE = 'D', _('Discharge')

    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHERS = 'O', _('Other')

    class MaritalStatus(models.TextChoices):
        SINGLE = 'S', _('Single')
        MARRIED = 'M', _('Married')

        # WIDOWED = 'W', _('Widowed')
        # DIVORCED = 'D', _('Divorced')
        # SEPARATED = 'S', _('Separated')

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    mobile_number = models.CharField(max_length=11, blank=True, null=True, verbose_name=_('Mobile number'))
    phone_number = models.CharField(max_length=11, blank=True, null=True, verbose_name=_('Phone number'))
    address = models.CharField(max_length=280, blank=True, null=True, verbose_name=_('Address'))
    military_service_status = models.CharField(max_length=2,
                                               choices=MilitaryServiceStatus.choices,
                                               blank=True, null=True,
                                               verbose_name=_('Military service status')
                                               )
    gender = models.CharField(max_length=1,
                              choices=Gender.choices,
                              blank=True, null=True,
                              verbose_name=_('Gender')
                              )
    marital_status = models.CharField(max_length=1,
                                      choices=MaritalStatus.choices,
                                      blank=True, null=True,
                                      verbose_name=_('Marital status')
                                      )
    city_of_residence = models.CharField(max_length=80, null=True, blank=True, verbose_name=_('City of residence'))
    bio = models.TextField(null=True, blank=True, verbose_name=_('Bio'))
    skills = models.ManyToManyField(Skill)

    def get_maximum_educational_level(self):
        return max(
            [EducationalLevel(eb.level) for eb in self.educationalbackground_set.all()],
            default=EducationalLevel.OTHERS,
            key=lambda el: el.order_index
        )

    def __str__(self):
        return str(self.user)


class AltEmail(models.Model):
    address = models.EmailField()
    user_profile = models.ForeignKey(UserProfile,
                                     on_delete=models.CASCADE,
                                     related_name="alt_emails")
    verification_token = models.CharField(max_length=50, null=True,
                                          unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)

    def refresh_verification_token(self):
        while True:
            new_verification_token = get_random_string(50)
            try:
                self.verification_token = new_verification_token
                self.save()
                break
            except IntegrityError:
                continue

    def __str__(self):
        return f'{self.user_profile} alt email: {self.address}'


class EducationalBackground(models.Model):
    """
    Each UserProfile can have multiple EducationalBackground instances (OneToMany relationship).
    """
    MIN_YEAR = 1300
    MAX_YEAR = 1450

    field = models.CharField(max_length=80, verbose_name=_('Field'))
    institute = models.CharField(max_length=80, verbose_name=_('Institue'))
    level = models.CharField(max_length=2,
                             choices=EducationalLevel.choices,
                             verbose_name=_('Level'))
    start_year = models.IntegerField(validators=[MinValueValidator(MIN_YEAR),
                                                 MaxValueValidator(MAX_YEAR)],
                                     verbose_name=_('Start year'))
    finish_year = models.IntegerField(validators=[MinValueValidator(MIN_YEAR),
                                                  MaxValueValidator(MAX_YEAR)],
                                      verbose_name=_('Finish year'),
                                      null=False,
                                      blank=True)

    is_currently_studying = models.BooleanField(verbose_name=_('Is currently studying'))
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        _str = ""
        if self.level:
            _str += f" {self.get_level_display()}"
        if self.institute:
            _str += f" @ {self.institute}"
        if self.start_year:
            if get_language() == 'fa':
                _str += f" ({translate_numbers(self.start_year)})"
            else:
                _str += f" ({self.start_year})"
        return _str


class Application(models.Model):
    class State(models.TextChoices):
        ACCEPTED = 'A', _('Accepted')
        REJECTED = 'R', _('Rejected')
        PENDING = 'P', _('Pending')

    state = models.CharField(choices=State.choices, max_length=1, default=State.PENDING)
    offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='applications')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True, verbose_name=_('Resume'))
    reject_reason = models.TextField(null=True, blank=True, verbose_name=_('Reject Reason'))

    def __str__(self):
        return f"{self.user} application for {self.offer}"


class Resume(models.Model):
    resume_file = models.FileField(upload_to='user_resumes', verbose_name='resume')
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='resume')

    def delete(self, using=None, keep_parents=False):
        self.resume_file.storage.delete(self.resume_file.name)
        super().delete()

    @staticmethod
    def delete_resume(profile):
        try:
            resume = Resume.objects.get(user_profile=profile)
        except Resume.DoesNotExist:
            return
        resume.delete()
