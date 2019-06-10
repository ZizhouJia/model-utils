import os
import random

import numpy as np
import torch
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
# import Image
#the dict dict["file name"]=label
class dict_dataset(torch.utils.data.Dataset):
    def __init__(self,dataset_dict,path,mode,transform,percent=[0.7,0.1,0.2],shuffle=True,load_mode=False,load_mode_reshape_size=(600,600)):
        self.dataset_dict=dataset_dict
        self.path=path
        self.mode=mode
        self.load_mode=load_mode
        self.load_mode_reshape_size=load_mode_reshape_size
        self.dataset_dict_list=self.dataset_dict.keys()
        random.seed(666)
        random.shuffle(self.dataset_dict_list)
        self.transform=transform[self.mode]
        self.train_data_numbers=int(len(self.dataset_dict_list)*percent[0])
        self.val_data_numbers=int(len(self.dataset_dict_list)*percent[1])
        self.test_data_numbers=len(self.dataset_dict_list)-self.train_data_numbers-self.val_data_numbers
        self.image_dict={}

    def _read_image(self,key_name):
        image_name=os.path.join(self.path,key_name)
        image=Image.open(image_name+".jpg").convert('RGB')
        if(self.load_mode):
            return image.resize(self.load_mode_reshape_size,Image.BILINEAR)
        else:
            return image


    def _mapping_index(self,index):
        actual_index=index
        if(self.mode=="train"):
            return actual_index
        if(self.mode=="val"):
            return actual_index+self.train_data_numbers
        if(self.mode=="test"):
            return actual_index+self.train_data_numbers+self.val_data_numbers
        return actual_index

    def __getitem__(self,index):
        actual_index=self._mapping_index(index)
        key_name=self.dataset_dict_list[actual_index]
        label=self.dataset_dict[key_name]
        image=None
        if(self.load_mode):
            if(self.image_dict.has_key(key_name)):
                image=self.image_dict[key_name]
            else:
                image=self._read_image(key_name)
                self.image_dict[key_name]=image
        else:
            image=self._read_image(key_name)
        image=self.transform(image)

        if(isinstance(label,list)):
            label.insert(0,image)
            return tuple(label)
        if(isinstance(label,tuple)):
            label=list(label)
            label.insert(0,image)
            return tuple(label)
        else:
            return image,label

    def __len__(self):
        if(self.mode=="train"):
            return self.train_data_numbers
        if(self.mode=="val"):
            return self.val_data_numbers
        if(self.mode=="test"):
            return self.test_data_numbers

class three_set_dataset(dict_dataset):
    def __init__(self,dataset_dict,path,mode,transform,load_mode=False,load_mode_reshape_size=(600,600)):
        self.path=path
        self.mode=mode
        self.transform=transform[self.mode]
        self.load_mode=load_mode
        self.load_mode_reshape_size=load_mode_reshape_size
        train_dict=dataset_dict["train"]
        val_dict=dataset_dict["val"]
        test_dict=dataset_dict["test"]
        self.train_data_numbers=len(train_dict)
        self.val_data_numbers=len(val_dict)
        self.test_data_numbers=len(test_dict)
        self.dataset_dict_list=train_dict.keys()+val_dict.keys()+test_dict.keys()
        self.dataset_dict=dict(train_dict.items()+val_dict.items()+test_dict.items())
        self.image_dict={}

class matrix_dataset(torch.utils.data.Dataset):
    def __init__(self,matrix,label,mode,transform=None,id=None,soft_label=None,shuffle=True,percent=[0.7,0.1,0.2]):
        self.matrix=matrix
        self.label=label
        self.soft_label=soft_label
        self.id=id
        np.random.seed(666)
        index=np.arange(self.matrix.shape[0])
        np.random.shuffle(index)
        self.matrix=self.matrix[index]
        self.label=self.label[index]
        if(self.soft_label is not None):
            self.soft_label=self.soft_label[index]
        if(self.id is not None):
            self.id=self.id[index]
        self.mode=mode
        self.transform=transform
        self.train_data_numbers=int(self.matrix.shape[0]*percent[0])
        self.val_data_numbers=int(self.matrix.shape[0]*percent[1])
        self.test_data_numbers=self.matrix.shape[0]-self.train_data_numbers-self.val_data_numbers

    def _mapping_index(self,index):
        actual_index=index
        if(self.mode=="train"):
            return actual_index
        if(self.mode=="val"):
            return actual_index+self.train_data_numbers
        if(self.mode=="test"):
            return actual_index+self.train_data_numbers+self.val_data_numbers
        return actual_index

    def __getitem__(self,index):
        actual_index=self._mapping_index(index)
        id=""
        if(self.id is not None):
            id=self.id[actual_index]
        if(self.soft_label is not None):
            return id,torch.Tensor(self.matrix[actual_index]),self.label[actual_index],torch.Tensor(self.soft_label[actual_index])
        else:
            return id,torch.Tensor(self.matrix[actual_index]),self.label[actual_index]

    def __len__(self):
        if(self.mode=="train"):
            return self.train_data_numbers
        if(self.mode=="val"):
            return self.val_data_numbers
        if(self.mode=="test"):
            return self.test_data_numbers
