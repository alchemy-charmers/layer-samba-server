#!/usr/bin/python3
'''
Reusable pytest fixtures for functional testing

Environment variables
---------------------

test_preserve_model:
if set, the testing model won't be torn down at the end of the testing session
'''

import asyncio
import json
import os
import uuid
import pytest
import subprocess
import juju
from juju.controller import Controller
from juju.errors import JujuError

STAT_CMD = '''python3 - <<EOF
import json
import os

s = os.stat('%s')
stat_hash = {
    'uid': s.st_uid,
    'gid': s.st_gid,
    'mode': oct(s.st_mode),
    'size': s.st_size
}
stat_json = json.dumps(stat_hash)
print(stat_json)

EOF
'''


@pytest.fixture(scope='module')
def event_loop():
    '''Override the default pytest event loop to allow for fixtures using a
    broader scope'''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    yield loop
    loop.close()
    asyncio.set_event_loop(None)


@pytest.fixture(scope='module')
async def controller():
    '''Connect to the current controller'''
    _controller = Controller()
    await _controller.connect_current()
    yield _controller
    await _controller.disconnect()


@pytest.fixture(scope='module')
async def model(controller):
    '''This model lives only for the duration of the test'''
    model_name = "functest-{}".format(str(uuid.uuid4())[-12:])
    _model = await controller.add_model(model_name,
                                        cloud_name=os.getenv('PYTEST_CLOUD_NAME'),
                                        region=os.getenv('PYTEST_CLOUD_REGION'),
                                        )
    # https://github.com/juju/python-libjuju/issues/267
    subprocess.check_call(['juju', 'models'])
    while model_name not in await controller.list_models():
        await asyncio.sleep(1)
    yield _model
    await _model.disconnect()
    if not os.getenv('PYTEST_KEEP_MODEL'):
        await controller.destroy_model(model_name)
        while model_name in await controller.list_models():
            await asyncio.sleep(1)


@pytest.fixture
async def get_app(model):
    '''Returns the application requested'''
    async def _get_app(name):
        try:
            return model.applications[name]
        except KeyError:
            raise JujuError("Cannot find application {}".format(name))
    return _get_app


@pytest.fixture
async def get_unit(model):
    '''Returns the requested <app_name>/<unit_number> unit'''
    async def _get_unit(name):
        try:
            (app_name, unit_number) = name.split('/')
            return model.applications[app_name].units[unit_number]
        except (KeyError, ValueError):
            raise JujuError("Cannot find unit {}".format(name))
    return _get_unit


@pytest.fixture
async def get_entity(get_unit, get_app):
    '''Returns a unit or an application'''
    async def _get_entity(name):
        try:
            return await get_unit(name)
        except JujuError:
            try:
                return await get_app(name)
            except JujuError:
                raise JujuError("Cannot find entity {}".format(name))
    return _get_entity


@pytest.fixture
async def run_command(get_unit):
    '''
    Runs a command on a unit.

    :param cmd: Command to be run
    :param target: Unit object or unit name string
    '''
    async def _run_command(cmd, target):
        unit = (
            target
            if isinstance(target, juju.unit.Unit)
            else await get_unit(target)
        )
        action = await unit.run(cmd)
        return action.results
    return _run_command


@pytest.fixture
async def file_stat(run_command):
    '''
    Runs stat on a file

    :param path: File path
    :param target: Unit object or unit name string
    '''
    async def _file_stat(path, target):
        cmd = STAT_CMD % path
        results = await run_command(cmd, target)
        return json.loads(results['Stdout'])
    return _file_stat


@pytest.fixture
async def file_contents(run_command):
    '''
    Returns the contents of a file

    :param path: File path
    :param target: Unit object or unit name string
    '''
    async def _file_contents(path, target):
        cmd = 'cat {}'.format(path)
        results = await run_command(cmd, target)
        return results['Stdout']
    return _file_contents


@pytest.fixture
async def reconfigure_app(get_app, model):
    '''Applies a different config to the requested app'''
    async def _reconfigure_app(cfg, target):
        application = (
            target
            if isinstance(target, juju.application.Application)
            else await get_app(target)
        )
        await application.set_config(cfg)
        await application.get_config()
        await model.block_until(lambda: application.status == 'active')
    return _reconfigure_app
