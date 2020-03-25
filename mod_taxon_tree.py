import pickle
#import json # TODO: for3 django fixture
import pandas as pd

class TaxonTree(object):
    '''
    output tree_flat only, try make layered tree if needed

    tree_flat struct:
      - s: scientific name
      - v: vernacular name
      - p: parent (depends on rank_column_map[rank]['parent'])
      - n: speies count
      - a: append column data, seperate with |
    '''
    DEFAULT_RANK_LIST = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus']
    rank_column_map = {}
    tree_flat = {} # dict by rank_list
    rank_list = []
    is_debug = False

    def __init__(
            self,
            infile,
            rank_column_map,
            rank_list=[],
            is_debug=False):
        self.df = pd.read_csv(infile)
        if rank_list:
            self.rank_list = rank_list
        else:
            self.rank_list = self.DEFAULT_RANK_LIST
        self.rank_column_map = rank_column_map
        self.is_debug = is_debug

    def set_rank_list(self, rank_list=[]):
        if rank_list:
            self.rank_list = rank_list

    def log(self, cat, title, v):
        if self.is_debug:
            print ('[TaxonTree|{}] {}: '.format(cat, title), v)

    def info(self):
        self.log('info', 'columns', self.df.columns.to_list())
        self.log('info', 'head', self.df.head())

    def make_tree(self, item_range=[]):
        tree_flat = self.tree_flat if self.tree_flat else self.make_tree_flat(item_range)
        #tree = {} # TODO
        return tree_flat

    def make_tree_flat(self, item_range=[]):
        tree_flat = {} # dict by
        counter = 0
        rank_list = self.rank_list
        rank_column_map = self.rank_column_map
        begin = item_range[0] if item_range else 0
        end = item_range[1] if item_range else len(self.df)
        self.log('make_tree_flat', 'rank_list', self.rank_list)
        self.log('make_tree_flat', 'item_range', [begin, end])
        for row in self.df[begin:end].iterrows():
            counter += 1
            # find ranks
            for rank in rank_list:

                if rank not in tree_flat:
                    tree_flat[rank] = {}

                col_map = rank_column_map[rank]

                if pd.isna(row[1][col_map['name']]):
                    continue

                # taxon_id
                taxon_id = ''
                if '|' in col_map['key']:
                    key_list = col_map['key'].split('|')
                    taxon_id = '|'.join([
                        str(row[1][key_list[0]]),
                        str(row[1][key_list[1]]),
                        ])
                else:
                    taxon_id = str(row[1][col_map['key']])

                # parent
                taxon_parent = ''
                if col_map['parent']:
                    if not pd.isna(row[1][col_map['parent']]):
                        taxon_parent = str(row[1][col_map['parent']])

                if taxon_id not in tree_flat[rank]:

                    v = ''
                    if not pd.isna(row[1][col_map['vernacular']]):
                        v = str(row[1][col_map['vernacular']])

                    tree_flat[rank][taxon_id] = {
                        's': str(row[1][col_map['name']]),
                        'n': 0,
                        'v': v,
                        'p': taxon_parent,
                    }
                    if col_map.get('append', ''):
                        append_cols = col_map['append'].split('|')
                        append_list = []
                        for append_col in append_cols:
                            if pd.isna(row[1][append_col]):
                                append_list.append('--')
                            else:
                                append_list.append(str(row[1][append_col]))
                        tree_flat[rank][taxon_id]['a'] = '|'.join(append_list)

                tree_flat[rank][taxon_id]['n'] += 1

        self.log('make_tree_flat' ,'counter', counter)
        for i in self.rank_list:
            self.log('make_tree_flat', 'rank:{}'.format(i), len(tree_flat[i]))

        self.tree_flat = tree_flat
        return tree_flat

    def save(self, filename):
        self.log('save', 'filename', filename)
        with open(filename, 'wb') as handle:
            pickle.dump(self.tree_flat, handle)

    def read(self, filename):
        self.log('read', 'filename', filename)
        with open(filename, 'rb') as handle:
            self.tree_flat = pickle.load(handle)
            return self.tree_flat

    def check_duplicate(self, rank):
        namelist = []
        tree_flat = self.tree_flat
        taxa = tree_flat[rank]
        num_taxa = len(taxa)
        diff = []
        for k,v in taxa.items():
            if v['s'] not in namelist:
                namelist.append(v['s'])
            else:
                v['k'] = k
                self.log('check_duplicate', rank, str(v))
                diff.append(v)
        if len(namelist) != num_taxa:
            self.log('check_duplicate', rank, 'has {} duplicate names'.format(num_taxa-len(namelist)))
        else:
            self.log('check_duplicate', rank, 'looks good!')
        return diff
