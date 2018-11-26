
import numpy as np 
from torch import nn 
import torch.nn.functional as F


def new_size_conv(size, kernel, stride=1, padding=0): 
    return np.floor((size + 2*padding - (kernel -1)-1)/stride +1)
    
    
def new_size_max_pool(size, kernel, stride=None, padding=0): 
    if stride == None: 
        stride = kernel
    return np.floor((size + 2*padding - (kernel -1)-1)/stride +1)

def calc_alexnet_size(size): 
    x = new_size_conv(size, 6,3,2)
    x = new_size_max_pool(x,3,2)
    x = new_size_conv(x,5,1,2)
    x = new_size_max_pool(x,3,2)
    x = new_size_conv(x,3,1,1)
    x = new_size_conv(x,3,1,1)
    x = new_size_conv(x,3,1,1)
    out = new_size_max_pool(x,2,2)
    
    return out


class AlexNet(nn.Module):
    def __init__(self, n_in=3, n_classes=10, n_filters=64, size=32):
        super(AlexNet, self).__init__()

        n_h1 = 3 * n_filters
        n_h2 = 2 * n_h1
        
        self.features = nn.Sequential(
            nn.Conv2d(n_in, n_filters, kernel_size=6, stride=3, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(n_filters, n_h1, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2),
            nn.Conv2d(n_h1, n_h2, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(n_h2, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        out_feat_size = calc_alexnet_size(size)
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * out_feat_size * out_feat_size, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, n_classes),
        )
        
    def forward(self, x):

        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x
    
class tiny_cnn(nn.Module): 
    def __init__(self, n_in=3, n_classes=10, n_filters=64, size=64): 
        super(tiny_cnn, self).__init__()
       
        
        self.size = size 
        self.n_filters = n_filters

        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(n_in, n_filters, kernel_size=5, stride=1, padding=2), 
            nn.BatchNorm2d(n_filters), 
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(n_filters, 2*n_filters, kernel_size=5, stride=1, padding=2), 
            nn.BatchNorm2d(2*n_filters), 
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        ) 
        self.fc = nn.Linear(2*n_filters * (self.size//4) * (self.size//4), 2*n_filters)
        self.output = nn.Linear(2*n_filters, n_classes)
        
    def forward(self, x): 
        x = self.conv_block_1(x)
        x = self.conv_block_2(x)
        x = x.view(x.size(0), -1)
        #x = x.view(-1, 2*self.n_filters * (self.size//4) * (self.size//4))
        x = self.fc(x)
        out = self.output(x)
        
        return out
    
    
class mlleaks_cnn(nn.Module): 
    def __init__(self, n_in=3, n_classes=10, n_filters=64, size=128): 
        super(mlleaks_cnn, self).__init__()
        
        self.n_filters = n_filters 
        
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(n_in, n_filters, kernel_size=5, stride=1, padding=2), 
            nn.BatchNorm2d(n_filters), 
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(n_filters, 2*n_filters, kernel_size=5, stride=1, padding=2), 
            nn.BatchNorm2d(2*n_filters), 
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        ) 
        self.fc = nn.Linear(2*n_filters * 8 * 8, size)
        self.output = nn.Linear(2*n_filters, n_classes)
        
    def forward(self, x): 
        x = self.conv_block_1(x)
        x = self.conv_block_2(x)
        x = x.view(-1, 2*self.n_filters * 8 * 8)
        x = self.fc(x)
        out = self.output(x)
        
        return out
    
class mlleaks_mlp(nn.Module): 
    def __init__(self, n_in=3, n_classes=1, n_filters=64, size=64): 
        super(mlleaks_mlp, self).__init__()
        
        self.hidden = nn.Linear(n_in, n_filters)
        #self.bn = nn.BatchNorm1d(n_filters)
        self.output = nn.Linear(n_filters, n_classes)
        
    def forward(self, x): 
        x = F.sigmoid(self.hidden(x))
        #x = self.bn(x)
        out = self.output(x)
        #out = F.sigmoid(self.output(x))
        
        return out
    

class cnn(nn.Module): 
    def __init__(self, n_in, n_classes, n_filters, size): 
        super(cnn, self).__init__()
        
        self.n_filters = n_filters 
        
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(n_in, n_filters, kernel_size=3, padding=1), 
            nn.BatchNorm2d(n_filters), 
            nn.ReLU(inplace=True), 
            nn.MaxPool2d(2)
        ) 
        # shape = [Batch_size, n_filters, height/2, width/2]
            
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(n_filters, n_filters*2, kernel_size=3, padding=1), 
            nn.BatchNorm2d(n_filters*2), 
            nn.ReLU(inplace=True), 
            nn.MaxPool2d(2)
        ) 
        # shape = [Batch_size, n_filters*2, height/4, width/4] 
        
        self.dense_block_1 = nn.Sequential(
            ##nn.Linear(n_filters * 2 * 8 * 8, 64), 
            nn.Linear(n_filters*2 * 8 * 8, 128), 
            ##nn.BatchNorm1d(64), 
            ##nn.ReLU(inplace=True)
        ) 
        # shape = [Batch_size, 64]
        
        self.dense_block_2 = nn.Sequential(
            nn.Linear(64, 32), 
            nn.BatchNorm1d(32), 
            nn.ReLU(inplace=True)
        ) 
        # shape = [Batch_size, 32]
        
        self.dense_block_3 = nn.Sequential( 
            nn.Linear(32, n_classes), 
            nn.BatchNorm1d(n_classes)
        ) 
        # shape = [Batch_size, 10]
        
        
    def forward(self, x): 
        x = self.conv_block_1(x)
        x = self.conv_block_2(x)

        x = x.view(-1, self.n_filters*2 * 8 * 8)
        x = self.dense_block_1(x)
        x = self.dense_block_2(x)
        out = self.dense_block_3(x)

        return out
        
        
