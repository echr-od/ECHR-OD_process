from echr.steps.deploy import parse_server_parameters, runner


class TestRunner:

    @staticmethod
    def test_params_none():
        ok, params = parse_server_parameters(params_str=None)
        assert not ok
        assert params == []

    @staticmethod
    def test_params_missing_all():
        ok, params = parse_server_parameters(params_str="")
        assert not ok
        assert params == ['user', 'password', 'host', 'folder', 'build', 'workflow']

    @staticmethod
    def test_params_missing_some():
        ok, params = parse_server_parameters(params_str="user=foo password=bar")
        assert not ok
        assert params == ['host', 'folder', 'build', 'workflow']

    @staticmethod
    def test_params_ok():
        params_str = "host=localhost user=foo password=bar " \
                     "folder=/tmp/ECHR-OD_process/build/ build=echr_update workflow=database"
        ok, params = parse_server_parameters(params_str=params_str)
        assert ok
        assert params == {'host': 'localhost',
                          'user': 'foo',
                          'password': 'bar',
                          'folder': '/tmp/ECHR-OD_process/build/',
                          'build': 'echr_update',
                          'workflow': 'database'}

    @staticmethod
    def test_running_missing_params():
        rc = runner(params_str="user=foo password=bar", build="/tmp/", detach=False, force=False, update=False)
        assert rc == 2

    @staticmethod
    def test_running_exception_params():
        rc = runner(params_str=None, build="/tmp/", detach=False, force=False, update=False)
        assert rc == 11