from fastapi import APIRouter, Depends
from app.utils.depends import validate_token
from . import (api_agents, api_campaigns, api_coverage,
    api_graph, api_listeners, api_mapping, api_mitre, api_modules,
    api_results, api_scheduler, api_search, api_sigma, api_stagers,
    api_states, api_stats, api_tasks, api_workers)

api_v1 = APIRouter()

api_v1.include_router(api_agents.router,
    dependencies=[Depends(validate_token)],
    tags=['agents']
)

api_v1.include_router(api_campaigns.router,
    dependencies=[Depends(validate_token)],
    tags=['campaigns']
)

api_v1.include_router(api_coverage.router,
    dependencies=[Depends(validate_token)],
    tags=['coverage']
)

api_v1.include_router(api_graph.router,
    dependencies=[Depends(validate_token)],
    tags=['graph']
)

api_v1.include_router(api_listeners.router, 
    dependencies=[Depends(validate_token)], 
    tags=['listeners']
)

api_v1.include_router(api_mapping.router,
    dependencies=[Depends(validate_token)],
    tags=['mapping']
)

api_v1.include_router(api_mitre.router,
    dependencies=[Depends(validate_token)],
    tags=['mitre']
)

api_v1.include_router(api_modules.router,
    dependencies=[Depends(validate_token)],
    tags=['modules']
)

api_v1.include_router(api_results.router,
    dependencies=[Depends(validate_token)], 
    tags=['results']
)

api_v1.include_router(api_scheduler.router,
    dependencies=[Depends(validate_token)],
    tags=['scheduler']
)

api_v1.include_router(api_search.router, 
    dependencies=[Depends(validate_token)],
    tags=['search']
)

api_v1.include_router(api_sigma.router,
    dependencies=[Depends(validate_token)],
    tags=['sigma']
)

api_v1.include_router(api_stagers.router,
    dependencies=[Depends(validate_token)],
    tags=['stagers']
)

api_v1.include_router(api_states.router,
    dependencies=[Depends(validate_token)],
    tags=['states']
)

api_v1.include_router(api_stats.router,
    dependencies=[Depends(validate_token)],
    tags=['stats']
)

api_v1.include_router(api_tasks.router,
    dependencies=[Depends(validate_token)],
    tags=['tasks']
)

api_v1.include_router(api_workers.router,
    dependencies=[Depends(validate_token)],
    tags=['workers']
)

