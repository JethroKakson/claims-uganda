from django.shortcuts import render
from Staff.models import Staff
from plotly import graph_objs as go
from Cases.models import Case
from django.utils.timezone import now
from Appointments.forms import AppointmentForm
from FeeNotes.forms import FeeNoteForm
from FeeNotes.models import FeeNote
from django.contrib.auth.decorators import login_required
from Reports.models import Report
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ninja import NinjaAPI
from django.core.signals import request_finished, got_request_exception
from django.dispatch import receiver
import sys
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import subprocess
from django.http import JsonResponse
from django.conf import settings

def git_pull(request):
    try:
        repo_path = settings.BASE_DIR
        subprocess.check_call(['git', '-C', repo_path, 'stash'])
        subprocess.check_call(['git', '-C', repo_path, 'pull'])
        subject = 'New Deploy🚀🚀🚀'
        image = '/static/assets/img/server.jpg'
        image_url = request.build_absolute_uri(image)
        html_message = render_to_string('deploy_email.html', {'date': now().strftime('%Y-%m-%d %H:%M:%S'), 'image': image_url})
        plain_message = strip_tags(html_message)
        from_email = 'Claims System <info@claimsug.com>'
        to = 'mukisaelijah293@gmail.com'
        mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
        return JsonResponse({"status": "success", "message": "Repository updated successfully."})
    except subprocess.CalledProcessError as e:
        return JsonResponse({"status": "error", "message": f"Failed to pull the repository: {str(e)}"}, status=500)

@receiver(got_request_exception)
def track_errors(sender, **kwargs):
    request = kwargs['request']
    exc_type, exc_value, exc_traceback = sys.exc_info()
    view_name = request.resolver_match.view_name
    app_name = request.resolver_match.app_name
    logged_in_user = request.user
    subject = 'Bug Detected! Fix Urgently.'
    html_message = render_to_string('error_email.html', {'user': logged_in_user, 'view': view_name, 'date': now().strftime('%Y-%m-%d %H:%M:%S'), 'error': str(exc_value), 'error_type': str(exc_type.__name__)})
    plain_message = strip_tags(html_message)
    from_email = 'Claims System <info@claimsug.com>'
    to = 'mukisaelijah293@gmail.com'
    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

    

api = NinjaAPI(title="Claims Api Documentation")

@login_required
def dashboard(request):
    cases = Case.objects.all()      
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = []
    for month in months:
        if request.user.staff.department == 'Assessors':
            data.append(Case.objects.filter(date_reported__month=months.index(month)+1, date_reported__year=now().year, assessor=request.user.staff.assessor).count())
        else:
            data.append(Case.objects.filter(date_reported__month=months.index(month)+1, date_reported__year=now().year).count())
    fig = go.Figure(data=[go.Bar(y=data, x=months)])
    fig.update_layout(title=f'Cases handled per month ({now().year})', xaxis_title='Month', yaxis_title='Count')
    div = fig.to_html(full_html=False)
    staff = Staff.objects.all().count()
    fee_note_form = FeeNoteForm()
    if request.user.staff.department == 'Assessors':
        fee_note_form.fields['case'].queryset = FeeNoteForm().fields['case'].queryset.filter(assessor=request.user.staff.assessor, fee_note=None)
    appointments = request.user.staff.appointments.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(appointments, 4)
    try:
        appointments = paginator.page(page)
    except PageNotAnInteger:
        appointments = paginator.page(1)
    except EmptyPage:
        appointments = paginator.page(paginator.num_pages)
    return render(request, 'dashboard.html', {'staff_count': staff, 'div': div, 'cases': cases, 'appointment_form': AppointmentForm(), 'fee_note_form': fee_note_form, 'case_count': Case.objects.all().count(), 'fee_note_count': FeeNote.objects.all().count(), 'report_count': Report.objects.all().count(), 'appointments': appointments})


@api.get('/')
def root(request):
    return 'Claims api v1'