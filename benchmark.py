import tensorflow as tf
import numpy as np
from n3fit.backends import operations as op
import time


REPLICAS = 100
FLAVORS = 14
BATCH = 1
GRIDPOINTS = 50
NDATA = 15
NDATA_TRAIN = 11  # after tr mask
MASK_FLAVORS = 9 ** 2

def create_random_tensor(tensor_shape, seed=42):
    np.random.seed(seed)
    np_array = np.random.normal(size=tensor_shape)
    tensor = tf.constant(np.random.normal(size=tensor_shape))
    return tensor

def define_inputs(seed):
    pdf = create_random_tensor((BATCH, GRIDPOINTS, FLAVORS, REPLICAS), seed=seed)
    fk = create_random_tensor((NDATA, MASK_FLAVORS, GRIDPOINTS, GRIDPOINTS), seed=seed+1)
    invcov = create_random_tensor((REPLICAS, NDATA_TRAIN, NDATA_TRAIN), seed=seed+2)

    # this needs to be a (FLAVORS, FLAVORS) boolean matrix with exactly 9^2 Trues
    basis_mask = np.zeros((FLAVORS, FLAVORS), dtype=bool)
    for i in range(9):
        for j in range(9):
            basis_mask[i, j] = True
    basis_mask = tf.constant(basis_mask)

    mask2 = create_random_tensor((NDATA, NDATA_TRAIN), seed=4)  # not sure how this is done
    return {
            'pdf': pdf,
            'fk': fk,
            'invcov': invcov,
            'basis_mask': basis_mask,
            'mask2': mask2,
            }

def compute(pdf, basis_mask, fk, invcov, mask2):
    "implementation more or less as in nnpdf"
    # next 3 lines out of pdf_masked_convolution:
    pdf = tf.squeeze(pdf, axis=0)  # (GRIDPOINTS, FLAVORS, REPLICAS)
    luminosity = tf.einsum('air,bjr->jibar', pdf, pdf)  # (FLAVORS, FLAVORS, GRIDPOINTS, GRIDPOINTS, REPLICAS)
    pdf_x_pdf = tf.boolean_mask(luminosity, basis_mask)  # (MASK_FLAVORS, GRIDPOINTS, GRIDPOINTS, REPLICAS)

    # next 3 lines in DY
    res = op.tensor_product(fk, pdf_x_pdf, axes=3)  # (NDATA, REPLICAS)
    ret = op.transpose(res)  # (REPLICAS, NDATA)
    DY_out = op.batchit(ret)  # (BATCH, REPLICAS, NDATA)

    # masking
    DY_out_masked = op.tensor_product(DY_out, mask2, axes=1)  # (BATCH, REPLICAS, NDATA_TRAIN)


    # loss
    # skipping the not so relevant lines:
    # tmp_raw = self._y_true - y_pred
    # tmp = op.op_multiply([tmp_raw, self.mask])
    y = DY_out_masked
    losses = op.einsum("bri, rij, brj -> r", y, invcov, y)  # (REPLICAS,)

    return losses

def compute_replicafirst(pdf, basis_mask, fk, invcov, mask2):
    pdf = tf.squeeze(pdf, axis=0)
    luminosity = tf.einsum('rxf,ryg->rgfyx', pdf, pdf)
    pdf_x_pdf = tf.boolean_mask(luminosity, basis_mask, axis=1)
    ret = tf.einsum('nfij, rfij -> rn', fk, pdf_x_pdf)
    DY_out = op.batchit(ret)  # (BATCH, REPLICAS, NDATA)
    DY_out_masked = op.tensor_product(DY_out, mask2, axes=1)  # (BATCH, REPLICAS, NDATA_TRAIN)
    y = DY_out_masked
    losses = op.einsum("bri, rij, brj -> r", y, invcov, y)  # (REPLICAS,)
    return losses

def compute_alltogether(pdf, basis_mask, fk, invcov, mask2):
    DY_out = tf.einsum('brxf, fgF, nFxy, bryg -> brn', pdf, basis_mask, fk, pdf)
    DY_out_masked = op.tensor_product(DY_out, mask2, axes=1)  # (BATCH, REPLICAS, NDATA_TRAIN)
    y = DY_out_masked
    losses = op.einsum("bri, rij, brj -> r", y, invcov, y)  # (REPLICAS,)
    return losses


def define_inputs_replicafirst(seed):
    inputs = define_inputs(seed)
    inputs['pdf'] = tf.transpose(inputs['pdf'], perm=[0, 3, 1, 2])
    return inputs

def define_inputs_alltogether(seed):
    inputs = define_inputs_replicafirst(seed)
    inputs['basis_mask'] = tensor_from_mask(inputs['basis_mask'])
    return inputs

def tensor_from_mask(mask):
    """
    Create a rank 3 tensor that replicates the functionality of tf.boolean_mask

    Args:
        mask: a rank 2 boolean tensor

    Returns:
        rank 3 tensor with shape (mask.shape[0], mask.shape[1], tf.reduce_sum(mask))
        of zeros and ones such that
        tf.boolean_mask(tensor, mask, axis=1) == tf.einsum('fg..., fgF -> F...', tensor, tensor_from_mask(mask))
    """
    mask_array = []
    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j] == True:
                temp_matrix = np.zeros((mask.shape[0], mask.shape[1]))
                temp_matrix[i, j] = 1
                mask_array.append(temp_matrix)
    mask = np.stack(mask_array, axis=-1)
    mask_tensor = tf.convert_to_tensor(mask)
    return mask_tensor

def timeit(nreps, create_inputs, function):
    inputs = create_inputs(42)
    start = time.time()
    for _ in range(nreps):
        function(**inputs)
    end = time.time()
    print(f"{function.__name__} took {end-start} seconds, {(end-start)/nreps} per call")

def test_equal():
    original = compute(**define_inputs(42))
    replicafirst = compute_replicafirst(**define_inputs_replicafirst(42))
    alltogether = compute_alltogether(**define_inputs_alltogether(42))
    # this gives really 0
    print(f"difference between original and replicafirst: {tf.reduce_sum(original - replicafirst)} (relative: {tf.reduce_sum(original - replicafirst)/tf.reduce_sum(original)})")
    # this gives 10^-15 for relative
    print(f"difference between original and alltogether: {tf.reduce_sum(original - alltogether)} (relative: {tf.reduce_sum(original - alltogether)/tf.reduce_sum(original)})")

#test_equal()

NREPS = 10
timeit(NREPS, define_inputs, compute)
timeit(NREPS, define_inputs_replicafirst, compute_replicafirst)
timeit(NREPS, define_inputs_alltogether, compute_alltogether)
