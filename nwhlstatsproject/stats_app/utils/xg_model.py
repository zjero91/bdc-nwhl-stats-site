import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from stats_app.utils.load_base_data import TEAM_MODEL_DATA

def create_model():
    data = TEAM_MODEL_DATA.copy()
    
    corsi = ['Shot', 'Goal']
    data = data[data['Event'].isin(corsi)]
    data = data[data['state'] == '5v5']

    independent = data[['is_home', 'seconds', 'distance', 'angle', 'Detail 1', 'Detail 2', 'Detail 3', 'Detail 4',
                        'time_prev', 'prev_team', 'prev_event', 'is_rebound', 'is_rush']]
    dependent = data['is_goal']

    independent = pd.get_dummies(independent)

    x_train, x_test, y_train, y_test = train_test_split(independent, dependent, test_size=0.2, random_state=113)
    
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_train)

    model = LogisticRegression(random_state=202, max_iter=500)
    model.fit(x_scaled, y_train)
    
    model_cols = independent.columns.tolist()
    
    return model, model_cols, scaler

def calculate_xg(data):
    independent = data[['is_home', 'seconds', 'distance', 'angle', 'Detail 1', 'Detail 2', 'Detail 3', 'Detail 4',
                        'time_prev', 'prev_team', 'prev_event', 'is_rebound', 'is_rush']]

    independent = pd.get_dummies(independent)
    
    independent = independent.reindex(columns=XG_MODEL_COLS, fill_value=0)
    
    in_scaled = XG_MODEL_SCALAR.transform(independent)
    
    dependent_pred = XG_MODEL.predict_proba(in_scaled)[:, 1]

    return pd.DataFrame({
        'event_id': data['event_id'].values,
        'xg': dependent_pred
    })

XG_MODEL, XG_MODEL_COLS, XG_MODEL_SCALAR = create_model()