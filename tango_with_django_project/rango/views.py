from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category
from rango.models import Page
from rango.models import UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User



def index(request):
    request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html', context_dict)


    # template = 'rango/index.html'
    return response


# def about(request):
#     if request.session.test_cookie_worked():
#         print("TEST COOKIE WORKED!")
#         request.session.delete_test_cookie()
#     context_dict = {'mensajeAbout': "Este es el about"}
#     return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)


# def add_category(request):
#     form = CategoryForm()
#
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#
#         if form.is_valid():
#             form.save(commit=True)
#             return index(request)
#         else:
#             print(form.errors)
#     return render(request, 'rango/add_category.html', {'form': form})


class AddCategoryView(View):

    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm()
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
        return render(request, 'rango/add_category.html', {'form': form})



def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


# def register(request):
#
#     registered = False
#
#     if request.method == 'POST':
#         user_form = UserForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#                 profile.save()
#                 registered = True
#         else:
#             print(user_form.errors, profile_form.erros)
#     else:
#         user_form = UserForm()
#         profile_form = UserProfileForm()
#     return render(request, 'rango/register.html', {'user_form': user_form,
#                                                    'profile_form': profile_form,
#                                                   'registered': registered})


# def user_login(request):
#
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)
#
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#             else:
#                 return HttpResponse("Tu cuenta está desactivada.")
#         else:
#             print("Invalid login details: {0}, {1}".format(username, password))
#             # return HttpResponse("Invalid login details supplied.")
#             return render(request, 'rango/login.html', {'error_message':'Invalid username and/or password entered. Try again'})
#     else:
#         return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('index'))


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def goto_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

        try:
            page = Page.objects.get(id=page_id)
            page.views = page.views + 1
            page.save()
            url = page.url
        except:
            pass
    return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
    if form.is_valid():
        user_profile = form.save(commit=False)
        user_profile.user = request.user
        user_profile.save()
        return redirect('index')
    else:
        print(form.errors)
        context_dict = {'form': form}
    return render(request, 'rango/profile_registration.html', context_dict)


class AboutView(View):
    def get(self, request):
        # view logic
        visitor_cookie_handler(request)
        return render(request, 'rango/about.html',
                      context={'visits': request.session['visits']})


class ProfileView(View):
    def get_user_details(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect('index')

        userprofile = UserProfile.objects.get_or_create(user=user)[0]
        form = UserProfileForm({'website': userprofile.website,
                                'picture': userprofile.picture})
        return (user, userprofile, form)

    @method_decorator(login_required)
    def get(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        return render(request, 'rango/profile.html',
                               {'userprofile': userprofile,
                                   'selecteduser': user,
                                   'form': form})

    @method_decorator(login_required)
    def post(self, request, username):
        (user, userprofile, form) = self.get_user_details(username)
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)
            return render(request, 'rango/profile.html',
                          {'userprofile': userprofile,
                           'selecteduser': user,
                           'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()
    return render(request, 'rango/list_profiles.html',
                           {'userprofile_list': userprofile_list})
