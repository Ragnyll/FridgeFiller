from django.shortcuts import render
from django.views.generic import TemplateView
from .models import User, Group, List


def disp_info(request):
    users = User.objects.all()
    groups = Group.objects.all()
    lists = List.objects.all()
    return render(request, 'lists/disp_info.html',{'users': users})

class test(TemplateView):
    template_name = 'lists/test.html'
