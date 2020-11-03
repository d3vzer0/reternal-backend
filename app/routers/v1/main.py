from fastapi import APIRouter, Depends, Security
from app.utils.depends import validate_token
from . import (api_agents, api_campaigns, api_coverage,
    api_graph, api_listeners, api_mapping, api_mitre, api_modules,
    api_results, api_scheduler, api_search, api_sigma, api_stagers,
    api_states, api_stats, api_tasks, api_workers)

api_v1 = APIRouter()

api_v1.include_router(api_agents.router,
    tags=['agents']
)

api_v1.include_router(api_campaigns.router,
    tags=['campaigns']
)

api_v1.include_router(api_coverage.router,
    tags=['coverage']
)

api_v1.include_router(api_graph.router,
    tags=['graph']
)

api_v1.include_router(api_listeners.router, 
    tags=['listeners']
)

api_v1.include_router(api_mapping.router,
    tags=['mapping']
)

api_v1.include_router(api_mitre.router,
    tags=['mitre']
)

api_v1.include_router(api_modules.router,
    tags=['modules']
)

api_v1.include_router(api_results.router,
    tags=['results']
)

api_v1.include_router(api_scheduler.router,
    tags=['scheduler']
)

api_v1.include_router(api_search.router, 
    tags=['search']
)

api_v1.include_router(api_sigma.router,
    tags=['sigma']
)

api_v1.include_router(api_stagers.router,
    tags=['stagers']
)

api_v1.include_router(api_states.router,
    tags=['states']
)

api_v1.include_router(api_stats.router,
    tags=['stats']
)

api_v1.include_router(api_tasks.router,
    tags=['tasks']
)

api_v1.include_router(api_workers.router,
    tags=['workers']
)

