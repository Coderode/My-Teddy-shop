from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.contrib import messages
from . models import Blogpost

# Create your views here.
def index(request):
    allPosts = Blogpost.objects.all()
    params = {'allPosts':allPosts}
    return render(request, 'blog/index.html',params)

def blogpost(request, id):
    total = Blogpost.objects.all().count()
    post = Blogpost.objects.filter(post_id = id)[0]  #it returns array and it has only one object so taking 0 index
    if id <= 1 :
        nextPost = Blogpost.objects.filter(post_id = id+1)[0]
        prevPost = {'obj': 'null'}
    elif id >= total :
        nextPost = {'obj': 'null'}
        prevPost = Blogpost.objects.filter(post_id = id-1)[0]
    else :
        nextPost = Blogpost.objects.filter(post_id = id+1)[0]
        prevPost = Blogpost.objects.filter(post_id = id-1)[0]
    param = {'post':post,'nextPost':nextPost,'prevPost':prevPost}
    return render(request, 'blog/blogpost.html',param)
