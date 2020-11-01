from app.database.models.techniques import Techniques
from typing import List, Dict


class CSVExport:
    def __init__(self, *args, **kwargs):
        self.techniques = Techniques.objects()

    def actors(self):
        pipeline = [
            { '$unwind': { 'path': '$actors',  'preserveNullAndEmptyArrays': False } },
            { '$project': {
                '_id': 0, 
                'technique': { '$arrayElemAt': [ '$references.external_id', 0 ] }, 
                'actor': '$actors.name'
                }
            }
        ]
        return list(self.techniques.aggregate(pipeline))

    def platforms(self):
        pipeline = [
            { '$unwind': { 'path': '$platforms',  'preserveNullAndEmptyArrays': False } },
            { '$project': {
                '_id': 0, 
                'technique': { '$arrayElemAt': [ '$references.external_id', 0 ] }, 
                'platform': '$platforms'
                }
            }
        ]

        return list(self.techniques.aggregate(pipeline))

    def permissions(self):
        pipeline = [
            { '$unwind': { 'path': '$permissions_required',  'preserveNullAndEmptyArrays': False } },
            { '$project': {
                '_id': 0, 
                'technique': { '$arrayElemAt': [ '$references.external_id', 0 ] }, 
                'permission_required': '$permissions_required'
                }
            }
        ]
        return list(self.techniques.aggregate(pipeline))


    def phases(self):
        pipeline = [
            { '$unwind': { 'path': '$kill_chain_phases',  'preserveNullAndEmptyArrays': False } },
            { '$project': {
                '_id': 0, 
                'technique': { '$arrayElemAt': [ '$references.external_id', 0 ] }, 
                'kill_chain_phase': '$kill_chain_phases'
                }
            }
        ]
        return list(self.techniques.aggregate(pipeline))
