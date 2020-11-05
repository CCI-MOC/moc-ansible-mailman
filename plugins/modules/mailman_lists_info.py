from ansible.module_utils.basic import AnsibleModule
from ansible_collections.moc.mailman.plugins.module_utils.mailman import Mailman


def run_module():
    mm = Mailman()

    module_args = dict()

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result['mailman'] = {
        'lists': mm.list_lists(),
    }

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
