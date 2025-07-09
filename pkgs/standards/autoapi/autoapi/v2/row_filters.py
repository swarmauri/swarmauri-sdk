def _apply_row_filters(model, q, ctx, *, strategy: str = "intersection") -> Query:
    """Return *q* filtered by every mix-in the model inherits.

    strategy = "intersection"  → AND all predicates
    strategy = "union"         → OR  predicates (wider view)
    """
    predicates = []
    for mixin in (AuthnBound, MemberBound):  # extend list as needed
        if issubclass(model, mixin):
            predicates.append(mixin.filter_for_ctx(q, ctx).whereclause)

    if not predicates:
        return q  # model not bound at all

    if strategy == "intersection":
        for p in predicates:
            q = q.filter(p)
        return q    else:  # union
        return q.filter(or_(*predicates))
