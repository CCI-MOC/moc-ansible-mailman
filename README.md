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

### Back up configuration for all lists

```
- name: get list of mailing lists
  mailman_lists_info:
  register: lists

- name: get information for each list
  mailman_list_info:
    name: "{{ item }}"
  loop: "{{ lists.mailman.lists }}"
  register: detail

- name: save list information to a file
  copy:
    content: "{{ detail.results|json_query('[].mailman')|to_nice_json }}"
    dest: lists.json
```

[mailman]: https://list.org/
