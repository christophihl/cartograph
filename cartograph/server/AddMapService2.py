import codecs
import csv
import json
import os
import pipes
from ConfigParser import SafeConfigParser
import falcon
import pandas
from cartograph.server.Map import Map


# TODO: move all these server-level configs into the meta config file
# This may be a good time to rethink the format of that file as well.
# Should it also use SafeConfig
from cartograph.server.ServerUtils import pid_exists, build_map

STATUS_NOT_STARTED = 'NOT_STARTED'
STATUS_RUNNING = 'RUNNING'
STATUS_FAILED = 'FAILED'
STATUS_SUCCEEDED = 'SUCCEEDED'

def filter_tsv(source_dir, target_dir, ids, filename):
    """Pare down the contents of <source_dir>/<filename> to only rows that start with an id in <ids>, and output them to
    <target_dir>/<filename>. <target_dir> must already exist. Also transfers over the first line of the file, which is
    assumed to be the header.
    e.g.
    filter_tsv(source_dir='/some/path/', dest_dir='/another/path', ids=['1', '3', '5'], filename='file.tsv')
    /some/path/file.tsv (before function call):
    id  name
    1   hello
    2   world
    3   foo
    4   bar
    5   spam
    /another/path/file.tsv (after function call):
    id  name
    1   hello
    3   foo
    5   spam
    :param source_dir: str of path to dir containing source data files (i.e. "/some/path/")
    :param target_dir: str of path to dir where result data files will be placed (i.e. "/another/path/")
    :param ids: an iterable of ids (each member should be a str); result data files will only have rows w\ these ids
    :param filename: the name of the file in <source_dir> to be filtered into a file of the same name in <target_dir>
    :return:
    """
    with codecs.open(os.path.join(source_dir, filename), 'r') as read_file, \
            codecs.open(os.path.join(target_dir, filename), 'w') as write_file:
        reader = csv.reader(read_file, delimiter='\t')
        writer = csv.writer(write_file, delimiter='\t', lineterminator='\n')
        write_file.write(read_file.readline())  # Transfer the header
        for row in reader:
            if row[0] in ids:
                writer.writerow(row)



class AddMapService:
    """A service to allow clients to build maps from already-uploaded data files (see UploadService). When POSTed to,
    this service will attempt to filter the appropriate (TSV) data files from a parent map, which is currently
    hard-coded as 'simple'. It will then create a config file and launch the build process from that config file. Once
    built, it will add the path of that config file to the active multi-config file and the list of active maps in
    self.map_services.
    """

    def __init__(self, server_config):
        """Initialize an AddMapService, a service to allow the client to build maps from already uploaded data files.
        When the client POSTs to this service, if there is a file in the upload directory of the matching name (i.e.
        map_name.tsv), this service will build a map with that name from that file.

        :param server_config: ServerConfig object
        :param upload_dir: (str) path to directory containing uploaded map data files
        """
        self.conf = server_config
        self.upload_dir = server_config.get('DEFAULT','upload_dir')

    def on_post(self, req, resp):
        """Making a POST request to this URL will cause the server to attempt to build a map from a file in the
        upload_dir by the name of <map_name>.tsv. If no such file exists, this service will respond with a 404.

        {
           "mapId":"zoo",
           "mapTitle":"Foo",
           "email":"shilad@gmail.com",
           "layers":[
              {
                 "field":"Clusters",
                 "id":"clusters",
                 "title":"Thematic Clusters",
                 "description":"This visualization shows groups of thematically related articles.",
                 "datatype":"qualitative",
                 "numColors":"7"
              },
              {
                 "field":"Popularity",
                 "id":"pop",
                 "title":"Popularity",
                 "description":"Popularity",
                 "datatype":"sequential",
                 "numColors":"3"
              }
           ]
        }

        """
        body = req.stream.read()
        js = json.loads(body)
        map_id = js['mapId']

        # Try to open map data file, raise 404 if not found in upload directory
        map_file_name = map_id + '.tsv'
        if map_file_name not in os.listdir(self.upload_dir):
            raise falcon.HTTPNotFound(description='No map file for ' + repr(map_file_name))
        input_file = open(os.path.join(self.upload_dir, map_file_name), 'r')

        map_config, map_config_path = self.gen_config(map_id, js)

        # Build from the new config file
        # This should go away
        build_map(map_config_path)

        # Clean up: delete the uploaded map data file
        os.remove(os.path.join(self.upload_dir, map_file_name))

        # Return helpful information to client
        resp.body = json.dumps({
            'success' : True,
            'map_name': map_id,
        })

    def get_logs(self, map_id):
        """
        Returns the luigi output log for the given map, or empty string if it doesn't exist
        """
        path = self.conf.getForDataset(map_id, 'DEFAULT', 'ext_dir') + '/build.log'
        if not os.path.isfile(path):
            return ''
        return open(path).read()

    def on_get(self, req, resp):
        map_id = req.get_param('map', required=True)
        status = get_build_status(self.conf, map_id)
        logs = self.get_logs(map_id)

        # Create a JSON representation of the resource
        resp.body = json.dumps({ 'status' : status, 'log' : logs }, ensure_ascii=False)

        resp.content_type = 'application/json'

    def gen_config(self, map_name, map_info):
        """Generate the config file for a user-generated map named <map_name> and return a path to it

        :param map_name: name of new map
        :return: path to the newly-generated config file
        """
        # Generate a new config file
        # Start with base values from template
        config = SafeConfigParser()
        config.read(self.conf.get('DEFAULT', 'map_config_template'))

        # Set name of dataset
        config.set('DEFAULT', 'dataset', map_name)


        # TODO: adjust parameters for size of dataset:
        # - numClusters
        # - perplexity
        # - water level
        # - min_num_in_cluster
        # - num_contours
        # - contour_bins

        ext_dir = self.conf.getForDataset(map_name, 'DEFAULT', 'ext_dir')
        active = []

        for info in map_info['layers']:
            #if info['field'] == 'Clusters': continue  # TODO: Fix this up
            id = info['id']
            field = info['field']

            # Configure settings for a metric
            metric_settings = {
                'type': info['datatype'],
                'path': os.path.join(ext_dir, id) + '.tsv',
                'field': field,
                'colorCode': info['colorScheme']
            }

            # Define new metric in config file
            config.set('Metrics', id, json.dumps(metric_settings))
            active.append(id)

        config.set('Metrics', 'active', ' '.join(active))

        # Write newly-generated config to file
        config_path = self.conf.getForDataset(map_name, 'DEFAULT', 'map_config_path')
        config_dir = os.path.dirname(config_path)
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        config.write(open(config_path, 'w'))

        return config, config_path

def get_status_path(server_conf, map_id):
    return server_conf.getForDataset(map_id, 'DEFAULT', 'ext_dir') + '/status.txt'

def get_build_status(server_conf, map_id):
    """
    Returns the status of map creation for the specified map.
    Double checks that maps that should be running ARE actually running.
    """
    path = get_status_path(server_conf, map_id)
    if not os.path.isfile(path):
        return STATUS_NOT_STARTED
    tokens = open(path).read().strip().split()
    status = tokens[0]
    if status == STATUS_RUNNING:
        pid = tokens[1]
        if not pid_exists(int(pid)):
            status = STATUS_FAILED
    return status