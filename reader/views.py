from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators import csrf
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import render
from reader.readPassport import extract_all
from .models import Log
import glob
import os
# Create your views here.

def change_log(status, filename):
    if len(Log.objects.all()) > 0:
        obj = Log.objects.order_by("-start_at")[0]
        obj.status = status
        obj.filename = filename
        obj.save()

@csrf_exempt
def read_document(request):
    file = None
    if request.method == "POST":
        try:
            log_obj = Log(
                start_at=now(),
                status='preparing',
                filename='',
            )
            log_obj.save()
            temp_files = glob.glob("reader/tmp/*")
            for file in temp_files:
                os.remove(file)
            file = request.FILES['file']
            print(file)
            change_log('started', file.name)
            default_storage.save("reader/tmp/temp_img.jpg", file)
            change_log('processing', file.name)
            op = extract_all("reader/tmp/temp_img.jpg")
            opt = {'data': op, 'error':False, 'err_msg': ''}
            change_log('completed', file.name)
            return JsonResponse(opt)
        except BaseException as e:
            opt = {'data': None, 'error':True, 'err_msg': str(e)}
            change_log('failed', file.name)
            return JsonResponse(opt)

@csrf_exempt
def get_log_snapshot(request):
     if request.method == "GET":
        logs = Log.objects.order_by("-start_at")[:10]
        log_dict = {'data': []}
        for i in range(len(logs)):
            log_dict['data'].append({
                'Filename': logs[i].filename,
                'Status': logs[i].status,
            })
        return JsonResponse(log_dict)

def index(request):
    return render(request, "index.html")