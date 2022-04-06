import ndspy.rom
import ndspy.narc
import hashlib
from Buffer import Buffer
import pickle


class PatchCreator:
    def __init__(self, modified_rom, original_rom):
        self.modified = ndspy.rom.NintendoDSRom.fromFile(modified_rom)
        self.original = ndspy.rom.NintendoDSRom.fromFile(original_rom)
        self.patches = []

    def create(self):
        for index in range(len(self.modified.files)):
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
                    self.patches.append(narc_patch)
                else:
                    self.patches.append(Patch(index, modified_file))
        return self.patches

    def pickle(self, output_file):
        with open(output_file, 'wb') as out_file:
            pickle.dump(self.patches, out_file)


class PatchApplier:
    def __init__(self, patch_file, rom):
        with open(patch_file, 'rb') as in_file:
            self.patches = pickle.load(in_file)
        self.rom = ndspy.rom.NintendoDSRom.fromFile(rom)

    def apply(self):
        for patch in self.patches:
            if isinstance(patch, list):
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
                self.rom.files[patch.file_id] = patch.data

    def write(self, output_file):
        self.rom.saveToFile(output_file)


class Patch:
    def __init__(self, file_id, data, sub_file_id=-1):
        self.file_id = file_id
        self.data = data
        self.sub_file_id = sub_file_id

    def __str__(self):
        if self.sub_file_id == -1:
            return 'File %i with data %s' % (self.file_id, str(self.data))
        else:
            return 'File %i sub-file %i with data %s' % (self.file_id, self.sub_file_id, str(self.data))
