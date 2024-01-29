#   Copyright 2023 DIAPath - CMMI Gosselies Belgium (diapath@cmmi.be)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import json, csv, sys, os
from tqdm.auto import tqdm
import vtoq

def main():
    fn_tsv, fn_json = sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None
    if len(sys.argv) != 3 or not os.path.exists(fn_tsv):
        print("Usage:\ntest_vtoq.py filename.tsv config.json")
        return

    #Here we defined the annotation classifications for QuPath (name, color as 6 bytes RGB hex value)
    with open(fn_json) as f:
        # The keys are the ROI indexes used in Visiopharm
        classes = {int(c): vtoq.Classification(name, int(rgb, 16)) for c, (name, rgb) in json.load(f).items()}

    #Iterate through the TSV file making dictionaries from the header line
    with open(fn_tsv, newline='') as csvfile:
        reader = list(csv.DictReader(csvfile, delimiter='\t'))
        pbar = tqdm(total=len(reader))
        for row in reader:
            fn_image = row['Image']
            fn_mld = row['LayerData']
            if not os.path.isfile(fn_image):
                pbar.set_description(f'{fn_image} does not exist')
            elif not os.path.isfile(fn_mld):
                pbar.set_description(f'{fn_mld} does not exist')
            else:
                pbar.set_description(f'Converting {fn_mld}')
                #This is NDPI specific, but the idea to split this function out of do_convert is that
                #maybe we'll be able to read the scale_factor and offset a different way
                scale_factor, offset = vtoq.get_scale_offset(fn_image)
                fn_json = os.path.join('json', f'{".".join(os.path.split(fn_image)[1].split(".")[:-1])}.json')
                vtoq.do_convert(fn_mld, fn_image, fn_json, classes=classes, overwrite=True, scale_factor=scale_factor, offset=offset)
            pbar.update(1)
        pbar.close()

if __name__ == '__main__':
    main()
