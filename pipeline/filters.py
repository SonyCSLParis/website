import django_filters
import itertools
from django.db.models import Q
from .models import Pipeline


class PipelineFilter(django_filters.FilterSet):
    ex = django_filters.filters.CharFilter(method='filter_ex')
    search_fields = ['name', 'description']

    # take a single input and search for it across all search fields
    # https://spapas.github.io/2016/09/12/django-split-query/
    def filter_ex(self, qs, name, value):
        if value:
            q_parts = value.split()

            # Permutation code copied from http://stackoverflow.com/a/12935562/119071

            list1 = self.search_fields
            list2 = q_parts
            perms = [zip(x, list2) for x in itertools.permutations(list1, len(list2))]

            q_totals = Q()
            for perm in perms:
                q_part = Q()
                for p in perm:
                    q_part = q_part & Q(**{p[0] + '__icontains': p[1]})
                q_totals = q_totals | q_part

            qs = qs.filter(q_totals)
        return qs

    class Meta:
        model = Pipeline
        fields = ['ex']
