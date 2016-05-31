def has_perm(user, perm, obj=None):
    if not user.is_authenticated():
        return False
    if perm == 'admin_view':
        return user.is_staff
    elif perm == 'user_edit':
        return obj == user
    elif perm == 'article_new':
        return True
    elif perm == 'article_edit':
        return obj.creator == user
    elif perm == 'article_delete':
        return obj.creator == user
    elif perm == 'article_vote_new':
        return True
    elif perm == 'article_tag_vote_new':
        return True
