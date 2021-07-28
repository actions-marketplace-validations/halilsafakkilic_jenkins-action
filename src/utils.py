import sys
import time
import traceback

from api4jenkins import Jenkins as JenkinsAPI
from api4jenkins.build import Build
from api4jenkins.queue import QueueItem


def str_to_bool(value: str) -> bool:
    if value == 'true':
        return True

    return False


class GithubAction:
    def set_output(output_key: str, output_val):
        print('::set-output name=' + output_key + '::' + str(output_val))

    def warning(message: str, file: str = None, line: str = None, col: str = None):
        args = GithubAction.build_args(file, line, col)

        output = '::warning'
        if len(args) > 0:
            output += ' ' + args

        output += '::' + message

        print(output)

    def build_args(file: str = None, line: str = None, col: str = None):
        args = {}

        if file is not None:
            args.update({'file': file})

        if line is not None:
            args.update({'line': line})

        if col is not None:
            args.update({'col': col})

        return ','.join(str(v) for v in args.values())

    def error(message: str, file: str = None, line: str = None, col: str = None):
        args = GithubAction.build_args(file, line, col)

        output = '::error'
        if len(args) > 0:
            output += ' ' + args

        output += '::' + message

        print(output)
        sys.exit(1)


class Jenkins:
    _operation_start_time = None

    def __init__(self, baseurl: str, username: str, password: str, debug_mode: bool, timeout: int, sleep_time: int):
        self.instance = JenkinsAPI(baseurl, auth=(username, password))

        self.debug = debug_mode
        self.timeout = timeout
        self.sleep_time = sleep_time

    def run_job(self, job_name, params=None, wait_for_result=False):
        try:
            # Debug
            if self.debug:
                if params is None:
                    params = {'debug': True}
                else:
                    params.update({'debug': True})

            self._run_job(job_name, params, wait_for_result)

        except:
            if self.debug:
                traceback.print_exc()
            else:
                GithubAction.error('If you want to show error detail please set DEBUG=true.')

            GithubAction.error('Unexpected Exception')

    def _run_job(self, job_name, params: dict = None, wait_for_result=False):
        queue_item: QueueItem = self.instance.build_job(job_name, **params)

        print('Build is created: #' + str(queue_item.id))
        GithubAction.set_output('build_id', queue_item.id)

        if wait_for_result:
            build = self._wait_for_build(queue_item)

            self._jenkins_console(build)

    def _check_timeout(self):
        if self.timeout and ((time.time() - self._operation_start_time) > self.timeout):
            GithubAction.error('Operation timed out.')

    def _wait_for_build(self, queue_item):
        self._operation_start_time = time.time()

        print('Build is starting...')
        build = self._get_build(queue_item)

        print('Build is running...')
        build_status = self._get_build_status(build)

        print('\n', end='')
        self._parse_build_status(build_status)

        return build

    def _get_build(self, queue_item) -> Build:
        self._check_timeout()

        if not queue_item.get_build():
            time.sleep(self.sleep_time)

            return self._get_build(queue_item)

        return queue_item.get_build()

    def _get_build_status(self, build: Build):
        self._check_timeout()

        if build.result is None:
            time.sleep(self.sleep_time)

            return self._get_build_status(build)

        return build.result

    @staticmethod
    def _parse_build_status(build_status):
        if build_status == 'FAILURE':
            GithubAction.error('Build is failed.')

        elif build_status == 'SUCCESS':
            print('Build is succeeded.')

        elif build_status == 'ABORTED':
            GithubAction.warning('Build is aborted.')

        else:
            GithubAction.warning('Undefined Build Status: ' + build_status)

    @staticmethod
    def _jenkins_console(build: Build):
        console = ''
        for line in build.console_text():
            console += line.decode('utf-8') + '\n'

        print('#' * 70)
        print(console)
