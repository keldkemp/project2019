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


is_logged_admin = rules.is_authenticated & is_admin
is_logged_manager = rules.is_authenticated & is_manager
is_logged_worker = rules.is_authenticated & is_worker
is_logged_personnel = rules.is_authenticated & (is_admin | is_manager | is_worker)

# Generic permission, can be used, until detailed are needed


rules.add_perm('admin', is_logged_admin)
rules.add_perm('manager', is_logged_admin)
rules.add_perm('worker', is_logged_admin)

rules.add_perm('profile', is_logged_personnel)
