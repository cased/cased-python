class Query:
    @classmethod
    def make_phrase_from_dict(cls, data):
        """
        Given a dict, return a single string appropriate for use in a
        'phrase' query. Note, this does not yet work with nested queries,
        e.g., {"actor": ["jill", "jane"]}, "action": "user.login"}

        The return value is a string that may include multiple additive
        filters for a search, just one filter, or none. For example:
            "(action=user.login AND actor=jill)
        """

        phrase = "("

        items = data.items()
        remaining = len(items)

        for k, v in items:
            remaining = remaining - 1

            part = "{}:{}".format(k, v)
            phrase = phrase + part

            # conjunct if we have more to add
            if remaining != 0:
                phrase = phrase + " AND "

        # finish the phrase
        phrase = phrase + ")"

        return phrase
