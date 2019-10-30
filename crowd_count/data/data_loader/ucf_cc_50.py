# -*- coding:utf-8 -*-
# ucf_cc_50 dataset

from torch.utils.data import Dataset
import glob
from PIL import Image
import cv2
import numpy as np
import h5py


class UCFCC50(Dataset):

    def __init__(self, mode="train", **kwargs):
        self.root = "../data/ucf_cc_50/"
        self.sum_path = glob.glob(self.root + "*.jpg")
        self.paths = self.sum_path[: 40] if mode == 'train' else self.sum_path[40:]
        if mode == "train":
            self.paths *= 4
        self.transform = kwargs['transform']
        self.length = len(self.paths)
        self.dataset = self.load_data()

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        img, den = self.dataset[item]
        if self.transform is not None:
            img = self.transform(img)
        return img, den

    def load_data(self):
        result = []
        index = 0
        for img_path in self.paths:
            gt_path = img_path.replace('.jpg', '.h5').replace('images', 'ground_truth')
            img = Image.open(img_path).convert('RGB')
            with h5py.File(gt_path, 'r')  as gt_file:
                den = np.asarray(gt_file['density'])
            h = den.shape[0]
            w = den.shape[1]
            h_trans = h // 8
            w_trans = w // 8
            den = cv2.resize(den, (w_trans, h_trans),
                             interpolation=cv2.INTER_CUBIC) * (h * w) / (h_trans * w_trans)
            den = den[np.newaxis, :]
            result.append([img, den])
            if index % 100 == 99 or index == self.length:
                print("load {0}/{1} images".format(index + 1, self.length))
            index += 1
        return result
