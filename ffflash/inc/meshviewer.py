from ffflash.inc.rankfile import handle_rankfile
from ffflash.lib.files import check_file_location, load_file
from ffflash.lib.remote import fetch_www_struct
from ffflash.lib.text import replace_text

def _meshviewer_fetch(ff):
    if not ff.access_for('meshviewer'):
        return False

    ff.log('fetching meshviewer data {}'.format(ff.args.nodelist))

    nodes = (
        load_file(ff.args.meshviewer, fallback=None, as_yaml=False)
        if check_file_location(ff.args.meshviewer, must_exist=True) else
        fetch_www_struct(ff.args.meshviewer, fallback=None, as_yaml=False)
    )

    if not nodes or not isinstance(nodes, dict):
        return ff.log(
            'could not fetch meshviewer file {}'.format(ff.args.nodelist),
            level=False
        )

    if not all([(a in nodes) for a in ['links', 'nodes', 'timestamp']]):
        return ff.log(
            'this is no nodelist {}'.format(ff.args.nodelist),
            level=False
        )

    ff.log('successfully fetched meshviewer data from {}'.format(ff.args.nodelist))
    return nodes.get("nodes", [])

def _node_count(ff, nodes):
    domain = ff.args.domain

    relevant_nodes = [
        node for node in nodes
            if node.get('is_online', False) and (domain is None or domain == node.get("domain"))
    ]

    clients = sum([node.get('clients', 0) for node in relevant_nodes])

    return len(relevant_nodes), clients, relevant_nodes

def _meshviewer_dump(ff, nodes, clients):
    '''
    Store the counted numbers in the api-file.

    Sets the key ``state`` . ``nodes`` with the node number.

    Leaves ``state`` . ``description`` untouched, if any already present.
    If empty, or the pattern ``\[[\d]+ Nodes, [\d]+ Clients\]`` is matched,
    the numbers in the pattern will be replaced.

    :param ff: running :class:`ffflash.main.FFFlash` instance
    :param nodes: Number of online nodes
    :param clients: Number of their clients
    :return: ``True`` if :attr:`api` was modified else ``False``
    '''
    if not ff.access_for('meshviewer'):
        return False

    modified = []
    if ff.api.pull('state', 'nodes') is not None:
        ff.api.push(nodes, 'state', 'nodes')
        ff.log('stored {} in state.nodes'.format(nodes))
        modified.append(True)

    descr = ff.api.pull('state', 'description')
    if descr is not None:
        new = '[{} Nodes, {} Clients]'.format(nodes, clients)
        new_descr = (replace_text(
            r'(\[[\d]+ Nodes, [\d]+ Clients\])', new, descr
        ) if descr else new)
        ff.api.push(new_descr, 'state', 'description')
        ff.log('stored {} nodes and {} clients in state.description'.format(
            nodes, clients
        ))
        modified.append(True)

    return any(modified)

def handle_meshviewer(ff):
    if not ff.access_for('meshviewer'):
        return False

    nodes = _meshviewer_fetch(ff)
    if not nodes:
        return False

    modified = []

    node_count, clients, relevant_nodes = _node_count(ff, nodes)
    if all([nodes, clients]):
        modified.append(
            _meshviewer_dump(ff, node_count, clients)
        )

    if ff.access_for('rankfile'):
        modified.append(
            handle_rankfile(ff, relevant_nodes)
        )

    return any(modified)
