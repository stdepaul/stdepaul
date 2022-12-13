from django.contrib import admin
from django.urls import path, include

from root_app import views as root_views
from wiki import views as wiki_views

from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-home', root_views.api_home, name='api_home'),

    path('accounts/', include('allauth.urls')),
    #path('martor/', include('martor.urls')),

    path('', root_views.home, name='home'),
   
    path('about', root_views.about, name='about'),
    
    path('terms', root_views.terms, name='terms'),
    path('privacy', root_views.privacy, name='privacy'),
    path('rules', root_views.rules, name='rules'),

    # stdepaul.org/assistance/us-tx-dallas/food-assistance/ <-- button here, "create wiki entry"

    path('profile/<slug:user>/', root_views.profile, name='profile'),
    path('edit-profile/<slug:slug>/', login_required(root_views.ProfileUpdateView.as_view()), name='update_profile'),

    path('messages/inbox/', login_required(root_views.inbox), name='messages_inbox'),
    path('messages/', include('django_messages.urls')),

    path('become-a-helper', login_required(root_views.HelperCreateView.as_view()), name='helper_create'),
    path('my-organizations', login_required(root_views.my_organizations), name='helper_list'),
    path('help/<slug:location>/helper/<int:pk>/<slug:slug>', root_views.HelperDetailView.as_view(), name='helper_detail'),
    path('help/<slug:location>/helper/update/<int:pk>/<slug:slug>', login_required(root_views.HelperUpdateView.as_view()), name='helper_update'),
    path('help/<slug:location>/helper/delete/<int:pk>/<slug:slug>', login_required(root_views.HelperDeleteView.as_view()), name='helper_delete'),

    path('help/<slug:location>/', root_views.posts, name='posts_home'),
    # stdepaul.org/help/us-tx-dallas/?help-types=food-assistance+housing-assistance

    path('help/<slug:location>/post/create', login_required(root_views.PostCreateView.as_view()), name='post_create'),
    path('help/<slug:location>/post/<int:pk>/<slug:slug>', root_views.PostDetailView.as_view(), name='post_detail'),
    path('help/<slug:location>/post/update/<int:pk>/<slug:slug>', login_required(root_views.PostUpdateView.as_view()), name='post_update'),
    path('help/<slug:location>/post/delete/<int:pk>/<slug:slug>', login_required(root_views.PostDeleteView.as_view()), name='post_update'),

    path('help/<slug:location>/wiki', wiki_views.wiki_home, name='wiki_home'),
    path('help/<slug:location>/wiki/entry/create/', login_required(wiki_views.WikiEntryCreateView.as_view()), name='wiki_entry_create'),
    path('help/<slug:location>/wiki/<int:pk>/<slug:slug>', wiki_views.WikiEntryDetailView.as_view(), name='wiki_entry_detail'),
    path('help/<slug:location>/wiki/update/<int:pk>/<slug:slug>', login_required(wiki_views.WikiEntryUpdateView.as_view()), name='wiki_entry_update'),
    # path('help/<slug:location>/wiki/delete/<int:pk>/<slug:slug>', login_required(wiki_views.WikiEntryDeleteView.as_view()), name='wiki_entry_update'),

    path('comment/create/', login_required(root_views.CommentCreateView.as_view()), name='comment_create'),
    path('comment/delete/<int:pk>/', login_required(root_views.CommentDeleteView.as_view()), name='comment_delete'),

    path('become-a-moderator', login_required(root_views.become_a_moderator), name='become-a-moderator'),

    #path('search', root_views.search, name='search'),


]
