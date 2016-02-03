from django.shortcuts import render
from .models import User, Group, List


def disp_info(request):
    users = User.objects.all()
    groups = Group.objects.all()
    lists = List.objects.all()
    return render(request, 'list/disp_info.html',{'users': users})
