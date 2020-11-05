from ansible.module_utils.basic import AnsibleModule
from ansible_collections.moc.mailman.plugins.module_utils.mailman import Mailman, CalledProcessError


def run_module():
    mm = Mailman()

    module_args = dict(
        state=dict(type='str', default='present'),
        name=dict(type='str', required=True),
        members=dict(type='list', required=True),
        digest_members=dict(type='list'),
        notify_members=dict(type='bool'),
        notify_admins=dict(type='bool'),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        list_name = module.params['name']
        want_members = module.params['members']

        regular_members = mm.list_regular_members(list_name)

        result['members'] = regular_members

        if module.params['state'] == 'present':
            if want_members and any(member not in regular_members for member in want_members):
                result['changed'] = True

            if module.check_mode:
                module.exit_json(**result)

            if result['changed']:
                result['stdout'] = mm.add_regular_members(list_name, want_members)
        elif module.params['state'] == 'absent':
            if want_members and any(member in regular_members for member in want_members):
                result['changed'] = True

            if module.check_mode:
                module.exit_json(**result)

            if result['changed']:
                result['stdout'] = mm.remove_members(list_name, want_members)

        result['members'] = mm.list_regular_members(list_name)
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
