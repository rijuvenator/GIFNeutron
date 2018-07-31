#! /usr/bin/env python

import sys


##\brief static "constant" dictionary for ME11 mapping: <tt>CAENchannels['ME11name'] = [[board, ch],..[board,ch]]<\tt> for 6 layers
class ME11mapping:
    CAENchannels_={
        "CSC_ME_P11_C01": [[ 0,  6], [ 0,  7], [ 0,  8], [ 0,  9], [ 0, 10], [ 0, 11]],
        "CSC_ME_P11_C02": [[ 0, 12], [ 0, 13], [ 0, 14], [ 0, 15], [ 0, 16], [ 0, 17]],
        "CSC_ME_P11_C03": [[ 0, 18], [ 0, 19], [ 0, 20], [ 0, 21], [ 0, 22], [ 0, 23]],
        "CSC_ME_P11_C04": [[ 0, 24], [ 0, 25], [ 0, 26], [ 0, 27], [ 2,  0], [ 2,  1]],
        "CSC_ME_P11_C05": [[ 2,  2], [ 2,  3], [ 2,  4], [ 2,  5], [ 2,  6], [ 2,  7]],
        "CSC_ME_P11_C06": [[ 2,  8], [ 2,  9], [ 2, 10], [ 2, 11], [ 2, 12], [ 2, 13]],
        "CSC_ME_P11_C07": [[ 2, 14], [ 2, 15], [ 2, 16], [ 2, 17], [ 2, 18], [ 2, 19]],
        "CSC_ME_P11_C08": [[ 2, 20], [ 2, 21], [ 2, 22], [ 2, 23], [ 2, 24], [ 2, 25]],
        "CSC_ME_P11_C09": [[ 2, 26], [ 2, 27], [ 4,  0], [ 4,  1], [ 4,  2], [ 4,  3]],
        "CSC_ME_P11_C10": [[ 4,  4], [ 4,  5], [ 4,  6], [ 4,  7], [ 4,  8], [ 4,  9]],
        "CSC_ME_P11_C11": [[ 4, 10], [ 4, 11], [ 4, 12], [ 4, 13], [ 4, 14], [ 4, 15]],
        "CSC_ME_P11_C12": [[ 4, 16], [ 4, 17], [ 4, 18], [ 4, 19], [ 4, 20], [ 4, 21]],
        "CSC_ME_P11_C13": [[ 4, 22], [ 4, 23], [ 4, 24], [ 4, 25], [ 4, 26], [ 4, 27]],
        "CSC_ME_P11_C14": [[ 6,  0], [ 6,  1], [ 6,  2], [ 6,  3], [ 6,  4], [ 6,  5]],
        "CSC_ME_P11_C15": [[ 6,  6], [ 6,  7], [ 6,  8], [ 6,  9], [ 6, 10], [ 6, 11]],
        "CSC_ME_P11_C16": [[ 6, 12], [ 6, 13], [ 6, 14], [ 6, 15], [ 6, 16], [ 6, 17]],
        "CSC_ME_P11_C17": [[ 6, 18], [ 6, 19], [ 6, 20], [ 6, 21], [ 6, 22], [ 6, 23]],

        "CSC_ME_P11_C18": [[ 8,  0], [ 8,  1], [ 8,  2], [ 8,  3], [ 8,  4], [ 8,  5]],
        "CSC_ME_P11_C19": [[ 8,  6], [ 8,  7], [ 8,  8], [ 8,  9], [ 8, 10], [ 8, 11]],
        "CSC_ME_P11_C20": [[ 8, 12], [ 8, 13], [ 8, 14], [ 8, 15], [ 8, 16], [ 8, 17]],
        "CSC_ME_P11_C21": [[ 8, 18], [ 8, 19], [ 8, 20], [ 8, 21], [ 8, 22], [ 8, 23]],
        "CSC_ME_P11_C22": [[ 8, 24], [ 8, 25], [ 8, 26], [ 8, 27], [10,  0], [10,  1]],
        "CSC_ME_P11_C23": [[10,  2], [10,  3], [10,  4], [10,  5], [10,  6], [10,  7]],
        "CSC_ME_P11_C24": [[10,  8], [10,  9], [10, 10], [10, 11], [10, 12], [10, 13]],
        "CSC_ME_P11_C25": [[10, 14], [10, 15], [10, 16], [10, 17], [10, 18], [10, 19]],
        "CSC_ME_P11_C26": [[10, 20], [10, 21], [10, 22], [10, 23], [10, 24], [10, 25]],
        "CSC_ME_P11_C27": [[10, 26], [10, 27], [12,  0], [12,  1], [12,  2], [12,  3]],
        "CSC_ME_P11_C28": [[12,  4], [12,  4], [12,  6], [12,  7], [12,  8], [12,  9]],
        "CSC_ME_P11_C29": [[12, 10], [12, 11], [12, 12], [12, 13], [12, 14], [12, 15]],
        "CSC_ME_P11_C30": [[12, 16], [12, 17], [12, 18], [12, 19], [12, 20], [12, 21]],
        "CSC_ME_P11_C31": [[12, 22], [12, 23], [12, 24], [12, 25], [12, 26], [12, 27]],
        "CSC_ME_P11_C32": [[14,  0], [14,  1], [14,  2], [14,  3], [14,  4], [14,  5]],
        "CSC_ME_P11_C33": [[14,  6], [14,  7], [14,  8], [14,  9], [14, 10], [14, 11]],
        "CSC_ME_P11_C34": [[14, 12], [14, 13], [14, 14], [14, 15], [14, 16], [14, 17]],
        "CSC_ME_P11_C35": [[14, 18], [14, 19], [14, 20], [14, 21], [14, 22], [14, 23]],

        "CSC_ME_P11_C36": [[ 0,  0], [ 0,  1], [ 0,  2], [ 0,  3], [ 0,  4], [ 0,  5]],
        
        
        "CSC_ME_N11_C01": [[ 0,  6], [ 0,  7], [ 0,  8], [ 0,  9], [ 0, 10], [ 0, 11]],
        "CSC_ME_N11_C02": [[ 0, 12], [ 0, 13], [ 0, 14], [ 0, 15], [ 0, 16], [ 0, 17]],
        "CSC_ME_N11_C03": [[ 0, 18], [ 0, 19], [ 0, 20], [ 0, 21], [ 0, 22], [ 0, 23]],
        "CSC_ME_N11_C04": [[ 0, 24], [ 0, 25], [ 0, 26], [ 0, 27], [ 2,  0], [ 2,  1]],
        "CSC_ME_N11_C05": [[ 2,  2], [ 2,  3], [ 2,  4], [ 2,  5], [ 2,  6], [ 2,  7]],
        "CSC_ME_N11_C06": [[ 2,  8], [ 2,  9], [ 2, 10], [ 2, 11], [ 2, 12], [ 2, 13]],
        "CSC_ME_N11_C07": [[ 2, 14], [ 2, 15], [ 2, 16], [ 2, 17], [ 2, 18], [ 2, 19]],
        "CSC_ME_N11_C08": [[ 2, 20], [ 2, 21], [ 2, 22], [ 2, 23], [ 2, 24], [ 2, 25]],
        "CSC_ME_N11_C09": [[ 2, 26], [ 2, 27], [ 4,  0], [ 4,  1], [ 4,  2], [ 4,  3]],
        "CSC_ME_N11_C10": [[ 4,  4], [ 4,  5], [ 4,  6], [ 4,  7], [ 4,  8], [ 4,  9]],
        "CSC_ME_N11_C11": [[ 4, 10], [ 4, 11], [ 4, 12], [ 4, 13], [ 4, 14], [ 4, 15]],
        "CSC_ME_N11_C12": [[ 4, 16], [ 4, 17], [ 4, 18], [ 4, 19], [ 4, 20], [ 4, 21]],
        "CSC_ME_N11_C13": [[ 4, 22], [ 4, 23], [ 4, 24], [ 4, 25], [ 4, 26], [ 4, 27]],
        "CSC_ME_N11_C14": [[ 6,  0], [ 6,  1], [ 6,  2], [ 6,  3], [ 6,  4], [ 6,  5]],
        "CSC_ME_N11_C15": [[ 6,  6], [ 6,  7], [ 6,  8], [ 6,  9], [ 6, 10], [ 6, 11]],
        "CSC_ME_N11_C16": [[ 6, 12], [ 6, 13], [ 6, 14], [ 6, 15], [ 6, 16], [ 6, 17]],
        "CSC_ME_N11_C17": [[ 6, 18], [ 6, 19], [ 6, 20], [ 6, 21], [ 6, 22], [ 6, 23]],
                
        "CSC_ME_N11_C18": [[ 8,  0], [ 8,  1], [ 8,  2], [ 8,  3], [ 8,  4], [ 8,  5]],
        "CSC_ME_N11_C19": [[ 8,  6], [ 8,  7], [ 8,  8], [ 8,  9], [ 8, 10], [ 8, 11]],
        "CSC_ME_N11_C20": [[ 8, 12], [ 8, 13], [ 8, 14], [ 8, 15], [ 8, 16], [ 8, 17]],
        "CSC_ME_N11_C21": [[ 8, 18], [ 8, 19], [ 8, 20], [ 8, 21], [ 8, 22], [ 8, 23]],
        "CSC_ME_N11_C22": [[ 8, 24], [ 8, 25], [ 8, 26], [ 8, 27], [10,  0], [10,  1]],
        "CSC_ME_N11_C23": [[10,  2], [10,  3], [10,  4], [10,  5], [10,  6], [10,  7]],
        "CSC_ME_N11_C24": [[10,  8], [10,  9], [10, 10], [10, 11], [10, 12], [10, 13]],
        "CSC_ME_N11_C25": [[10, 14], [10, 15], [10, 16], [10, 17], [10, 18], [10, 19]],
        "CSC_ME_N11_C26": [[10, 20], [10, 21], [10, 22], [10, 23], [10, 24], [10, 25]],
        "CSC_ME_N11_C27": [[10, 26], [10, 27], [12,  0], [12,  1], [12,  2], [12,  3]],
        "CSC_ME_N11_C28": [[12,  4], [12,  4], [12,  6], [12,  7], [12,  8], [12,  9]],
        "CSC_ME_N11_C29": [[12, 10], [12, 11], [12, 12], [12, 13], [12, 14], [12, 15]],
        "CSC_ME_N11_C30": [[12, 16], [12, 17], [12, 18], [12, 19], [12, 20], [12, 21]],
        "CSC_ME_N11_C31": [[12, 22], [12, 23], [12, 24], [12, 25], [12, 26], [12, 27]],
        "CSC_ME_N11_C32": [[14,  0], [14,  1], [14,  2], [14,  3], [14,  4], [14,  5]],
        "CSC_ME_N11_C33": [[14,  6], [14,  7], [14,  8], [14,  9], [14, 10], [14, 11]],
        "CSC_ME_N11_C34": [[14, 12], [14, 13], [14, 14], [14, 15], [14, 16], [14, 17]],
        "CSC_ME_N11_C35": [[14, 18], [14, 19], [14, 20], [14, 21], [14, 22], [14, 23]],
                
        "CSC_ME_N11_C36": [[ 0,  0], [ 0,  1], [ 0,  2], [ 0,  3], [ 0,  4], [ 0,  5]]        
    }
    