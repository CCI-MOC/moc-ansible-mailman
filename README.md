# moc.mailman

Modules for interacting with [Mailman][] mailing lists.

## Examples

### Create a mailing list

```
- name: create a mailing list
  mailman_list:
    name: example-list
    owner: mallory@example.com
    config:
      subject_prefix: '[EXAMPLE] '
      description: >-
        This is a list demonstrating the moc.mailman Ansible
        collection.
```

### Manage list membership

```
- name: subscribe addresses to a list
  mailman_list_members:
    name: example-list
    members:
      - alice@example.com
      - bob@example.com

- name: remove addresses from a list
  mailman_list_members:
    name: example-list
    state: absent
    members:
      - trudy@example.com
```

[mailman]: https://list.org/
