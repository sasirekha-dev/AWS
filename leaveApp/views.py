'''
            API endpoint for leave management
Query leavebalance by employee id, status, Overlap and
manger view by status, overlap, employee
As employee apply for leave
As Manager approve/ reject leave request and update status

'''
import json
import datetime
from govuk_bank_holidays.bank_holidays import BankHolidays
import numpy as np
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from leaveApp.models import LeaveHistory, Employee

# Create your views here.
MAX_ANNUAL_LEAVE = 30


def getempleave_list(request, workerid, status):
    '''Get Employee Leave List by Status
    keyword arguments:
    workerID - ID of worker
    staus - 'approved' (Approved)/'pending' (Pending)/'rejected' (Rejected)/'ALL'
    return:
    Json response
    List of leaves applied by worker
    '''
    try:
        emp_obj = Employee.objects.get(workerID=workerid)
        print('STATUS', status)

        if status == 'all':
            emp_leaves = list(
                LeaveHistory.objects.filter(workerID=emp_obj).values())
        elif status in ('approved', 'pending', 'rejected'):
            emp_leaves = list(LeaveHistory.objects.filter(
                workerID=emp_obj, status=status).values())
            result = LeaveHistory.objects.prefetch_related(
                'workerID').filter(status=status)
            for details in result:

                dump = json.dumps({'workerID': str(details.workerID.workerID),
                                  'leaveID': str(details.leaveID),
                                   'firstname': str(details.workerID.firstName),
                                   'lastname': str(details.workerID.lastName),
                                   'vacation_start_date': str(details.vacation_start_date),
                                   'vacation_end_date': str(details.vacation_end_date)}
                                  )
            return HttpResponse(dump, content_type='application/json')

        else:
            dump = json.dumps(
                {'Error': 'provide approved/rejected/pending'})
            return HttpResponse(dump, content_type='application/json')
        return JsonResponse(emp_leaves, safe=False)
    except ObjectDoesNotExist:
        dump = json.dumps({'Error': 'not found'})
        return HttpResponse(dump, content_type='application/json')


def calculateleavebalance(workerid):
    ''' Leave balance calculator
    input: worker idea

    return: count of leaves approved
    '''
    vacationdays = set()
    leaves = LeaveHistory.objects.filter(workerID=workerid)
    for leave in leaves:
        if leave.status == 'approved':
            dates = np.arange(leave.vacation_start_date.date(),
                              leave.vacation_end_date.date())
            vacationdays.update(dates)
    vacationdays_total = np.is_busday(
        list(vacationdays), holidays=bankholidays_UK()).sum()

    return vacationdays_total


def getleavebalance(request, workerid):
    '''Get Employee Leave List by workerID
    keyword arguments:
    workerID - ID of worker
    return:
    Json response
    {'leavesAvailed':..,'balance':...}
    '''
    vacationdays_total = 0
    try:
        emp = Employee.objects.get(workerID=workerid)
        vacationdays_total = calculateleavebalance(workerid)
        dump = json.dumps({'leavesavailed': str(vacationdays_total),
                           'balance': str((MAX_ANNUAL_LEAVE-vacationdays_total))})

    except ObjectDoesNotExist:
        dump = json.dumps({'error': 'Employee doesnot exist'})
    return HttpResponse(dump, content_type='application/json')


def leaverequest(request, workerid, startdate, enddate):
    '''Update leave based on start date and end date
    keyword arguments:
        workerID - ID of worker,
        startDate,
        endDate

    return:
        Json response
        {'status':..,'comments':...}
    '''
    startdate = datetime.datetime.strptime(startdate, "%m-%d-%Y")
    enddate = datetime.datetime.strptime(enddate, "%m-%d-%Y")

    emp = Employee.objects.get(workerID=workerid)
    mgr = emp.managerID
    vacationdays_total = calculateleavebalance(workerid)
    requestedleave = np.busday_count([startdate.date()], [enddate.date()],
                                     holidays=bankholidays_UK())
    if vacationdays_total+requestedleave <= MAX_ANNUAL_LEAVE:
        LeaveHistory.objects.create(workerID=emp, status='pending',
                                    vacation_start_date=startdate,
                                    vacation_end_date=enddate,
                                    request_created_at=datetime.datetime.now(),
                                    managerID=mgr)

        dump = json.dumps({'status': 'success'})

    else:
        dump = json.dumps({'status': 'failed',
                           'comment': 'pending available leave:'
                           + str(MAX_ANNUAL_LEAVE-vacationdays_total)
                           + ' but requested '+str(requestedleave)})
    return HttpResponse(dump, content_type='application/json')


def bankholidays_UK():
    '''UK bank holiday list
    keyword arguments:
        None
    return:
        UK bank holiday list
    '''

    bank_holiday_list = []
    bank_holidays = BankHolidays()
    for bank_holiday in bank_holidays.get_holidays():
        #print(bank_holiday['title'], 'is on', bank_holiday['date'])
        bank_holiday_list.append(bank_holiday['date'])
    return bank_holiday_list


