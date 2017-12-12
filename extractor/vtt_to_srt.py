import os
import sys


def get_file_name(dir, file_extension):
    f_list = os.listdir(dir)

    result_list = []
    # print f_list
    for file_name in f_list:
        if os.path.splitext(file_name)[1] == file_extension:
            result_list.append(os.path.join(dir, file_name))
            print file_name
    return result_list


def change_vtt_to_srt(file_name):
    with open(file_name, 'r') as input_file:
        f_name_comp = os.path.splitext(file_name)[0]
        file_srt_name = f_name_comp + '.srt'
        with open(file_srt_name, 'w') as output_file:
            for line in input_file:
                if line[:6] != 'WEBVTT':
                    output_file.write(line.replace('.', ','))
    os.remove(file_name)

def vtt_to_srt(name):
    if os.path.isdir(name):
        file_list = get_file_name(name, ".vtt")
        for file in file_list:
            change_vtt_to_srt(file)
    elif os.path.isfile(name):
        change_vtt_to_srt(name)
    else:
        print("arg[0] should be file name or dir");
