import argparse
import os
import sys

import tifffile as tf
import numpy as np

_description = """Normalizes image stacks against background.

Uses background.tif if it already exists in the current working directory;
otherwise, computes the background image at each (x,y) location as the 5th
percentile of that location's value over the image stack.
"""

def main():
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument('--output', '-o', metavar='normalized.tif',
                        default='normalized.tif', help='Output filename')
    parser.add_argument('infile')
    args = parser.parse_args()

    infile = args.infile
    print 'Reading image stack'
    t = tf.TiffFile(infile)
    ar = tf.stack_pages(t.pages)
    n = ar.shape[0]

    if os.path.exists('background.tif'):
        print 'Reading background image'
        bg = tf.imread('background.tif')
    else:
        print 'Computing background image'
        sorted_ar = ar.copy()
        sorted_ar.sort(0)
        bg = sorted_ar[int(round(0.01*n,0))]
        print 'Saving background image'
        tf.imsave('background.tif', bg)
        del sorted_ar

    print 'Performing background normalization'
    ar = ar.astype(np.int16)
    for i in range(n):
        ar[i] -= bg
    ar[ar < 0] = 0
    ar = ar.astype(np.uint16)

    print 'Writing normalized image'
    with tf.TiffWriter(args.output) as out:
        for i in range(n):
            if (i % 100) == 0:
                print i,
                sys.stdout.flush()
            out.save(ar[i])
    print

if __name__ == "__main__":
    main()
