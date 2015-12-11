import os
import unittest
import subprocess
from subprocess import CalledProcessError


class TestDockerCaching(unittest.TestCase):
    branched_history = dict()

    @classmethod
    def setUpClass(cls):
        try:
            subprocess.check_output(["docker", "rmi", "-f", "docker_build"])
            subprocess.check_output(["docker", "rmi", "-f", "caching_simple"])
            subprocess.check_output(["docker", "rmi", "-f", "docker_py_build"])
        except CalledProcessError as e:
            pass

    def _test_build(self):
        key = 'docker-build'
        print key.replace("-", " ")
        subprocess.check_output(["docker", "build", "-t", "docker_build", "context"])
        self.branched_history[key] = subprocess.check_output(["docker", "history", "-q", "docker_build"]).splitlines()
        self.branched_history[key].reverse()

    def _test_context_build(self):
        key = 'docker-context-build'
        print key.replace("-", " ")
        with open("context.tar") as f:
            subprocess.check_output(["docker", "build", "-t", "docker_build", "-"], stdin=f)
        self.branched_history[key] = subprocess.check_output(["docker", "history", "-q", "docker_build"]).splitlines()
        self.branched_history[key].reverse()

    def _test_compose_build(self):
        key = 'docker-compose-build'
        print key.replace("-", " ")
        subprocess.check_output(["docker-compose", "-p", "caching", "build"])
        self.branched_history[key] = subprocess.check_output(["docker", "history", "-q", "caching_simple"]).splitlines()
        self.branched_history[key].reverse()

    def _test_py_build(self):
        key = 'docker_py-build'
        print key.replace("-", " ")
        from compose.cli.docker_client import docker_client
        cli = docker_client()
        cli.ping()
        for _ in cli.build(path="context", tag="docker_py_build", rm=True):
            pass
        self.branched_history[key] = subprocess.check_output(["docker", "history", "-q", "docker_py_build"]).splitlines()
        self.branched_history[key].reverse()

    def _test_py_context_build(self):
        key = 'docker_py-context-build'
        print key.replace("-", " ")
        from compose.cli.docker_client import docker_client
        cli = docker_client()
        cli.ping()
        with open("context.tar") as f:
            for _ in cli.build(tag="docker_py_context_build", fileobj=f, custom_context=True, rm=True):
                pass
        self.branched_history[key] = subprocess.check_output(["docker", "history", "-q", "docker_py_context_build"]).splitlines()
        self.branched_history[key].reverse()

    def test_compare_cache(self):
        self._test_py_context_build()
        self._test_build()
        self._test_context_build()
        self._test_py_build()
        self._test_compose_build()
        self.assertTrue(self.branched_history)
        max_key_length = max(map(lambda x: len(x), self.branched_history.keys()))
        for k, v in self.branched_history.iteritems():
            print("{}: {}".format(k.rjust(max_key_length), v))

        keys = self.branched_history.keys()
        primary_key = keys.pop()
        for key in keys:
            self.assertListEqual(self.branched_history[primary_key], self.branched_history[key])


if __name__ == '__main__':
    unittest.main()
