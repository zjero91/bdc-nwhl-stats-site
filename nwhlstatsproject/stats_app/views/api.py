from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..serializers import TeamPeriodSerializer, TeamDiffSerializer, ShotsPeriodSerializer, ShotsGoalDiffSerializer
import pandas as pd
from stats_app.utils.load_api_data import TEAM_PERIOD_DATA, TEAM_DIFF_DATA, TEAM_MODEL_DATA
from stats_app.utils.xg_model import calculate_xg

@api_view(['GET'])
def get_team_period(request):
    # Pull in the loaded data
    data = TEAM_PERIOD_DATA
    
    # Get query params
    teamid = request.query_params.get('teamid')
    period = request.query_params.get('period')
    state = request.query_params.get('state')
    
    # Apply filters
    if teamid is not None:
        data = data[data['team_id'] == int(teamid)]
    if period is not None:
        data = data[data['period'] == int(period)]
    if state is not None:
        data = data[data['state'] == str(state)]

    # Calculate stats
    data['pass_tot'] = data['passes'] + data['pass_fail']
    data['pass_pct'] = data.apply(lambda row: round(row['passes']/row['pass_tot'], 2) if row['pass_tot'] > 0 else 0, axis=1)
    
    data = data.to_dict('records')
    
    serializer = TeamPeriodSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_shots_period(request):
    # Pull in the loaded data
    data = TEAM_MODEL_DATA
    
    data = data[data['Event'].isin(['Shot', 'Goal'])]

    xg_pred = calculate_xg(data)
    data = pd.merge(data, xg_pred, on='event_id', how='left')

    data = data.rename(columns={'Detail 1': 'shot_type', 'X Coordinate': 'x_coord',
                                'Y Coordinate': 'y_coord', 'Period': 'period'})
    
    data['xg'] = data['xg'].round(1)
    
    # Get query params
    teamid = request.query_params.get('teamid')
    period = request.query_params.get('period')
    state = request.query_params.get('state')
    
    # Apply filters
    if teamid is not None:
        data = data[data['team_id'] == int(teamid)]
    if period is not None:
        data = data[data['period'] == int(period)]
    if state is not None:
        data = data[data['state'] == str(state)]

    data = data.to_dict('records')
    
    serializer = ShotsPeriodSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_team_diff(request):
    # Pull in the loaded data
    data = TEAM_DIFF_DATA
    
    # Get query params
    teamid = request.query_params.get('teamid')
    goaldiff = request.query_params.get('goaldiff')
    state = request.query_params.get('state')
    
    # Apply filters
    if teamid is not None:
        data = data[data['team_id'] == int(teamid)]
    if goaldiff is not None:
        data = data[data['goal_diff'] == int(goaldiff)]
    if state is not None:
        data = data[data['state'] == str(state)]

    data = data.to_dict('records')
    
    serializer = TeamDiffSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_shots_diff(request):
    # Pull in the loaded data
    data = TEAM_MODEL_DATA
    
    data = data[data['Event'].isin(['Shot', 'Goal'])]

    xg_pred = calculate_xg(data)
    data = pd.merge(data, xg_pred, on='event_id', how='left')

    data = data.rename(columns={'Detail 1': 'shot_type', 'X Coordinate': 'x_coord',
                                'Y Coordinate': 'y_coord', 'goal_diff': 'goal_diff'})
    
    data['xg'] = data['xg'].round(1)
    
    # Get query params
    teamid = request.query_params.get('teamid')
    goaldiff = request.query_params.get('goaldiff')
    state = request.query_params.get('state')
    
    # Apply filters
    if teamid is not None:
        data = data[data['team_id'] == int(teamid)]
    if goaldiff is not None:
        data = data[data['goal_diff'] == int(goaldiff)]
    if state is not None:
        data = data[data['state'] == str(state)]

    data = data.to_dict('records')
    
    serializer = ShotsGoalDiffSerializer(data=data, many=True)
    serializer.is_valid(raise_exception=True)
    
    return Response(serializer.data)