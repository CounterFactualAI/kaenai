import os
import argparse
import torch as pt
import pytorch_lightning as pl
from torch.distributed.elastic.multiprocessing.errors import record
from torch import nn
from torch.nn import functional as F
from torch.utils.data import TensorDataset, DataLoader
from torchvision.datasets import MNIST
from torchvision import datasets, transforms

from torch.utils.data.distributed import DistributedSampler

class MNISTClassifier(pl.LightningModule):

  #hyperparameters are passed using **kwargs
  def __init__(self, **kwargs):
    super(MNISTClassifier, self).__init__()

    #init hparams from the **kwargs
    self.save_hyperparameters()
    pt.manual_seed(int(self.hparams.seed))
    self.lr = float(self.hparams.lr)
    self.gamma = float(self.hparams.gamma)

    train_kwargs = {'batch_size': self.hparams.batch_size}
    test_kwargs = {'batch_size': self.hparams.test_batch_size}
    val_kwargs = {'batch_size': self.hparams.val_batch_size}

    if not self.hparams.no_cuda and pt.cuda.is_available():
        cuda_kwargs = {'pin_memory': True,
                      'shuffle': False}
        for ds in (train_kwargs, test_kwargs, val_kwargs):
          ds.update(cuda_kwargs)   
    self.train_kwargs = train_kwargs
    self.test_kwargs = test_kwargs
    self.val_kwargs = val_kwargs

    #prepare the datasets
    transform=transforms.Compose([transforms.ToTensor(), 
                              transforms.Normalize((0.1307,), (0.3081,))])
    self.mnist_train = MNIST('../data', train=True, download=True, transform=transform)
    self.mnist_test = MNIST('../data', train=False, download=True, transform=transform)
    self.mnist_val = MNIST('../data', train=False, download=True, transform=transform)


    #prepare the model
    self.conv1 = nn.Conv2d(1, 32, 3, 1)
    self.conv2 = nn.Conv2d(32, 64, 3, 1)
    self.dropout1 = nn.Dropout(0.25)
    self.dropout2 = nn.Dropout(0.5)
    self.fc1 = nn.Linear(9216, 128)
    self.fc2 = nn.Linear(128, 10)

  def train_dataloader(self):
    train_loader = pt.utils.data.DataLoader(self.mnist_train,
                        num_workers = 4,
                        **self.train_kwargs,
                        )

    return train_loader
		
  def test_dataloader(self):			
    test_loader = pt.utils.data.DataLoader(self.mnist_test, 
                                          **self.val_kwargs)
    return test_loader

  def val_dataloader(self):
    val_loader = pt.utils.data.DataLoader(self.mnist_val, 
    #                                      num_workers = 4,
                                          **self.test_kwargs)
    return val_loader

  def forward(self, x):

    x = self.conv1(x)
    x = F.relu(x)
    x = self.conv2(x)
    x = F.relu(x)
    x = F.max_pool2d(x, 2)
    x = self.dropout1(x)
    x = pt.flatten(x, 1)
    x = self.fc1(x)
    x = F.relu(x)
    x = self.dropout2(x)
    x = self.fc2(x)
    output = F.log_softmax(x, dim=1)

    return output

  def cross_entropy_loss(self, logits, labels):
    return F.nll_loss(logits, labels)

  def training_step(self, train_batch, batch_idx):
    x, y = train_batch
    logits = self.forward(x)
    loss = self.cross_entropy_loss(logits, y)

    logs = {'train_loss': loss}
    return {'loss': loss, 'log': logs}

  def validation_step(self, val_batch, batch_idx):
    x, y = val_batch
    logits = self.forward(x)
    loss = self.cross_entropy_loss(logits, y)
    self.log('val_loss', loss, prog_bar=True, sync_dist=True)
    return {'val_loss': loss}

  def test_step(self, val_batch, batch_idx):
    x, y = val_batch
    logits = self.forward(x)
    loss = self.cross_entropy_loss(logits, y)
    self.log('test_loss', loss, prog_bar=True, sync_dist = True)
    return {'test_loss': loss}

  def validation_epoch_end(self, outputs):
    avg_loss = pt.stack([x['val_loss'] for x in outputs]).mean()
    tensorboard_logs = {'val_loss': avg_loss}
    self.log('avg_val_loss', avg_loss, sync_dist=True)
    return {'avg_val_loss': avg_loss, 'log': tensorboard_logs}

  def test_epoch_end(self, outputs):
    avg_loss = pt.stack([x['test_loss'] for x in outputs]).mean()
    tensorboard_logs = {'test_loss': avg_loss}
    self.log('avg_test_loss', avg_loss, sync_dist=True)
    return {'avg_test_loss': avg_loss, 'log': tensorboard_logs}

  def configure_optimizers(self):
    optimizer = pt.optim.Adadelta(self.parameters(), lr=self.lr, )
    lr_scheduler = {'scheduler': pt.optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=self.gamma),
                    'name': 'step_lr'}

    return [optimizer], [lr_scheduler]
  
@record
def main(args):

  model = MNISTClassifier(**vars(args))

  trainer_kwargs = {'accelerator': 'cpu',
                    'num_nodes': int(os.environ['WORLD_SIZE'] if 'WORLD_SIZE' in os.environ else 1),
                    'strategy': 'ddp_find_unused_parameters_false',
                    }
  if not args.no_cuda and pt.cuda.is_available():
    trainer_kwargs = {
        'accelerator': 'gpu'
    }
    if pt.cuda.device_count() > 1:
        trainer_kwargs.update({
            'strategy': 'ddp_find_unused_parameters_false',
            'devices': '-1'
            })
  
  trainer = pl.Trainer(max_epochs=args.epochs, 
  #                    profiler = 'simple',
                        # num_nodes = 2,
                      default_root_dir=os.getcwd(),
                        **trainer_kwargs,) #gpus=1

  trainer.fit(model, 
              # train_dataloaders=train, 
              # val_dataloaders=val
              )    


  print(trainer.test(model,
                # dataloaders = test
                ))

if __name__ == '__main__':
  # Training settings
  parser = argparse.ArgumentParser(description='PyTorch Lightning MNIST Example')
  parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                      help='input batch size for training (default: 64)')
  parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                      help='input batch size for testing (default: 1000)')
  parser.add_argument('--val-batch-size', type=int, default=1000, metavar='N',
                      help='input batch size for validation (default: 1000)')    
  parser.add_argument('--epochs', type=int, default=14, metavar='N',
                      help='number of epochs to train (default: 14)')
  parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
                      help='learning rate (default: 1.0)')
  parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                      help='Learning rate step gamma (default: 0.7)')
  parser.add_argument('--distributed', action='store_true', default=False,
                      help='enables distributed training')
  parser.add_argument('--no-cuda', action='store_true', default=False,
                      help='disables CUDA training')
  parser.add_argument('--no-mps', action='store_true', default=False,
                      help='disables macOS GPU training')
  parser.add_argument('--dry-run', action='store_true', default=False,
                      help='quickly check a single pass')
  parser.add_argument('--seed', type=int, default=1, metavar='S',
                      help='random seed (default: 1)')
  parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                      help='how many batches to wait before logging training status')
  parser.add_argument('--save-model', action='store_true', default=False,
                      help='For Saving the current Model')
  args = parser.parse_args()    
  
  main(args)