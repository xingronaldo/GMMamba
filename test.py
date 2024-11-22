from util.metric_tool import ConfuseMatrixMeter
import torch
from option import Options
from data.cd_dataset import DataLoader
from model.create_model import create_model
from tqdm import tqdm
import os
import numpy as np
from skimage import io

if __name__ == '__main__':
    opt = Options().parse()
    opt.phase = 'test'
    test_loader = DataLoader(opt)
    test_data = test_loader.load_data()
    test_size = len(test_loader)
    print("#testing images = %d" % test_size)

    opt.load_pretrain = True
    model = create_model(opt)

    tbar = tqdm(test_data, ncols=80)
    total_iters = test_size
    running_metric = ConfuseMatrixMeter(n_class=2)
    running_metric.clear()

    model.eval()
    with torch.no_grad():
        for i, _data in enumerate(tbar):
            val_pred = model.inference(_data['img1'].cuda(), _data['img2'].cuda())
            # update metric
            val_target = _data['cd_label'].detach()
            val_pred = torch.argmax(val_pred.detach(), dim=1)
            save_path = os.path.join(opt.result_dir, str(_data['fname'][0]).split('.')[0] + '.png')
            val_pred_ = val_pred[0].cpu().numpy() * 255
            io.imsave(save_path, np.array(np.squeeze(val_pred_), dtype=np.uint8))
            _ = running_metric.update_cm(pr=val_pred.cpu().numpy(), gt=val_target.cpu().numpy())
        val_scores = running_metric.get_scores()
        message = '(phase: %s) ' % (opt.phase)
        for k, v in val_scores.items():
            message += '%s: %.3f ' % (k, v * 100)
        print(message)