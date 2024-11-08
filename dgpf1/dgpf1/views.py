import datetime
from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views import debug
from django.shortcuts import render
import sys
import globus_sdk
from globus_portal_framework.gsearch import get_index

from dgpf1.hpced.download import download

@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = open(settings.STATIC_ROOT + '/img/favicon.ico', 'rb')
    return FileResponse(file)

def Debug_Details(request, format=None, **kwargs):
    return debug.technical_500_response(request, *sys.exc_info(), status_code=400)


@cache_control(max_age=300, immutable=True, public=True)  # five minutes
def search_about(request: HttpRequest, index: str) -> HttpResponse:
    index_info = get_index(index)
    info = globus_sdk.SearchClient().get_index(index_info["uuid"]).data
    info["creation_date"] = datetime.datetime.fromisoformat(info["creation_date"])
    # Comment out or change the order of fields below to determine how they are displayed
    fields = [
        # {"field_name": "@datatype"}
        # {"field_name": "@version"},
        {"field_name": "display_name", "display_name": "Display Name"},
        {"field_name": "creation_date", "type": "date", "display_name": "Creation Date"},
        {"field_name": "id"},
        {"field_name": "is_trial", "display_name": "Trial Index"},
        {"field_name": "max_size_in_mb", "type": "int", "display_name": "Max Size in MB"},
        {"field_name": "num_entries", "type": "int", "display_name": "Number of Entries"},
        {"field_name": "num_subjects", "type": "int", "display_name": "Number of Subjects"},
        {"field_name": "size_in_mb", "type": "int", "display_name": "Size in MB"},
        {"field_name": "status"},
        # {"field_name": "subscription_id"},
    ]
    display_fields = fields.copy()
    for field in display_fields:
        field["value"] = info[field["field_name"]]
        field["display_name"] = field.get("display_name") or field["field_name"].capitalize()
    context = dict(index_info=display_fields)
    return render(request, "globus-portal-framework/v2/search-about.html", context)


def download_as_html(request: HttpRequest, index: str) -> HttpResponse:

    # download the requested metadata into html and assign a filename
    status, content = download(request.session['search'], request.user)
    filename = request.session['search']['query'] if status else "Error"

    # HttpResponse to render
    response = HttpResponse(content,
        headers={
            "Content-Type": "html",
            "Content-Disposition": 'attachment; filename="' + filename +'.html"'
        }
    )
    return response
    