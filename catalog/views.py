from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse

from .models import Objects, ObjectTypes, Columns, Relationships, Owners


def index(request):
    RESULTS_PER_PAGE = 3
    context = {}
    query = ""
    filter = "-1"

    # TODO: remove
    print("query: ", request.GET.get('q'))
    print("page: ", request.GET.get('page'))
    print("filter: ", request.GET.get('filter'))

    # if there is a query, retrieve it otherwise set it empty
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    # if there is a filter, retrieve it otherwise set as all
    if request.GET:
        filter = request.GET.get('filter', '-1')
        context['filter'] = str(filter)

    # TODO: filter on type as well. handle case of all
    # grab a query set of objects containing the query
    object_list = Objects \
        .objects \
        .filter(object_name__icontains=f"{query}") \
        .select_related('object_type') \

    if filter != "-1":
        object_list = object_list.filter(object_type=filter)

    object_list = object_list.order_by("id")

    # set up a paginator on the query set and handle edge cases
    page = request.GET.get('page', 1)
    paginator = Paginator(object_list, RESULTS_PER_PAGE)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    context['page_obj'] = page_obj

    context['page_range'] = paginator.get_elided_page_range(number=page, on_each_side=1, on_ends=1)

    # pass in the object types
    object_types = ObjectTypes.objects.all()
    context["object_types"] = object_types

    return render(request, "catalog/index.html", context)


def detail(request, object_id):
    context = {}
    obj = get_object_or_404(Objects.objects.select_related('object_type'), pk=object_id)
    context["obj"] = obj

    columns = Columns.objects.filter(parent=obj)
    if columns.exists:
        context["columns"] = columns

    owners = Owners.objects.filter(assigned_object=object_id).select_related('owner_type')
    if owners.exists:
        context["owners"] = owners

    return render(request, "catalog/detail.html", context)


def lineage(request):

    node_id = request.GET.get("node_id")
    if not node_id:
        return JsonResponse({'error': 'Mising node_id parameter'}, status=400)

    try:
        node_id = int(node_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid node_id parameter'}, status=400)

    downstream_relationships = Relationships.objects.raw('''
        WITH RECURSIVE rec(id, parent_id, parent_name, child_id, child_name, depth) AS (
            SELECT r.id, r.parent_id, o1.object_name, r.child_id, o2.object_name, 1 as depth
            FROM catalog_relationships r
            JOIN catalog_objects o1
            on o1.id = r.parent_id
            JOIN catalog_objects o2
            on o2.id = r.child_id
            WHERE parent_id = %s

            UNION ALL

            SELECT c.id, c.parent_id, o1.object_name, c.child_id, o2.object_name, r.depth + 1
            FROM catalog_relationships c
            JOIN rec r
            ON r.child_id = c.parent_id
            JOIN catalog_objects o1
            on o1.id = c.parent_id
            JOIN catalog_objects o2
            on o2.id = c.child_id
            where r.depth < 5
        )
        SELECT DISTINCT * FROM rec
    ''', [node_id])

    upstream_relationships = Relationships.objects.raw('''
        WITH RECURSIVE rec(id, parent_id, parent_name, child_id, child_name, depth) AS (
            SELECT r.id, r.parent_id, o1.object_name, r.child_id, o2.object_name, 1 as depth
            FROM catalog_relationships r
            JOIN catalog_objects o1
            on o1.id = r.parent_id
            JOIN catalog_objects o2
            on o2.id = r.child_id
            WHERE child_id = %s

            UNION ALL

            SELECT c.id, c.parent_id, o1.object_name, c.child_id, o2.object_name, r.depth + 1
            FROM catalog_relationships c
            JOIN rec r
            ON r.parent_id = c.child_id
            JOIN catalog_objects o1
            on o1.id = c.parent_id
            JOIN catalog_objects o2
            on o2.id = c.child_id
            where depth < 5
        )
        SELECT DISTINCT * FROM rec
    ''', [node_id])

    nodes_list = set()
    edges_list = set()
    for d in downstream_relationships:
        nodes_list.add((d.parent_id, d.parent_name))
        nodes_list.add((d.child_id, d.child_name))
        edges_list.add((d.parent_id, d.child_id))
    for u in upstream_relationships:
        nodes_list.add((u.parent_id, u.parent_name))
        nodes_list.add((u.child_id, u.child_name))
        edges_list.add((u.parent_id, u.child_id))

    nodes = []
    for (id, name) in nodes_list:
        node_data = {"id": str(id), "label": str(name)}
        if id == node_id:
            node_data['isRoot'] = True
        nodes.append({"data": node_data})
    edges = [{"data": {"source": str(e[0]), "target": str(e[1])}} for e in edges_list]

    return JsonResponse({"elements": nodes + edges})
