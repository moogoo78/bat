from mod_taxon_tree import TaxonTree

'''
make taxon_tree & generate for django fixture
'''
## TaiCoL 的 xxx_id 不能用, 有很多重複的
rank_column_map = {
    'kingdom': {
        'key': 'kingdom',
        'name': 'kingdom',
        'vernacular': 'kingdom_c',
        'parent': '',
    },
    'phylum': {
        'key': 'phylum|kingdom',
        'name': 'phylum',
        'vernacular': 'phylum_c',
        'parent': 'kingdom',
    },
    'class': {
        'key': 'class|phylum',
        'name': 'class',
        'vernacular': 'class_c',
        'parent': 'phylum',
    },
    'order': {
        'key': 'order|class',
        'name': 'order',
        'vernacular': 'order_c',
        'parent': 'class',
    },
    'family': {
        'key': 'family|order',
        'name': 'family',
        'vernacular': 'family_c',
        'parent': 'order',
    },
    'genus': {
        'key': 'genus|family',
        'name': 'genus',
        'vernacular': 'genus_c',
        'parent': 'family',
    },
    'species': {
        'key': 'name_code',
        'name': 'species',
        'vernacular': 'common_name_c',
        'parent': 'genus',
        'append': 'name_code|is_accepted_name|accepted_name_code|infraspecies|infraspecies_marker|infraspecies2|infraspecies2_marker|author|author2'
    },
}
rank_list = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
tt = TaxonTree('res/table_specieslist-200313.csv', rank_column_map, rank_list, is_debug=True)
#tt.info()
#a = tt.make_tree([0, 20])

#a = tt.make_tree()
#tt.save('dist/taicol-0313-flat.pickle')

a = tt.read('dist/taicol-0313-flat.pickle')

#tt.check_duplicate('family')
#tt.check_duplicate('phylum')

# to django fixture
import json
pk = 0
model = 'data.taxon'
data = []
rank_parent_data = {x:{} for x in tt.rank_list}
for rank in a:

    for key in a[rank]:
        pk += 1
        taxon_data = a[rank][key]
        d = {
            'model': 'data.taxon',
            'pk': pk,
            'fields': {
                'rank': rank,
                'name': taxon_data['s'],
                'name_zh': taxon_data['v'],
                'count': taxon_data['n'],
                'tree_id': 1,
            }
        }
        #print (d)
        rank_parent_data[rank][key] = pk

        parent_key = taxon_data.get('p', '')
        if parent_key:
            parent_rank = tt.rank_list[tt.rank_list.index(rank)-1]
            #print ('parent',key, parent_rank, parent_key)
            if rank_parent_data[parent_rank].get(parent_key, ''):
                d['fields']['parent_id'] = rank_parent_data[parent_rank][parent_key]

        if rank == 'species':
            append_list = taxon_data['a'].split('|')
            d['fields']['source_id'] = append_list[0]
            d['fields']['is_accepted_name'] = True if append_list[1] == '1.0' else False
            d['fields']['verbose'] = taxon_data['a']
        data.append(d)
print (pk)

f = open('dist/taibif-data-taxon.json', 'w')
f.write(json.dumps(data))
f.close()




