from app.workers import celery
from app.utils.sigmaloader import SigmaLoader

# emit an event
@celery.task(name='api.sigma.package.create')
def create_package(target, data):
    ''' Convert selection of sigma rules to specified target platform '''
    target_rules = SigmaLoader().convert_rules(data)
    return target_rules
