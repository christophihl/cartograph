import logging
import os
import shutil

from cartograph import Config
from cartograph.server.CountryService import CountryService
from cartograph.server.LoggingService import LoggingService
from cartograph.server.AddMetricService import AddMetricService
from cartograph.server.PointService import PointService
from cartograph.server.RasterService import RasterService
from cartograph.server.RelatedPointsService import RelatedPointsService
from cartograph.server.SearchService import SearchService
from cartograph.server.StaticService import StaticService
from cartograph.server.TemplateService import TemplateService
from cartograph.server.TileService import TileService


class MapService:
    """A set of services for a particular map    
    """
    def __init__(self, conf_path):
        """Initialize all necessary services for a map for this
        :param conf_path: Path to config file for this map
        """
        if not os.path.isfile(conf_path):
            raise Exception, 'Cartograph Config Path %s does not exist' % `conf_path`

        self.last_update = os.path.getmtime(conf_path)
        self._send_update = False
    
        conf = Config.initConf(conf_path)
        self.name = conf.get('DEFAULT', 'dataset')
    
        if os.getenv('CLEAR_CACHE'):
            logging.info('clearing cache directory %s' % conf.get('DEFAULT', 'webCacheDir'))
            shutil.rmtree(conf.get('DEFAULT', 'webCacheDir'), ignore_errors=True)
    
        if os.getenv('BASE_URL'):
            conf.set('Server', 'base_url', os.getenv('BASE_URL'))
    
        logging.info('initializing services for ' + self.name)

        self.add_metric_service = AddMetricService(conf_path, self)
        self.logging_service = LoggingService(conf)
        self.point_service = PointService(conf)
        self.country_service = CountryService(conf)
        self.tile_service = TileService(conf, self.point_service, self.country_service)
        self.mapnik_service = RasterService(conf, self.point_service, self.country_service)
        self.template_service = TemplateService(conf)
        self.related_points_service = RelatedPointsService(conf, self.point_service)
        self.static_service = StaticService(conf)
        self.search_service = SearchService(self.point_service)

    def trigger_update(self):
        """Trigger an update to be propagated system-wide
        :return:
        """
        print("Update triggered for map %s" % (self.name,))
        self._send_update = True

    def needs_update(self):
        """Check if this map wants to trigger an update. If this returns True, it is the responsibility of the caller to
        change the modification time of the active meta-conf, if there is one. All server instances should be watching
        the mod time of the meta-conf to know when to update their maps. If this
        :return: True if
        """
        needs_update = self._send_update
        self._send_update = False
        if needs_update:
            print('Map %s requests an update!' % (self.name,))
        return needs_update
