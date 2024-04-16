from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
import subprocess, threading
import logging, json, os
from . import models

logger = logging.getLogger('lunawaelections')

@csrf_exempt
@require_http_methods(["POST"])
def auth(request):
    try:
        data = json.loads(request.body)
        if data.get('password', '') == '0000':

            response = HttpResponse("Success", status=200)
            logger.debug(f"Auth Api: {response.content}")
            return response
    except Exception as e:
        logger.error(f"Error occurred during deletion: {e}", exc_info=True)

    response = HttpResponse("Failure", status=401)
    logger.debug(f"Auth Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["POST"])
def upload(request):
    if request.FILES.get('image'):
        try:
            image = request.FILES['image']
            file_path = os.path.join(settings.UPLOAD_ROOT, image.name)
            default_storage.save(file_path, image)

            androidDevice = image.name.split('_')[1]
            android_id = models.AndroidID.objects.get_or_create(name=androidDevice)[0]
            new_image = models.Image.objects.create(name=image.name, android_id=android_id)
            if new_image.status != "Invalid":
                response = HttpResponse("Upload Successfully", status=200)
                
        except Exception as e:
            logger.error(f"Error occurred during upload: {e}", exc_info=True)
            response = HttpResponse("Invalid Image", status=400)
    else:
        response = HttpResponse("No Image", status=400)
    
    logger.debug(f"Upload Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["GET"])
def get_image(request, img_name):
    try:
        out_path = os.path.join(settings.PROCESS_ROOT, img_name)
        if os.path.exists(out_path):
            with open(out_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="image/jpeg", status=200)
                logger.debug(f"Get image Api: {response}")
                return response
        elif models.Image.objects.get(name=img_name).status == "Processing":
                response = HttpResponse("Try again", status=401)
    except Exception as e:
        logger.error(f"Error occurred during get image: {e}", exc_info=True)
        response = HttpResponse("Failure", status=401)

    logger.debug(f"Get image Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["GET"])
def counter(request, android_id):
    try:
        counter = models.AndroidID.objects.get_or_create(name=android_id)[0].counter
        response = HttpResponse(counter, status=200)
    except Exception as e:
        logger.error(f"Error occurred during counter: {e}", exc_info=True)
        response = HttpResponse("Failure", status=401)

    logger.debug(f"Counter Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["GET"])
def delete(request, android_id):
    try:
        android = models.AndroidID.objects.filter(name=android_id).first()
        if android:
            allimages = models.Image.objects.filter(android_id=android)
            if allimages.exists():
                for image in allimages:
                    image.delete()

            android.delete()

        response = HttpResponse("Success", status=200)
    except Exception as e:
        logger.error(f"Error occurred during deletion: {e}", exc_info=True)
        response = HttpResponse("Failure", status=401)

    logger.debug(f"Delete Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["GET"])
def stats(request):
    try:
        members = models.Member.objects.all()
        response_data = "\n".join(str(member) for member in members)
        response = HttpResponse(response_data, content_type="text/csv", status=200)
    except Exception as e:
        logger.error(f"Error occurred during stats: {e}", exc_info=True)
        response = HttpResponse("Failure", status=401)

    logger.debug(f"Stats Api: {response.content}")
    return response

def run_streamlit():
    command = "streamlit run app.py --server.address 0.0.0.0 --server.port 8501".split(" ")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Streamlit Started")
    else:
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)

@csrf_exempt
@require_http_methods(["GET"])
def streamlit(request):
    if not settings.STREAMLIT_RUN:
        settings.STREAMLIT_RUN = True
        threading.Thread(target=run_streamlit).start()

    scheme = request.scheme
    host_header = request.META.get('HTTP_HOST', 'localhost')
    host = host_header.split(':')[0]
    # port = '80' if scheme == 'http' else '443'
    full_url = f"{scheme}://{host}:8501/"
    return render(request, 'streamlit.html', {'full_url': full_url})