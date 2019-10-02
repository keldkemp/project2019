from django.urls import path, include
from django.contrib.auth import views as auth_views
from CRM.views import auth, users, qualifications


auth_urlpatterns = ([
    path('', auth.CrmLoginRedirectView.as_view()),
    path('login/', auth_views.LoginView.as_view(template_name='CRM/auth/login.html'),
         name='login'),
    path('logout/', auth.CrmLogoutView.as_view(), name='logout'),
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
    path('password-change-first/', auth.PasswordChangeFirsView.as_view(), name='password-change-first'),
    path('password-change-done/', auth.PasswordChangeDoneView.as_view(), name='password-change-done'),
    path('profile/', auth.ProfileView.as_view(), name='profile'),
], 'accounts')

users_urlpatterns = ([
    path('', users.ShowUsers.as_view(), name='list'),
    path('add/', users.CreateUser.as_view(), name='add'),
    path('add/password-see/', users.PasswordSee.as_view(), name='password-see'),

], 'users')

qualifications_urlpatterns = ([
    path('', qualifications.ShowQualification.as_view(), name='list'),
    path('add/', qualifications.CreateQualifications.as_view(), name='add'),
    path('<int:pk>/', qualifications.DetailQualifications.as_view(), name='detail'),
    path('<int:pk>/update/', qualifications.UpdateQualifications.as_view(), name='update'),
    path('<int:pk>/delete/', qualifications.DeleteQualifications.as_view(), name='delete'),
], 'qualifications')

urlpatterns = [
    path('', auth.CrmLoginRedirectView.as_view()),
    path('accounts/', include(auth_urlpatterns)),
    path('users/', include(users_urlpatterns)),
    path('qualifications/', include(qualifications_urlpatterns)),
]

