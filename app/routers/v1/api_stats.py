from app.utils.depends import validate_token
from fastapi import Depends, APIRouter
from app.database.models.techniques import Techniques
from app.database.models.coverage import Coverage
from app.database.models.sigma import Sigma


router = APIRouter()

@router.get('/stats/count/rules')
async def stats_count_rules():
    ''' Get total count of sigma rules '''
    return {'count': Sigma.objects().count()}


@router.get('/stats/count/coverage')
async def stats_count_coverage():
    ''' Get total count of datasources with coverage '''
    return {'count': Coverage.objects(enabled=True).count()}


@router.get('/stats/count/techniques')
async def stats_count_coverage():
    ''' Get total count of mapped datasources '''
    return {'count': Techniques.objects().count()}

