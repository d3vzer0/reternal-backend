from app.workers import celery
from app.database.models import Indices
from app.workers.search.schemas.indices import IndiceList


@celery.task(name='api.indices.task.update')
def update_indices(task_response, integration, execution_date):
    convert_schema = IndiceList(**{'integration':integration, 'execution_date': execution_date,
        'indices': task_response}).dict()
    for indice in convert_schema['indices']:
        Indices().create(**indice, **{'integration': convert_schema['integration'],
            'execution_date': convert_schema['execution_date']})
