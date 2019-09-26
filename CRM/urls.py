from django.urls import path, include
from django.contrib.auth import views as auth_views
from CRM.views import managers
from CRM.views import auth



auth_urlpatterns = ([
    path('', auth.CrmLoginRedirectView.as_view()),
    path('login/', auth_views.LoginView.as_view(template_name='CRM/auth/login.html'),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'redirect/',
        auth.CrmLoginRedirectView.as_view(),
        name='login-redirect'
    ),
    path(
            'password-change/',
            auth.PasswordChangeView.as_view(),
            name='password-change'
        ),
    path('profile/', auth.ProfileView.as_view(), name='profile'),
], 'accounts')

manager_urlpatterns = ([
    path('managers/', managers.ShowManagers.as_view(), name='managers')

], 'users')

urlpatterns = [
    path('', auth.CrmLoginRedirectView.as_view()),
    path('accounts/', include(auth_urlpatterns)),
    path('users/', include(manager_urlpatterns)),
]

