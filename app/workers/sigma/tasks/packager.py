from app.workers import celery
from app.utils.sigmaloader import Sigma

# emit an event
@celery.task(name='api.sigma.package.create')
def create_package(target, data):
    ''' Convert selection of sigma rules to specified target platform '''
    target_rules = Sigma(data).export(target=target)
    return target_rules
