from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from . import processing
import json, cv2, os
import logging

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
    except: pass

    response = HttpResponse("Failure", status=401)
    logger.debug(f"Auth Api: {response.content}")
    return response

@csrf_exempt
@require_http_methods(["POST"])
def upload(request):
    if request.FILES.get('image'):
        image = request.FILES['image']
        file_path = os.path.join(settings.UPLOAD_ROOT, image.name)
        default_storage.save(file_path, image)

        out_path = os.path.join(settings.PROCESS_ROOT, image.name)
        image = processing.check_valid(file_path)
        if image is not False:
            image = processing.draw_bbox(image)
            cv2.imwrite(out_path, image)
            with open(out_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="image/jpeg", status=200)
                logger.debug(f"Upload Api: {response}")
                return response
        
        response = HttpResponse("Invalid Image", status=400)
        logger.debug(f"Upload Api: {response.content}")
        return response
    else:
        response = HttpResponse("No Image", status=400)
        logger.debug(f"Upload Api: {response.content}")
        return response