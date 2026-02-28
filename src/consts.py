import dataclasses
from pathlib import Path

from .vendor.ankiutils.consts import AddonConsts as BaseAddonConsts
from .vendor.ankiutils.consts import get_consts


@dataclasses.dataclass
class AddonConsts(BaseAddonConsts):
    userfiles_dir: Path
    dicts_dir: Path
    icons_dir: Path


base_consts = get_consts(__name__)
consts = AddonConsts(
    **dataclasses.asdict(base_consts),
    userfiles_dir=base_consts.dir / "user_files",
    dicts_dir=base_consts.dir / "user_files" / "dictionaries",
    icons_dir=base_consts.dir / "icons",
)
consts.dicts_dir.mkdir(exist_ok=True)
