# This function is used to make the All Category shows the category menu in page as admin has added which which categories
from .models import Category

def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)

