import torch

from pytorch_complex_tensor import ComplexTensor
from pylops_gpu.utils.complex import conj
from pylops_gpu import LinearOperator, aslinearoperator


def cg(A, y, x=None, niter=10, tol=1e-10):
    """Conjugate gradient

    Solve a system of equations given the square operator ``A`` and data ``y``
    using conjugate gradient iterations.

    Parameters
    ----------
    A : :obj:`torch.Tensor` or :obj:`pylops_gpu.LinearOperator`
        Operator to invert of size :math:`[N \times N]`
    y : :obj:`torch.Tensor`
        Data of size :math:`[N \times 1]`
    x0 : :obj:`torch.Tensor`, optional
        Initial guess
    niter : :obj:`int`
        Number of iterations
    tol : :obj:`int`
        Residual norm tolerance

    Returns
    -------
    x : :obj:`torch.Tensor`
        Estimated model
    iiter : :obj:`torch.Tensor`
        Max number of iterations model
    """
    complex_problem = True if isinstance(y, ComplexTensor) else False
    if not isinstance(A, LinearOperator):
        A = aslinearoperator(A)
    if x is None:
        if complex_problem:
            x = ComplexTensor(torch.zeros((2 * y.shape[-1], 1),
                                          dtype=y.dtype)).t()
        else:
            x = torch.zeros_like(y)

    r = y - A.matvec(x)
    d = r.clone()
    if complex_problem:
        d = ComplexTensor(d)
        kold = torch.sum(conj(r) * r)
    else:
        kold = torch.sum(r * r)
    iiter = 0
    while iiter < niter and kold > tol:
        Ad = A.matvec(d)
        dAd = torch.sum(conj(d) * Ad) if complex_problem else torch.sum(d * Ad)
        a = kold / dAd
        x += a * d
        r -= a * Ad
        k = torch.sum(conj(r) * r) if complex_problem else torch.sum(r * r)
        b = k / kold
        d = r + b * d
        kold = k
        iiter += 1
    return x, iiter