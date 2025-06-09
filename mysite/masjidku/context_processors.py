from django.conf import settings


from masjidku.models import Page


def get_settings(request):
    return {
        'web_title': settings.MASJIDKU['web_title'],
        'my_footer': settings.MASJIDKU['footer'],
        'menu' : {
            'sejarah': Page.objects.filter(jenis='Sejarah').first(),
            'kepengurusan': Page.objects.filter(jenis='Kepengurusan').first(),
            'program': Page.objects.filter(jenis='Program'),
        }
    }

