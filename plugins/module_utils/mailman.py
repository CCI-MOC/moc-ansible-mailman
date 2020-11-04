import json
import logging
import os
import subprocess
import tempfile

log = logging.getLogger(__name__)
default_path = '/usr/lib/mailman/bin'


class CalledProcessError(Exception):
    def __init__(self, command, returncode, stdout, stderr):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class Mailman(object):
    def __init__(self, path=None, allowed_commands=None):
        self.path = path or default_path
        self.allowed_commands = allowed_commands or []

    def __getattr__(self, cmdname):
        def wrapper(_cmd):
            def wrapped(*args, **kwargs):
                cmd = [cmdname]
                cmd.extend(args)

                raw = kwargs.get('raw')
                if 'raw' in kwargs:
                    del kwargs['raw']

                if 'stdin' in kwargs:
                    stdin = kwargs['stdin'].encode()
                    del kwargs['stdin']
                else:
                    stdin = None

                log.debug('running command: %s', cmd)
                p = subprocess.Popen(cmd,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     **kwargs)
                out, err = p.communicate(input=stdin)
                ret = p.wait()

                if ret != 0:
                    raise CalledProcessError(cmd, ret, out, err)

                return out if raw else out.decode()

            return wrapped

        if cmdname.startswith('_'):
            cmdname = cmdname[1:]

        if self.allowed_commands and cmdname not in self.allowed_commands:
            raise ValueError(cmdname)

        cmdname = os.path.join(self.path, cmdname)
        return wrapper(cmdname)

    def list_lists(self,
                   advertised_only=False,
                   domain=None):

        args = ['-b']

        if advertised_only:
            args.append('-a')

        if domain:
            args.extend(('-V', domain))

        return self._list_lists(*args).splitlines()

    def list_all_members(self, listname):
        return self._list_members(listname).splitlines()

    def list_regular_members(self, listname):
        return self._list_members('-r', listname).splitlines()

    def list_digest_members(self, listname):
        return self._list_members('-d', listname).splitlines()

    def list_exists(self, listname):
        return listname in self.list_lists()

    def is_already_subscribed(self, email, listname):
        return email in self.list_members(listname).splitlines()

    def subscribe(self, email, listname):
        return self.add_members(
            '-a', 'n', '-w', 'n',
            '-r', '-', listname,
            _in=email)

    def unsubscribe(self, email, listname):
        return self.remove_members(
            '-n', '-N',
            '-f', '-', listname,
            _in=email)

    def create_list(self, name, owner, password,
                    urlhost=None, emailhost=None, quiet=None):
        cmd = []
        if urlhost:
            cmd.extend(('--urlhost', urlhost))
        if emailhost:
            cmd.extend(('--emailhost', emailhost))
        if quiet:
            cmd.append('-q')

        cmd.extend((name, owner, password))
        return self.newlist(*cmd)

    def remove_list(self, name, remove_archives=False):
        cmd = []
        if remove_archives:
            cmd.append('-a')

        cmd.append(name)
        return self.rmlist(*cmd)

    def add_regular_members(self, listname, members,
                            notify_members=False,
                            notify_admins=False):

        self.add_members(
            '-w{}'.format('y' if notify_members else 'n'),
            '-a{}'.format('y' if notify_admins else 'n'),
            '-r', '-',
            listname,
            stdin='\n'.join(members))

    def remove_regular_members(self, listname, members,
                               notify_members=False,
                               notify_admins=False):

        args = ['-f', '-']

        if not notify_members:
            args.append('-n')

        if not notify_admins:
            args.append('-N')

        args.append(listname)

        self.remove_members(
            *args,
            stdin='\n'.join(members))

    def get_list_config(self, listname):
        config = self.config_list('-o', '-', listname, raw=True)
        ns = {}
        exec(config, ns)
        return {k: v
                for k, v in ns.items()
                if not k.startswith('_')}

    def set_list_config(self, listname, config):
        with tempfile.NamedTemporaryFile() as fd:
            fd.write('true = True\n')
            fd.write('false = False\n')

            for k, v in config.items():
                fd.write("{} = {}\n".format(k, json.dumps(v)))

            fd.flush()
            return self.config_list('-i', fd.name, listname)


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
