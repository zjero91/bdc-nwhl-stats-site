from django.conf import settings
import pandas as pd
import duckdb
import os

def load_raw_data():
    data_file_name = "olympic_womens_dataset.csv"
    data_file_path = os.path.join(settings.BASE_DIR, 'stats_app', 'data', data_file_name)
    raw_data = pd.read_csv(data_file_path)
    
    return raw_data

def load_team_model_data():
    raw_data = RAW_DATA.copy()
    
    raw_data = raw_data[raw_data['Team'].str.contains('Olympic')].copy()
    raw_data['Team'] = raw_data['Team'].str.replace('Olympic (Women) - ', '')
    raw_data['Home Team'] = raw_data['Home Team'].str.replace('Olympic (Women) - ', '')
    raw_data['Away Team'] = raw_data['Away Team'].str.replace('Olympic (Women) - ', '')
    
    team_model_data = duckdb.sql("""
        SELECT
            DENSE_RANK() OVER(ORDER BY game_date, "Home Team") AS game_id,
            DENSE_RANK() OVER(ORDER BY "Home Team") AS home_team_id,
            DENSE_RANK() OVER(ORDER BY "Away Team") AS away_team_id,
            DENSE_RANK() OVER(ORDER BY "Team") AS team_id,
            ROW_NUMBER() OVER(ORDER BY game_date, "Home Team", "Period", "Clock" ASC) AS event_id,
            CASE
                WHEN "Team" = "Home Team"
                THEN 1
                ELSE 0
            END AS is_home,
            CAST(SPLIT_PART("Clock", ':', 1) AS INTEGER) * 60 +
            CAST(SPLIT_PART("Clock", ':', 2) AS INTEGER) AS seconds,
            CASE
                WHEN "Team" = "Home Team"
                THEN "Home Team Skaters" || 'v' || "Away Team Skaters"
                WHEN "Team" = "Away Team"
                THEN "Away Team Skaters" || 'v' || "Home Team Skaters"
            END AS state,
            CASE
                WHEN "Team" = "Home Team"
                THEN "Home Team Goals" - "Away Team Goals"
                WHEN "Team" = "Away Team"
                THEN "Away Team Goals" - "Home Team Goals"
            END AS goal_diff,
            CASE
                WHEN "Event" = 'Goal'
                THEN 1
                ELSE 0
            END AS is_goal,
            SQRT(POWER("X Coordinate" - 189, 2) + POWER("Y Coordinate" - 42.5,2))
            AS distance,
            DEGREES(
                ACOS(
                    ((189 - "X Coordinate") * (189 - "X Coordinate") + (39.5 - "Y Coordinate") * (45.5 - "Y Coordinate")) /
                    (SQRT(POWER(189 - "X Coordinate", 2) + POWER(39.5 - "Y Coordinate", 2)) *
                    SQRT(POWER(189 - "X Coordinate", 2) + POWER(45.5 - "Y Coordinate", 2)))
                )
            ) AS angle,
            *
        FROM raw_data
        ORDER BY game_id, "Period", seconds DESC
    """).df()

    # Calculate additional stats
    team_model_data['time_prev'] = abs(team_model_data['seconds'].diff())
    team_model_data['prev_team'] = team_model_data['Team'].shift(1)
    team_model_data['prev_event'] = team_model_data['Event'].shift(1)
    team_model_data['dis_prev'] = team_model_data['distance'].diff()
    team_model_data['is_rebound'] = (
        (team_model_data['prev_event'].isin(['Shot', 'Goal'])) & (team_model_data['time_prev'] <= 3)
    ).astype(int)
    team_model_data['is_rush'] = (
        (team_model_data['dis_prev'] >= 25) & (team_model_data['time_prev'] <= 4)
    ).astype(int)
    
    return team_model_data

RAW_DATA = load_raw_data()
TEAM_MODEL_DATA = load_team_model_data()