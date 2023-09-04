from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, TemplateView, DetailView, ListView, UpdateView

from .forms import UserAvatarForm
from .models import Profile


def about_me_view(request):
    context = {}
    template_name = "myauth/about-me.html"
    if request.method == "GET":
        obj = get_object_or_404(Profile, pk=Profile.objects.get(user_id=request.user.id).pk)
        form = UserAvatarForm(instance=obj)
    if request.method == "POST":
        form = UserAvatarForm(request.POST)
        print('form - ', form)
        if form.is_valid():
            form.save()
    context['form'] = form
    return render(request, template_name, context)


class AboutMeView(TemplateView):
    model = Profile
    template_name = "myauth/about-me.html"
    form_class = UserAvatarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.filter(user=self.request.user).first()
        context['user'] = self.request.user
        context['profile'] = profile
        context['form'] = self.form_class(self.request.GET, instance=profile)
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        profile = Profile.objects.filter(user=self.request.user).first()
        form = self.form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
        return render(request, self.template_name, self.get_context_data(**kwargs))


class UserListView(ListView):
    model = Profile
    template_name = "myauth/users-list.html"
    context_object_name = "profiles"


class UserDetailView(DetailView):
    template_name = "myauth/user-details.html"
    model = Profile
    context_object_name = "profile"


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Profile
    template_name = "myauth/user-update.html"
    context_object_name = "profile"
    fields = ('avatar',)

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse(
            "myauth:user_details",
            kwargs={"pk": self.object.pk}
        )


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('shopapp:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)
        return response


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("msg", "Hello", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("msg", "default value")
    return HttpResponse(f"Cookie value: {value}")


def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spamaggs"
    return HttpResponse("Settion set!")


def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value}")


