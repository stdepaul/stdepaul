from django.shortcuts import render

def home(request):
	context = {}
	template_name = 'home.html'
	return render(request, template_name, context)
