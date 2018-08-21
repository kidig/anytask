from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from anytask.api.views import login_required_basic_auth
from anytask.issues.models import Issue


# def token_auth_required(view):
#     def check_auth(request, *args, **kwargs):
#         http_auth = request.META.get('HTTP_AUTHORIZATION')
#         if not http_auth:
#             return HttpResponse(status=401)
#
#         return view(request, *args, **kwargs)
#
#     return check_auth


@csrf_exempt
@login_required_basic_auth
@require_http_methods(['POST'])
def update_jupyter_task(request, task_id):
    student_id = request.POST.get('student_id')
    if not student_id:
        return HttpResponse(status=400)

    issue, created = Issue.objects.get_or_create(task_id=task_id, student_id=student_id)

