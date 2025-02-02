from typing import Callable, Iterable, Tuple

import torch
import math
from torch.optim import Optimizer


class AdamW(Optimizer):
    def __init__(
            self,
            params: Iterable[torch.nn.parameter.Parameter],
            lr: float = 1e-3,
            betas: Tuple[float, float] = (0.9, 0.999),
            eps: float = 1e-6,
            weight_decay: float = 0.0,
            correct_bias: bool = True,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {} - should be >= 0.0".format(eps))
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, correct_bias=correct_bias)
        super().__init__(params, defaults)


    def step(self, closure: Callable = None):
        loss = None
        if closure is not None:
            loss = closure()
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")
                # State should be stored in this dictionary
                state = self.state[p]
                if len(state) == 0:
                    state['m1'] = torch.zeros_like(grad)
                    state['m2'] = torch.zeros_like(grad)
                    state['step'] = 0
                state['step'] += 1
                # Access hyperparameters from the `group` dictionary
                alpha = group["lr"]
                beta1, beta2 = group['betas']
                eps =  group['eps']
                lambda_ = group['weight_decay']
                correct_bias = group['correct_bias']
                # Update first and second moments of the gradients
                grad = grad + lambda_* p.data # weight decay
                m1 = beta1*state['m1']+(1-beta1)*grad
                m2 = beta2*state['m2']+(1-beta2)*grad**2
                # Bias correction
                if correct_bias:
                    m1_bias_corr = m1/(1-(beta1**state['step']))
                    m2_bias_corr = m2/(1-(beta2**state['step']))
                # Please note that we are using the "efficient version" given in
                # https://arxiv.org/abs/1412.6980
                # Update parameters
                # Add weight decay after the main gradient-based updates.
                # Please note that the learning rate should be incorporated into this update.
                p.data = p.data - 1.*(alpha*m1_bias_corr/(torch.sqrt(m2_bias_corr)+eps) + alpha*lambda_*p.data) # weight decay term
                state['m1'] = m1
                state['m2'] = m2
        return loss


    def step(self, closure: Callable = None):
        loss = None
        if closure is not None:
            loss = closure()
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")
                # State should be stored in this dictionary
                state = self.state[p]
                if len(state) == 0:
                    state['m1'] = torch.zeros_like(grad)
                    state['m2'] = torch.zeros_like(grad)
                    state['step'] = 0
                state['step'] += 1
                # Access hyperparameters from the `group` dictionary
                alpha = group["lr"]
                beta1, beta2 = group['betas']
                eps =  group['eps']
                lambda_ = group['weight_decay']
                correct_bias = group['correct_bias']
                # Update first and second moments of the gradients
                p.data = p.data - lambda_*alpha*p.data  # weight decay
                m1 = beta1*state['m1']+(1-beta1)*grad
                m2 = beta2*state['m2']+(1-beta2)*grad**2
                # Bias correction
                if correct_bias:
                    m1_bias_corr = m1/(1-(beta1**state['step']))
                    m2_bias_corr = m2/(1-(beta2**state['step']))
                # Please note that we are using the "efficient version" given in
                # https://arxiv.org/abs/1412.6980
                # Update parameters
                # Add weight decay after the main gradient-based updates.
                # Please note that the learning rate should be incorporated into this update.
                p.data = p.data - 1.*(alpha*m1_bias_corr/(torch.sqrt(m2_bias_corr)+eps)) # weight decay term
                state['m1'] = m1
                state['m2'] = m2
        return loss
