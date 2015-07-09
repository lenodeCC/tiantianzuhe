from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns
from tiantianzuhe import views
urlpatterns = patterns('',
    url(r'^createtoken/$', views.CreateToken.as_view()),
    url(r'^reg/$', views.Reg.as_view()),
    url(r'^isreged/$', views.IsReged.as_view()),
    url(r'^login/$', views.Login.as_view()),
    url(r'^thirdlogin/$', views.ThirdLogin.as_view()),
    url(r'^forgetpw/$', views.ForgetPW.as_view()),
    url(r'^getbanner/$', views.GetBanner.as_view()),
    url(r'^makemessage/$', views.MakeMessage.as_view()),
    url(r'^getmessage/$', views.GetMessage.as_view()),
    url(r'^getmessageusers/$', views.GetMessageUsers.as_view()),
    url(r'^findfriends/$', views.FindUsers.as_view()),
    url(r'^raisegroup/$', views.RaiseGroup.as_view()),
    url(r'^colgroup/$', views.ColGroup.as_view()),
    url(r'^removegroup/$', views.RemoveGroup.as_view()),
    url(r'^getgroups/$', views.GetGroups.as_view()),                       
    url(r'^makecomment/$', views.MakeComment.as_view()),
    url(r'^makecommenttocomment/$', views.MakeCommentToComment.as_view()),
    url(r'^getcommentlist/$', views.GetCommentList.as_view()),
    url(r'^getcommentlisttocomment/$', views.GetCommentListToComment.as_view()),
    url(r'^getgroupofmonth/$', views.GetGroupOfMonth.as_view()),
    url(r'^getgroupofday/$', views.GetGroupOfDay.as_view()),
    url(r'^getzuhedetail/$', views.GetZuheDetail.as_view()),
    url(r'^deftheday/$', views.DefTheDay.as_view()),                       
    url(r'^gethelp/$', views.GetHelp.as_view()), 
    url(r'^gettiantianhelp/$', views.GetTiantianHelp.as_view()),
    url(r'^getzuhehelp/$', views.GetZuheHelp.as_view()),


                       
    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)
