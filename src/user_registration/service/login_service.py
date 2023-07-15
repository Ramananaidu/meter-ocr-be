from fastapi import FastAPI, status, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import src.user_registration.schema as schema
from src.user_registration.settings import get_db, logger
from src.user_registration.model import Users
from src.user_registration.utils.utils import get_hashed_password, create_access_token, verify_password
from src.user_registration.face_registration import FaceRecognition

app = FastAPI()


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

# let's create router
router = APIRouter(
    prefix='/login',
    tags=['User Management']
)


@router.post('/face_signup', status_code=status.HTTP_201_CREATED)
def Face_SignUp(payload: schema.UserSignup, images: schema.FaceImages, db: Session = Depends(get_db)):
    try:
        logger.info("Signup process started")
        query = db.query(Users).filter(Users.email == payload.email).all()
        print("payload",payload)
        print("query",query)
        logger.info('data')
        if len(query) == 0:
            print("inside if")
            user_data = {
                'email': payload.email,
                'password': get_hashed_password(payload.password),
                'username':payload.username,
                'first_name':payload.first_name,
                'last_name':payload.last_name
            }
            
            new_note = Users(**user_data)
            print("new_note",new_note)

            db.add(new_note)

            # Add face embeddings to the database
            fr = FaceRecognition(db)
            fr.run_face_recognition(images.images, payload.username)

            db.commit()
            db.refresh(new_note)
            data = {
                'response_code': 200,
                'Status': 'Success',
                'data': []
            }
            logger.info("Signup process finished")
            return data
        else:
            data = {
                'response_code': 400,
                'Status': 'Failed',
                'data': []
            }
            logger.error("Signup process failed")
            return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed',
            'data': str(e)
        }
        logger.error("Signup process failed")
        return data

@router.post('/signup', status_code=status.HTTP_201_CREATED)
def SignUp(payload: schema.UserSignup, db: Session = Depends(get_db)):
    try:
        logger.info("Signup process started")
        query = db.query(Users).filter(Users.email == payload.email).all()
        print("payload",payload)
        print("query",query)
        logger.info('data')
        if len(query) == 0:
            print("inside if")
            user_data = {
                'email': payload.email,
                'password': get_hashed_password(payload.password),
                'username':payload.username,
                'first_name':payload.first_name,
                'last_name':payload.last_name
            }
            
            new_note = Users(**user_data)
            print("new_note",new_note)
            '''
            The ** operator in Python is used to unpack a dictionary. 
            So, Users(**user_data) is equivalent to Users(email='example@example.com', password='hashed_password') 
            if user_data is {'email': 'example@example.com', 'password': 'hashed_password'}.
            '''
            db.add(new_note)
            db.commit()
            db.refresh(new_note)
            data = {
                'response_code': 200,
                'Status': 'Success',
                'data': []
            }
            logger.info("Signup process finished")
            return data
        else:
            data = {
                'response_code': 400,
                'Status': 'Failed',
                'data': []
            }
            logger.error("Signup process failed")
            return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed',
            'data': str(e)
        }
        logger.error("Signup process failed")
        return data


@router.post('/login')
def Login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        query = db.query(Users).filter(Users.email == form_data.username).all()
        if not query[0].email:
            data = {
                'response_code': 400,
                'Status': 'Failed',
                'data': 'Email does not exists!!'
            }
            return data
        hashed_pass = query[0].password
        if not verify_password(form_data.password, hashed_pass):
            data = {
                'response_code': 400,
                'Status': 'Failed',
                'data': 'Email (or) Password wrong!!'
            }
            return data
        access_token = create_access_token(query[0].email)
        # refresh_token = create_refresh_token(query[0].email)
        data = {
            'response_code': 200,
            'Status': 'Success',
            'data': {
                'access_token': access_token,
                # 'refresh_token': refresh_token,
            }
        }
        print(data)
        return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed or Internal server error',
            'data': str(e)
        }
        return data


@router.put('/update_password')
def Update_password(payload: schema.UpdatePassword, db: Session = Depends(get_db),
                    token: str = Depends(reuseable_oauth)):
    try:
        query = db.query(Users).filter(Users.email == payload.email)
        if not query[0].email:
            data = {
                'response_code': 400,
                'Status': 'Not a valid user',
                'data': []
            }
            return data
        hashed_password = query[0].password
        if not verify_password(payload.old_password, hashed_password):
            data = {
                'response_code': 400,
                'Status': 'Old password not matching!!',
                'data': []
            }
            return data
        update_pass = get_hashed_password(payload.new_password)
        query.update({'password': update_pass})
        # query[0].password =
        db.commit()
        # db.refresh(update_pass)
        data = {
            'response_code': 200,
            'Status': 'Success',
            'data': 'password changed successfully!!'
        }
        return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed',
            'data': f'Internal Server Error, str({e})'
        }
        return data


@router.post('/forgot_password')
def Forgot_password(payload: schema.ForgotPassword, db: Session = Depends(get_db)):
    try:
        query = db.query(Users).filter(Users.email == payload.email)
        if not query:
            data = {
                'response_code': 400,
                'Status': "You're not a user!!",
                'data': []
            }
            return data
        otp_value = 5678
        query.update({'phone_number': otp_value})
        db.commit()
        data = {
            'response_code': 200,
            'Status': 'Success',
            'data': 'OTP sent successfully!!'
        }
        return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed',
            'data': f'Internal Server Error, str({e})'
        }
        return data


@router.post('/reset_password')
def Reset_password(payload: schema.ResetPassword, db: Session = Depends(get_db)):
    try:
        query = db.query(Users).filter(Users.email == payload.email)
        if not query:
            data = {
                'response_code': 400,
                'Status': "You're not a user!!",
                'data': []
            }
            return data
        if not query[0].phone_number == payload.otp:
            data = {
                'response_code': 400,
                'Status': "OTP not matching!!, Please give the valid OTP",
                'data': []
            }
            return data
        new_pass = get_hashed_password(payload.password)
        query.update({'password': new_pass})
        db.commit()
        data = {
            'response_code': 200,
            'Status': 'Success',
            'data': 'password updated successfully!!'
        }
        return data
    except Exception as e:
        data = {
            'response_code': 500,
            'Status': 'Failed',
            'data': f'Internal Server Error, str({e})'
        }
        return data
