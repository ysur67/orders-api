import os
import shutil
from pathlib import Path, PosixPath
from typing import Iterable, List, Optional


def create_directory(target_dir: PosixPath, dir_name: str) -> PosixPath:
    full_path = target_dir / dir_name
    Path(full_path).mkdir(parents=True, exist_ok=True)
    return full_path


def get_directory_by_name(path: PosixPath, name: str) -> Optional[PosixPath]:
    result = [obj for obj in path.iterdir() if obj.is_dir()
              and obj.name == name]
    if not result:
        return None
    if len(result) == 1:
        return result[0]
    raise ValueError(f"Check import directory {path}")


def remove_file(path_: str) -> bool:
    try:
        os.remove(path_)
        return True
    except FileNotFoundError:
        return False


def move_file_or_directory(
    path_: PosixPath,
    target_dir: PosixPath,
) -> None:
    object_ = str(path_.absolute())
    to_dir = str(target_dir.absolute())
    if path_.is_dir():
        return shutil.copytree(object_, to_dir, dirs_exist_ok=True)
    elif path_.is_file():
        _ = remove_file(f'{to_dir}/{path_.name}')
        return shutil.move(object_, to_dir)
    raise NotImplementedError(f'There is no approach for {path_.absolute()}')


def get_files_by_ext(dir_path: PosixPath, ext: str) -> List[PosixPath]:
    return list(dir_path.glob(f'**/*.{ext}'))


def get_file_by_name(files: List[PosixPath], file_name: str) -> Optional[PosixPath]:
    for file_ in files:
        if file_name in file_.name:
            return file_
    return None


def remove_directory(path_: PosixPath, raise_exception: bool = False):
    return shutil.rmtree(str(path_.absolute()), ignore_errors=not raise_exception)


def get_files_from_dir(path: Path) -> Iterable:
    dir_ = path.glob("*.*")
    return [obj for obj in dir_ if obj.is_file()]


def check_if_file_exist(path: Path) -> bool:
    try:
        with open(path, 'rb') as _:
            return True
    except FileNotFoundError:
        return False


def is_file(path: Path) -> bool:
    return Path.is_file(path)


def write_in_file(path: Path, body: str) -> None:
    with open(path, 'w') as file:
        file.write(body)
