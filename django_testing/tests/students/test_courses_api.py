import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student

@pytest.fixture
def user():
    return APIClient()

@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory
    

@pytest.mark.django_db  #проверка получения первого курса (retrieve-логика)
def test_course_filter(client, course_factory):
    courses = course_factory(_quantity = 1)
    course_id = courses[0].id
    response =  client.get(f'/api/v1/courses/{course_id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == courses[0].name
    
@pytest.mark.django_db #проверка получения списка курсов (list-логика)
def test_course_list(client, course_factory):
    courses = course_factory(_quantity = 5)
    response =  client.get('/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    for k, v in enumerate(data):
        assert v['name'] == courses[k].name
            
@pytest.mark.django_db #проверка фильтрации списка курсов по id
def test_course_one(client, course_factory):
    courses = course_factory(_quantity = 5)
    response =  client.get(f'/api/v1/courses/', data={'id': courses[0].id})
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name
    
@pytest.mark.django_db #проверка фильтрации списка курсов по name;
def test_course_filter_name(client, course_factory):
    courses = course_factory(_quantity = 5)
    response =  client.get(f'/api/v1/courses/', data={'name': courses[0].name})
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == courses[0].name
    
@pytest.mark.django_db #тест успешного создания курса
def test_course_create(client):
    Student_1 = Student.objects.create(name = 'Oleg', birth_date = '1997-01-01')
    Student_2 = Student.objects.create(name = 'Vova', birth_date = '1994-01-01')
    response = client.post(f'/api/v1/courses/', data={
        'name': 'first_one',
        'students' : [Student_1.id, Student_2.id]
        })
    assert response.status_code == 201
    
@pytest.mark.django_db #тест успешного обновления курса
def test_course_update(client, course_factory):   
    student = Student.objects.create(name='Student_1', birth_date='1993-01-10')
    course = course_factory(_quantity=4)
    response = client.patch(f'/api/v1/courses/{course[0].id}/', data={
        'students': [student.id]
    }, content_type='application/json')
    assert response.status_code == 200
    data = response.json()
    assert data['students'] == [student.id]
    
@pytest.mark.django_db #тест успешного удаления курса
def test_course_delete(client, course_factory):
    course = course_factory(_quantity=4)
    response = client.delete(f'/api/v1/courses/{course[0].id}/')
    assert response.status_code == 204


@pytest.mark.django_db #Ограничить число студентов на курсе    
def test_with_specific_settings(client, settings, student_factory):
    students = student_factory(_quantity=15)
    settings.MAX_STUDENTS_PER_COURSE = 20
    response = client.post(f'/api/v1/courses/', data={
    'name': 'first_one',
    'students' : [i.id for i in students]
    })
    data = response.json()
    assert settings.MAX_STUDENTS_PER_COURSE >= len(data['students'])