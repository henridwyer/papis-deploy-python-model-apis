import os
import joblib
from celery import Celery

# Set up celery
CELERY_BROKER_URL = 'redis://redis'
CELERY_RESULT_BACKEND = 'redis://redis'

celery = Celery('predict', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)
celery.conf.update()

# Load the model
if os.environ.get('CELERY_WORKER'):
    model = joblib.load('model.pkl')

@celery.task
def predict_text(text):
    """Get the prediction from the model."""
    prediction = model.predict_proba([text]).tolist()[0]
    return prediction
