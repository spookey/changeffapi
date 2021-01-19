from ffflash.inc.nodelist import handle_nodelist
from ffflash.inc.sidecars import handle_sidecars
from ffflash.inc.meshviewer import handle_meshviewer
from ffflash.info import info
from ffflash.lib.api import FFApi
from ffflash.lib.args import parsed_args
from ffflash.lib.clock import get_iso_timestamp
from ffflash.lib.files import check_file_location, dump_file, load_file


class FFFlash:
    '''
    This is the main object, which stores all relevant information,
    and the :class:`ffflash.lib.api.FFApi` itself.

    :param args: ``Namespace`` object from :meth:`ffflash.lib.args.parsed_args`
    '''
    def __init__(self, args):
        self.args = args
        self.location = check_file_location(self.args.APIfile, must_exist=True)
        self.api = None

        self.load_api()

    def load_api(self):
        '''
        Populate :attr:`api` with :class:`ffflash.lib.api.FFApi` with content
        loaded from :attr:`location`.

        :attr:`api` is populated only once, this prevents accidental reloads.
        '''
        if (self.api is None) and self.location:
            c = load_file(self.location, as_yaml=False)
            if c:
                self.api = FFApi(c)

    def set_timestamp(self):
        '''
        Inject :meth:`ffflash.lib.clock.get_iso_timestamp`
        into ``state.lastchange``.
        '''
        if self.access_for('api'):
            if self.api.pull('state', 'lastchange') is not None:
                self.api.push(get_iso_timestamp(), 'state', 'lastchange')

    def save(self):
        '''
        Save content from :attr:`api` (:class:`ffflash.lib.api.FFApi`) into
        :attr:`location`.
        A :meth:`ffflash.lib.api.FFApi.timestamp` is triggered before saving.
        '''
        if self.access_for('api'):
            self.set_timestamp()
            return dump_file(self.location, self.api.c, as_yaml=False)

    def access_for(self, name):
        '''
        Check if it is save to access the api and/or depending files.

        :param name: String specifier of part to access.
        :return: ``True`` or ``False``
        '''
        return all([
            (self.api is not None),
            {
                'api': self.location,
                'sidecars': self.args.sidecars,
                'nodelist': self.args.nodelist,
                'meshviewer': self.args.meshviewer,
                'rankfile': all([
                    (self.args.meshviewer or self.args.nodelist), self.args.rankfile
                ]),
            }.get(name, False)
        ])

    def log(self, message, level=True):
        '''
        Very advanced Logger. For professional use only.

        :param message: Some message string to display
        :param level: Severity of message. Can be anything as this is also the
            return value. There are three predefined rules:

            * ``True``: *info* (is dismissed unless ``--verbose`` was given)
            * ``None``: *warn*
            * ``False``: *error*
        :return: ``level``
        '''
        c = {
            True: 'info', None: 'warn', False: 'error'
        }.get(level, level) if (
            level is None or isinstance(level, (bool, str))
        ) else 'output'

        if self.args.verbose or level is not True:
            print('{}\t{}'.format(c.upper(), message))
        return level


def run(argv=None):
    '''
    Main function of |info_cname|.
    '''
    ff = FFFlash(parsed_args(argv))
    ff.log(info.ident)

    if not ff.access_for('api'):
        return (not ff.log('error loading API file', level=False))

    modified = []

    if ff.access_for('sidecars'):
        modified.append(
            handle_sidecars(ff)
        )

    if ff.access_for('nodelist'):
        modified.append(
            handle_nodelist(ff)
        )

    if ff.access_for('meshviewer'):
        modified.append(
            handle_meshviewer(ff)
        )

    if ff.args.dry:
        ff.log('\n{}'.format(ff.api.pretty()), level='API file preview')
    else:
        if any(modified):
            ff.save()
            ff.log('saved api file')

    return (not any(modified))
