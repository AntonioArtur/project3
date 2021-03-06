import os
import pandas as pd
from src.ml.data import process_data
from src.ml.model import load_model, load_encoder, load_lb, inference
from fastapi import FastAPI
from pydantic import BaseModel


if "DYNO" in os.environ and os.path.isdir(".dvc"):
    os.system("dvc config core.no_scm true")
    if os.system("dvc pull") != 0:
        exit("dvc pull failed")
    os.system("rm -r .dvc .apt/usr/lib/dvc")


app = FastAPI()


class User(BaseModel):
    age: int
    workclass: str
    fnlgt: int
    education: str
    education_num: int
    marital_status: str
    occupation: str
    relationship: str
    race: str
    sex: str
    capital_gain: int
    capital_loss: int
    hours_per_week: int
    native_country: str

    class Config:
        schema_extra = {
            "example": {
                        "age": 39,
                        "workclass": "State-gov",
                        "fnlgt": 77516,
                        "education": "Bachelors",
                        "education_num": 13,
                        "marital_status": "Never-married",
                        "occupation": "Adm-clerical",
                        "relationship": "Not-in-family",
                        "race": "White",
                        "sex": "Male",
                        "capital_gain": 2174,
                        "capital_loss": 0,
                        "hours_per_week": 40,
                        "native_country": "United-States"
            }
        }


@app.get("/")
async def info():
    return {"author": "antonio artur",
            "date": "2022 mar 28",
            "local": "brazil"}


@app.post("/inference")
async def inference_api(user: User):

    model = load_model("model/model.pkl")
    encoder = load_encoder("model/encoder.pkl")
    lb = load_lb("model/lb.pkl")

    cat_features = [
                "workclass",
                "education",
                "marital-status",
                "occupation",
                "relationship",
                "race",
                "sex",
                "native-country",
            ]

    data = [user.age, user.workclass, user.fnlgt, user.education,
            user.education_num, user.marital_status, user.occupation,
            user.relationship, user.race, user.sex, user.capital_gain,
            user.capital_loss, user.hours_per_week, user.native_country]

    columns = ['age', 'workclass', 'fnlgt', 'education', 'education-num',
               'marital-status', 'occupation', 'relationship', 'race', 'sex',
               'capital-gain', 'capital-loss',
               'hours-per-week', 'native-country']

    df = pd.DataFrame([dict(zip(columns, data))])

    print(df)
    print(df.columns)

    X, _, _, _ = process_data(df, categorical_features=cat_features,
                              training=False, encoder=encoder, lb=lb)

    predictions = inference(model, X)
    predictions = lb.inverse_transform(predictions)[0]
    return {"prediction": predictions}
