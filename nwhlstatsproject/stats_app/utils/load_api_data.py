import pandas as pd
import duckdb
from stats_app.utils.load_base_data import TEAM_MODEL_DATA
from .xg_model import calculate_xg

def load_team_period_data():
    raw_data = TEAM_MODEL_DATA.copy()
    
    corsi_data = raw_data[raw_data['Event'].isin(['Shot', 'Goal'])].copy()
    
    xg_pred = calculate_xg(corsi_data)
    
    raw_data = pd.merge(raw_data, xg_pred, on='event_id', how='left')
    
    raw_data['xg'] = raw_data['xg'].fillna(0)
    
    team_period_data = duckdb.sql("""
        with add_id as (
            SELECT
                CASE
                    WHEN "Team" = "Home Team"
                    THEN "Home Team"
                    ELSE "Away Team"
                END AS team_name,
                *
            FROM raw_data
        ),

        total_fo as (
            SELECT
                game_id,
                "Period",
                state,
                COUNT(CASE WHEN "Event" = 'Faceoff Win' THEN 1 ELSE NULL END) AS tot_fo
            FROM add_id
            GROUP BY game_id, "Period", state
        )

        SELECT
            team_id,
            MAX(team_name) as team_name,
            "Period" as period,
            state,
            COUNT(DISTINCT game_id) as gp,
            COUNT(CASE WHEN "Event" = 'Faceoff Win' THEN 1 ELSE NULL END) AS fow,
            MAX(tot_fo) as tot_fo,
            COUNT(CASE WHEN "Event" = 'Shot' THEN 1 ELSE NULL END) AS sat,
            COUNT(CASE WHEN "Event" = 'Shot' AND "Detail 2" = 'Blocked' THEN 1 ELSE NULL END) AS blocked_shots,
            COUNT(CASE WHEN "Event" = 'Goal' THEN 1 ELSE NULL END) AS goals,
            ROUND(SUM(xg),1) as xg,
            COUNT(CASE WHEN "Event" = 'Play' THEN 1 ELSE NULL END) AS passes,
            COUNT(CASE WHEN "Event" = 'Incomplete Play' THEN 1 ELSE NULL END) AS pass_fail,
            COUNT(CASE WHEN "Event" = 'Takeaway' THEN 1 ELSE NULL END) AS takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" > 125 THEN 1 ELSE NULL END) AS oz_takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" >= 75 AND "X Coordinate" <= 125 THEN 1 ELSE NULL END) AS nz_takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" < 75 THEN 1 ELSE NULL END) AS dz_takeaways,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' THEN 1 ELSE NULL END) AS lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" > 125 THEN 1 ELSE NULL END) AS oz_lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" >= 75 AND "X Coordinate" <= 125 THEN 1 ELSE NULL END) AS nz_lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" < 75 THEN 1 ELSE NULL END) AS dz_lpr,
            COUNT(CASE WHEN "Event" = 'Dump In/Out' THEN 1 ELSE NULL END) AS dumps,
            COUNT(CASE WHEN "Event" = 'Zone Entry' THEN 1 ELSE NULL END) AS entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Carried' THEN 1 ELSE NULL END) AS carried_entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Dumped' THEN 1 ELSE NULL END) AS dumped_entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Played' THEN 1 ELSE NULL END) AS played_entries,
            COUNT(CASE WHEN "Event" = 'Penalty Taken' THEN 1 ELSE NULL END) AS penalties
        FROM add_id
        LEFT JOIN total_fo using(game_id, "Period", state)
        GROUP BY team_id, "Period", state
        ORDER BY team_id, "Period"
    """).df()

    # Calculate stats
    team_period_data['pass_tot'] = team_period_data['passes'] + team_period_data['pass_fail']
    team_period_data['pass_pct'] = team_period_data.apply(lambda row: round(row['passes']/row['pass_tot'], 2) if row['pass_tot'] > 0 else 0, axis=1)
    team_period_data['fow'] = team_period_data.apply(lambda row: round(row['fow']/row['tot_fo'], 2) if row['tot_fo'] > 0 else 0, axis=1)
    
    # Per GP stats
    team_period_data['sat'] = team_period_data.apply(lambda row: round(row['sat']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['blocked_shots'] = team_period_data.apply(lambda row: round(row['blocked_shots']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['takeaways'] = team_period_data.apply(lambda row: round(row['takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['oz_takeaways'] = team_period_data.apply(lambda row: round(row['oz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['nz_takeaways'] = team_period_data.apply(lambda row: round(row['nz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['dz_takeaways'] = team_period_data.apply(lambda row: round(row['dz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['lpr'] = team_period_data.apply(lambda row: round(row['lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['oz_lpr'] = team_period_data.apply(lambda row: round(row['oz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['nz_lpr'] = team_period_data.apply(lambda row: round(row['nz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['dz_lpr'] = team_period_data.apply(lambda row: round(row['dz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['dumps'] = team_period_data.apply(lambda row: round(row['dumps']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['entries'] = team_period_data.apply(lambda row: round(row['entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['carried_entries'] = team_period_data.apply(lambda row: round(row['carried_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['dumped_entries'] = team_period_data.apply(lambda row: round(row['dumped_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['played_entries'] = team_period_data.apply(lambda row: round(row['played_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_period_data['penalties'] = team_period_data.apply(lambda row: round(row['penalties']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)

    return team_period_data

def load_team_diff_data():
    raw_data = TEAM_MODEL_DATA.copy()
    
    corsi_data = raw_data[raw_data['Event'].isin(['Shot', 'Goal'])].copy()
    
    xg_pred = calculate_xg(corsi_data)
    
    raw_data = pd.merge(raw_data, xg_pred, on='event_id', how='left')
    
    raw_data['xg'] = raw_data['xg'].fillna(0)
    
    team_diff_data = duckdb.sql("""
        with add_id as (
            SELECT
                CASE
                    WHEN "Team" = "Home Team"
                    THEN "Home Team"
                    ELSE "Away Team"
                END AS team_name,
                *
            FROM raw_data
        ),

        total_fo as (
            SELECT
                game_id,
                goal_diff,
                state,
                COUNT(CASE WHEN "Event" = 'Faceoff Win' THEN 1 ELSE NULL END) AS tot_fo
            FROM add_id
            GROUP BY game_id, goal_diff, state
        )

        SELECT
            team_id,
            MAX(team_name) as team_name,
            goal_diff,
            state,
            COUNT(DISTINCT game_id) as gp,
            COUNT(CASE WHEN "Event" = 'Faceoff Win' THEN 1 ELSE NULL END) AS fow,
            MAX(tot_fo) as tot_fo,
            COUNT(CASE WHEN "Event" = 'Shot' THEN 1 ELSE NULL END) AS sat,
            COUNT(CASE WHEN "Event" = 'Shot' AND "Detail 2" = 'Blocked' THEN 1 ELSE NULL END) AS blocked_shots,
            COUNT(CASE WHEN "Event" = 'Goal' THEN 1 ELSE NULL END) AS goals,
            ROUND(SUM(xg),1) as xg,
            COUNT(CASE WHEN "Event" = 'Play' THEN 1 ELSE NULL END) AS passes,
            COUNT(CASE WHEN "Event" = 'Incomplete Play' THEN 1 ELSE NULL END) AS pass_fail,
            COUNT(CASE WHEN "Event" = 'Takeaway' THEN 1 ELSE NULL END) AS takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" > 125 THEN 1 ELSE NULL END) AS oz_takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" >= 75 AND "X Coordinate" <= 125 THEN 1 ELSE NULL END) AS nz_takeaways,
            COUNT(CASE WHEN "Event" = 'Takeaway' AND "X Coordinate" < 75 THEN 1 ELSE NULL END) AS dz_takeaways,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' THEN 1 ELSE NULL END) AS lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" > 125 THEN 1 ELSE NULL END) AS oz_lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" >= 75 AND "X Coordinate" <= 125 THEN 1 ELSE NULL END) AS nz_lpr,
            COUNT(CASE WHEN "Event" = 'Puck Recovery' AND "X Coordinate" < 75 THEN 1 ELSE NULL END) AS dz_lpr,
            COUNT(CASE WHEN "Event" = 'Dump In/Out' THEN 1 ELSE NULL END) AS dumps,
            COUNT(CASE WHEN "Event" = 'Zone Entry' THEN 1 ELSE NULL END) AS entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Carried' THEN 1 ELSE NULL END) AS carried_entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Dumped' THEN 1 ELSE NULL END) AS dumped_entries,
            COUNT(CASE WHEN "Event" = 'Zone Entry' AND "Detail 1" = 'Played' THEN 1 ELSE NULL END) AS played_entries,
            COUNT(CASE WHEN "Event" = 'Penalty Taken' THEN 1 ELSE NULL END) AS penalties
        FROM add_id
        LEFT JOIN total_fo using(game_id, goal_diff, state)
        GROUP BY team_id, goal_diff, state
        ORDER BY team_id, goal_diff
    """).df()

    # Calculate stats
    team_diff_data['pass_tot'] = team_diff_data['passes'] + team_diff_data['pass_fail']
    team_diff_data['pass_pct'] = team_diff_data.apply(lambda row: round(row['passes']/row['pass_tot'], 2) if row['pass_tot'] > 0 else 0, axis=1)
    team_diff_data['fow'] = team_diff_data.apply(lambda row: round(row['fow']/row['tot_fo'], 2) if row['tot_fo'] > 0 else 0, axis=1)
    
    # Per GP stats
    team_diff_data['sat'] = team_diff_data.apply(lambda row: round(row['sat']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['blocked_shots'] = team_diff_data.apply(lambda row: round(row['blocked_shots']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['takeaways'] = team_diff_data.apply(lambda row: round(row['takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['oz_takeaways'] = team_diff_data.apply(lambda row: round(row['oz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['nz_takeaways'] = team_diff_data.apply(lambda row: round(row['nz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['dz_takeaways'] = team_diff_data.apply(lambda row: round(row['dz_takeaways']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['lpr'] = team_diff_data.apply(lambda row: round(row['lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['oz_lpr'] = team_diff_data.apply(lambda row: round(row['oz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['nz_lpr'] = team_diff_data.apply(lambda row: round(row['nz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['dz_lpr'] = team_diff_data.apply(lambda row: round(row['dz_lpr']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['dumps'] = team_diff_data.apply(lambda row: round(row['dumps']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['entries'] = team_diff_data.apply(lambda row: round(row['entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['carried_entries'] = team_diff_data.apply(lambda row: round(row['carried_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['dumped_entries'] = team_diff_data.apply(lambda row: round(row['dumped_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['played_entries'] = team_diff_data.apply(lambda row: round(row['played_entries']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)
    team_diff_data['penalties'] = team_diff_data.apply(lambda row: round(row['penalties']/row['gp'], 1) if row['gp'] > 0 else 0, axis=1)

    return team_diff_data

TEAM_PERIOD_DATA = load_team_period_data()
TEAM_DIFF_DATA = load_team_diff_data()