from django.shortcuts import render

def period_stats(request):
    return render(request, "period_stats.html")

def goaldiff_stats(request):
    return render(request, "goaldiff_stats.html")