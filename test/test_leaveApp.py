import pytest
import datetime
import json
from leaveApp.models import Employee, LeaveHistory
from django.urls import reverse
from leaveApp.views import getempleave_list


@pytest.mark.django_db
def test_employeedb():
    mgr1 = Employee.objects.create(workerID=100, firstName='raja', lastName='s')
    mgr2 = Employee.objects.create(workerID=200, firstName='sasi', lastName='s')
    emp1 = Employee.objects.create(workerID=300, firstName='sam', lastName='s',
                                   managerID=mgr1)
    emp2 = Employee.objects.create(workerID=301, firstName='John', lastName='j',
                                   managerID=mgr1)
    emp3 = Employee.objects.create(workerID=302, firstName='mike', lastName='m',
                                   managerID=mgr2)

    lr1 = LeaveHistory.objects.create(leaveID=1, workerID=emp1,
                                      status='pending', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 10, 9, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 10, 10, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 10, 12, 23, 55, 59, 342380))

    lr2 = LeaveHistory.objects.create(leaveID=2, workerID=emp1,
                                      status='pending', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 11, 10, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 10, 12, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 10, 12, 23, 55, 59, 342380))

    lr5 = LeaveHistory.objects.create(leaveID=5, workerID=emp1,
                                      status='rejected', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 12, 29, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 12, 29, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 12, 29, 23, 55, 59, 342380))

    lr3 = LeaveHistory.objects.create(leaveID=3, workerID=emp2,
                                      status='approved', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 11, 9, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 11, 10, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 11, 13, 23, 55, 59, 342380))

    lr4 = LeaveHistory.objects.create(leaveID=4, workerID=emp2,
                                      status='approved', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 11, 9, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 11, 6, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 11, 13, 23, 55, 59, 342380))

    lr6 = LeaveHistory.objects.create(leaveID=6, workerID=emp2,
                                      status='pending', managerID=mgr1,
                                      request_created_at=datetime.datetime(
                                          2022, 11, 9, 23, 55, 59, 342380),
                                      vacation_start_date=datetime.datetime(
                                          2022, 12, 1, 22, 55, 59, 342380),
                                      vacation_end_date=datetime.datetime(2022, 12, 30, 23, 55, 59, 342380))

    assert Employee.objects.count() == 5
    assert LeaveHistory.objects.count() == 6


@pytest.mark.django_db
def test_getempleave_list_1(client):
    test_employeedb()
    response = client.get('/getleaves/300/all/')
    print('TEST_1', response.json())
    assert response.json()[0]['leaveID'] == 1
    assert response.json()[1]['leaveID'] == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_getempleave_list_2(client):
    test_employeedb()
    response = client.get('/getleaves/300/pending/')
    assert response.json()[0]['leaveID'] == 1
    assert response.json()[1]['leaveID'] == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_getempleave_list_3(client):
    test_employeedb()
    response = client.get('/getleaves/300/approved/')
    assert len(response.json()) == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_getempleave_list_4(client):
    test_employeedb()
    response = client.get('/getleaves/300/rejected/')
    assert len(response.json()) == 1
    assert response.status_code == 200


@pytest.mark.django_db
def test_getempleave_list_5(client):
    test_employeedb()
    response = client.get('/getleaves/100/all/')
    assert len(response.json()) == 0
    assert response.status_code == 200


@pytest.mark.django_db
def test_getempleave_list_6(client):
    test_employeedb()
    response = client.get('/getleaves/400/approved/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_getLeaveBalance_1(client):
    test_employeedb()
    response = client.get('/getleavebalance/300/')
    json_response = json.loads(response.content)
    assert json_response['balance'] == '30'


@pytest.mark.django_db
def test_getLeaveBalance_2(client):
    test_employeedb()
    response = client.get('/getleavebalance/400/')
    json_response = json.loads(response.content)
    assert json_response['error'] == 'Employee doesnot exist'


@pytest.mark.django_db
def test_getLeaveBalance_3(client):
    test_employeedb()
    response = client.get('/getleavebalance/301/')
    json_response = json.loads(response.content)
    print('-*-', json_response)
    assert json_response['leavesavailed'] == '5'


@pytest.mark.django_db
def test_leaveRequest_1(client):
    test_employeedb()
    startdate = '11-25-2022'
    enddate = '11-27-2022'
    api = '/requestLeave/100/'+startdate+'/'+enddate+'/'
    print(api)
    response = client.get(api)
    json_response = json.loads(response.content)
    assert json_response['status'] == 'success'
    leave = LeaveHistory.objects.get(vacation_start_date=datetime.datetime.strptime(startdate, "%m-%d-%Y"),
                                     vacation_end_date=datetime.datetime.strptime(enddate, "%m-%d-%Y"))
    status = leave.status
    assert status == 'pending'


@pytest.mark.django_db
def test_leaveRequest_2(client):
    test_employeedb()
    startdate = '11-25-2022'
    enddate = '11-27-2022'
    api = '/requestLeave/100/'+startdate+'/'+enddate+'/'
    response = client.get(api)
    json_response = json.loads(response.content)
    assert json_response['status'] == 'success'
    leave = LeaveHistory.objects.get(vacation_start_date=datetime.datetime.strptime(startdate, "%m-%d-%Y"),
                                     vacation_end_date=datetime.datetime.strptime(enddate, "%m-%d-%Y"))
    status = leave.status
    assert status == 'pending'


@pytest.mark.django_db
def test_getoverlappingrequests_1(client):
    test_employeedb()
    response = client.get('/getOverlapLeaves/100/')
    response = json.loads(response.content)
    print('**********', response)
    assert len(response) == 3


@pytest.mark.django_db
def test_getoverlappingrequests_2(client):
    test_employeedb()
    response = client.get('/getOverlapLeaves/300/')
    response = json.loads(response.content)
    print(response)
    assert response['error'] == 'overlap records NOT found'


@pytest.mark.django_db
def test_getEmployeeRequests_1(client):
    test_employeedb()
    response = client.get('/getEmployeeRequests/100/pending/')
    response = json.loads(response.content)
    assert len(response) == 3


@pytest.mark.django_db
def test__getEmpLeavesOverview1(client):
    test_employeedb()
    response = client.get('/getEmpLeavesOverview/100/300/')
    response = json.loads(response.content)
    assert len(response) == 3


@pytest.mark.django_db
def test__updateStatus_1(client):
    test_employeedb()
    json_response = json.loads(client.get('/updateStatus/3/rejected/').content)
    assert json_response['status'] == 'success'
    leave = LeaveHistory.objects.get(leaveID=3)
    status = leave.status
    assert status == 'rejected'


@pytest.mark.django_db
def test__updateStatus_2(client):
    test_employeedb()
    json_response = json.loads(client.get('/updateStatus/6/approved/').content)
    assert json_response['status'] == 'success'
    leave = LeaveHistory.objects.get(leaveID=6)
    assert leave.status == 'approved'
