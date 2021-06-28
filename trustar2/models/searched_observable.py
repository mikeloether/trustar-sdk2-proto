



class SearchedObservable(object):


    def __init__(self, type, value, first_seen, last_seen, enclave_guids, tags):
        self.type = type
        self.value = value
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.enclave_guids = enclave_guids
        self.tags = tags


    def __str__(self):
        return "SearchedObservable(type={}, value={})".format(self.type, self.value)


    def __repr__(self):
        return str(self)


    @classmethod
    def from_dict(cls, obs_dict):
        return cls(
            type=obs_dict.get("type"),
            value=obs_dict.get("value"),
            first_seen=obs_dict.get("firstSeen"),
            last_seen=obs_dict.get("lastSeen"),
            enclave_guids=obs_dict.get("enclaveGuids"),
            tags=obs_dict.get("tags")
        )
