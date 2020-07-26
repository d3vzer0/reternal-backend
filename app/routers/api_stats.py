from app.utils.depends import validate_token
from fastapi import Depends, APIRouter
from app.database.models import Techniques, Coverage, Sigma


router = APIRouter()

@router.get('/stats/count')
async def stats_count(current_user: dict = Depends(validate_token)):
    ''' Get total count of mapped datasources '''
    stats_count = {
        'coverage': len(Coverage.objects(enabled=True)),
        'techniques': len(Techniques.objects()),
        'rules':  len(Sigma.objects())
    }
    return stats_count
