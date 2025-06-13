from django import template

register = template.Library()

@register.filter
def get_nama_by_list(siswa_list, id):
    return next((s.nama for s in siswa_list if s.id == id), id)

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def get_nama_by_queryset(queryset, id):
    return queryset.filter(id=id).first().nama if queryset.filter(id=id).exists() else "-"

@register.filter
def get_item(dict_data, key):
    return dict_data.get(key, [])
