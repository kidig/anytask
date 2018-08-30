import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from unidecode import unidecode

from api.views import login_required_basic_auth
from issues.models import Issue, Event, File
from issues.model_issue_field import IssueField
from tasks.models import Task

from users.models import UserProfile


logger = logging.getLogger('django.request')


@csrf_exempt
@login_required_basic_auth
@require_http_methods(['POST'])
def update_jupyter_task(request):
    user = request.user

    assignment_id = request.POST.get('name')
    student_id = request.POST.get('student')
    score = request.POST.get('score')
    timestamp = request.POST.get('timestamp')
    logger.debug('REQUEST: %r', request.POST)

    if not student_id or not assignment_id:
        return HttpResponse(status=400)

    try:
        profile = UserProfile.objects.get(ya_passport_login=student_id)
    except UserProfile.DoesNotExist:
        return HttpResponse('No student found', status=404)

    try:
        task = Task.objects.get(type=Task.TYPE_IPYNB, nb_assignment_name=assignment_id)
    except Task.DoesNotExist:
        return HttpResponse('No task found', status=404)

    issue, created = Issue.objects.get_or_create(task=task, student=profile.user)
    issue.set_status_accepted(user)

    if score:
        try:
            issue.set_byname('mark', float(score))
        except ValueError:
            return HttpResponse('Wrong score: {}'.format(score), status=400)

    if request.FILES:
        try:
            field = IssueField.objects.get(name='file')
        except IssueField.DoesNotExist:
            return HttpResponse('No issue field', status=404)

        event = Event.objects.create(issue_id=issue.id, author=user, field=field)

        for name, file in request.FILES.iteritems():
            file.name = unidecode(file.name)
            File.objects.create(file=file, event=event)

    return HttpResponse(status=200)
