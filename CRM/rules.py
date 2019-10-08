import rules

# Detail about rule system: https://github.com/dfunckt/django-rules


@rules.predicate
def is_admin(user) -> bool:
    return user.is_admin


@rules.predicate
def is_manager(user) -> bool:
    return user.is_manager


@rules.predicate
def is_worker(user) -> bool:
    return user.is_worker


@rules.predicate
def is_first_login(user) -> bool:
    return user.is_first_login


is_logged_admin = rules.is_authenticated & is_admin & is_first_login
is_logged_manager = rules.is_authenticated & is_manager & is_first_login
is_logged_worker = rules.is_authenticated & is_worker & is_first_login
is_logged_manager_admin = rules.is_authenticated & (is_admin | is_manager) & is_first_login
is_logged_personnel = rules.is_authenticated & (is_admin | is_manager | is_worker) & is_first_login

# Generic permission, can be used, until detailed are needed


rules.add_perm('admin', is_logged_admin)
rules.add_perm('manager', is_logged_manager)
rules.add_perm('worker', is_logged_worker)

rules.add_perm('profile', is_logged_personnel)
rules.add_perm('add_user', is_logged_manager_admin)
rules.add_perm('delete_user', is_logged_manager_admin)
rules.add_perm('users_list', is_logged_personnel)
