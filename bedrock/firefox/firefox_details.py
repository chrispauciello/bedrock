import re
from operator import itemgetter
from urllib import urlencode

from product_details import ProductDetails


# TODO: port this to django-mozilla-product-details
class FirefoxDetails(ProductDetails):
    download_base_url_direct = 'https://download.mozilla.org/'
    download_base_url_transition = '/products/download.html'
    platform_info = {
        'Windows': {
            'title': 'Windows',
            'id': 'win',
        },
        'OS X': {
            'title': 'Mac OS X',
            'id': 'osx',
        },
        'Linux': {
            'title': 'Linux',
            'id': 'linux',
        },
    }
    channel_map = {
        'aurora': 'FIREFOX_AURORA',
        'beta': 'LATEST_FIREFOX_DEVEL_VERSION',
        'esr': 'FIREFOX_ESR',
        'release': 'LATEST_FIREFOX_VERSION',
    }

    def __init__(self):
        super(FirefoxDetails, self).__init__()

    def latest_version(self, channel):
        version = self.channel_map.get(channel, 'LATEST_FIREFOX_VERSION')
        return self.firefox_versions[version]

    def latest_major_version(self, channel):
        """Return latest major version as an int."""
        lv = self.latest_version(channel)
        try:
            return int(lv.split('.')[0])
        except ValueError:
            return 0

    @property
    def esr_major_versions(self):
        return range(10, self.latest_major_version('release'), 7)

    def _matches_query(self, info, query):
        words = re.split(r',|,?\s+', query.strip().lower())
        return all((word in info['name_en'].lower() or
                    word in info['name_native'].lower()) for word in words)

    def _get_filtered_builds(self, builds, version, query=None):
        """
        Get a list of builds, sorted by english locale name, for a specific
        Firefox version.
        :param builds: a build dict from the JSON
        :param version: a firefox version. one of self.latest_versions.
        :param query: a string to match against native or english locale name
        :return: list
        """
        f_builds = []
        for locale, build in builds.iteritems():
            build_info = {
                'locale': locale,
                'name_en': self.languages[locale]['English'],
                'name_native': self.languages[locale]['native'],
                'platforms': {},
            }

            platforms = build.get(version)
            if not platforms:
                continue

            # only include builds that match a search query
            if query is not None and not self._matches_query(build_info, query):
                continue

            for plat in platforms:
                build_info['platforms'][plat] = {
                    'download_url': self.get_download_url(plat, locale,
                                                          version),
                }

            f_builds.append(build_info)

        return sorted(f_builds, key=itemgetter('name_en'))

    def get_filtered_full_builds(self, version, query=None):
        """
        Return filtered builds for the fully translated releases.
        :param version: a firefox version. one of self.latest_version.
        :param query: a string to match against native or english locale name
        :return: list
        """
        return self._get_filtered_builds(self.firefox_primary_builds,
                                         version, query)

    def get_filtered_test_builds(self, version, query=None):
        """
        Return filtered builds for the translated releases in beta.
        :param version: a firefox version. one of self.latest_version.
        :param query: a string to match against native or english locale name
        :return: list
        """
        return self._get_filtered_builds(self.firefox_beta_builds,
                                         version, query)

    def get_download_url(self, platform, language, version, product='firefox'):
        """
        Get direct download url for the product.
        :param platform: OS. one of self.platform_info.keys()
        :param language: a locale. e.g. pt-BR. one exception is ja-JP-mac
        :param version: a firefox version. one of self.latest_version.
        :param product: optional. probably 'firefox'
        :return: string url
        """
        if platform == 'OS X' and language == 'ja':
            language = 'ja-JP-mac'
        return '?'.join([self.download_base_url_direct,
                         urlencode([
                             ('product', '%s-%s' % (product, version)),
                             ('os', self.platform_info[platform]['id']),
                             # Order matters, lang must be last for bouncer.
                             ('lang', language),
                         ])])


class MobileDetails(ProductDetails):
    channel_map = {
        'aurora': 'alpha_version',
        'beta': 'beta_version',
        'release': 'version',
    }

    def __init__(self):
        super(MobileDetails, self).__init__()

    def latest_version(self, channel):
        version = self.channel_map.get(channel, 'version')
        return self.mobile_details[version]


firefox_details = FirefoxDetails()
mobile_details = MobileDetails()