class mlp(nn.Module): 
    def __init__(self, n_in, n_classes, n_filters, size): 
        super(mlp, self).__init__()
        
        self.n_filters = n_filters 
        
        # shape = [Batch_size, k (top k posteriors)] 
        
        self.dense_block_1 = nn.Sequential(
            nn.Linear(n_in, n_filters*2), 
            #nn.BatchNorm1d(n_filters*2), 
            nn.ReLU(inplace=True)
        ) 
        # shape = [Batch_size, n_filters*2]
        
        self.dense_block_2 = nn.Sequential(
            nn.Linear(n_filters*2, n_filters*2), 
            #nn.BatchNorm1d(n_filters*2), 
            nn.ReLU(inplace=True)
        ) 
        # shape = [Batch_size, 32]
        
        self.dense_block_3 = nn.Sequential( 
            nn.Linear(n_filters*2, n_classes), 
            #nn.BatchNorm1d(n_classes), 
            nn.Sigmoid()
        ) 
        # shape = [Batch_size, 10]
        
        
    def forward(self, x): 

        x = self.dense_block_1(x)
        x = self.dense_block_2(x)
        out = self.dense_block_3(x)

        return out

            
def weights_init(m): 
    if isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.Linear): 
        nn.init.xavier_normal_(m.weight.data)
        nn.init.constant_(m.bias, 0)


PREDEF_MODELS = {"alexnet"     : AlexNet,
                 "cnn"         : cnn,
                 "tiny_cnn"    : tiny_cnn,
                 "mlleaks_cnn" : mlleaks_cnn,
                 "mlp"         : mlp,
                 "mlleaks_mlp" : mlleaks_mlp}


def get_predef_model(name=""):
    """
    Convenience function for retreiving predefined model arch

    Parameters
    ----------
    name : {'alexnet', 'cnn', 'tiny_cnn', 'mlleaks_cnn', 'mlp', 'mlleaks_mlp'}
        Name of model

    Returns
    -------
    model : Model
        Predefined model arch
    """
    name = name.lower()
    if name in PREDEF_MODELS:
        model = PREDEF_MODELS[name]
        return model
    else:
        raise ValueError('Invalid predefined model, {}, requested.'
                         ' Must be in {}'.format(name, PREDEF_MODELS.keys()))
