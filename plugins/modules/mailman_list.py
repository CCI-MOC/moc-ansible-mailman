import random
import string

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.moc.mailman.plugins.module_utils.mailman import Mailman, CalledProcessError


def random_password():
    return ''.join(random.sample(string.ascii_letters + string.digits, 15))


def run_module():
    mm = Mailman()

    module_args = dict(
        state=dict(type='str', default='present'),
        name=dict(type='str', required=True),
        owner=dict(type='str'),
        password=dict(type='str', no_log=True),
        emailhost=dict(type='str'),
        urlhost=dict(type='str'),
        remove_archives=dict(type='bool', default=False),
        quiet=dict(type='bool', default=False),
        config=dict(type='dict'),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    list_name = module.params['name']
    list_owner = module.params['owner']
    list_password = module.params['password']

    try:
        if module.params['state'] == 'present':
            if list_owner is None:
                module.fail_json(msg='missing list owner')

            if list_password is None:
                list_password = random_password()

            if not mm.list_exists(list_name):
                result['changed'] = True

                if module.check_mode:
                    module.exit_json(**result)

                out = mm.create_list(
                    list_name, list_owner, list_password,
                    quiet=module.params['quiet'],
                    urlhost=module.params['urlhost'],
                    emailhost=module.params['emailhost'])
                result['stdout'] = out

            cur_config = mm.get_list_config(list_name)
            new_config = {}
            for k, v in module.params.get('config', {}).items():
                if cur_config[k] != v:
                    new_config[k] = v

            if new_config:
                result['changed'] = True
                mm.set_list_config(list_name, new_config)

            result['config'] = mm.get_list_config(list_name)
            result['new_config'] = new_config
        elif module.params['state'] == 'absent':
            if mm.list_exists(list_name):
                result['changed'] = True

                if module.check_mode:
                    module.exit_json(**result)

                out = mm.remove_list(
                    list_name,
                    remove_archives=module.params['remove_archives'])
                result['stdout'] = out

        module.exit_json(**result)
    except CalledProcessError as err:
        module.fail_json(
            msg="command failed",
            command=err.command,
            returncode=err.returncode,
            stdout=err.stdout,
            stderr=err.stderr,
        )


def main():
    run_module()


if __name__ == '__main__':
    main()
