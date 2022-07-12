from enum import Enum

import crcmod
import ndspy.rom
import ndspy.narc
import hashlib
from Buffer import Buffer
import pickle
import xdelta3


class PatchCreator:
    def __init__(self, modified_rom, original_rom):
        self.modified = ndspy.rom.NintendoDSRom.fromFile(modified_rom)
        self.original = ndspy.rom.NintendoDSRom.fromFile(original_rom)
        self.patches = []
        self.xdelta = False
        self.game_code = self.original.idCode

    def create(self):
        num_overlays = int(len(self.modified.arm9OverlayTable) / 32)
        for index in range(num_overlays, len(self.modified.files)):
            modified_file = self.modified.files[index]
            original_file = self.original.files[index]

            if modified_file != original_file:
                narc = False
                buffer = Buffer(self.modified.files[index])
                if buffer.read_bytes(4) == 'NARC'.encode():
                    narc = True

                if narc:
                    narc_patch = []
                    modified_narc = ndspy.narc.NARC(modified_file)
                    original_narc = ndspy.narc.NARC(original_file)
                    for sub_index in range(len(modified_narc.files)):
                        if sub_index < len(original_narc.files):
                            modified_sub_file = modified_narc.files[sub_index]
                            original_sub_file = original_narc.files[sub_index]

                            if modified_sub_file != original_sub_file:
                                narc_patch.append(Patch(index, modified_sub_file, sub_file_id=sub_index))
                        else:
                            modified_sub_file = modified_narc.files[sub_index]
                            narc_patch.append(Patch(index, modified_sub_file, sub_file_id=sub_index))
                    if len(narc_patch) != 0:
                        self.patches.append(narc_patch)
                else:
                    self.patches.append(Patch(index, modified_file))

        for index in range(num_overlays):
            self.create_for_binaries(self.modified.files[index], self.original.files[index], index)
        self.create_for_binaries(self.modified.arm9, self.original.arm9, BinaryIds.ARM9)
        self.create_for_binaries(self.modified.arm7, self.original.arm7, BinaryIds.ARM7)
        self.create_for_binaries(self.modified.arm9OverlayTable, self.original.arm9OverlayTable, BinaryIds.Y9)
        self.create_for_binaries(self.modified.arm7OverlayTable, self.original.arm7OverlayTable, BinaryIds.Y7)
        self.create_for_binaries(self.modified.iconBanner, self.original.iconBanner, BinaryIds.ICON_BANNER)

    def create_for_binaries(self, modified_file, original_file, index):
        if modified_file != original_file:
            self.xdelta = True
            delta = xdelta3.encode(bytes(original_file), bytes(modified_file))
            self.patches.append(Patch(index, delta, binary=True))

    def pickle(self, output_file):
        with open(output_file, 'wb') as out_file:
            pickle.dump(PatchContainer(self.patches, self.xdelta, self.game_code), out_file)


class PatchApplier:

    def __init__(self, patch_file, rom):
        self.valid_patch = self.PatchValidation.INVALID_PATCH_FILE

        with open(rom, 'rb') as in_data:
            if len(in_data.read()) < 0x200:
                self.valid_patch = self.PatchValidation.INVALID_ROM_FILE
                return
        self.rom = ndspy.rom.NintendoDSRom.fromFile(rom)

        with open(patch_file, 'rb') as in_file:
            container = pickle.load(in_file)

        if isinstance(container, PatchContainer):
            self.patches = container.patches
            self.game_code = container.game_code
            self.valid_patch = self.PatchValidation.VALID
        else:
            return

        if not self.rom.idCode.startswith(self.game_code):
            self.valid_patch = self.PatchValidation.INVALID_ROM_GAME_CODE
            return

    def apply(self):
        for patch in self.patches:
            if isinstance(patch, list):  # file is a narc
                index = patch[0].file_id
                narc = ndspy.narc.NARC(self.rom.files[index])
                for sub_patch in patch:
                    if sub_patch.sub_file_id < len(narc.files):
                        narc.files[sub_patch.sub_file_id] = sub_patch.data
                    else:
                        while len(narc.files) <= sub_patch.sub_file_id:
                            narc.files.append(bytearray(0))
                        narc.files[sub_patch.sub_file_id] = sub_patch.data
                self.rom.files[index] = narc.save()
            else:
                if not patch.binary:  # file is not a code binary
                    self.rom.files[patch.file_id] = patch.data
                else:  # file is a code binary
                    if patch.file_id >= 0:  # file is not arm9 or arm7 - therefore is overlay
                        self.rom.files[patch.file_id] = bytearray(xdelta3.decode(bytes(self.rom.files[patch.file_id]), patch.data))
                    else:  # file is arm9 or arm7
                        if patch.file_id == BinaryIds.ARM9:  # file is arm9
                            self.rom.arm9 = bytearray(xdelta3.decode(bytes(self.rom.arm9), patch.data))
                        elif patch.file_id == BinaryIds.ARM7:  # file is arm7
                            self.rom.arm7 = bytearray(xdelta3.decode(bytes(self.rom.arm7), patch.data))
                        elif patch.file_id == BinaryIds.Y9:  # file is y9
                            self.rom.arm9OverlayTable = bytearray(
                                xdelta3.decode(bytes(self.rom.arm9OverlayTable), patch.data))
                        elif patch.file_id == BinaryIds.Y7:  # file is y7
                            self.rom.arm7OverlayTable = bytearray(
                                xdelta3.decode(bytes(self.rom.arm7OverlayTable), patch.data))
                        elif patch.file_id == BinaryIds.ICON_BANNER:  # file is icon/banner
                            self.rom.iconBanner = bytearray(xdelta3.decode(bytes(self.rom.iconBanner), patch.data))

    def write(self, output_file):
        self.rom.saveToFile(output_file)

    class PatchValidation(Enum):
        VALID = 0
        INVALID_PATCH_FILE = 1
        INVALID_ROM_FILE = 2
        INVALID_ROM_GAME_CODE = 3


class BinaryIds(Enum):
    ARM9 = -1
    ARM7 = -2
    Y9 = -3
    Y7 = -4
    ICON_BANNER = -5

class Patch:
    def __init__(self, file_id, data, sub_file_id=-1, binary=False):
        self.file_id = file_id
        self.data = data
        self.sub_file_id = sub_file_id
        self.binary = binary

    def __str__(self):
        file_type = 'File'
        if self.binary:
            file_type = 'Binary'
        if self.sub_file_id == -1:
            return '%s %i with data %s' % (file_type, self.file_id, str(self.data))
        else:
            return 'File %i sub-file %i with data %s' % (self.file_id, self.sub_file_id, str(self.data))


class PatchContainer:
    def __init__(self, patches, xdelta, game_code):
        self.patches = patches
        self.xdelta = xdelta
        if xdelta:
            self.game_code = game_code
        else:
            self.game_code = game_code[:3]
