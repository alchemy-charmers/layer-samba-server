import pytest
import os
import yaml
from juju.model import Model

# Treat tests as coroutines
pytestmark = pytest.mark.asyncio

# Load charm metadata
metadata = yaml.load(open("./metadata.yaml"))
juju_repository = os.getenv('JUJU_REPOSITORY',
                            '.').rstrip('/')
charmname = metadata['name']
series = ['bionic', 'xenial']


@pytest.fixture
async def model():
    model = Model()
    await model.connect_current()
    yield model
    await model.disconnect()


@pytest.fixture
async def apps(model):
    apps = []
    for entry in series:
        app = model.applications['{}-{}'.format(
            charmname,
            entry)]
        apps.append(app)
    return apps


@pytest.mark.parametrize('series', series)
async def test_serviceaccount_deploy(model, series):
    # this has been modified from the template, as the template
    # deploys from the layer, rather than the built charm, which
    # needs to be fixed
    await model.deploy('{}/builds/{}'.format(
            juju_repository, charmname),
            series=series,
            application_name='{}-{}'.format(
                charmname, series))
    assert True


async def test_serviceaccount_status(apps, model):
    for app in apps:
        await model.block_until(lambda: app.status == 'active')
    assert True
