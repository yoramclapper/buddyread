from django.shortcuts import redirect

def index(request):
    # Redirects to the URL named "books" in the "books" app
    return redirect("books")
