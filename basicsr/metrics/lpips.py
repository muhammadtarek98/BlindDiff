import cv2
import numpy as np
from torchvision.transforms.functional import normalize
from BlindDiff.basicsr.metrics.metric_util import reorder_image, to_y_channel
from BlindDiff.basicsr.utils.registry import METRIC_REGISTRY
from BlindDiff.basicsr.utils import img2tensor
try:
    import lpips
except ImportError:
    print('Please install lpips: pip install lpips')


@METRIC_REGISTRY.register()
def calculate_lpips(img, img2, crop_border, loss_fn_vgg, input_order='HWC', test_y_channel=False,  **kwargs):
    """Calculate PSNR (Peak Signal-to-Noise Ratio).

    Ref: https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio

    Args:
        img (ndarray): Images with range [0, 255].
        img2 (ndarray): Images with range [0, 255].
        crop_border (int): Cropped pixels in each edge of an image. These
            pixels are not involved in the PSNR calculation.
        input_order (str): Whether the input order is 'HWC' or 'CHW'.
            Default: 'HWC'.
        test_y_channel (bool): Test on Y channel of YCbCr. Default: False.

    Returns:
        float: psnr result.
    """

    assert img.shape == img2.shape, (f'Image shapes are different: {img.shape}, {img2.shape}.')
    if input_order not in ['HWC', 'CHW']:
        raise ValueError(f'Wrong input_order {input_order}. Supported input_orders are ' '"HWC" and "CHW"')
    img = reorder_image(img, input_order=input_order)
    img2 = reorder_image(img2, input_order=input_order)
    img = img.astype(np.float64) /255.
    img2 = img2.astype(np.float64) /255.

    mean = [0.5, 0.5, 0.5]
    std = [0.5, 0.5, 0.5]

    if crop_border != 0:
        img = img[crop_border:-crop_border, crop_border:-crop_border, ...]
        img2 = img2[crop_border:-crop_border, crop_border:-crop_border, ...]

    img, img2 = img2tensor([img, img2], bgr2rgb=True, float32=True)

    normalize(img, mean, std, inplace=True)
    normalize(img2, mean, std, inplace=True)

    lpips_val = loss_fn_vgg(img.unsqueeze(0).cuda(), img2.unsqueeze(0).cuda())
    

    return lpips_val.item()
