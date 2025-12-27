from django.http import HttpResponse, HttpRequest, Http404
from django.shortcuts import render

from .models import Function


def index(request: HttpRequest) -> HttpResponse:
    function_list = Function.objects.all()
    context = {"function_list": function_list}
    return render(request, "explorer/index.html", context)


def function(request: HttpRequest, function_id: int) -> HttpResponse:
    try:
        function_name = Function.objects.get(id=function_id)
    except Function.DoesNotExist:
        raise Http404(f"Function {function_id} does not exist!")
    return HttpResponse(f"This is function {function_id}: {function_name}")
