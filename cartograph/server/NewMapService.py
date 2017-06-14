import csv
import falcon
import os


def filter_tsv(source_dir, target_dir, ids, filename):
    """Pare down the contents of <source_dir>/<filename> to only rows that start with an id in <ids>, and output them to
    <target_dir>/<filename>. <target_dir> must already exist.

    e.g.
    filter_tsv(source_dir='/some/path/', dest_dir='/another/path', ids=['1', '3', '5'], filename='file.tsv')

    /some/path/file.tsv (before function call):
    1   hello
    2   world
    3   foo
    4   bar
    5   spam

    /another/path/file.tsv (after function call):
    1   hello
    3   foo
    5   spam

    :param source_dir:
    :param target_dir:
    :param ids: an iterable of the ids
    :param filename: the name of the file in <source_dir> to be filtered into a file of the same name in <target_dir>
    :return:
    """

    with open(os.path.join(source_dir, filename), 'r') as read_file:
        with open(os.path.join(target_dir, filename), 'w') as write_file:
            popularities_reader = csv.reader(read_file, delimiter='\t')
            popularities_writer = csv.writer(write_file, delimiter='\t')
            for row in popularities_reader:
                if row[0] in ids:
                    popularities_writer.writerow(row)


class NewMapService:
    BASE_PATH = './data/ext/'
    SOURCE_DIR = os.path.join(BASE_PATH, 'simple/')  # Path to source data (which will be pared down for the user)

    def on_get(self, req, resp):
        resp.stream = open('./web/newMap.html', 'rb')
        resp.content_type = 'text/html'

    def on_post(self, req, resp):
        post_data = falcon.uri.parse_query_string(req.stream.read())
        resp.body = ''

        # Generate dictionary of article names to IDs TODO: is there a way to do this once (instead of once per POST)?
        names_path = os.path.join(self.SOURCE_DIR, 'names.tsv')
        name_dict = {}
        with open(names_path, 'r') as names:
            names_reader = csv.reader(names, delimiter='\t')
            for row in names_reader:
                name_dict[row[1]] = row[0]

        # Generate list of IDs for article names in user request
        ids = []
        for term in post_data['articles'].split('\r\n'):
            try:
                ids += [name_dict[term]]  # Attempts to find entry in dict of Articles to IDs
            except KeyError:
                resp.body += 'NO MATCH FOR TERM: %s\n' % (term,)

        # Create the destination directory (if it doesn't exist already)
        target_path = os.path.join(self.BASE_PATH, post_data['name'])
        if not os.path.exists(target_path) and not os.path.isdir(target_path):
            os.makedirs(target_path)

        # For each of the data files, filter it and output it to the target directory
        for filename in ['ids.tsv', 'links.tsv', 'names.tsv', 'popularity.tsv', 'vectors.tsv']:
            filter_tsv(self.SOURCE_DIR, target_path, ids, filename)