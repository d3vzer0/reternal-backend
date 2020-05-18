from workers import app
from workers import app
from database.models import Indices
from workers.search.schemas.indices import IndiceList


@app.task(name='api.indices.task.update')
def update_indices(task_response, integration, execution_date):
    convert_schema = IndiceList(**{'integration':integration, 'execution_date': execution_date,
        'indices': task_response}).dict()
    for indice in convert_schema['indices']:
        Indices().create(**indice, **{'integration': convert_schema['integration'],
            'execution_date': convert_schema['execution_date']})