import torch
import pandas as pd
import numpy as np
from scvis import data
from encoder import VAE, LATENT_DIMENSION, LEARNING_RATE, BATCH_SIZE, MAX_EPOCH, CustomLoss, PERPLEXITY, L2_REGULARISATION
import datetime

MIN_ITER = 3000
MAX_ITER = 30000

# Script for housing
x = pd.read_csv('./Data/X.tsv', sep='\t').values
y = pd.read_csv('./Data/y.tsv', sep='\t').values
train_data = data.DataSet(x, y)

input_dim = x.shape[1]

# Neural net object, optimizer and criterion
net = VAE(input_dim, latent_dim=LATENT_DIMENSION)
net.train()
optimizer = torch.optim.Adam(net.parameters(), lr=LEARNING_RATE, betas=(0.9, 0.999), eps=0.001, weight_decay=L2_REGULARISATION)
criterion = CustomLoss(input_dim, net)

# Run a training epoch
iter_per_epoch = round(x.shape[0] / BATCH_SIZE)
iter_n = int(iter_per_epoch * MAX_EPOCH)
if iter_n < MIN_ITER:
    iter_n = MIN_ITER
elif iter_n > MAX_ITER:
    iter_n = np.max([MAX_ITER, iter_per_epoch * 2])

print("Started: "+ str(datetime.datetime.now().time()))
print("Total iterations: " + str(iter_n))
for iter_i in range(iter_n):
    if iter_i % 50 == 0:
        print("Iter: " + '{:>8}'.format(str(iter_i)) + "   " + str(datetime.datetime.now().time()))

    x_batch, y_batch = train_data.next_batch(BATCH_SIZE)

    # clears old gradients from the last step (otherwise you’d just accumulate the gradients from all loss.backward() calls).
    optimizer.zero_grad()

    p, z, encoder_mu, encoder_log_var, decoder_mu, decoder_log_var, dof = net(x_batch)
    loss = criterion(x_batch=x_batch,
                     p=p,
                     z_batch=z,
                     encoder_mu=encoder_mu,
                     encoder_log_var=encoder_log_var,
                     decoder_mu=decoder_mu,
                     decoder_log_var=decoder_log_var,
                     iter=iter_i+1,
                     dof=dof)

    # loss.backward() computes the derivative of the loss w.r.t. the parameters (or anything requiring gradients) using backpropagation.
    loss.backward()

    # TODO clip_gradient like in scvis
    torch.nn.utils.clip_grad_norm_(loss, max_norm=10.0)

    # optimizer.step() causes the optimizer to take a step based on the gradients of the parameters.
    optimizer.step()
print("Ended: "+ str(datetime.datetime.now().time()))

torch.save({
    'perplexity': PERPLEXITY,
    'regularizer': L2_REGULARISATION,
    'batch_size': BATCH_SIZE,
    'learning_rate': LEARNING_RATE,
    'latent_dimension': LATENT_DIMENSION,
    'activation': 'ELU',
    'model_state_dict': net.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
}, 'model.pt')

print(torch.load('model.pt')['model_state_dict'])