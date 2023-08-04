from django.contrib import admin
from .forms import JobOfferForm, UserProfileForm
from .models import *
from django.urls import path


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    form = JobOfferForm
    filter_horizontal = ('skills_required',)

    def response_add(self, request, obj, post_url_continue=None):
        if obj.is_enabled:
            obj.send_offer_suggestion_email_to_qualified_users()
        return super(JobOfferAdmin, self).response_add(request, obj, post_url_continue)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        previous_offer = JobOffer.objects.get(pk=object_id)
        received_email_users = list(CustomUser.objects.qualified_users_for_offer(previous_offer))
        result = super(JobOfferAdmin, self).change_view(request, object_id, form_url, extra_context)
        new_offer = JobOffer.objects.get(pk=object_id)
        if new_offer.is_enabled:
            new_offer.send_offer_suggestion_email_to_qualified_users(*received_email_users)
        return result


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    model = UserProfile
    filter_horizontal = ('skills',)
    form = UserProfileForm


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    model = Application
    list_filter = ('offer__company',)
    ordering = ['created_at']


class PendingApplication(Application):
    class Meta:
        proxy = True


@admin.register(PendingApplication)
class PendingApplicationAdmin(ApplicationAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(state='P')

    exclude = ['state', 'reject_reason']
    change_form_template = "custom_admin/pending_application_change_form.html"

    def response_change(self, request, obj):
        if "reject" in request.POST:
            obj.reject_reason = request.POST.get("reject_reason")
            obj.state = Application.State.REJECTED
        elif "accept" in request.POST:
            obj.state = Application.State.ACCEPTED
        obj.save()
        return super().response_change(request, obj)


admin.site.register(Company)
admin.site.register(Skill)
admin.site.register(AltEmail)
admin.site.register(EducationalBackground)
admin.site.register(Resume)
