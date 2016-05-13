def has_perm(user, perm, obj=None):
    if not user.is_authenticated():
        return False
    if perm == 'article_new':
        return user.is_authenticated()
    elif perm == 'article_edit':
        return obj.creator == user
    elif perm == 'article_delete':
        return obj.creator == user
    elif perm == 'user_edit':
        return obj == user
    elif perm == 'admin_view':
        return user.is_staff
