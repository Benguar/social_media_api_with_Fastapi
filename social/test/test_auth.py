from social.test.config_test import fake_user_service,fake_session,test_client
from social import version

#i want to check if the user is created successfully and if the password is hashed and not stored in plain text

def test_create_user(fake_session,fake_user_service,test_client):
    data = {
            "username": "Benguar",
            "email": "iqmbenzy@gmail.com",
            "password": "You dont wanna know"
        }
    response = test_client.post(
        url=f"/social/users/{version}/add_user",
        json= data
    )
    assert response.status_code == 201
    
