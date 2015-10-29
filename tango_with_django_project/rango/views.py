from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query


def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Query database for list of all categories stored
    # List is placed in context_dict to be passed to template engine
    page_list = Page.objects.order_by('-views')[:5]
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'boldmessage': "Taking the 'Dry' out of 'Dry Country'.",
                    'categories': category_list,
                    'pages': page_list,
                    }

    # Server side cookies
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        las_visit_time = datetime.strptime(last_visit[: -7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - las_visit_time).seconds > 60:
            visits += 1
            reset_last_visit_time = True
    # 'last visit' cookie doesn't exist, create it
    else:
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits

    # Add cookie 'visit' tally to dict
    context_dict['visits'] = visits
    response = render(request, 'rango/index.html', context_dict)
    # Return a rendered response to send to the client.
    return response


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict = {'visits': count}
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    context_dict = {'category_name_slug': category_name_slug}

    try:
        # Find a category name slug with the given name
        # If not, .get() raises a DoesNotExist exception
        # .get() method returns model instance, or raises exception
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all associated pages.
        # Filter returns >= 1 model instance
        pages = Page.objects.filter(category=category)

        # Adds results list to template context under name pages
        context_dict['pages'] = pages

        # Add category object from database to context dictionary
        # Used in template to verify category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        # If specified category is not found
        # Do nothing. 'No category" displayed
        pass

    # Render response and return it to client
    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    # HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Form valid?
        if form.is_valid():
            # Save new category to database
            form.save(commit=True)

            # call index(), show homepage
            return index(request)
        else:
            # form had errors, print to terminal
            print form.errors
    else:
        # if request wasn't a POST, display form to enter details
        form = CategoryForm()

    # bad form or details, no form supplies
    # render form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here
                return HttpResponseRedirect('/rango/')
                # return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run Bing function to get the results list
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

#def register(request):
#    If registration successful, registered changes to True
#    registered = False
#
#   if request.method == 'POST':
#        user_form = UserForm(data=request.POST)
#        profile_form = UserProfileForm(data=request.POST)
#
#        if user_form.is_valid() and profile_form.is_valid():
#            user = user_form.save()
#            user.set_password(user.password)
#            user.save()
#            profile = profile_form.save(commit=False)
#            profile.user = user
#
#            if 'picture' in request.FILES:
#                profile.picture = request.FILES['picture']
#
#            profile.save()
#            registered = True
#        else:
#            print user_form.errors, profile_form.errors
#
#    else:
#        user_form = UserForm()
#        profile_form = UserProfileForm()
#
#    return render(request,
#                  'rango/register.html',
#                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})
#
#
#def user_login(request):
#    if request.method == 'POST':
#        username = request.POST.get('username')
#        password = request.POST.get('password')
#        user = authenticate(username=username, password=password)
#
#        if user:
#            if user.is_active:
#                login(request, user)
#                return HttpResponseRedirect('/rango/')
#            else:
#                HttpResponse("Your Rango account is disabled.")
#        else:
#            print "Invalid login details: {0}, {1}".format(username, password)
#            return HttpResponse("Hmm... Looks like a username or password doesn't match.  Those \
#            phone touchscreens can be a pain. Go back and give it another shot.")
#    else:
#        return render(request, 'rango/login.html', {})
#

@login_required
def restricted(request):
    context_dict = {}
    return render(request, 'rango/restricted.html', {})


#@login_required
#def user_logout(request):
#    logout(request)
#    return HttpResponseRedirect('/rango/')


