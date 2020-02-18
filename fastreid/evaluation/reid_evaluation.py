# encoding: utf-8
"""
@author:  liaoxingyu
@contact: sherlockliao01@gmail.com
"""
import copy
from collections import OrderedDict

import torch

from .evaluator import DatasetEvaluator
from .rank import evaluate_rank


class ReidEvaluator(DatasetEvaluator):
    def __init__(self, cfg, num_query):
        self._num_query = num_query

        self.features = []
        self.pids = []
        self.camids = []

    def reset(self):
        self.features = []
        self.pids = []
        self.camids = []

    def process(self, outputs):
        self.features.append(outputs[0].cpu())
        self.pids.extend(outputs[1].cpu().numpy())
        self.camids.extend(outputs[2].cpu().numpy())

    def evaluate(self):
        features = torch.cat(self.features, dim=0)

        # query feature, person ids and camera ids
        query_features = features[:self._num_query]
        query_pids = self.pids[:self._num_query]
        query_camids = self.camids[:self._num_query]

        # gallery features, person ids and camera ids
        gallery_features = features[self._num_query:]
        gallery_pids = self.pids[self._num_query:]
        gallery_camids = self.camids[self._num_query:]

        self._results = OrderedDict()

        cos_dist = torch.mm(query_features, gallery_features.t()).numpy()
        cmc, mAP = evaluate_rank(-cos_dist, query_pids, gallery_pids, query_camids, gallery_camids)
        for r in [1, 5, 10]:
            self._results['Rank-{}'.format(r)] = cmc[r - 1]
        self._results['mAP'] = mAP

        return copy.deepcopy(self._results)
