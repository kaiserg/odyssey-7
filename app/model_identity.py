"""Cheap local weight-change detection after a successful adapter validation."""


def weight_stamp(model):
    files = sorted(model.glob('*.safetensors'))
    if not files:
        raise ValueError('No local model weights found')
    return {file.name: {'bytes': file.stat().st_size, 'mtime_ns': file.stat().st_mtime_ns}
            for file in files}
