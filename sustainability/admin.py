# sustainability/admin.py
from django.contrib import admin
from django.utils.html import format_html

# Keep a handy link on the admin index header; no fake model needed.
admin.site.site_header = "Django Admin"
admin.site.site_title = "Django Admin"
admin.site.index_title = format_html(
    'Administration — <a href="{}">Sustainability</a>',
    "/admin/sustainability/monitor/"
)
