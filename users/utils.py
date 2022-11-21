from users.models import Profile,Skill
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

def searchProfiles(request):
    search_query=''

    if request.GET.get('search_query'):
        search_query=request.GET.get('search_query')
    skills=Skill.objects.filter(name__icontains=search_query)
    profile=Profile.objects.distinct().filter(Q(name__icontains=search_query) | 
    Q(short_bio__icontains=search_query) |
    Q(skill__in=skills)
    )

    return profile,search_query

def paginatioProfiles(request,profiles,result):

    page=request.GET.get('page')
    paginator=Paginator(profiles,result)
    try:
        profiles=paginator.page(page)
    except PageNotAnInteger:
        page=1
        profiles=paginator.page(page)
    except EmptyPage :
        page=paginator.num_pages
        profiles=paginator.page(page)
    
    leftIndex=(int(page)-2)
    if leftIndex<1:
        leftIndex=1
    rightIndex=(int(page)+3)
    if rightIndex>paginator.num_pages:
        rightIndex=paginator.num_pages+1

    custom_range=range(leftIndex,rightIndex)

    return profiles,custom_range