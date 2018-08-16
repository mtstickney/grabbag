from django.http import HttpResponse

def say_hi(request):
    return HttpResponse("Hi there!", content_type="text/plain")
