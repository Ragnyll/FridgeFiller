from django.shortcuts import render

def disp_info(request):
    return render(request, 'listapp/disp_info.html')
