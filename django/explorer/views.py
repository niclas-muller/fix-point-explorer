from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError

from explorer.models import Function
from django_stubs_ext import StrOrPromise

import numpy as np
import plotly.express as px


class IndexView(View):
    def get(
        self, request: HttpRequest, message: None | StrOrPromise = None
    ) -> HttpResponse:
        function_list = Function.objects.all()
        context = {
            "function_list": function_list,
            "message": message,
        }
        return render(request, "explorer/index.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if "function_string" in request.POST:
            function_string = request.POST["function_string"]
            try:
                function = Function.create(function_string)
                function.save()
                return HttpResponseRedirect(reverse("explorer:index"))
            except ValidationError as e:
                return self.get(request, message=e.message)

        return self.get(request)


class DetailView(View):
    def get(
        self,
        request: HttpRequest,
        function_id: int,
        message: None | str = None,
        parameters: None | dict[str, complex] = None,
    ) -> HttpResponse:
        function_obj = get_object_or_404(Function, pk=function_id)
        if parameters:
            function_lambda = function_obj.as_lambda(parameters)
            if function_lambda is not None:
                x = np.linspace(-1, 1, num=100)
                y = np.angle(function_lambda(x))
                fig = px.scatter(x=x, y=y)
            else:
                fig = px.scatter(x=[0], y=[0])
        else:
            fig = px.scatter(x=[0], y=[0])

        img = fig.to_html(full_html=False)
        context = {
            "function": function_obj,
            "parameter_names": function_obj.parameter_names,
            "parameters": parameters,
            "message": message,
            "image": img,
        }

        return render(request, "explorer/detail.html", context)

    def post(self, request: HttpRequest, function_id: int) -> HttpResponse:
        parameters: dict[str, complex] = {}
        for entry in request.POST:
            if entry.startswith("param:"):
                _, parameter, component = entry.split(":")
                try:
                    value = complex(request.POST[entry])
                except ValueError:
                    msg = f"Could not convert input {request.POST[entry]} to float."
                    return self.get(request, function_id, message=msg)
                value *= 1.0 if component == "real" else 1.0j
                if parameter in parameters:
                    parameters[parameter] += value
                else:
                    parameters.update({parameter: value})
        return self.get(request, function_id, parameters=parameters)
