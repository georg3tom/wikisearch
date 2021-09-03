from omegaconf import DictConfig, OmegaConf, errors as OCErrors


def load_yaml(f):
    try:
        mapping = OmegaConf.load(f)
    except FileNotFoundError as e:
        raise e
    if mapping is None:
        mapping = OmegaConf.create()
    return mapping
