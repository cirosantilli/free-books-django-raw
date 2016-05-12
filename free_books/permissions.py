def has_perm(user, perm, obj=None):
    if perm == 'article_new':
        return user.is_authenticated()
    elif perm == 'article_edit':
        return user.is_authenticated() and obj.creator == user
    elif perm == 'article_delete':
        return user.is_authenticated() and obj.creator == user
