from app.workers import app
from app.database.models import SourceTypes
from app.workers.search.schemas.logsources import LogsourceList


@app.task(name='api.logsources.task.update')
def update_logsources(task_response, integration, execution_date):
    convert_schema = LogsourceList(**{'integration':integration, 'execution_date': execution_date,
        'logsources': task_response}).dict()
    for logsource in convert_schema['logsources']:
        SourceTypes().create(**logsource, **{'integration': convert_schema['integration'],
            'execution_date': convert_schema['execution_date']})
