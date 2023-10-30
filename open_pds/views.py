from django.shortcuts import render

# Create your views here.
def get_title(request):
    return render(request, "webbase/index.html")