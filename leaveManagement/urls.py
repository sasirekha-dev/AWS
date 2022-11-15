"""leaveManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from leaveApp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('getleaves/<int:workerid>/<str:status>/',
         views.getempleave_list, name='getleaves'),
    path('getleavebalance/<int:workerid>/', views.getleavebalance),
    path('requestLeave/<int:workerid>/<str:startdate>/<str:enddate>/',
         views.leaverequest),
    path('getEmployeeRequests/<int:managerid>/<str:status>/',
         views.getemployee_requests_by_status),
    path('getEmpLeavesOverview/<int:managerid>/<int:workerid>/',
         views.getemployeeleaves_manager),
    path('getOverlapLeaves/<int:managerid>/', views.getoverlappingrequests),
    path('updateStatus/<int:leaveid>/<str:status>/', views.updatestatus),
]
