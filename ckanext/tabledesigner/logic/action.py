# encoding: utf-8
from ckan.plugins.toolkit import get_action, chained_action


@chained_action
def resource_create(original_action, context, data_dict):
    _tabledesigner_info = data_dict.pop('_tabledesigner_info', None)
    res = original_action(context, data_dict)
    _create_datastore_table(res, _tabledesigner_info)
    return res


@chained_action
def resource_update(original_action, context, data_dict):
    res = original_action(context, data_dict)
    res = _create_datastore_table(res)
    return res


def _create_datastore_table(res, info=None):
    if res.get('url_type') != 'tabledesigner':
        return
    if not res.get('datastore_active'):
        primary_key = [f['id'] for f in info if f.get('pk')]

        get_action('datastore_create')({}, {
            'resource_id': res['id'],
            'force': True,  # required because url_type != datastore
            'primary_key': primary_key,
            'fields': [{
                'id': i['id'],
                'type': i['type'],
                'info': {
                    k:v for (k, v) in i.items()
                    if k != 'id' and k != 'type'
                },
            } for i in info]
        })
    views = get_action('resource_view_list')({}, {
        'id': res['id']
    })
    if any(v['view_type'] == 'datatables_view' for v in views):
        return
    get_action('resource_view_create')({}, {
        'resource_id': res['id'],
        'view_type': 'datatables_view',
        'title': 'Table Designer',
    })