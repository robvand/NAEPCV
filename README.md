# NAE/ACI pre change validation

Ansible NAE Module
Make sure to insert nae.py in your local location for module_utils/network/aci/ and nae_prechange.py in modules/. Using ansible --version will show the default paths for these locations. In your ansible.cfg file, these can be modified by setting the module_utils and library vars.

See https://docs.ansible.com/ansible/latest/reference_appendices/config.html for more

Usage Administrivia
When creating a pre-change analysis from a manual "changes" payload string, all changes must be passed as denoted in usage.yaml, first with | and then the change payload contained within [] (even for singular changes).

Run all playbooks with at least v level verbosity, although vvv and vvvv are recommended since output is heavily truncated with lower verbosity. This is especially relevant when using any options with state: query.