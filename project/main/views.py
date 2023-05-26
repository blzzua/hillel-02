# from django.core.mail import mail_admins
from django.urls import reverse_lazy
from django.views.generic import FormView
from main.forms import ContactForm
from project.celery import mail_admins_task


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contacts/index.html'
    success_url = reverse_lazy('main_contacts')

    def form_valid(self, form):
        message_parts = {
            'Subject': 'Contact form ' + form.cleaned_data["email"],
            'Body': form.cleaned_data["text"],
        }
        mail_admins_task.delay(message_parts=message_parts)
        return super().form_valid(form)
