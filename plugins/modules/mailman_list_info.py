from ansible.module_utils.basic import AnsibleModule
from ansible_collections.moc.mailman.plugins.module_utils.mailman import Mailman


def run_module():
    mm = Mailman()

    module_args = dict(
        state=dict(type='str', default='present'),
        name=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    list_name = module.params['name']

    result['mailman'] = {
        'members': mm.list_regular_members(list_name),
        'digest_members': mm.list_digest_members(list_name),
        'config': mm.get_list_config(list_name),
    }

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