def getemployee_requests_by_status(request, managerid, status):
    ''' manager to view list of leaves by status
    keyword arguments:
        manager ID, status (A (Approved)/P (pending))
    return:
        leaves list
    '''
    leaves = None
    if status == 'approved':
        leaves = list(LeaveHistory.objects.filter(
            managerID=managerid, status='approved').values())
    elif status == 'pending':
        leaves = list(LeaveHistory.objects.filter(
            managerID=managerid, status='pending').values())
    else:
        leaves = list(LeaveHistory.objects.filter(
            managerID=managerid).values())

    return JsonResponse(leaves, safe=False)


def groupdaterange(leavelist, idlist):
    ''' group the overlapping date ranges
    keyword arguments:
        leaves request filtered with managerID,leaveid list
    return:
        groups as dictionary
    '''
    print(leavelist)
    group = {}
    leaveindex = []
    while len(leavelist) != 0:
        for i, date in enumerate(leavelist):
            if i == 0:

                min1 = datetime.datetime.strptime(
                    str(date[0]), '%Y-%m-%d').date()
                max1 = datetime.datetime.strptime(
                    str(date[1]), '%Y-%m-%d').date()
                leaveindex.append(idlist[i])
                continue

            min2 = datetime.datetime.strptime(
                str(date[0]), '%Y-%m-%d').date()
            max2 = datetime.datetime.strptime(
                str(date[1]), '%Y-%m-%d').date()
            if (min1 >= min2 and max1 <= max2):
                min1 = min2
                max1 = max2
                leaveindex.append(idlist[i])

            # (max1>=min2 and max1<max2): # inbound
            elif min2 <= max1 < max2:
                max1 = max2
                leaveindex.append(idlist[i])

            elif min2 < min1 <= max2:  # (min1>min2 and min1<=max2):
                min1 = min2
                leaveindex.append(idlist[i])

            elif (min1 <= min2 and max1 >= max2):
                leaveindex.append(idlist[i])
                #print('in bound, but no change')
        group[str(min1)+'_'+str(max1)] = leaveindex
        temp = leavelist.copy()
        for _ in leaveindex:
            num = leavelist[idlist.index(_)]
            temp.remove(num)
        leavelist = temp.copy()
        for _ in leaveindex:
            idlist.remove(_)
            print(id)
        leaveindex = []

    return group


def getemployeeleaves_manager(request, managerid, workerid):
    ''' manager to view list of leaves by worker ID
    keyword arguments:
        manager ID,workerID
    return:
        leaves list
    '''
    leaves = LeaveHistory.objects.filter(Q(managerID=managerid)
                                         & Q(workerID=workerid)).values()
    if leaves:
        return JsonResponse(list(leaves), safe=False)
    else:
        dump = json.dumps({'Error': 'no records found'})
        return HttpResponse(dump, content_type='application/json')


def getoverlappingrequests(request, managerid):
    ''' manager to view list of overlapping leaves
    keyword arguments:
        manager ID
    return:
        leaves list
    '''
    leavelist = []
    idlist = []
    overlapleaveids = set()
    leaves = LeaveHistory.objects.filter(managerID=managerid)
    for leave in leaves:
        startdate = leave.vacation_start_date.date()
        enddate = leave.vacation_end_date.date()
        leavelist.append([startdate, enddate])
        idlist.append(leave.leaveID)
    leavegroup = groupdaterange(leavelist, idlist)
    subgroups = {}
    if len(leavegroup.keys()):
        for groupid, group in leavegroup.items():
            subgroups[groupid] = (
                list(LeaveHistory.objects.filter(leaveID__in=group).values()))
        print('------------------------->', subgroups)
        return JsonResponse(subgroups, safe=False)
    else:
        dump = json.dumps({'error': 'overlap records NOT found'})
        return HttpResponse(dump, content_type='application/json')


def updatestatus(request, leaveid, status):
    ''' update status depending on leave balance
    keyword arguments:
        leave ID, status (A (Approve)/P (pending)/R (reject))
    return:
        leaves list
    '''
    try:
        leave = LeaveHistory.objects.get(leaveID=leaveid)
        if leave and status == 'approved' and leave.status != 'approved':
            vacationdays_total = calculateleavebalance(leave.workerID)
            requestedleave = np.busday_count([leave.vacation_start_date.date()],
                                             [leave.vacation_end_date.date()],
                                             holidays=bankholidays_UK())
            print('total days', vacationdays_total+requestedleave)
            if vacationdays_total+requestedleave <= MAX_ANNUAL_LEAVE:
                leave.status = status
                leave.save()
            else:
                dump = json.dumps({'status': 'failed',
                                   'comment': 'pending available leave:' +
                                  str(MAX_ANNUAL_LEAVE -
                                      vacationdays_total)
                                   + ' but requested '+str(requestedleave)})

        elif leave and status == 'rejected':
            leave.status = status
            leave.save()

        dump = json.dumps({'status': 'success'})
        return HttpResponse(dump, content_type='application/json')
    except ObjectDoesNotExist:
        dump = json.dumps({'error': 'invalid leave request'})
        return HttpResponse(dump, content_type='application/json')
