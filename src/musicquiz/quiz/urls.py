from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('musicquiz.quiz.views',
    (r'^$', 'index'),
    (r'^question/$', 'question'),
    (r'^game_history/$', 'game_history'),
    
    # Example:
    # (r'^musicquiz/', include('musicquiz.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
