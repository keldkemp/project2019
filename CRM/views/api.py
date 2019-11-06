from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from CRM.models import Worker, Time


# Create your views here.

@csrf_exempt
def connect(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(username=username, password=password)

    if user is not None:
        user_send = Worker.objects.filter(id=user.id).values("username")
        time_send = Time.objects.filter(worker_id=user.id).values("time_of_arrival", "time_of_leaving")
        return JsonResponse({'user': list(user_send), 'time': list(time_send)})
    else:
        return
