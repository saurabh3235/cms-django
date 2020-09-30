from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from django.forms import modelformset_factory

from .push_notification_sender import PushNotificationSender
from ...decorators import region_permission_required
from ...forms.push_notifications import (
    PushNotificationForm,
    PushNotificationTranslationForm,
)
from ...models import Language, PushNotification, PushNotificationTranslation, Region


@method_decorator(login_required, name="dispatch")
@method_decorator(region_permission_required, name="dispatch")
class PushNotificationView(PermissionRequiredMixin, TemplateView):
    permission_required = "cms.view_push_notifications"
    raise_exception = True

    template_name = "push_notifications/push_notification_form.html"
    base_context = {"current_menu_item": "push_notifications"}
    push_sender = PushNotificationSender()

    def get(self, request, *args, **kwargs):
        print(kwargs.get("push_notification_id"))
        push_notification = PushNotification.objects.filter(
            id=kwargs.get("push_notification_id")
        ).first()
        region = Region.objects.get(slug=kwargs.get("region_slug"))
        language = Language.objects.get(code=kwargs.get("language_code"))
        num_languages = len(region.languages)
        if push_notification is not None:
            pn_form = PushNotificationForm(instance=push_notification)
            PNTFormset = modelformset_factory(PushNotificationTranslation, form=PushNotificationTranslationForm, max_num=num_languages, extra=num_languages)
            pnt_formset = PNTFormset(queryset=push_notification.translations.order_by("language"))
            print("loading")
        else:
            pn_form = PushNotificationForm()
            initial_data = []
            for lang in region.languages:
                lang_data = {"language": lang.id}
                initial_data.append(lang_data)
            PNTFormset = PushNotificationForm()
            pnt_formset = modelformset_factory(PushNotificationTranslation, form=PushNotificationTranslationForm, max_num=num_languages, extra=num_languages)(initial=initial_data)
            print("new")

        print(pnt_formset)

        return render(request, self.template_name, {
            **self.base_context,
            'push_notification': push_notification,
            'push_notification_form': pn_form,
            'pnt_formset': pnt_formset,
            'language': language,
            'languages': region.languages,
        })

    # pylint: disable=too-many-branches,unused-argument
    def post(self, request, *args, **kwargs):

        if not request.user.has_perm("cms.edit_push_notifications"):
            raise PermissionDenied

        if "submit_send" in request.POST:
            if not request.user.has_perm("cms.send_push_notifications"):
                raise PermissionDenied

        region = Region.objects.get(slug=kwargs.get("region_slug"))
        language = Language.objects.get(code=kwargs.get("language_code"))
        num_languages = len(region.languages)

        PushNewsFormset = modelformset_factory(PushNotificationTranslation, form=PushNotificationTranslationForm, max_num=num_languages)
        pnt_formset = PushNewsFormset(request.POST)
        print(pnt_formset)
        pn_form = PushNotificationForm(request.POST)
        if pn_form.is_valid():
            push_notification = pn_form.save(commit=False)
            push_notification.region = region
            push_notification.save()

        if pnt_formset.is_valid():
            for form in pnt_formset:
                translation = form.save(commit=False)
                translation.push_notification = push_notification
                translation.save()
            messages.success(request, "Push Notification saved.")

        return render(
            request,
            self.template_name,
            {
                **self.base_context,
                'push_notification': push_notification,
                'push_notification_form': pn_form,
                'pnt_formset': pnt_formset,
                "language": language,
                "languages": region.languages,
            },
        )
