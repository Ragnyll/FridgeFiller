from django.shortcuts import render
from .models import User, Group, List


def disp_info(request):
    users = User.objects.all()
    return render(request, 'listapp/disp_info.html',{'users': users})
