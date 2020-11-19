import dateparser

from base import fluent, Methods, Params, Param
from query import Query
from trustar_enums import ObservableTypes, SortColumns, AttributeTypes


class SearchIndicatorParamSerializer(Params):

    def serialize(self):
        return {n.key: n.value for n in self}


@fluent
class SearchIndicator:
    url = "/indicators"

    def __init__(self, config):
        self.trustar = config
        self.params = SearchIndicatorParamSerializer()
        self.tags = None
        self.from_date = None
        self.to_date = None
        self.page_size = 25
        self.indicator_id = None

    @property
    def endpoint(self):
        return self.trustar.request_details.get("api_endpoint") + self.url

    @property
    def tag_endpoint(self):
        return self.endpoint + "/{}/tags".format(self.indicator_id)

    def set_tag(self, tag):
        self.tags.add(tag)

    def set_page_size(self, size):
        self.page_size = size

    def set_custom_param(self, param):
        self.params.add(param)  # Receives a Param object

    @staticmethod
    def _get_timestamp(date):
        dt_obj = dateparser.parse(date)
        return int(dt_obj.strftime("%s"))

    def _valid_dates(self):
        return not (self.from_date and self.to_date and self.to_date < self.from_date)

    def set_query_term(self, query):
        self.params.add(Param("queryTerm", query))

    def set_from(self, from_date):
        if not isinstance(from_date, int):
            from_date = self._get_timestamp(from_date)
            self.from_date = from_date

        self.set_custom_param(Param("from", from_date))

    def set_to(self, to_date):
        if not isinstance(to_date, int):
            to_date = self._get_timestamp(to_date)
            self.to_date = to_date

        self.set_custom_param(Param("to", to_date))

    def set_sort_column(self, column):
        if not column in SortColumns.members():
            raise AttributeError(
                "column should be one of the following: {}".format(
                    list(SortColumns.members())
                ))

        self.params.add(Param("sortColumn", column))

    def set_priority_scores(self, scores):
        if any([s for s in scores if s > 3 or s < -1]):
            raise AttributeError(
                "scores should be a list of integers between -1 and 3"
            )

        self.params.add(Param("priorityScores", scores))

    def set_enclave_ids(self, enclave_ids):
        if not isinstance(enclave_ids, list):
            enclave_ids = [enclave_ids]
        self.set_custom_param(Param("enclaveIds", enclave_ids))

    def set_observable_types(self, types):
        selected_types = set(types)
        valid_types = set(ObservableTypes.members())
        if not selected_types.issubset(valid_types):
            raise AttributeError(
                "observable type should be one of the following: {}".format(
                    valid_types)
                )

        self.set_custom_param(Param("types", types))

    def set_attributes(self, attributes):
        attribute_types = [a.get("type") for a in attributes]
        selected_attributes = set(attribute_types)
        valid_attributes = set(AttributeTypes.members())
        if not selected_attributes.issubset(valid_attributes):
            raise AttributeError(
                "attribute type should be one of the following: {}".format(
                    valid_attributes
                ))

        self.set_custom_param(Param("attributes", attributes))

    def set_related_observables(self, observables):
        obs_types = [o.get("type") for o in observables]
        selected_observables = set(obs_types)
        valid_observables = set(ObservableTypes.members())
        if not selected_observables.issubset(valid_observables):
            raise AttributeError(
                "observable type should be one of the following: {}".format(
                    obs_types
                ))

        self.set_custom_param(Param("relatedObservables", observables))

    def set_indicator_id(self, indicator_id):
        self.indicator_id = indicator_id

    def query(self):
        # TODO check that the both the start and to are set
        if not self._valid_dates():
            raise AttributeError("Polling window should end after the start of it.")
        return Query(self.trustar, self.endpoint, Methods.POST, params=self.params,
                     query_string=("pageSize", str(self.page_size)))

    def create_tag(self):
        if not "tag" and "tag_id" in self.params:
            raise AttributeError("Indicator id and a tag are required for creating a new user tag")
        return Query(self.trustar, self.endpoint, Methods.POST, query_string=self.tag_endpoint).fetch_one()

    def delete_tag(self):
        if not self.indicator_id:
            raise AttributeError("Indicator id and a tag required for deleting a user tag")
        return Query(self.trustar, self.endpoint, Methods.DELETE, query_string=self.tag_endpoint).fetch_one()